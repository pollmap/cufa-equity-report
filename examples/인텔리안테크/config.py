"""
인텔리안테크(189300) CUFA 기업분석보고서 — config.py
Single Source of Truth: 모든 재무 데이터, 가정, 상수를 여기에 정의.
서브에이전트는 이 파일에서만 데이터를 import한다.

데이터 수집일: 2026-04-06 (KST)
출처: DART CFS(연결), pykrx, ECOS, 증권사 리포트
"""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# ============================================================
# 날짜 설정 (하드코딩 금지 — datetime.now 사용)
# ============================================================
KST = ZoneInfo('Asia/Seoul')
REPORT_DATE = datetime.now(KST)
REPORT_DATE_STR = REPORT_DATE.strftime('%Y년 %m월 %d일')
REPORT_YEAR = REPORT_DATE.year
EST_YEARS = [REPORT_YEAR, REPORT_YEAR + 1, REPORT_YEAR + 2]  # 2026E, 2027E, 2028E
ACTUAL_YEARS = [REPORT_YEAR - 1, REPORT_YEAR - 2, REPORT_YEAR - 3]  # 2025A, 2024A, 2023A
DATA_AS_OF = '2026-04-06'

# ============================================================
# 종목 기본 정보
# ============================================================
TICKER = '189300'
COMPANY_NAME = '인텔리안테크'
COMPANY_NAME_EN = 'INTELLIAN TECHNOLOGIES Inc.'
MARKET = 'KOSDAQ'
SUBTITLE = 'LEO 시대의 지상 인프라를 독점하다'
SECTOR = 'IT / 통신장비 (산업분류: 26429)'
LISTING_DATE = '2016-12-23'

# ============================================================
# 팀 정보
# ============================================================
TEAM_NAME = 'CUFA 리서치팀'
TEAM_MEMBERS = ['이찬희']

# ============================================================
# 주가 데이터 (출처: pykrx, 2026-04-06)
# ============================================================
CURRENT_PRICE = 111_200  # 원 (2026.04.06 종가)
SHARES_OUTSTANDING = 10_733_334  # 주 (자본금 5,366,667,000 / 액면 500)
MARKET_CAP = 11_935  # 억원 (10,733,334 × 111,200 / 1억)
WEEK52_HIGH = 149_400  # 원 (출처: pykrx 1Y history)
WEEK52_LOW = 30_800  # 원
YTD_CHANGE_PCT = None

# ============================================================
# 투자의견
# ============================================================
OPINION = 'BUY'
TARGET_PRICE = 155_000  # 원 (Phase 9 밸류에이션 결과)
UPSIDE_PCT = round((155_000 / CURRENT_PRICE - 1) * 100, 1)  # +39.4%

