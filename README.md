# CUFA Equity Research Report System

**AI 기반 기업분석보고서 자동 생성 시스템** — 충북대학교 가치투자학회(CUFA)

어떤 종목이든 동일한 품질의 인터랙티브 HTML 보고서를 생성하는 범용 도구.

## Features

- **인터랙티브 HTML** — 다크 테마, SVG 차트, Float TOC, 진행률 바
- **SMIC 수준 문체** — 볼드 첫문장, 전환어, 다단계 추론 체인
- **4중 밸류에이션** — PSR/PER + DCF + Reverse DCF + Football Field
- **Kill Conditions** — 투자논지 사망 조건 명시
- **자동 검증** — HARD_MIN + SMIC 문체 Evaluator
- **KIS 백테스트 연동** — 투자포인트 → 매매전략 → 백테스트 자동화

## Quick Start

```bash
# 1. 종목 config 작성
cp data/templates/config_template.py examples/종목명/config.py
# config.py 데이터 채우기

# 2. 보고서 빌드
python builder/build.py examples/종목명/config.py

# 3. 품질 검증
python builder/evaluator.py output/종목명_CUFA_보고서.html

# 4. 브라우저에서 확인
open output/종목명_CUFA_보고서.html
```

## Architecture

```
cufa-equity-report/
├── template/
│   ├── style.css             # HD건설기계 v4-1 표준 CSS (수정 금지)
│   ├── style_extended.css    # CUFA 추가 컴포넌트
│   ├── components.py         # SVG 15종 + 테이블 + 레이아웃
│   └── interactive.js        # Float TOC, progress bar
├── builder/
│   ├── build.py              # 메인 빌드 엔진
│   └── evaluator.py          # 품질 검증
├── data/
│   └── templates/            # config.py 템플릿
├── trading/                  # KIS 백테스트 연동
├── examples/                 # 종목별 예시
└── docs/                     # SKILL.md, DESIGN.md
```

## Design System

| 변수 | 값 | 용도 |
|------|-----|------|
| `--bg` | #0D0D1A | 배경 |
| `--card-bg` | #161628 | 카드/차트 배경 |
| `--purple` | #7C6AF7 | 시그니처 |
| `--green` | #00E09E | 상승/긍정 |
| `--red` | #FF4D4D | 하락/부정 |
| `--text` | #E8E6F0 | 본문 |

## Benchmarks

SMIC(서울대)/YIG(연세대)/STAR(성균관대) 보고서 15편 역설계 기반.

| 항목 | CUFA | SMIC 평균 |
|------|:----:|:---------:|
| 디자인/UX | 9/10 | 7/10 |
| 밸류에이션 | 9/10 | 6/10 |
| 텍스트 밀도 | 7/10 | 9/10 |
| 추론 깊이 | 7/10 | 8/10 |

## Report Quality Standards

- 텍스트: 80,000자+
- SVG 차트: 25개+
- 테이블: 25개+
- 섹션: 11개 (기업개요~Appendix)
- 밸류에이션: 3종+ 크로스체크

## License

MIT License

## Credits

- **CUFA** (충북대학교 가치투자학회) — 투자 분석 방법론
- **Claude Code** — AI 보조 개발
- **SMIC/YIG/STAR** — 벤치마크 레퍼런스 (보고서 구조 참고)
