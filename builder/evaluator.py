"""
CUFA 보고서 품질 검증 엔진 (Evaluator)
HARD_MIN + SMIC 문체 검증
"""
import re
import sys


def evaluate(html_path: str) -> dict:
    """HTML 보고서를 읽고 품질 점수를 산출한다."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    text_only = re.sub(r'<[^>]+>', '', html)
    text_chars = len(text_only.replace(' ', '').replace('\n', ''))

    results = {}

    # === HARD_MIN ===
    results['text_chars'] = text_chars
    results['svg_count'] = html.count('<svg ')
    results['table_count'] = html.count('<table')
    results['h2h3_count'] = html.count('<h2') + html.count('<h3')
    results['file_bytes'] = len(html.encode('utf-8'))

    # === SMIC 문체 검증 ===
    results['dongsa_count'] = html.count('동사')
    results['company_name_count'] = sum(1 for _ in re.finditer(r'이노스페이스|동 기업', html))
    results['strong_count'] = html.count('<strong>')
    results['transition_words'] = sum(
        html.count(w) for w in ['전술한', '그렇다면', '이에 더해', '한편', '이처럼', '실제로', '다만']
    )
    results['counter_arg_count'] = html.count('counter-arg')

    # === 판정 ===
    hard_min = {
        'text_80k': (text_chars >= 80000, f'{text_chars:,}/80,000'),
        'svg_25': (results['svg_count'] >= 25, f'{results["svg_count"]}/25'),
        'tables_25': (results['table_count'] >= 25, f'{results["table_count"]}/25'),
        'h2h3_20': (results['h2h3_count'] >= 20, f'{results["h2h3_count"]}/20'),
    }

    smic_style = {
        'dongsa_ratio': (40 <= results['dongsa_count'] <= 120, f'{results["dongsa_count"]} (40~120)'),
        'transitions_50': (results['transition_words'] >= 30, f'{results["transition_words"]}/30+'),
        'counter_args_3': (results['counter_arg_count'] >= 3, f'{results["counter_arg_count"]}/3+'),
    }

    results['hard_min'] = hard_min
    results['smic_style'] = smic_style

    # 출력
    print(f'\n=== CUFA Evaluator: {html_path} ===')
    print(f'Text: {text_chars:,} chars | SVG: {results["svg_count"]} | Tables: {results["table_count"]} | Size: {results["file_bytes"]:,} bytes')

    print(f'\n--- HARD_MIN ---')
    all_pass = True
    for name, (passed, detail) in hard_min.items():
        status = 'PASS' if passed else 'FAIL'
        if not passed:
            all_pass = False
        print(f'  [{status}] {name}: {detail}')

    print(f'\n--- SMIC Style ---')
    for name, (passed, detail) in smic_style.items():
        status = 'PASS' if passed else 'WARN'
        print(f'  [{status}] {name}: {detail}')

    print(f'\n{"ALL PASS" if all_pass else "FAILED — 보강 필요"}')
    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python evaluator.py <report.html>')
        sys.exit(1)
    evaluate(sys.argv[1])
