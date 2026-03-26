---
name: inline-mla-dsa-widget
description: "MLA/DSA 아키텍처형 인라인 위젯. show_widget(claude.ai) 또는 단독 HTML(Claude Code)로 분석·비교·의사결정·브리핑을 시각화. 트리거: '분석', '비교', '정리', '현황', '브리핑', '스코어', '평가', '옵션', '선택지', '우선순위', 'MLA DSA', '아키텍처로', '위젯으로'. 파일 생성보다 인라인 우선. 모든 분석·비교·의사결정에서 자동 적용."
---

# 인라인 MLA/DSA 위젯 스킬 v2

## 1. 핵심 원칙

- **인라인 우선.** claude.ai에서는 show_widget, Claude Code에서는 단독 HTML 파일 생성.
- **플랫/클린.** 투명 배경 + CSS 변수. 다크 배경 하드코딩 금지(호스트 테마 존중).
- **MLA 압축 → DSA 스코어링 → FlashMLA 실행** 3단계 구조.
- **sendPrompt() 버튼**으로 다음 액션 즉시 연결 (Claude Code에서는 링크/버튼 대체).
- **데이터 밀도 우선.** 장문 텍스트 대신 수치+바+카드로 압축. 설명은 대화 본문에.

## 2. 환경별 사용법

### claude.ai (show_widget)
```
1. visualize:read_me → modules: ["interactive"]
2. visualize:show_widget → title, loading_messages, widget_code
3. widget_code에 HTML+CSS+JS 직접 작성 (DOCTYPE/html/head/body 태그 금지)
```

### Claude Code (단독 HTML)
```
1. /home/claude/ 또는 /mnt/user-data/outputs/ 에 .html 파일 생성
2. <!DOCTYPE html> + <html> + <head> + <body> 포함
3. CSS 변수 대신 실제 색상값 사용 (다크: #0D0D1A, 보라: #7C6AF7)
4. sendPrompt() 대신 일반 버튼/링크 사용
```

### CSS 변수 ↔ 다크테마 매핑 (Claude Code용)
| CSS 변수 (claude.ai) | 다크 실제값 (Claude Code) |
|---|---|
| --color-background-primary | #0D0D1A |
| --color-background-secondary | #161628 |
| --color-text-primary | #E8E6F0 |
| --color-text-secondary | #A09CB0 |
| --color-text-tertiary | #6B6780 |
| --color-border-tertiary | #2A2845 |
| --color-text-success | #2ECC71 |
| --color-text-danger | #E63946 |
| --color-text-warning | #F5A623 |
| --color-text-info | #3B82F6 |
| accent (보라) | #7C6AF7 |

## 3. 컴포넌트 라이브러리

### 3.1 메트릭 카드 (상단 요약 — 2~4열)
용도: 핵심 수치를 한눈에. 페이지 최상단에 배치.

```html
<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:1.5rem;">
  <div style="background:var(--color-background-secondary);border-radius:var(--border-radius-md);padding:1rem;">
    <p style="font-size:13px;color:var(--color-text-secondary);margin:0;">라벨</p>
    <p style="font-size:22px;font-weight:500;margin:4px 0 0;">값</p>
    <p style="font-size:12px;color:var(--color-text-success);margin:2px 0 0;">서브텍스트</p>
  </div>
  <!-- 반복 -->
</div>
```

규칙:
- 4열 초과 금지. 3열 이하가 모바일 안전.
- 위험/긴급 = color-text-danger, 성공 = color-text-success
- 숫자는 반드시 반올림 (Math.round, toFixed)

### 3.2 스코어 바 (MLA 차원별 점수)
용도: 5~10개 차원을 수치+바로 시각화. 종합 스코어 하단 표시.

