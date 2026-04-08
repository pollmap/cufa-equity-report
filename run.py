#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CUFA Equity Report — 원커맨드 자동 빌드 파이프라인

Usage:
    python run.py 삼성전자          # HTML + 엑셀 + GitHub 자동
    python run.py 삼성전자 --no-git  # GitHub 제외
    python run.py 삼성전자 --eval    # Evaluator 상세 리포트 포함
    python run.py --list             # 빌드 가능 종목 목록

What it does (자동):
  1. examples/{종목}/config.py 존재 확인
  2. builder/build.py → HTML 보고서 생성
  3. builder/evaluator.py → 품질 검증
  4. examples/{종목}/build_xlsx.py → 엑셀 재무데이터 생성
  5. git add + commit + push → GitHub 자동 업데이트
  6. 연도 자동 적용 (2026 → 2027 → 2028 매년 자동)
"""
from __future__ import annotations
import argparse, importlib.util, subprocess, sys, os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"
OUTPUT   = ROOT / "output"
BUILDER  = ROOT / "builder" / "build.py"
EVALUATOR= ROOT / "builder" / "evaluator.py"
KST = ZoneInfo('Asia/Seoul')

# ─── 연도 유틸 ───────────────────────────────────────────────
def current_report_year() -> int:
    """현재 KST 연도 자동 반환 (2026 → 2027 등 매년 자동)."""
    return datetime.now(KST).year

def year_label(year_int: int, report_year: int) -> str:
    """2025 → '2025A' (과거), 2026 → '2026E' (추정)."""
    return f"{year_int}A" if year_int < report_year else f"{year_int}E"

# ─── 종목 목록 ───────────────────────────────────────────────
def list_tickers() -> list[str]:
    """examples/ 하위 폴더 중 config.py 있는 것만 반환."""
    return [
        d.name for d in EXAMPLES.iterdir()
        if d.is_dir() and (d / "config.py").exists()
        and not d.name.startswith('_')
    ]

# ─── 메인 빌드 ───────────────────────────────────────────────
def build(ticker: str, no_git: bool = False, eval_detail: bool = False) -> bool:
    print(f"\n{'='*60}")
    print(f"  CUFA 자동 빌드 — {ticker}")
    rpt_year = current_report_year()
    print(f"  기준 연도: {rpt_year} (추정 기준: {rpt_year}E~{rpt_year+2}E)")
    print(f"  실행일시: {datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')}")
    print(f"{'='*60}\n")

    example_dir = EXAMPLES / ticker
    config_path = example_dir / "config.py"

    # 1. 종목 폴더 확인
    if not config_path.exists():
        print(f"✗ {ticker}/config.py 없음 — 먼저 config.py를 작성하세요.")
        print(f"  경로: {config_path}")
        return False
    print(f"[1] config.py 확인 → {config_path}")

    # 2. HTML 빌드
    print(f"\n[2] HTML 보고서 빌드...")
    r = subprocess.run(
        [sys.executable, str(BUILDER), str(config_path)],
        capture_output=True,
    )
    stdout = r.stdout.decode('utf-8', errors='replace') if r.stdout else ''
    stderr = r.stderr.decode('utf-8', errors='replace') if r.stderr else ''
    if r.returncode != 0:
        print(f"  ✗ 빌드 실패:\n{stderr[-500:]}")
        return False
    # 출력에서 파일 크기/텍스트 수 추출
    for line in stdout.split('\n'):
        if 'Report saved' in line or 'Size:' in line or 'Text:' in line:
            print(f"  {line.strip()}")

    # HTML 파일 경로
    html_files = list(OUTPUT.glob(f"{ticker}*.html"))
    if not html_files:
        # 영문 이름 탐색
        html_files = list(OUTPUT.glob("*.html"))
    html_path = html_files[-1] if html_files else None

    # 3. Evaluator
    print(f"\n[3] Evaluator v2 품질 검증...")
    if html_path:
        eval_args = [sys.executable, str(EVALUATOR), str(html_path)]
        if eval_detail:
            eval_args.append("--style-report")
        r2 = subprocess.run(eval_args, capture_output=True)
        out2 = (r2.stdout or b'').decode('utf-8', errors='replace')
        err2 = (r2.stderr or b'').decode('utf-8', errors='replace')
        output_lines = (out2 + err2).split('\n')
        pass_count = sum(1 for l in output_lines if '[PASS]' in l)
        fail_count = sum(1 for l in output_lines if '[FAIL]' in l)
        warn_count = sum(1 for l in output_lines if '[WARN]' in l)
        status = "ALL PASS ✅" if fail_count == 0 else f"FAIL {fail_count}건 ⚠️"
        print(f"  → PASS {pass_count} / FAIL {fail_count} / WARN {warn_count} — {status}")
        if fail_count > 0:
            for l in output_lines:
                if '[FAIL]' in l:
                    print(f"    {l.strip()}")
    else:
        print("  → HTML 파일 미발견, 평가 건너뜀")

    # 4. 엑셀 빌드
    print(f"\n[4] 엑셀 재무데이터 생성...")
    xlsx_builder = example_dir / "build_xlsx.py"
    if xlsx_builder.exists():
        r3 = subprocess.run(
            [sys.executable, str(xlsx_builder)],
            capture_output=True,
        )
        xlsx_files = list(OUTPUT.glob(f"{ticker}*.xlsx"))
        if xlsx_files:
            size_kb = xlsx_files[-1].stat().st_size // 1024
            print(f"  ✅ {xlsx_files[-1].name} ({size_kb}KB)")
        else:
            print(f"  ⚠️  엑셀 파일 미발견 (빌드 스크립트 확인 필요)")
    else:
        print(f"  ⚠️  {ticker}/build_xlsx.py 없음 — 엑셀 생성 건너뜀")

    # 5. GitHub 자동 커밋/푸시
    if not no_git:
        print(f"\n[5] GitHub 자동 업데이트...")
        _git_auto_push(ticker, rpt_year)
    else:
        print(f"\n[5] GitHub 건너뜀 (--no-git)")

    # 6. 최종 요약
    print(f"\n{'─'*60}")
    print(f"  ✅ 빌드 완료 — {ticker} ({datetime.now(KST).strftime('%H:%M KST')})")
    if html_path:
        print(f"  📄 HTML: {html_path.name}")
    if xlsx_files := list(OUTPUT.glob(f"{ticker}*.xlsx")):
        print(f"  📊 Excel: {xlsx_files[-1].name}")
    print(f"  🌐 GitHub: pollmap/cufa-equity-report")
    print(f"{'─'*60}\n")
    return True

def _git_auto_push(ticker: str, rpt_year: int):
    """examples/{ticker}/ 변경사항 자동 커밋 + 푸시."""
    try:
        example_dir = EXAMPLES / ticker
        # git add
        subprocess.run(['git', 'add', str(example_dir)], cwd=ROOT, check=True,
                       capture_output=True)
        # git status --short
        r = subprocess.run(['git', 'status', '--short'], cwd=ROOT,
                           capture_output=True, text=True, encoding='utf-8')
        if not r.stdout.strip():
            print("  → 변경사항 없음, 커밋 건너뜀")
            return
        # git commit
        msg = (
            f"feat: {ticker} CUFA 보고서 업데이트 ({rpt_year}년 기준)\n\n"
            f"- config.py / sections.py / build_xlsx.py 업데이트\n"
            f"- 기준일: {datetime.now(KST).strftime('%Y-%m-%d')} KST"
        )
        subprocess.run(['git', 'commit', '-m', msg], cwd=ROOT, check=True,
                       capture_output=True)
        # git push
        r_push = subprocess.run(['git', 'push', 'origin', 'master'], cwd=ROOT,
                                 capture_output=True)
        if r_push.returncode == 0:
            print(f"  ✅ GitHub push 완료 → pollmap/cufa-equity-report")
        else:
            err = (r_push.stderr or b'').decode('utf-8', errors='replace')
            print(f"  ⚠️  push 실패: {err[:100]}")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Git 오류: {e}")

# ─── CLI ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="CUFA 원커맨드 자동 빌드 파이프라인"
    )
    parser.add_argument('ticker', nargs='?', help='종목명 (예: 삼성전자)')
    parser.add_argument('--no-git', action='store_true', help='GitHub 업로드 건너뜀')
    parser.add_argument('--eval',   action='store_true', help='Evaluator 상세 리포트')
    parser.add_argument('--list',   action='store_true', help='빌드 가능 종목 목록')
    parser.add_argument('--all',    action='store_true', help='모든 종목 순차 빌드')
    args = parser.parse_args()

    if args.list or not args.ticker:
        tickers = list_tickers()
        print(f"\n빌드 가능 종목 ({len(tickers)}개):")
        for t in tickers:
            cfg = EXAMPLES / t / "config.py"
            spec = importlib.util.spec_from_file_location("cfg", cfg)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                price = getattr(mod, 'CURRENT_PRICE', '?')
                opinion = getattr(mod, 'OPINION', '?')
                tp = getattr(mod, 'TARGET_PRICE', '?')
                print(f"  {t:15s}  {opinion}  현재가 {price:,}원  TP {tp:,}원")
            except Exception:
                print(f"  {t}")
        print(f"\n사용법: python run.py {{종목명}}")
        return

    if args.all:
        for t in list_tickers():
            build(t, no_git=args.no_git, eval_detail=args.eval)
    else:
        ok = build(args.ticker, no_git=args.no_git, eval_detail=args.eval)
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
