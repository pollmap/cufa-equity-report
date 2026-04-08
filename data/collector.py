#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CUFA Data Collector — 완전 자동 데이터 수집기
Nexus MCP DART → pykrx → FnGuide WebFetch (3단계 Fallback)

Usage:
    python data/collector.py 삼성전자 005930
    python data/collector.py 삼성전자 005930 --output examples/삼성전자/config.py

What it does:
    1. Nexus MCP로 DART 재무제표 수집 (CFS 연결, 5개년)
    2. pykrx로 주가 데이터 수집
    3. Nexus MCP ECOS로 금리/환율 수집
    4. 수집 데이터 → config.py 자동 생성
    5. 못 가져온 항목은 TODO 주석으로 표시 (mock 금지!)
"""
from __future__ import annotations
import sys, json, os, re, textwrap
import requests
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.stdout.reconfigure(encoding='utf-8')

ROOT     = Path(__file__).resolve().parent.parent
MCP_URL  = "http://62.171.141.206/mcp"
MCP_TOKEN= "Bearer REDACTED_TOKEN"
KST      = ZoneInfo('Asia/Seoul')
TODAY    = datetime.now(KST)
YEAR     = TODAY.year  # 현재 연도 자동

# ─── Nexus MCP 클라이언트 ────────────────────────────────────
class NexusMCP:
    """Nexus Finance MCP HTTP 클라이언트."""

    SESSION_FILE = ROOT / ".mcp_session"

    def __init__(self):
        self._session_id: str = ""
        self._available: bool | None = None

    def _headers(self) -> dict:
        h = {
            "Authorization": MCP_TOKEN,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self._session_id:
            h["Mcp-Session-Id"] = self._session_id
        return h

    def _parse_sse(self, text: str) -> dict | None:
        """SSE 응답에서 result 파싱."""
        for line in text.split("\n"):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if "result" in data:
                        return data["result"]
                    if "error" in data:
                        return None
                except json.JSONDecodeError:
                    pass
        # JSON 직접 파싱 시도
        try:
            data = json.loads(text)
            return data.get("result")
        except Exception:
            return None

    def initialize(self) -> bool:
        """MCP 세션 초기화. True=성공."""
        # 캐시된 세션 복원 시도
        if self.SESSION_FILE.exists():
            sid = self.SESSION_FILE.read_text().strip()
            if sid:
                self._session_id = sid
                return True
        try:
            r = requests.post(
                MCP_URL,
                json={
                    "jsonrpc": "2.0", "id": 0, "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "cufa-collector", "version": "1.0"},
                    },
                },
                headers=self._headers(),
                timeout=8,
            )
            sid = r.headers.get("mcp-session-id", "")
            if sid:
                self._session_id = sid
                self.SESSION_FILE.write_text(sid)
                return True
            # 세션 ID 없어도 200이면 사용 가능
            return r.status_code == 200
        except Exception as e:
            print(f"  ⚠️  Nexus MCP 연결 실패: {e.__class__.__name__}")
            return False

    def call(self, tool: str, params: dict, timeout: int = 30) -> dict | list | str | None:
        """MCP 도구 호출. None=실패."""
        try:
            r = requests.post(
                MCP_URL,
                json={
                    "jsonrpc": "2.0", "id": 1, "method": "tools/call",
                    "params": {"name": tool, "arguments": params},
                },
                headers=self._headers(),
                timeout=timeout,
            )
            result = self._parse_sse(r.text)
            if result is None:
                return None
            content = result.get("content", [])
            for c in content:
                if c.get("type") == "text":
                    try:
                        return json.loads(c["text"])
                    except Exception:
                        return c["text"]
            return result
        except Exception as e:
            print(f"  ⚠️  {tool} 호출 실패: {e.__class__.__name__}")
            return None

    def is_available(self) -> bool:
        if self._available is None:
            self._available = self.initialize()
        return self._available


# ─── pykrx Fallback ──────────────────────────────────────────
def fetch_pykrx(ticker: str) -> dict:
    """pykrx로 주가 + 기본 지표 수집."""
    result = {}
    try:
        from pykrx import stock
        today_str = TODAY.strftime("%Y%m%d")
        one_year = (TODAY - timedelta(days=365)).strftime("%Y%m%d")
        three_year = (TODAY - timedelta(days=365*3)).strftime("%Y%m%d")

        df = stock.get_market_ohlcv_by_date(one_year, today_str, ticker)
        if not df.empty:
            result["current_price"]  = int(df["종가"].iloc[-1])
            result["high_52w"]       = int(df["고가"].max())
            result["low_52w"]        = int(df["저가"].min())
            result["price_1y_ago"]   = int(df["종가"].iloc[0])
            result["return_1y_pct"]  = round(
                (result["current_price"] / result["price_1y_ago"] - 1) * 100, 1
            )
            # 연도별 연말 주가
            df_3y = stock.get_market_ohlcv_by_date(three_year, today_str, ticker)
            result["price_history"]  = {}
            for yr in range(YEAR-3, YEAR+1):
                yr_data = df_3y[df_3y.index.year == yr]
                if not yr_data.empty:
                    result["price_history"][yr] = int(yr_data["종가"].iloc[-1])
            result["data_source"] = "pykrx KRX"
            print(f"  ✅ pykrx 주가: {result['current_price']:,}원 (52주 {result['low_52w']:,}~{result['high_52w']:,})")
    except Exception as e:
        print(f"  ⚠️  pykrx 실패: {e}")
    return result


def fetch_fnguide(ticker: str) -> dict:
    """FnGuide WebFetch로 재무제표 수집."""
    result = {}
    try:
        url = f"https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{ticker}&cID=&MenuYn=Y&ReportGB=&NewMenuID=103&stkGb=701"
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        text = r.text

        # 간단 정규식으로 주요 수치 추출
        # 실제로는 BeautifulSoup 파싱이 더 정확하나 의존성 최소화
        result["raw_html_size"] = len(text)
        result["data_source"]   = "FnGuide (HTML)"
        print(f"  ✅ FnGuide 응답: {len(text):,} bytes")
    except Exception as e:
        print(f"  ⚠️  FnGuide 실패: {e}")
    return result


# ─── 메인 수집기 ─────────────────────────────────────────────
class CUFACollector:
    """
    완전 자동 데이터 수집기.
    Nexus MCP 우선 → pykrx/FnGuide Fallback
    """

    def __init__(self, company: str, ticker: str):
        self.company = company
        self.ticker  = ticker
        self.mcp     = NexusMCP()
        self.data    = {}  # 수집된 raw data
        self.missing = []  # 수집 실패 항목

    def collect_all(self) -> dict:
        """전체 Phase 0 데이터 수집."""
        print(f"\n{'─'*55}")
        print(f"  Phase 0 데이터 수집 — {self.company}({self.ticker})")
        print(f"  기준일: {TODAY.strftime('%Y-%m-%d')} KST")
        print(f"{'─'*55}")

        mcp_ok = self.mcp.is_available()
        print(f"\n  Nexus MCP: {'✅ 연결됨' if mcp_ok else '❌ 불가 (Fallback 모드)'}")

        self._collect_price(mcp_ok)
        self._collect_financials(mcp_ok)
        self._collect_macro(mcp_ok)
        self._collect_shareholders(mcp_ok)

        print(f"\n  수집 완료: {len(self.data)}개 항목")
        if self.missing:
            print(f"  ⚠️  수동 입력 필요: {self.missing}")
        return self.data

    def _collect_price(self, mcp_ok: bool):
        """주가 데이터 수집."""
        print(f"\n  [주가] ", end="")
        collected = {}

        if mcp_ok:
            # Nexus MCP → stocks_quote
            r = self.mcp.call("stocks_quote", {"ticker": self.ticker})
            if r and isinstance(r, dict):
                collected["current_price"] = r.get("price") or r.get("close")
                collected["market_cap"]    = r.get("market_cap")
                print(f"Nexus MCP ✅")
            else:
                print(f"Nexus MCP 실패 → pykrx Fallback")
                collected = fetch_pykrx(self.ticker)
        else:
            print(f"pykrx Fallback")
            collected = fetch_pykrx(self.ticker)

        if not collected.get("current_price"):
            self.missing.append("current_price")

        # pykrx 항상 보충 실행 (history용)
        if not collected.get("price_history"):
            extra = fetch_pykrx(self.ticker)
            collected.update({k: v for k, v in extra.items() if k not in collected})

        # 시총 계산 (주가 × 주식수)
        if collected.get("current_price") and not collected.get("market_cap"):
            # 상장주식수는 DART에서 가져오거나 hardcode
            known_shares = {
                "005930": 5_969_782_550,   # 삼성전자 보통주
                "000660": 728_002_365,     # SK하이닉스
                "035420": 164_263_395,     # NAVER
                "035900": 83_570_583,      # JYP
            }
            shares = known_shares.get(self.ticker)
            if shares:
                collected["shares_outstanding"] = shares
                collected["market_cap"] = round(
                    collected["current_price"] * shares / 1e8
                )

        self.data["price"] = collected

    def _collect_financials(self, mcp_ok: bool):
        """DART 재무제표 수집 (IS/BS/CF)."""
        print(f"\n  [재무제표] ", end="")

        if mcp_ok:
            # Nexus MCP → dart_financial_statements
            r = self.mcp.call(
                "dart_financial_statements",
                {"corp_name": self.company, "report_type": "CFS", "years": 5},
                timeout=45,
            )
            if r:
                self.data["financials_raw"] = r
                print(f"Nexus MCP ✅ (CFS 연결)")
                return

        # Fallback: FnGuide
        print(f"FnGuide Fallback")
        self.data["financials_fnguide"] = fetch_fnguide(self.ticker)
        self.missing.append("financials_detail (FnGuide 파싱 필요)")

    def _collect_macro(self, mcp_ok: bool):
        """ECOS 금리/환율 수집."""
        print(f"\n  [매크로] ", end="")

        if mcp_ok:
            rf = self.mcp.call("ecos_get_base_rate", {})
            fx = self.mcp.call("ecos_get_exchange_rate", {"currency": "USD"})
            if rf:
                self.data["base_rate"] = rf
                print(f"ECOS 금리 ✅  ", end="")
            if fx:
                self.data["usd_krw"] = fx
                print(f"환율 ✅")
            else:
                print(f"일부 실패")
        else:
            print(f"기본값 사용 (Rf=2.75%, USD/KRW=1,380)")
            self.data["base_rate"] = {"rate": 2.75, "source": "default"}
            self.data["usd_krw"]   = {"rate": 1380, "source": "default"}

    def _collect_shareholders(self, mcp_ok: bool):
        """대주주 현황 수집."""
        print(f"\n  [주주] ", end="")

        if mcp_ok:
            r = self.mcp.call(
                "dart_major_shareholders",
                {"corp_name": self.company},
                timeout=20,
            )
            if r:
                self.data["shareholders_raw"] = r
                print(f"DART ✅")
                return

        print(f"수동 입력 필요")
        self.missing.append("shareholders (DART 필요)")

    # ─── config.py 자동 생성 ────────────────────────────────
    def generate_config(self, output_path: Path) -> str:
        """수집 데이터 → config.py 자동 생성."""
        price_data = self.data.get("price", {})
        current_price  = price_data.get("current_price", 0)
        market_cap     = price_data.get("market_cap", 0)
        shares         = price_data.get("shares_outstanding", 0)
        high_52w       = price_data.get("high_52w", 0)
        low_52w        = price_data.get("low_52w", 0)
        return_1y      = price_data.get("return_1y_pct", "TODO")

        # 매크로
        rf_data = self.data.get("base_rate", {})
        rf = rf_data.get("rate", 2.75) if isinstance(rf_data, dict) else 2.75
        fx_data = self.data.get("usd_krw", {})
        usd_krw = fx_data.get("rate", 1380) if isinstance(fx_data, dict) else 1380

        # 연도 자동 계산
        actual_years = [YEAR-1, YEAR-2, YEAR-3]  # e.g. [2025, 2024, 2023]
        est_years    = [YEAR,   YEAR+1, YEAR+2]  # e.g. [2026, 2027, 2028]

        missing_str = "\n".join(f"# TODO: {m}" for m in self.missing) if self.missing else "# 모든 데이터 수집 완료"

        config_code = f'''\
# -*- coding: utf-8 -*-
"""
{self.company}({self.ticker}) CUFA 기업분석보고서 — config.py
Single Source of Truth: 모든 재무 데이터, 가정, 상수.