```html
<div style="background:var(--color-background-primary);border:0.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);padding:1.25rem;">
  <p style="font-size:14px;font-weight:500;margin:0 0 12px;">타이틀</p>
  <!-- 차원별 반복 -->
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
    <span style="width:100px;font-size:13px;">차원명</span>
    <div style="flex:1;height:8px;background:var(--color-background-secondary);border-radius:4px;overflow:hidden;">
      <div style="height:100%;width:82%;background:var(--color-text-success);border-radius:4px;"></div>
    </div>
    <span style="width:40px;font-size:13px;font-weight:500;text-align:right;">82</span>
  </div>
  <!-- 종합 -->
  <div style="border-top:0.5px solid var(--color-border-tertiary);padding-top:8px;margin-top:8px;">
    <div style="display:flex;justify-content:space-between;">
      <span style="font-size:13px;font-weight:500;">종합</span>
      <span style="font-size:14px;font-weight:500;">75.4/100</span>
    </div>
  </div>
</div>
```

바 색상 기준:
- 80+ = color-text-success
- 60~79 = color-text-info
- 40~59 = color-text-warning
- <40 = color-text-danger

### 3.3 비교 카드 (옵션 비교 — 2~3열)
용도: 복수 옵션을 나란히 비교. 추천 옵션에 뱃지+두꺼운 테두리.

```html
<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;">
  <!-- 추천 옵션 -->
  <div style="background:var(--color-background-primary);border:2px solid var(--color-border-info);border-radius:var(--border-radius-lg);padding:1rem;">
    <span style="background:var(--color-background-info);color:var(--color-text-info);font-size:11px;padding:2px 8px;border-radius:var(--border-radius-md);">추천</span>
    <p style="font-weight:500;font-size:15px;margin:8px 0 2px;">옵션명</p>
    <p style="font-size:20px;font-weight:500;margin:0;">핵심수치</p>
    <p style="font-size:12px;color:var(--color-text-secondary);margin:6px 0 0;">설명</p>
  </div>
  <!-- 일반 옵션 -->
  <div style="background:var(--color-background-primary);border:0.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-lg);padding:1rem;">
    <!-- 동일 구조, border만 다름 -->
  </div>
</div>
```

### 3.4 플로우 (단계/프로세스)
용도: 실행 순서, 타임라인, 파이프라인.

```html
<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:12px;">
  <span style="background:var(--color-background-danger);color:var(--color-text-danger);padding:6px 12px;border-radius:var(--border-radius-md);font-weight:500;">1단계: 지금</span>
  <span style="color:var(--color-text-tertiary);">→</span>
  <span style="background:var(--color-background-warning);color:var(--color-text-warning);padding:6px 12px;border-radius:var(--border-radius-md);">2단계: 다음주</span>
  <span style="color:var(--color-text-tertiary);">→</span>
  <span style="background:var(--color-background-success);color:var(--color-text-success);padding:6px 12px;border-radius:var(--border-radius-md);">3단계: 완료</span>
</div>
```

색상 의미:
- danger(빨강) = 긴급/지금
- warning(주황) = 진행중/다음
- info(파랑) = 계획/준비
- success(초록) = 완료/달성

### 3.5 접이식 레이어 (클릭→상세)
용도: 대량 정보를 카테고리별로 접어서 보여주기. 메모리 맵, 프로젝트 현황 등.