# ============================================================
# 재무 데이터 (출처: DART CFS 연결, 단위: 억원)
# ============================================================
FINANCIALS = {
    # IS (포괄손익계산서) — 연결 기준
    'revenue': {
        2020: 1_101, 2021: 1_380, 2022: 2_395, 2023: 3_050, 2024: 2_578, 2025: 3_196,
        '2026E': 4_179, '2027E': 5_300, '2028E': 6_360,
        # 2026E: 키움증권 4,179억 (YoY +30.7%), 게이트웨이 1,300억 + VSAT 2,300억 + FPA/기타 579억
        # 2027E: YoY +26.8%, LEO 안테나 본격 양산 + 항공용 Panasonic 매출 반영
        # 2028E: YoY +20.0%, 게이트웨이 안정화 + 정부군 시장 본격 진입
    },
    'cost_of_revenue': {
        2020: 750, 2021: 963, 2022: 1_648, 2023: 2_104, 2024: 1_941, 2025: 2_252,
    },
    'gross_profit': {
        2020: 351, 2021: 417, 2022: 747, 2023: 946, 2024: 637, 2025: 944,
    },
    'rnd': {
        2020: 137, 2021: 170, 2022: 236, 2023: 352, 2024: 380, 2025: 372,
        # R&D 비율: 2025A 11.6%, 2024A 14.7% — 안테나 기술 기업 특성상 높은 R&D 투자
    },
    'sga': {
        2020: 182, 2021: 225, 2022: 358, 2023: 487, 2024: 451, 2025: 452,
    },
    'operating_income': {
        2020: 32, 2021: 22, 2022: 153, 2023: 107, 2024: -194, 2025: 120,
        '2026E': 345, '2027E': 530, '2028E': 700,
        # 2026E OPM 8.3%, 2027E 10.0%, 2028E 11.0% — 게이트웨이 고마진 믹스 개선
    },
    'opm': {
        2020: 2.9, 2021: 1.6, 2022: 6.4, 2023: 3.5, 2024: -7.5, 2025: 3.7,
        '2026E': 8.3, '2027E': 10.0, '2028E': 11.0,
    },
    'net_income': {
        2020: 6, 2021: 60, 2022: 160, 2023: 55, 2024: -30, 2025: 75,
        '2026E': 260, '2027E': 400, '2028E': 530,
    },
    'eps': {
        2023: 572, 2024: -288, 2025: 724,
        '2026E': 2_422, '2027E': 3_727, '2028E': 4_938,
        # EPS = NI / 발행주식수(10,733,334)
    },
    'ebitda': {
        2022: 240, 2023: 210, 2024: -90, 2025: 230,
        '2026E': 480, '2027E': 680, '2028E': 870,
    },

    # BS (재무상태표) — 연결 기준
    'total_assets': {
        2020: 1_528, 2021: 2_615, 2022: 3_704, 2023: 4_537, 2024: 4_407, 2025: 4_965,
    },
    'total_liabilities': {
        2020: 761, 2021: 995, 2022: 1_917, 2023: 1_787, 2024: 1_761, 2025: 2_302,
    },
    'stockholders_equity': {
        2020: 767, 2021: 1_620, 2022: 1_787, 2023: 2_750, 2024: 2_646, 2025: 2_663,
    },
    'cash': {
        2023: 559, 2024: 215, 2025: 328,
        # 기말 현금및현금성자산 (출처: DART CF)
    },
    'total_debt': {
        2022: 560, 2023: 480, 2024: 500, 2025: 650,
    },
    'current_assets': {
        2022: 2_143, 2023: 2_833, 2024: 2_253, 2025: 2_768,
    },
    'current_liabilities': {
        2022: 1_347, 2023: 1_017, 2024: 917, 2025: 1_476,
    },

    # CF (현금흐름표) — 2025 연결 기준
    'free_cashflow': {
        2025: -50,  # 추정: 영업CF - CAPEX
    },

    # 배당
    'dps': {
        2023: 100, 2024: 100, 2025: 200,
        # 2025년 DPS 200원, 배당성향 27.3% (출처: DART)
    },
}

# ============================================================
# 주요 재무비율 (2025A 기준)
# ============================================================
RATIOS = {
    'psr_ttm': round(MARKET_CAP / FINANCIALS['revenue'][2025], 2),  # 3.73
    'per_ttm': round(CURRENT_PRICE / FINANCIALS['eps'][2025], 1) if FINANCIALS['eps'].get(2025) else None,  # 153.6
    'per_fwd': round(CURRENT_PRICE / FINANCIALS['eps']['2026E'], 1),  # 45.9
    'pbr': round(MARKET_CAP / FINANCIALS['stockholders_equity'][2025], 2),  # 4.48
    'ev_ebitda_fwd': round((MARKET_CAP + FINANCIALS['total_debt'].get(2025, 0) - FINANCIALS['cash'].get(2025, 0)) / FINANCIALS['ebitda']['2026E'], 1),  # 26.2
    'debt_to_equity': round(FINANCIALS['total_liabilities'][2025] / FINANCIALS['stockholders_equity'][2025] * 100, 1),  # 86.5%
    'roe': round(FINANCIALS['net_income'][2025] / FINANCIALS['stockholders_equity'][2025] * 100, 1),  # 2.8%
    'roa': round(FINANCIALS['net_income'][2025] / FINANCIALS['total_assets'][2025] * 100, 1),  # 1.5%
    'current_ratio': round(FINANCIALS['current_assets'][2025] / FINANCIALS['current_liabilities'][2025], 2),  # 1.88
}

