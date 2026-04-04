"""
CUFA 보고서 품질 검증 엔진 (Evaluator v2)
HARD_MIN + SMIC 문체 + 할루시네이션 탐지 + 섹션별 글자수 검증
"""
import re
import sys
from typing import Optional


# ── 섹션별 최소 글자수 ──────────────────────────────────────
SECTION_MIN_CHARS: dict[str, int] = {
    'sec1': 3000,
    'sec2': 10000,
    'sec3': 4000,
    'sec4': 4000,
    'sec5': 4000,
    'sec6': 5000,
    'sec7': 3000,
    'sec8': 5000,
    'sec9': 4000,
    'sec10': 3000,
    'sec11': 2000,
}

# ── 할루시네이션 탐지 패턴 ──────────────────────────────────
HALLUCINATION_PATTERNS: list[re.Pattern] = [
    re.compile(r'약\s*\d+[%%]'),
    re.compile(r'대략\s*\d+'),
    re.compile(r'정도로\s*추정'),
    re.compile(r'일반적으로\s*\d+'),
    re.compile(r'보통\s*\d+'),
    re.compile(r'통상적으로'),
]

# ── 교차 참조 패턴 ──────────────────────────────────────────
CROSS_REF_PATTERNS: list[str] = [
    '전술한', '후술할', '전술했듯이', '앞서 언급한', '후술하는',
    '앞서 살펴본', '뒤에서 다룰', '상기한', '하기에서',
]

# ── 전환어 ──────────────────────────────────────────────────
TRANSITION_WORDS: list[str] = [
    '전술한', '그렇다면', '이에 더해', '한편', '이처럼',
    '실제로', '다만', '특히', '결국', '반면', '나아가',
    '요컨대', '따라서', '그럼에도', '물론',
]


def _strip_tags(html: str) -> str:
    """HTML 태그 제거, 텍스트만 추출."""
    return re.sub(r'<[^>]+>', '', html)


def _extract_paragraphs(html: str) -> list[str]:
    """<p>...</p> 태그 내용 추출 (raw HTML 포함)."""
    return re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)


def _extract_section_text(html: str, sec_id: str) -> str:
    """id="secN" 섹션의 텍스트를 추출한다.
    해당 id를 가진 요소부터 다음 동일 레벨 섹션(sec N) 또는 EOF까지."""
    pattern = r'id="' + re.escape(sec_id) + r'"[^>]*>(.*?)(?=id="sec\d+"|$)'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return ''
    return _strip_tags(match.group(1))


def _count_bold_first_sentences(html: str) -> tuple[int, list[dict]]:
    """<p><strong> 또는 <p> <strong>으로 시작하는 단락 수 + 미준수 목록."""
    paragraphs = _extract_paragraphs(html)
    bold_count = 0
    violations: list[dict] = []

    for i, p in enumerate(paragraphs):
        stripped = p.strip()
        # 빈 단락이나 짧은 단락(50자 미만)은 건너뜀
        text_only = _strip_tags(stripped)
        if len(text_only.strip()) < 50:
            continue
        if re.match(r'^<strong\b', stripped) or re.match(r'^\s*<strong\b', stripped):
            bold_count += 1
        else:
            preview = _strip_tags(stripped)[:20]
            violations.append({'index': i, 'preview': preview})

    return bold_count, violations


def _detect_hallucinations(html: str) -> list[dict]:
    """할루시네이션 의심 패턴 검출."""
    text = _strip_tags(html)
    findings: list[dict] = []
    for pat in HALLUCINATION_PATTERNS:
        for m in pat.finditer(text):
            start = max(0, m.start() - 15)
            end = min(len(text), m.end() + 15)
            context = text[start:end].replace('\n', ' ')
            findings.append({
                'pattern': pat.pattern,
                'match': m.group(),
                'context': f'...{context}...',
            })
    return findings


def _section_char_counts(html: str) -> dict[str, int]:
    """sec1~sec11 각 섹션 텍스트 글자수."""
    counts: dict[str, int] = {}
    for sec_id in SECTION_MIN_CHARS:
        text = _extract_section_text(html, sec_id)
        counts[sec_id] = len(text.replace(' ', '').replace('\n', ''))
    return counts


