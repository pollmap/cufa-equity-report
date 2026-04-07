---
name: project_cufa_next_report
description: 다음 세션 — KSS해운 v9.1 첫 실전 테스트
type: project
---

# 다음 세션: KSS해운 CUFA 보고서 (v9.1 첫 실전)

## 세션 1 완료 (2026-03-28): SKILL.md v9.1

### 최종 결과
- SKILL.md: 3,552줄 → **3,703줄** (수정+추가)
- build_template.py: **763줄** 신규 생성
- 수치 모순 17건 → 0건, 버그 5건 → 0건
- SMIC 벤치마크 6가지 + 글로벌 IB/헤지펀드 16가지 기법 전부 반영
- 37/37 전수 검증 PASS, VPS 동기화 완료

## 다음 세션 1순위: KSS해운

찬희님이 `/cufa-equity-report kss해운` 실행함 → 다음 세션에서 바로 시작

### 사전 준비
- [ ] KSS해운 종목코드 확인 (DART 검색)
- [ ] Nexus MCP dart_financial_statements로 CFS/OFS 수집
- [ ] 해운업 산업분석 (BDI, 컨테이너 운임, 벌크선 시장)
- [ ] Peer: HMM, 팬오션, 대한해운 등

### 적용할 v9.1 신규 기법 (전부!)
- Investment Thesis Dashboard (6-Box Grid)
- Key Debates (Bull vs Bear 대칭)
- Variant Perception (컨센서스 vs CUFA)
- Catalyst Timeline + Kill Conditions
- Forward PER/PBR 밴드
- Quality of Earnings + Earnings Surprise
- Management Scorecard
- Scenario Summary 테이블
- Compliance Notice 상세
- TP Revision History

### 보류: 한국콜마 (161890)
- 원래 세션 2 계획이었으나, 찬희님이 KSS해운 먼저 지시
- 한국콜마는 KSS해운 이후 세션에서