# ============================================================
# 대주주 구성 (출처: DART 주요주주, 2026.01 기준)
# ============================================================
SHAREHOLDERS = [
    ('성상엽(CEO) 외 특수관계인', 23.13, '창업자/대표이사, 보호예수'),
    ('에이텐벤처스 외 기관', 11.14, 'VC/기관투자자'),
    ('자사주', 2.5, '2025년 81.5억 자사주 매입'),
    ('기타 소액주주', 63.23, ''),
]

# ============================================================
# 사업부 구조 / 제품 라인업
# ============================================================
PRODUCTS = [
    {
        'name': 'Maritime VSAT',
        'type': '해상용 위성통신 안테나',
        'models': 'v45, v60, v85, v100, v240',
        'revenue_pct': 45,
        'description': '해상용 VSAT 안테나 글로벌 1위. Ku/Ka/C-band 대응. 세계 해상선박 15,000+대 장착.',
        'status': '양산 (M/S 1위)',
    },
    {
        'name': 'Gateway Antenna',
        'type': '지상 게이트웨이 안테나',
        'models': 'GX100HP, GX150HP, 대형 고정안테나',
        'revenue_pct': 33,
        'description': 'LEO/MEO 위성 사업자의 지상국 인프라. SES mPOWER 등 대형 프로젝트.',
        'status': '급성장 (2025 YoY +256%)',
    },
    {
        'name': 'Flat Panel Antenna',
        'type': '전자식 평판 안테나',
        'models': 'g-series (GX5)',
        'revenue_pct': 7,
        'description': 'LEO 위성 추적용 전자식 안테나. 기계식 대비 소형/경량/저비용.',
        'status': '양산 시작 (2025~)',
    },
    {
        'name': 'Military/Gov',
        'type': '정부/군 위성 터미널',
        'models': 'FLYAWAY Series',
        'revenue_pct': 10,
        'description': '군사/정부 전용 이동형 위성통신 단말기. 고마진 장기계약.',
        'status': '확대중',
    },
    {
        'name': 'TVRO',
        'type': '위성방송 수신안테나',
        'models': 'WorldView Series',
        'revenue_pct': 5,
        'description': '해상/RV용 위성TV 수신안테나. 레거시 제품, 축소 추세.',
        'status': '유지',
    },
]

# ============================================================
# 수주잔고 (출처: 증권사 리포트, 2025말 기준)
# ============================================================
BACKLOG = {
    'total_contracts': 12,
    'total_value_krw': 2_900,  # 억원 (게이트웨이 수주잔고 추정)
    'key_contracts': [
        {'client': 'SES', 'content': 'mPOWER 게이트웨이 안테나 공급', 'value': '711억', 'year': 2021},
        {'client': 'SES', 'content': '추가 게이트웨이 안테나 공급', 'value': '253억', 'year': 2025},
        {'client': 'Panasonic Avionics', 'content': '항공용 위성통신 안테나', 'value': '409억', 'year': 2025},
        {'client': 'Amazon Kuiper', 'content': '게이트웨이 안테나 (추정)', 'value': '미공개', 'year': 2025},
        {'client': '미국 정부기관', 'content': '정부/군 터미널', 'value': '미공개', 'year': 2024},
    ],
}