```html
<div id="layers"></div>
<script>
var L=[
  {name:"레이어명",color:"var(--color-background-info)",tc:"var(--color-text-info)",items:[
    {id:1,t:"항목명",d:"상세 설명 텍스트"},
  ]}
];
var el=document.getElementById('layers');
L.forEach(function(layer,li){
  var sec=document.createElement('div');
  sec.style.cssText='margin-bottom:12px;';
  var hdr=document.createElement('div');
  hdr.style.cssText='background:'+layer.color+';border-radius:var(--border-radius-md);padding:8px 14px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;';
  hdr.innerHTML='<span style="font-size:13px;font-weight:500;color:'+layer.tc+';">'+layer.name+' ('+layer.items.length+')</span><span style="font-size:11px;color:'+layer.tc+';" id="arr'+li+'">▼</span>';
  var body=document.createElement('div');
  body.id='body'+li;
  body.style.cssText='display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;padding:8px 0;';
  layer.items.forEach(function(item){
    var card=document.createElement('div');
    card.style.cssText='background:var(--color-background-primary);border:0.5px solid var(--color-border-tertiary);border-radius:var(--border-radius-md);padding:10px;cursor:pointer;';
    card.innerHTML='<div style="display:flex;justify-content:space-between;"><span style="font-size:12px;font-weight:500;">#'+item.id+' '+item.t+'</span><span style="font-size:10px;color:var(--color-text-tertiary);" id="ca'+item.id+'">+</span></div><div id="cd'+item.id+'" style="display:none;margin-top:6px;font-size:11px;color:var(--color-text-secondary);line-height:1.5;">'+item.d+'</div>';
    card.onclick=function(e){e.stopPropagation();var d=document.getElementById('cd'+item.id);var a=document.getElementById('ca'+item.id);if(d.style.display==='none'){d.style.display='block';a.textContent='−';}else{d.style.display='none';a.textContent='+';}};
    body.appendChild(card);
  });
  hdr.onclick=function(){var b=document.getElementById('body'+li);var a=document.getElementById('arr'+li);if(b.style.display==='none'){b.style.display='grid';a.textContent='▼';}else{b.style.display='none';a.textContent='▶';}};
  sec.appendChild(hdr);sec.appendChild(body);el.appendChild(sec);
});
</script>
```

### 3.6 체크리스트 (인터랙티브)
용도: TODO, 제출 전 점검, 마일스톤 추적.

```html
<div id="checklist"></div>
<script>
var checks=[
  {t:'항목 텍스트',critical:true},
  {t:'일반 항목',critical:false}
];
var el=document.getElementById('checklist');
checks.forEach(function(c,i){
  var row=document.createElement('div');
  row.style.cssText='display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:0.5px solid var(--color-border-tertiary);';
  row.innerHTML='<span style="width:24px;height:24px;border-radius:4px;border:1.5px solid '+(c.critical?'var(--color-text-danger)':'var(--color-border-secondary)')+';display:flex;align-items:center;justify-content:center;flex-shrink:0;cursor:pointer;" onclick="this.innerHTML=this.innerHTML?\'\':\'\u2713\';this.style.background=this.innerHTML?\'var(--color-background-success)\':\'\'"></span><span style="font-size:13px;'+(c.critical?'font-weight:500;':'color:var(--color-text-secondary);')+'">'+(i+1)+'. '+c.t+'</span>'+(c.critical?'<span style="font-size:10px;color:var(--color-text-danger);flex-shrink:0;">필수</span>':'');
  el.appendChild(row);
});
</script>
```

### 3.7 데이터 그리드 (표 대체)
용도: 구조화된 데이터를 위젯 안에서 보여줄 때. 마크다운 표보다 시각적.

```html
<div style="display:grid;grid-template-columns:120px 1fr 1fr;gap:6px;font-size:12px;">
  <span style="font-weight:500;color:var(--color-text-tertiary);">항목</span>
  <span style="font-weight:500;">옵션A</span>
  <span style="font-weight:500;">옵션B</span>
  <span style="color:var(--color-text-tertiary);">가격</span>
  <span>100만</span>
  <span style="color:var(--color-text-success);font-weight:500;">50만</span>
</div>
```

### 3.8 알림 박스 (상태별)
용도: 긴급 공지, 성공 메시지, 경고, 정보.

```html
<!-- 긴급 -->
<div style="background:var(--color-background-danger);border-radius:var(--border-radius-lg);padding:1rem;">
  <p style="font-size:14px;font-weight:500;color:var(--color-text-danger);margin:0 0 6px;">제목</p>
  <p style="font-size:13px;color:var(--color-text-danger);margin:0;">내용</p>
</div>
<!-- 성공 -->
<div style="background:var(--color-background-success);border-radius:var(--border-radius-lg);padding:1rem;">
  <p style="font-size:14px;font-weight:500;color:var(--color-text-success);margin:0;">내용</p>
</div>
```

### 3.9 sendPrompt 버튼
용도: 다음 액션을 즉시 실행. claude.ai 전용.