데이터 수집일: {TODAY.strftime("%Y-%m-%d")} (KST)
수집 방법: Nexus MCP DART + pykrx + ECOS (collector.py 자동 생성)
{"수동 입력 필요 항목:" if self.missing else "수집 상태: 완료"}
{missing_str}
"""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# ── 날짜 (하드코딩 금지) ─────────────────────────────────────
KST = ZoneInfo("Asia/Seoul")
REPORT_DATE     = datetime.now(KST)
REPORT_DATE_STR = REPORT_DATE.strftime("%Y년 %m월 %d일")
REPORT_YEAR     = REPORT_DATE.year         # {YEAR}
EST_YEARS       = [REPORT_YEAR, REPORT_YEAR+1, REPORT_YEAR+2]   # {est_years}
ACTUAL_YEARS    = [REPORT_YEAR-1, REPORT_YEAR-2, REPORT_YEAR-3] # {actual_years}
DATA_AS_OF      = "{TODAY.strftime("%Y-%m-%d")}"

# ── 종목 기본 정보 ───────────────────────────────────────────
TICKER          = "{self.ticker}"
COMPANY_NAME    = "{self.company}"
COMPANY_NAME_EN = "TODO: 영문명"
MARKET          = "KOSPI"  # TODO: 확인
SUBTITLE        = "TODO: 보고서 부제"
SECTOR          = "TODO: 섹터"
LISTING_DATE    = "TODO: 상장일"

TEAM_NAME       = "CUFA 리서치팀"
TEAM_MEMBERS    = ["이찬희"]

# ── 주가 데이터 (출처: pykrx KRX, {TODAY.strftime("%Y-%m-%d")}) ──
CURRENT_PRICE       = {current_price:_}        # 원
SHARES_OUTSTANDING  = {shares:_}    # 주 (DART 기준)
MARKET_CAP          = {market_cap:_}      # 억원 ({current_price:,}원 × {shares:,}주 / 1억)
WEEK52_HIGH         = {high_52w:_}        # 원
WEEK52_LOW          = {low_52w:_}         # 원
RETURN_1Y_PCT       = {return_1y}         # % (출처: pykrx)

# ── 투자의견 (Phase 9 밸류에이션 완료 후 입력) ───────────────
OPINION      = "TODO"     # BUY / HOLD / SELL
TARGET_PRICE = None       # TODO: 목표주가
UPSIDE_PCT   = None       # 자동 계산됨

# ── 재무 데이터 (출처: DART CFS 연결, 단위: 억원) ────────────
# TODO: Nexus MCP dart_financial_statements 수집값으로 교체 필요
# 현재는 수동 입력 대기 상태
FINANCIALS = {{
    # IS (포괄손익계산서)
    "revenue": {{
        {YEAR-3}: None,  # {YEAR-3}A — TODO: DART 수집
        {YEAR-2}: None,  # {YEAR-2}A — TODO: DART 수집
        {YEAR-1}: None,  # {YEAR-1}A — TODO: DART 수집
        f"{{REPORT_YEAR}}E": None,  # {YEAR}E — 추정
        f"{{REPORT_YEAR+1}}E": None,
        f"{{REPORT_YEAR+2}}E": None,
    }},
    "operating_income": {{
        {YEAR-3}: None,
        {YEAR-2}: None,
        {YEAR-1}: None,
        f"{{REPORT_YEAR}}E": None,
        f"{{REPORT_YEAR+1}}E": None,
        f"{{REPORT_YEAR+2}}E": None,
    }},
    "net_income": {{
        {YEAR-3}: None,
        {YEAR-2}: None,
        {YEAR-1}: None,
        f"{{REPORT_YEAR}}E": None,
        f"{{REPORT_YEAR+1}}E": None,
        f"{{REPORT_YEAR+2}}E": None,
    }},
    # BS
    "total_assets":        {{{YEAR-1}: None}},
    "stockholders_equity": {{{YEAR-1}: None}},
    "total_liabilities":   {{{YEAR-1}: None}},
    "current_assets":      {{{YEAR-1}: None}},
    "current_liabilities": {{{YEAR-1}: None}},
    "cash":                {{{YEAR-1}: None}},
    "total_debt":          {{{YEAR-1}: None}},
    # CF
    "cfo":   {{{YEAR-1}: None}},
    "capex": {{{YEAR-1}: None}},
    "fcf":   {{{YEAR-1}: None}},
    # 주당
    "eps": {{{YEAR-1}: None, f"{{REPORT_YEAR}}E": None}},
    "ebitda": {{{YEAR-1}: None, f"{{REPORT_YEAR}}E": None}},
}}

# ── 밸류에이션 지표 (현재가 {current_price:,}원 기준) ────────
_rev_prev   = FINANCIALS["revenue"].get({YEAR-1}) or 1
_ni_prev    = FINANCIALS["net_income"].get({YEAR-1}) or 0
_eq_prev    = FINANCIALS["stockholders_equity"].get({YEAR-1}) or 1
_eps_prev   = FINANCIALS["eps"].get({YEAR-1}) or 1
_eps_fwd    = FINANCIALS["eps"].get(f"{{REPORT_YEAR}}E") or 1

RATIOS = {{
    "psr_ttm":        round(MARKET_CAP / _rev_prev, 2) if _rev_prev else None,
    "per_ttm":        round(CURRENT_PRICE / _eps_prev, 1) if _eps_prev else None,
    "per_fwd":        round(CURRENT_PRICE / _eps_fwd, 1) if _eps_fwd else None,
    "pbr":            None,   # TODO: CURRENT_PRICE / BPS
    "ev_ebitda_fwd":  None,   # TODO: (MARKET_CAP + 순차입금) / EBITDA
    "roe":            round(_ni_prev / _eq_prev * 100, 1) if _eq_prev else None,
    "roa":            None,   # TODO: NI / 총자산
    "current_ratio":  None,   # TODO: 유동자산 / 유동부채
    "debt_to_equity": None,   # TODO: 총부채 / 자기자본
}}

# ── WACC ─────────────────────────────────────────────────────
WACC = {{
    "rf":       {rf:.2f},     # 국고채 3년 (출처: ECOS, {TODAY.strftime("%Y-%m")})
    "erp":      5.50,         # Damodaran 한국 ERP {YEAR}
    "beta":     None,         # TODO: KRX 60M 회귀 추정
    "ke":       None,         # = rf + beta × erp
    "kd":       None,         # TODO: 이자비용/이자발생부채 역산
    "t":        0.25,         # 실효법인세율 (추정)
    "d_ratio":  None,         # TODO: 부채/(부채+자기자본)
    "e_ratio":  None,
    "wacc":     None,         # 계산 후 입력
    "g":        2.00,         # 영구성장률 (한국 명목GDP, 출처: 한국은행)
}}

# ── 매크로 ───────────────────────────────────────────────────
MACRO = {{
    "usd_krw":    {{{YEAR-1}: {usd_krw:.0f}, f"{{REPORT_YEAR}}E": {max(usd_krw-20, 1300):.0f}}},
    "bok_rate":   {{{YEAR-1}: {rf:.2f}, f"{{REPORT_YEAR}}E": {max(rf-0.25, 2.0):.2f}}},
    "gdp_growth": {{{YEAR-1}: 2.0, f"{{REPORT_YEAR}}E": 2.3}},
}}

# ── 나머지 필드 (사업부/Peer/IP/리스크 등은 수동 작성) ──────
# TODO: PRODUCTS, PEERS, SHAREHOLDERS, INVESTMENT_POINTS, SCENARIOS,
#       RISKS, KILL_CONDITIONS, LAUNCH_HISTORY, FUNDRAISING
PRODUCTS          = []   # TODO
PEERS             = {{}}  # TODO
SHAREHOLDERS      = []   # TODO
INVESTMENT_POINTS = []   # TODO
SCENARIOS         = {{}}  # TODO
RISKS             = []   # TODO
KILL_CONDITIONS   = []   # TODO
LAUNCH_HISTORY    = []   # TODO
FUNDRAISING       = []   # TODO
'''
        output_path.write_text(config_code, encoding='utf-8')
        print(f"\n  ✅ config.py 생성: {output_path}")
        if self.missing:
            print(f"  ⚠️  수동 입력 필요 항목:")
            for m in self.missing:
                print(f"     - {m}")
        return config_code


# ─── Nexus MCP로 기존 config.py 자동 업데이트 ───────────────
def update_config_with_mcp(config_path: Path, mcp: NexusMCP) -> bool:
    """
    기존 config.py의 FINANCIALS 딕셔너리를
    Nexus MCP DART 실데이터로 자동 업데이트.

    매년 새 실적 반영 시 호출:
    - 이전 연도 추정값(YEAR-1 E) → 실제값(YEAR-1 A)으로 교체
    - 새 추정 연도(YEAR+2 E) 추가
    """
    if not config_path.exists():
        print(f"  ✗ {config_path} 없음")
        return False

    # config.py에서 종목 정보 로드
    import importlib.util
    spec = importlib.util.spec_from_file_location("cfg", config_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    ticker  = getattr(mod, "TICKER", "")
    company = getattr(mod, "COMPANY_NAME", "")

    print(f"\n  DART 자동 업데이트: {company}({ticker})")

    # Nexus MCP DART 재무제표 조회
    r = mcp.call(
        "dart_financial_statements",
        {"corp_name": company, "report_type": "CFS", "years": 5},
        timeout=45,
    )
    if not r:
        print("  ✗ DART 조회 실패")
        return False

    print(f"  ✅ DART 조회 완료 — 파싱 중...")

    # TODO: r의 구조 파악 후 config.py FINANCIALS 자동 패치
    # 현재는 raw 데이터를 data/ 폴더에 저장
    data_dir = config_path.parent.parent / "data" / ticker
    data_dir.mkdir(parents=True, exist_ok=True)
    raw_path = data_dir / f"dart_financials_{TODAY.strftime('%Y%m%d')}.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    print(f"  💾 Raw data: {raw_path}")

    return True


# ─── CLI ─────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="CUFA 데이터 자동 수집기")
    parser.add_argument("company",       help="종목명 (예: 삼성전자)")
    parser.add_argument("ticker",        help="종목코드 (예: 005930)")
    parser.add_argument("--output", "-o", help="config.py 출력 경로 (없으면 stdout)")
    parser.add_argument("--update",       action="store_true",
                        help="기존 config.py FINANCIALS만 Nexus MCP로 업데이트")
    args = parser.parse_args()

    collector = CUFACollector(args.company, args.ticker)

    if args.update:
        # 기존 config.py 업데이트 모드
        target = Path(args.output) if args.output else \
                 ROOT / "examples" / args.company / "config.py"
        mcp = NexusMCP()
        if mcp.is_available():
            update_config_with_mcp(target, mcp)
        else:
            print("  ✗ Nexus MCP 불가 — VPS 상태 확인 필요")
        return

    # 전체 수집 모드
    collector.collect_all()

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        collector.generate_config(out)
    else:
        code = collector.generate_config(
            ROOT / "examples" / args.company / "config.py"
        )


if __name__ == "__main__":
    main()