# ============================================================
# 투자포인트
# ============================================================
INVESTMENT_POINTS = [
    {
        'id': 1,
        'title': '"LEO 게이트웨이 = 안테나 슈퍼사이클"',
        'subtitle': '지상 인프라 없이 위성은 무용지물',
        'chain': [
            'Starlink/OneWeb/SES mPOWER/Amazon Kuiper 등 LEO 위성 3만기+ 발사 계획',
            '위성이 늘면 지상 게이트웨이 안테나도 비례 증가 (위성:게이트웨이 = N:1)',
            '인텔리안 = 비스타링크 게이트웨이 안테나 시장 M/S 1위',
            '2025년 게이트웨이 매출 1,057억(YoY +256%), 수주잔고 2,900억 = 2년 매출 가시성',
            '2026E 게이트웨이 1,300억 → 2028E 2,500억: TAM 자체가 구조적 확장',
        ],
    },
    {
        'id': 2,
        'title': '"非스타링크 진영의 무기 공급자"',
        'subtitle': 'Starlink을 제외한 모든 위성 사업자가 고객',
        'chain': [
            'Starlink이 LEO 위성통신 70%+ 장악 → 나머지 30% 사업자들의 경쟁 투자 가속',
            'SES(mPOWER), Amazon(Kuiper), Eutelsat(OneWeb), Telesat(Lightspeed) = 모두 인텔리안 고객',
            '고객 다변화 = 특정 사업자 의존도 낮음 + Lock-in 효과 (안테나 교체 비용 높음)',
            'Panasonic Avionics 409억 수주 = 항공 IFC 시장 진입, 비해상 고객 확대',
            '비스타링크 진영이 경쟁적으로 투자할수록 인텔리안의 수혜 확대',
        ],
    },
    {
        'id': 3,
        'title': '"해상 → 항공 → 정부군: 플랫폼 확장"',
        'subtitle': 'TAM 3배 확대와 고마진 믹스 전환',
        'chain': [
            '기존 해상 VSAT 시장(연 15억달러) 성숙 → 해상만으로는 성장 한계',
            '항공 IFC 시장(연 80억달러): Panasonic 수주 409억 = 항공 진입 시그널',
            '정부/군 시장(연 50억달러): FLYAWAY 터미널 + 미국 방산 인증 추진',
            'FPA(전자식 평판안테나) 양산 → 육상/차량/UAV 등 신규 플랫폼 장착 가능',
            'OPM: 해상 VSAT 5~8% → 게이트웨이 15~20% → 정부군 25~30% 고마진 전환',
        ],
    },
]

# ============================================================
# 리스크 요인
# ============================================================
RISKS = [
    {
        'name': 'Starlink 자체 안테나 생산',
        'probability': 40, 'impact': 70,
        'description': 'SpaceX가 Starlink 지상안테나를 100% 자체 생산. 게이트웨이도 내재화할 경우 TAM 축소.',
        'mitigation': 'Starlink 게이트웨이는 현재 자체 설계. 인텔리안은 非스타링크 전문. 고객 풀 겹치지 않음.',
        'eps_impact': 'EPS -500원 (게이트웨이 20% 축소 시)', 'monitoring': 'Starlink 게이트웨이 자체 생산 여부',
    },
    {
        'name': 'LEO 위성 사업자 투자 지연',
        'probability': 30, 'impact': 60,
        'description': 'Amazon Kuiper, Telesat 등 LEO 프로젝트 지연 시 게이트웨이 수주 이연.',
        'mitigation': 'SES mPOWER는 이미 운용중. 수주잔고 2,900억으로 2년 매출 확보. 단기 영향 제한적.',
        'eps_impact': 'EPS -300원 (2027E 게이트웨이 15% 이연)', 'monitoring': 'Kuiper 발사 일정 + Telesat 자금조달',
    },
    {
        'name': '환율 변동',
        'probability': 60, 'impact': 40,
        'description': '매출의 90%+가 달러 결제. 원화 강세 시 원화 환산 매출 감소.',
        'mitigation': '원가의 60%도 달러 연동(수입부품). 자연 헤지 효과. 순 환 노출 약 30%.',
        'eps_impact': 'USD/KRW 100원 하락 시 EPS -150원', 'monitoring': 'USD/KRW 환율',
    },
    {
        'name': 'FPA 기술 경쟁 심화',
        'probability': 50, 'impact': 50,
        'description': 'Kymeta, ThinKom 등 경쟁사 FPA 기술 추격. 가격 경쟁 가능.',
        'mitigation': '인텔리안 GX5는 이미 양산 단계. Kymeta는 아직 시장 침투 미미. 기계식→전자식 전환 과정에서 선발자 이점.',
        'eps_impact': 'FPA ASP 20% 하락 시 EPS -100원', 'monitoring': '경쟁사 FPA 양산 일정 + ASP 동향',
    },
    {
        'name': '대주주 지분 희석 / 오버행',
        'probability': 30, 'impact': 30,
        'description': 'CB/BW 전환 또는 보호예수 해제 시 물량 출회 가능.',
        'mitigation': '2025년 자사주 81.5억 매입 = 주주환원 의지 확인. DPS 100→200원 증가.',
        'eps_impact': '제한적', 'monitoring': '보호예수 해제 일정 + 자사주 매입 계획',
    },
]