def _avg_paragraph_length(html: str) -> float:
    """<p> 태그 내 텍스트 평균 길이 (공백 포함)."""
    paragraphs = _extract_paragraphs(html)
    lengths = []
    for p in paragraphs:
        text = _strip_tags(p).strip()
        if len(text) > 10:  # 의미 있는 단락만
            lengths.append(len(text))
    if not lengths:
        return 0.0
    return sum(lengths) / len(lengths)


def _text_bar(value: int, target: int, width: int = 40) -> str:
    """텍스트 기반 바 차트 한 줄."""
    ratio = min(value / target, 2.0) if target > 0 else 0
    filled = int(ratio * width / 2)  # 100% = width/2, 200% = width
    bar = '█' * filled + '░' * (width - filled)
    pct = int(ratio * 100)
    status = '✓' if value >= target else '✗'
    return f'{bar} {value:>6,}/{target:>6,} ({pct:>3}%) {status}'


def evaluate(html_path: str, *, style_report: bool = False) -> dict:
    """HTML 보고서를 읽고 품질 점수를 산출한다."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    text_only = _strip_tags(html)
    text_chars = len(text_only.replace(' ', '').replace('\n', ''))

    results: dict = {}

    # === HARD_MIN ===
    results['text_chars'] = text_chars
    results['svg_count'] = html.count('<svg ')
    results['table_count'] = html.count('<table')
    results['h2h3_count'] = html.count('<h2') + html.count('<h3')
    results['file_bytes'] = len(html.encode('utf-8'))

    # === SMIC 문체 검증 (기존) ===
    results['dongsa_count'] = html.count('동사')
    results['strong_count'] = html.count('<strong>')
    results['transition_words'] = sum(html.count(w) for w in TRANSITION_WORDS)
    results['counter_arg_count'] = html.count('counter-arg')

    # === SMIC 문체 검증 (v2 추가) ===
    bold_count, bold_violations = _count_bold_first_sentences(html)
    results['bold_first_sentence'] = bold_count
    results['bold_violations'] = bold_violations
    results['avg_paragraph_len'] = _avg_paragraph_length(html)
    results['cross_reference'] = sum(html.count(w) for w in CROSS_REF_PATTERNS)
    results['callout_count'] = len(re.findall(r'class=["\'][^"\']*callout[^"\']*["\']', html))
    results['chart_insight_count'] = len(re.findall(r'class=["\'][^"\']*chart-insight[^"\']*["\']', html))

    # === 할루시네이션 탐지 ===
    results['hallucinations'] = _detect_hallucinations(html)

    # === 섹션별 글자수 ===
    results['section_chars'] = _section_char_counts(html)

    # === 판정: HARD_MIN ===
    hard_min = {
        'text_80k': (text_chars >= 80000, f'{text_chars:,}/80,000'),
        'svg_25': (results['svg_count'] >= 25, f'{results["svg_count"]}/25'),
        'tables_25': (results['table_count'] >= 25, f'{results["table_count"]}/25'),
        'h2h3_20': (results['h2h3_count'] >= 20, f'{results["h2h3_count"]}/20'),
    }

    # === 판정: SMIC_STYLE ===
    avg_plen = results['avg_paragraph_len']
    smic_style = {
        'dongsa_ratio': (
            40 <= results['dongsa_count'] <= 120,
            f'{results["dongsa_count"]} (40~120)',
        ),
        'transitions_30': (
            results['transition_words'] >= 30,
            f'{results["transition_words"]}/30+',
        ),
        'counter_args_3': (
            results['counter_arg_count'] >= 3,
            f'{results["counter_arg_count"]}/3+',
        ),
        'bold_first_150': (
            bold_count >= 150,
            f'{bold_count}/150+',
        ),
        'avg_para_len': (
            150 <= avg_plen <= 450,
            f'{avg_plen:.0f} (150~450)',
        ),
        'cross_ref_5': (
            results['cross_reference'] >= 5,
            f'{results["cross_reference"]}/5+',
        ),
        'callout_3': (
            results['callout_count'] >= 3,
            f'{results["callout_count"]}/3+',
        ),
        'chart_insight': (
            results['chart_insight_count'] > 0,
            f'{results["chart_insight_count"]} (bonus)',
        ),
    }

    # === 판정: 섹션별 글자수 ===
    section_results: dict[str, tuple[bool, str]] = {}
    for sec_id, min_chars in SECTION_MIN_CHARS.items():
        actual = results['section_chars'].get(sec_id, 0)
        section_results[sec_id] = (
            actual >= min_chars,
            f'{actual:,}/{min_chars:,}',
        )

    results['hard_min'] = hard_min
    results['smic_style'] = smic_style
    results['section_results'] = section_results

    # ── 출력 ────────────────────────────────────────────────
    print(f'\n{"=" * 60}')
    print(f'  CUFA Evaluator v2: {html_path}')
    print(f'{"=" * 60}')
    print(f'Text: {text_chars:,} chars | SVG: {results["svg_count"]} '
          f'| Tables: {results["table_count"]} | Size: {results["file_bytes"]:,} bytes')

    # HARD_MIN
    print(f'\n--- HARD_MIN ---')
    all_pass = True
    for name, (passed, detail) in hard_min.items():
        status = 'PASS' if passed else 'FAIL'
        if not passed:
            all_pass = False
        print(f'  [{status}] {name}: {detail}')

    # SMIC Style
    print(f'\n--- SMIC_STYLE ---')
    for name, (passed, detail) in smic_style.items():
        status = 'PASS' if passed else 'WARN'
        print(f'  [{status}] {name}: {detail}')

    # 섹션별 글자수
    print(f'\n--- SECTION CHARS ---')
    for sec_id, (passed, detail) in section_results.items():
        status = 'PASS' if passed else 'FAIL'
        if not passed:
            all_pass = False
        print(f'  [{status}] {sec_id}: {detail}')

    # 할루시네이션
    hallu = results['hallucinations']
    if hallu:
        print(f'\n--- HALLUCINATION WARNING ({len(hallu)} hits) ---')
        for h in hallu[:15]:  # 최대 15개
            print(f'  [WARN] "{h["match"]}" → {h["context"]}')
        if len(hallu) > 15:
            print(f'  ... +{len(hallu) - 15} more')

    # 최종 판정
    print(f'\n{"ALL PASS" if all_pass else "FAILED — 보강 필요"}')

    # ── --style-report 모드 ─────────────────────────────────
    if style_report:
        _print_style_report(results)

    return results


def _print_style_report(results: dict) -> None:
    """상세 스타일 리포트 출력."""
    print(f'\n{"=" * 60}')
    print(f'  STYLE REPORT (상세)')
    print(f'{"=" * 60}')

    # 1) bold 미준수 단락
    violations = results.get('bold_violations', [])
    print(f'\n--- Bold 미준수 단락 ({len(violations)}건) ---')
    for v in violations[:30]:  # 최대 30개
        print(f'  [WARN] 단락 {v["index"]}: bold 없음 — "{v["preview"]}..."')
    if len(violations) > 30:
        print(f'  ... +{len(violations) - 30} more')

    # 2) 할루시네이션 전체 리스트
    hallu = results.get('hallucinations', [])
    print(f'\n--- 할루시네이션 패턴 ({len(hallu)}건) ---')
    for h in hallu:
        print(f'  [WARN] pattern=/{h["pattern"]}/ match="{h["match"]}" → {h["context"]}')

    # 3) 섹션별 글자수 바 차트
    section_chars = results.get('section_chars', {})
    print(f'\n--- 섹션별 글자수 바 차트 ---')
    for sec_id, min_chars in SECTION_MIN_CHARS.items():
        actual = section_chars.get(sec_id, 0)
        bar = _text_bar(actual, min_chars)
        print(f'  {sec_id:>5}: {bar}')


def main() -> None:
    """CLI 진입점."""
    args = sys.argv[1:]

    style_report = False
    if '--style-report' in args:
        style_report = True
        args.remove('--style-report')

    if not args:
        print('Usage: python evaluator.py [--style-report] <report.html>')
        sys.exit(1)

    html_path = args[0]
    evaluate(html_path, style_report=style_report)


if __name__ == '__main__':
    main()
