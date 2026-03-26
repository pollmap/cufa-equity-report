# 금융 데이터 리포트 생성

nexus-finance-mcp를 사용해서 금융 데이터 리포트를 생성해.

## 사용 가능한 데이터 소스 (131개 도구)

### 한국
- ECOS: 금리, 환율, 통화량, GDP — `ecos_*`
- DART: 재무제표, 기업개황, 대주주 — `dart_*`
- KRX: 주가, 거래량, 베타 — `stocks_*`
- KOSIS: 통계청 데이터 (인구, CPI, 고용) — `kosis_*`
- R-ONE: 부동산 가격지수, PIR — `rone_*`

### 글로벌
- FRED: 미국 매크로 — `global_macro_*`
- Yahoo: 미국 주식 — `us_equity_*`
- Crypto: 거래소 시세, 김치프리미엄 — `crypto_*`

## 사용자 요청에 따라
- 특정 종목 분석이면 DART + KRX 조합
- 거시경제면 ECOS + FRED 조합
- 부동산이면 R-ONE + KOSIS 조합
- 크립토면 crypto + defi + onchain 조합

mcporter로 데이터 수집: `mcporter call nexus-finance.<tool_name> key=value`