# ============================================================
# Kill Conditions (투자논지 사망 조건)
# ============================================================
KILL_CONDITIONS = [
    {'condition': '게이트웨이 수주잔고 1,500억 이하', 'current': '2,900억', 'margin': '1,400억', 'frequency': '분기별'},
    {'condition': '2026 연간 OPM 5% 미달', 'current': '2025A 3.7%', 'margin': '컨센서스 8.3%', 'frequency': '분기별'},
    {'condition': 'SES mPOWER 프로젝트 중단/축소', 'current': '정상 운용중', 'margin': '-', 'frequency': '월별'},
    {'condition': 'Amazon Kuiper 게이트웨이 자체 생산 전환', 'current': '미확인', 'margin': '-', 'frequency': '분기별'},
]

# ============================================================
# Peer 데이터 (출처: Bloomberg/Reuters, 2026.04)
# ============================================================
PEERS = {
    'VSAT': {
        'name': 'Viasat',
        'country': '미국',
        'market_cap_usd': 3_200,  # M$
        'revenue_usd': 4_000,  # M$ (FY2025)
        'psr': 0.8,
        'per': 25.0,
        'pbr': 1.5,
        'ev_ebitda': 8.5,
        'opm': 5.0,
        'description': '위성운용+단말기 통합 사업자',
    },
    'SATS': {
        'name': 'EchoStar/Hughes',
        'country': '미국',
        'market_cap_usd': 4_500,
        'revenue_usd': 1_800,
        'psr': 2.5,
        'per': 30.0,
        'pbr': 0.8,
        'ev_ebitda': 7.0,
        'opm': 12.0,
        'description': '위성운용+Hughes 브로드밴드',
    },
    'CMTL': {
        'name': 'Comtech Telecom',
        'country': '미국',
        'market_cap_usd': 400,
        'revenue_usd': 500,
        'psr': 0.8,
        'per': None,
        'pbr': 1.2,
        'ev_ebitda': 12.0,
        'opm': -3.0,
        'description': '위성지상국+정부 통신',
    },
    '189300': {
        'name': '인텔리안테크',
        'country': '한국',
        'market_cap_usd': round(MARKET_CAP / 15.1, 0),  # ~790M$
        'revenue_usd': round(FINANCIALS['revenue'][2025] / 15.1, 0),  # ~212M$
        'psr': RATIOS['psr_ttm'],
        'per': RATIOS['per_ttm'],
        'pbr': RATIOS['pbr'],
        'ev_ebitda': RATIOS['ev_ebitda_fwd'],
        'opm': FINANCIALS['opm'][2025],
        'description': '위성통신 안테나 전문 (글로벌 1위)',
    },
}

