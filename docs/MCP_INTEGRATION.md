# CUFA Equity Report x Nexus Finance MCP 통합 설계

> 작성일: 2026-04-04 | 버전: v1.0
> 목표: "종목코드 하나 넣으면 보고서+엑셀+백테스트 3종 자동 생성"

## 1. 현재 vs 목표 아키텍처

### 현재 (수동)
```
[사람이 config.py 수동 작성 (2-3시간)]
→ builder/build.py → HTML 보고서
→ builder/evaluator.py → 품질 검증
```

### 목표 (자동)
```
python data/collector.py 462350
→ MCP 5개 도구 병렬 호출 (10-15초)
→ examples/{종목}/config.py 자동 생성
→ [수동: 투자의견/IP/리스크 보완]
→ builder/build.py → HTML 보고서
→ builder/evaluator.py → 품질 검증
```

## 2. 네트워크

```
[로컬 Windows] --SSH 터널--> [VPS <MCP_VPS_HOST>]
collector.py                   127.0.0.1:8100/mcp
                               Nexus MCP (316도구)
```

SSH 터널: `ssh -f -N -L 18100:127.0.0.1:8100 -i ~/.ssh/cbnupollmap root@<MCP_VPS_HOST>`
이후 `http://127.0.0.1:18100/mcp`로 요청.

## 3. 5대 핵심 MCP 도구

| # | 도구 | config.py 필드 | 비고 |
|:-:|------|---------------|------|
| ① | dart_financial_statements | FINANCIALS (IS/BS/CF) | CFS 5개년, 원→억원 변환 |
| ② | stocks_quote | CURRENT_PRICE, MARKET_CAP, SHARES | |
| ③ | stocks_history | YTD_CHANGE_PCT, price_history.json | 1년 일봉 |
| ④ | ecos_get_base_rate | MACRO['risk_free_rate'] | 국고채 3년 |
| ⑤ | news_search | news.json | 최근 뉴스 20건 |

## 4. 자동 vs 수동 필드

### 자동 수집 (MCP)
TICKER, COMPANY_NAME, MARKET, CURRENT_PRICE, MARKET_CAP, SHARES,
WEEK52_HIGH/LOW, FINANCIALS 전체, RATIOS (계산), MACRO.risk_free_rate

### 수동 입력 필수
SUBTITLE, OPINION, TARGET_PRICE, INVESTMENT_POINTS, RISKS,
KILL_CONDITIONS, PRODUCTS, PEERS, SCENARIOS, CONSENSUS

## 5. 에러 처리

MCP 실패 시 빌드를 막지 않는다. 실패 필드는 `None` + `# TODO: 수동 입력` 주석.

## 6. 파일 구조

```
data/
├── collector.py       ← CLI 진입점
├── mcp_client.py      ← MCP HTTP 클라이언트 (JSON-RPC 2.0)
├── mappers/
│   ├── dart_mapper.py ← DART → FINANCIALS
│   ├── quote_mapper.py ← 시세 → 주가 변수
│   └── macro_mapper.py ← ECOS → MACRO
└── renderer.py        ← dict → config.py 렌더링
```

## 7. 인증

| 변수 | 용도 | 저장 |
|------|------|------|
| `MCP_URL` | 엔드포인트 | `.env` |
| `MCP_TOKEN` | Bearer 토큰 | `.env` |

`.env`는 `.gitignore`에 포함. 코드에 하드코딩 절대 금지.

## 8. 구현 우선순위

1. **Phase 1 MVP**: mcp_client + dart_mapper + quote_mapper + renderer + collector
2. **Phase 2**: macro + news + history
3. **Phase 3**: pipeline.py (원커맨드 자동화)
4. **Phase 4**: 엑셀 + 백테스트 연동
