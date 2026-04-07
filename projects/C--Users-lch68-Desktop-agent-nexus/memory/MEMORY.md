# Agent Squad Memory

## Architecture (OpenClaw = 본체)
- **OpenClaw 2026.3.2** on WSL2 Ubuntu 24.04 — Gateway on port 18789
- OpenClaw = 핵심. 에이전트 오케스트레이션, 대화, 라우팅, 협업 전부 처리
- 5 agents: main(NEXUS), doge, sophia, alpha, clio — ChatGPT Codex (OAuth)
- MCP 96 tools = OpenClaw 에이전트의 도구. calc/bot/web은 팔다리.
- Telegram: @isNEXUS_bot, streaming OFF, dmPolicy: pairing, groupPolicy: allowlist
- bot/ directory is ACTIVE data layer — used by MCP server

## v0.2 Upgrade (Phase K~T) — COMPLETED 2026-03-08
- 33 new MCP tools (96 total), ~5,600 LOC new code, 162 tests passing
- K: macro_framework +5fn (taylor_rule, real_rate, fci, liquidity, cross_market)
- L: calc/portfolio/ (correlation, optimizer, rebalance, attribution)
- M: calc/wealth_planning.py (compound, retirement, lifecycle, tax, emergency, debt)
- N: calc/real_estate.py + bot/real_estate.py (국토교통부 API, MOLIT_API_KEY)
- O: calc/sentiment.py + bot/sentiment.py (F&G, PCR, Breadth)
- P: calc/backtest.py (forward_returns, decay, regime, compare)
- Q: research_handler.py (5-agent Deep Research → CUFA report)
- S: debate_handler.py (Bull/Bear → CLIO judge → NEXUS verdict)
- R: /portfolio page, /api/data/portfolio, /api/data/sentiment
- T: 162 tests ALL PASSING, web build OK
- Handler split: calc_handlers_v2.py, bot_handlers_v2.py, tools_v2.py (MERGED back 2026-03-09)
- llm_client.py: OpenRouter API (for programmatic LLM calls in Python code)
- CLIO SOUL.md: 부동산 역사적 사이클 section added
- Sophia SOUL.md: 극단치 역발상 지침 section added

## Web Dashboard (Next.js 15)
- Auth: HMAC-SHA256 cookie, Edge Runtime middleware, timing-safe comparison
- Design: JetBrains Mono, solid cards #0f0f0f, purple #7c6af7, dark only
- Sidebar: 6 collapsible categories, w-52
- 23+ pages, ALL live data, ZERO mock/fallback

## API Routes (31 total)
- Auth: verify, logout
- Data: news, summary, crypto, derivatives, fx, macro, commodities, calendar, dart, dcf, history, agents, screener, morning-brief, insights, signals, autolearn, portfolio(v0.2), sentiment(v0.2)
- Stock: kr/[ticker], us/[ticker] | Reports: list + [id] | Valuechain
- CRUD: journal, watchlist, mcp

## MCP Tools (96 total = 63 v0.1 + 33 v0.2)
- server.py + tools.py (unified) + helpers.py + handlers/
- Handler files: calc_handlers, bot_handlers, data_handlers, code_handlers, research_handler, debate_handler
- v2 files MERGED into v1 and deleted (2026-03-09)

## Supabase
- Existing: journal_entries, watchlist, reports, insights
- Need migration: analyses, agent_logs, morning_briefs, signal_outcomes

## Tests (246 passing)
- calc/tests: dcf(19), ratios(23), risk_metrics(22), policy_filter(14), macro_framework(25), portfolio(13), wealth_planning(17), real_estate(13), sentiment(9), backtest(7)
- bot/tests (NEW 2026-03-09): test_data(10), test_crypto(6), test_dart(8), test_news(6), test_real_estate(6), test_sentiment(4), test_macro(7), test_autolearn(6), test_structure_monitor(9), test_cache(10)
- mcp_server/tests (NEW 2026-03-09): test_dispatcher(6), test_schema(6)
- test_technical requires pandas (skip without pandas)

## Quality Hardening (2026-03-09~10, COMMITTED a594808)
- bot/errors.py: NexusError hierarchy (DataFetchError, RateLimitError, ParseError, ConfigError, StorageError, DataNotFoundError)
- All bot/ modules (data, crypto, dart, news, real_estate, sentiment, macro/fred, macro/ecos, autolearn/accuracy) use typed exceptions
- mcp_server/server.py: NexusError → structured JSON error response
- bot/structure_monitor.py: HTML marker validation for naver/fnguide scraping + Telegram alert
- bot/cache.py: SQLite TTL cache as Supabase failover
- scripts/verify_autolearn.py: 5-step autolearn pipeline verification
- Review fix: dart.py ConfigError 일관성, bot_handlers/http_server format_dart_context(None) 크래시 방지
- 미수정 범위 (향후): bot/alerts.py, bot/calendar.py, bot/global_market.py, bot/conversations.py에 generic except 잔존

## .env Keys Required
- OPENROUTER_API_KEY (programmatic LLM calls in Python)
- SUPABASE_URL, SUPABASE_ANON_KEY, ACCESS_CODES, COOKIE_SECRET
- FRED, NAVER, MCP_SERVER_URL, FINNHUB, DART, ECOS, ETHERSCAN
- MOLIT_API_KEY (부동산 API, 공공데이터포털)

## Git Sync
- GitHub: pollmap/agent-nexus.git, both sides on `main` branch
- WSL2 auto-sync: crontab */5 * * * * scripts/auto_sync.sh

## User Preferences
- Chanhee: Korean, direct, hates wasted time, hates mock data
- OpenAI Codex via OAuth (OpenClaw native), OpenRouter for programmatic Python calls only
- Compact UI, real-time data only
- Portfolio tracking 안함 — 즐겨찾기(watchlist)만

## Hosting Migration (Planned)
- Target: Contabo VPS 10 (€4.50/mo, 4 vCPU, 8GB RAM, 75GB NVMe)
- OpenClaw 프리인스톨, 1-click setup
- Migration script: scripts/migrate_to_contabo.sh (9-step automated)
- Key changes: gateway bind 0.0.0.0, systemd services (mcp-http, nexus-web), auto_sync cron
- auto_sync.sh: hardcoded WSL path → script-relative path로 수정됨

## Still Needs
- **Contabo VPS 구매 후 마이그레이션 실행**
- Run supabase/migrations/run_all.sql (008_conversations 포함)
- Add MOLIT_API_KEY to .env (공공데이터포털)
- 30-page report via Telegram testing
- Kraken MCP 서버 실제 연결 테스트