```html
<button onclick="sendPrompt('다음 질문 텍스트')">버튼 라벨 ↗</button>
<button onclick="sendPrompt('두번째 액션')" style="margin-left:8px;">두번째 ↗</button>
```

## 4. MLA/DSA 워크플로우

### Step 1: MLA 차원 추출 (입력 → 압축)
- 분석 대상에서 5~10개 핵심 차원 도출
- 각 차원에 0~100 점수 + 근거 note
- 메트릭 카드로 요약 수치, 스코어 바로 차원별 점수

### Step 2: DSA 쿼리별 어텐션 (상황 → 선택)
- 사용자 목적에 따라 어떤 차원이 중요한지 가중치 조정
- 비교 카드로 옵션별 강약점 시각화
- 추천 옵션에 뱃지 + border-info

### Step 3: FlashMLA 실행 계획 (결정 → 액션)
- 플로우로 단계 시각화
- sendPrompt 버튼으로 다음 턴 연결
- 독립 액션은 병렬 배치 (grid)

## 5. 조합 패턴 (실전에서 검증된 것들)

### 패턴A: 사업 평가/심사 스코어카드
메트릭 카드(합격확률) → 스코어 바(P/S/S/T 각 점수) → 알림 박스(강점/약점) → 버튼

### 패턴B: 프로그램 비교/선택
메트릭 카드(총 건수/금액) → 비교 카드(3열) → 데이터 그리드(상세) → 플로우(실행순서) → 버튼

### 패턴C: 현황 브리핑/대시보드
메트릭 카드(KPI) → 접이식 레이어(카테고리별) → 알림 박스(긴급사항) → 체크리스트(TODO) → 버튼

### 패턴D: 의사결정/우선순위
메트릭 카드(요약) → 스코어 바(MLA 점수) → 비교 카드(top-k 옵션) → 플로우(추천 순서) → 버튼

## 6. 디자인 규칙

1. 투명 배경 (호스트 테마 존중). 다크 배경 하드코딩은 Claude Code 전용.
2. CSS 변수만 사용 (claude.ai). Claude Code는 §2 매핑표 참조.
3. 폰트: 시스템(Anthropic Sans) 그대로. import 금지.
4. 그라디언트, 그림자, 네온, 블러 금지.
5. 최소 폰트 11px. 제목 14~22px/500. 본문 12~13px/400.
6. 숫자는 반드시 Math.round() / toFixed() 처리.
7. border: 0.5px solid var(--color-border-tertiary). 추천 옵션만 2px.
8. border-radius: var(--border-radius-md) 기본, 카드는 var(--border-radius-lg).
9. 4열 초과 그리드 금지. 차원 15개 초과 금지.
10. loading_messages: 1~4개, 각 5단어 내외, 한국어, 재미있게.
11. title: snake_case, 고유하게 (e.g., startup_comparison_2026).
12. read_me 모듈: ["interactive"] 호출 후 사용 (claude.ai).

## 7. 트리거 패턴

자동 적용:
- 분석, 비교, 평가, 정리, 현황, 브리핑, 스코어
- 옵션, 선택지, 우선순위, 뭐가 나아, 어떤 게 좋아
- MLA, DSA, 아키텍처, 위젯으로, 인라인으로
- 프로그램 비교, 기업 비교, 사업 평가

명시적 트리거:
- "위젯으로 보여줘" / "인라인으로" / "아키텍처로" / "스코어카드로"

비적용:
- "텍스트로 줘" / "간단히" / 단순 팩트 질문 / 코드 작성

## 8. 안티패턴

- show_widget 대신 create_file로 HTML 파일 생성 (claude.ai에서)
- 위젯 안에 장문 텍스트 넣기 (설명은 대화 본문에)
- 6열 이상 그리드 / 차원 15개 이상
- 하드코딩 색상 (claude.ai에서)
- DOCTYPE/html/head/body 태그 (show_widget에서)
- position: fixed (iframe 뷰포트 붕괴)
- font-size 11px 미만
- 반올림 안 한 소수점 숫자
