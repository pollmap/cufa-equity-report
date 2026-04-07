# Agent Squad 마스터 플랜 요약

## 철학
- "AI computes. You decide." — AI가 참고용 투자의견 제공 가능, 최종 판단은 사용자
- 숫자는 calc/ Python만. LLM 계산 금지
- Sophia가 모든 분석에 반론 (Anti-Sycophancy)

## 아키텍처
- 사용자 → Telegram + Web Dashboard → OpenClaw Gateway → NEXUS → 4 subagents
- DB: Supabase (analyses, portfolio_items, journal_entries, value_chain, custom_valuations, agent_logs, morning_briefs)
- MCP Server: calc/ + bot/ 도구 노출 (최우선 과제)

## 5인 에이전트
| Agent | MBTI | Role |
|-------|------|------|
| NEXUS | ENFP | 팀리더, 오케스트레이터 |
| Doge | ISTP | CTO/엔지니어 |
| Sophia | INFJ | 철학자/검증자 (반론) |
| Alpha | ENTJ | CFO |
| CLIO | ISTJ | 역사가/리스크 |

## Option C 모드
- Mode 1 (Direct): 1 LLM 호출, NEXUS 단독
- Mode 2 (Quick): 2 호출, NEXUS → Sophia 반론
- Mode 3 (Deep): 5+ 호출, SMIC 7섹션 리포트

## 웹 페이지 목록 (17개)
1. Dashboard — 멀티에셋 오버뷰 (주식·채권·크립토·원자재·FX)
2. Stock Detail — Simply Wall St + FastGraphs 스타일, DCF 슬라이더
3. Macro — 수익률커브, 금리, 크레딧스프레드, 경제지표
4. FX — 원화기준 + 크로스페어 + DXY + 김프 + 금리차
5. Crypto — 전체시장 + 개별코인(온체인/파생/DeFi)
6. Commodities — 귀금속/에너지/산업금속/농산물 + 매크로연동
7. News — saveticker 스타일, GICS 11섹터 필터
8. Calendar — 경제지표 + 중앙은행 + 실적발표
9. DART — 관심기업 공시 자동추적 + AI요약
10. Journal — AI튜터(Sophia) 소크라테스5단계 + 적중률
11. Value Chain — React Flow 노드그래프
12. History — 분석히스토리
13. Reports — Mode 3 리포트뷰 + PDF
14. Portfolio — 포트폴리오 CRUD
15. Agents — 에이전트 활동 모니터
16. Settings — 종목관리, 알림설정
17. External Links — CUFA위키, 한경, 네이버리서치, DART, FRED, ECOS

## 인증
- 접속코드 8자리 (초대제), 1인1코드
- 모든 데이터 개인 격리 (user_code/user_id)
- 저널만 전체공개 읽기 (CUFA 회원간 학습)

## 데이터 소스 (40+ 무료 API)
- KR 주식: pykrx, FnGuide, 네이버, DART
- US 주식: yfinance
- 크립토: CoinGecko, Upbit, Binance, Bybit, DeFiLlama, Etherscan V2, Blockchair
- 채권: ECOS(국고채/회사채/콜금리), FRED(Treasury/스프레드)
- 매크로: FRED, ECOS, World Bank
- FX: ExchangeRate, ECOS, yfinance(DXY)
- 원자재: yfinance (선물티커 GC=F, CL=F 등)
- 뉴스: 네이버 검색 API + Finnhub
- 캘린더: Finnhub Economic Calendar
- DART: OpenDART API

## 디자인 시스템 핵심
- 다크 only (#0a0a0a base, #0f0f0f cards)
- 퍼플 시그니처 #7c6af7 (CTA 버튼만 gradient)
- JetBrains Mono: 제목, 라벨, 숫자, 버튼, 네비
- Inter: 본문 텍스트(문단)만
- 터미널 부팅 시퀀스 ($ nexus.dashboard() → ready.)
- 입력필드: >_ 프롬프트 접두사
- 금지: 흰배경, blue accent, 둥근모서리, 과한애니, 여백남용

## 저널 AI 튜터 5단계 (Sophia)
1. 전제 추출 (Premise) — NEXUS
2. 핵심 질문 (Elenchus) — Sophia
3. 반론 시나리오 (Counter) — Sophia + CLIO
4. 데이터 제안 (Evidence) — Alpha + Doge
5. 자기 질문 유도 (Self-inquiry) — NEXUS

## 로드맵 Phase
- Phase 1: MCP서버 + Supabase + bot/ 함수추가
- Phase 2: 웹 MVP (인증, 대시보드, 히스토리)
- Phase 3: 종목대시보드 + 리포트 + PDF
- Phase 4: 멀티에셋 대시보드 (매크로/FX/크립토/원자재)
- Phase 5: 뉴스 + 캘린더 + DART
- Phase 6: 투자저널 + AI튜터
- Phase 7: 밸류체인맵 (React Flow)
- Phase 8: 고도화 (백테스팅, Discord, VPS)