# ============================================================
# 산업 데이터
# ============================================================
INDUSTRY = {
    'sat_comm_market_2025': 32.0,  # $B (위성통신 전체 시장)
    'sat_comm_market_2030': 62.0,  # $B
    'sat_comm_cagr': 14.1,  # %
    'vsat_antenna_market_2025': 4.2,  # $B (VSAT 안테나 시장)
    'vsat_antenna_market_2030': 8.5,  # $B
    'vsat_antenna_cagr': 15.0,  # %
    'leo_satellites_planned': 30_000,  # 기 (향후 10년 발사 계획)
    'leo_gateway_market_2026': 2.0,  # $B (LEO 게이트웨이 시장)
    'maritime_vsat_installed': 15_000,  # 대 (글로벌 해상 VSAT 설치 대수)
    'ifc_market_2030': 12.0,  # $B (기내 인터넷 시장)
    'gov_mil_satcom_2025': 50.0,  # $B (정부/군 위성통신)
    'starlink_subscribers': 4_000_000,  # 명 (2026 추정)
    'ses_mpower_satellites': 11,  # 기 (MEO 위성)
    'amazon_kuiper_planned': 3_236,  # 기
    'telesat_lightspeed': 298,  # 기
    'intellian_maritime_ms': 35,  # % (해상 VSAT M/S 추정)
}

# ============================================================
# 시나리오 분석
# ============================================================
SCENARIOS = {
    'bull': {
        'price': 185_000,
        'upside': round((185_000 / CURRENT_PRICE - 1) * 100, 1),
        'prob': 25,
        'desc': 'Amazon Kuiper 대량 수주 확정 + 항공 IFC 추가 계약 + 2027E OPM 12%+',
    },
    'base': {
        'price': 155_000,
        'upside': round((155_000 / CURRENT_PRICE - 1) * 100, 1),
        'prob': 50,
        'desc': '컨센서스 수준 실적 달성 + 게이트웨이 수주 유지 + OPM 8~10%',
    },
    'bear': {
        'price': 85_000,
        'upside': round((85_000 / CURRENT_PRICE - 1) * 100, 1),
        'prob': 25,
        'desc': 'LEO 투자 지연 + 환율 급락 + FPA 경쟁 심화 → 2026E 매출 3,500억 하회',
    },
}

# ============================================================
# 매크로 데이터 (출처: ECOS, 2026.04.06)
# ============================================================
MACRO = {
    'risk_free_rate': 2.75,  # % (한국은행 기준금리, ECOS)
    'equity_risk_premium': 5.5,  # % (Damodaran 한국 ERP)
    'usd_krw': 1_507.6,  # 원/달러 (ECOS 2026.04.06)
    'beta': 1.20,  # (pykrx 60M weekly, vs KOSPI)
    'cost_of_equity': 2.75 + 1.20 * 5.5,  # = 9.35% (CAPM: Rf + β × ERP)
    'cost_of_debt': 4.5,  # % (추정, 신용등급 감안)
    'tax_rate': 22.0,  # % (법정 법인세율)
    'wacc': None,  # Phase 9에서 계산
    'terminal_growth': 2.0,  # % (명목GDP 성장률 근사)
}

# ============================================================
# 증권사 전망 (출처: 키움/한화/유진증권, 2026.02)
# ============================================================
CONSENSUS = {
    'coverage': 5,  # 커버리지 증권사 수
    'target_price_avg': 160_000,  # 원 (컨센서스 평균)
    'target_price_high': 185_000,  # 키움
    'target_price_low': 140_000,
    'revenue_2026E': 4_179,  # 억원
    'op_2026E': 345,  # 억원
    'ni_2026E': 260,  # 억원
    'revenue_2027E': 5_300,  # 억원
    'gateway_revenue_2026E': 1_300,  # 억원
}

# ============================================================
# 차트 색상 (CUFA 표준)
# ============================================================
CHART_COLORS = {
    'primary': '#7c6af7',
    'primary_light': '#a78bfa',
    'secondary': '#6cb4ee',
    'tertiary': '#4ecdc4',
    'quaternary': '#ffd93d',
    'positive': '#4ecdc4',
    'negative': '#ff6b6b',
    'gray': '#555555',
    'bg': '#0a0a0a',
    'surface': '#0f0f0f',
    'text': '#e0e0e0',
}
