# Demo-spec Authoring Cheatsheet (one-pass, QA-passing)

전체 `demo-spec.json`을 직접 작성하는 경로(적합한 Industry Pack이 없을 때)에서 **한 번에 유효하고
브라우저 QA를 통과하는** spec을 쓰기 위한 압축 참고표다. 작성 후 반드시 아래 린트를 먼저 돌린다:

```bash
python3 -B .github/skills/ai-platform-demo/scripts/lint_spec.py <session>/<app>-work/demo-spec.json
```

가장 빠른 방법: **`examples/precision-manufacturing.example.json`을 복사해 내부 ID는 그대로 두고
사람이 보는 문자열·숫자만 교체**한다(ID 연동이 자동으로 유지됨).

## 1. Straightforward + 지정 언어 준수

- `dashboard.hero.title`에서 고객 결과를 한 문장으로 먼저 말한다. 회사 소개·제품 목록·아키텍처 설명으로
  시작하지 않는다.
- 각 route는 임원 질문 하나와 primary action 하나만 강조하고, 클릭 전/후 상태가 눈에 띄게 달라야 한다.
- `DEMO_FOCUS`가 App Platform·CI/CD 중심이면 GitHub→App Platform route가 climax를 담당하고,
  Foundry route의 Platform·SRE·Release Agent가 운영 폐루프를 지원한다.

- 메뉴, hero, KPI명, 버튼, 상태, 표 머리글, 토스트, 에이전트 문구는 `meta.language`를 따른다.
- `meta.language`가 `ko`이면 자연스러운 한글을 기본으로 쓴다. linter가 메뉴와 hero를 검사한다.
- 공식 제품명(`Microsoft Foundry`, `Microsoft Agent Framework`, `GitHub Copilot`, `GitHub Actions`,
  `Azure Container Apps`, `Microsoft Entra ID`), 일반 약어·단위
  (`AI`, `KPI`, `OEE`, `API`, `PR`, `ESS`, `MWh`, `SOC`), 코드 식별자는 원문을 유지할 수 있다.
- 한국어 출력에는 장식용 영어를 남기지 않는다: `Overview`→`전체 현황`, `Live`→`실시간`,
  `Agent Studio`→`AI 에이전트`, `Governed`→`정책 적용`.

## 2. 배열 개수 (검증기 강제)
| 위치 | 개수 |
|---|---|
| `navigation` | **정확히 8**, ID 고정: dashboard, operations, simulator, improvement, finance, github, foundry, appPlatform |
| `story.routeScope` | 선택, canonical 순서의 **8개 전체**; 미지정해도 8개 모두 노출 |
| `story.guidedJourneys` | ≥2, 각 route **4~6개**, `dashboard`로 시작 · `bridges`는 route 수−1 |
| `story.scenarioTrace.steps` | **정확히 4**: 고객 업무 route → foundry → github → appPlatform |
| `dashboard.primaryAction` | dashboard 외 고정 route로 이동 |
| `dashboard.kpis` / `operations.kpis` / `improvement.kpis` / `github.kpis` / `foundry.kpis` | **각 정확히 4** |
| `dashboard.feed` | ≥4 · `dashboard.cards.items` ≥3 · `stream.values` ≥2 |
| `operations.flow.nodes` | **4~7** (그리고 `flow.events`도 노드 수만큼 권장) |
| `simulator.inputs` | ≥2(권장 3) · `secondary` ≥3 · `recommendations` ≥1 |
| `improvement.steps` | ≥5 · `factors` ≥4 · `impacts` ≥4 · `board.columns` **정확히 3**(각 `items` ≥1) |
| `finance.levers` | ≥3 · `summaryMetrics` ≥3 · `composition.segments` **정확히 4** |
| `github.issueHeaders` | ≥5 · `steps` ≥5 · `issues` ≥3(각 `diffLines` ≥2) |
| `foundry.profiles` | **5~7**(각 `qa` ≥3, 이름 모두 상이) · `orchestration.stages` ≥3 |
| `appPlatform.cards` | **정확히 3** · `learningLoop.steps` **정확히 4** · `controls.rows`/`memories.rows` ≥N |
| `github.sales` / `foundry.sales` / `appPlatform.sales` | 사업 KPI **정확히 2**, 차별화 기능 ≥3, 통제 증거 ≥3, buyer next step 필수 |

## 3. 내부 ID 연동 (반드시 일치)
- `simulator.inputs[].id` 집합 == 각 `simulator.secondary[].weights`의 키 집합. 모든 `recommendations[].inputId`는 그 집합에 속해야 한다.
- `finance.*.impacts` 키는 `finance.levers[].id`의 **부분집합**이다. 생략한 lever 영향은 0으로 처리한다.
- `operations.action.kpiUpdates`의 키는 바꿀 KPI의 0-based 인덱스(`"0"`~`"3"`)다.
> base를 복사하면 이 ID들이 그대로 유지되므로 **라벨만 바꾸고 id는 두는 것**이 가장 안전하다.

## 4. 색·상태 값
- `status.tone` / `hero.badge.tone`: `success` · `warning` · `danger` · `info` · `violet` (→ ok/warn/bad/info/violet 배지)
- `kpi.color`: `brand` · `info` · `accent` · `success` · `violet` · `warning`
- 디자인은 **고정 GitHub Primer Dark Dimmed 계열 soft-dark**라 색을 새로 만들지 않는다. `design`
  블록은 base의 것을 그대로 복사하며 `design.tokens`는 빈 객체다.

## 5. Rich text (에이전트 답변 등)
- 허용 태그: `b` `strong` `em` `code` `br` `div` `span`
- 허용 class(오직 message-stat용): `message-stats` · `message-stat-label` · `message-stat-value`
- 정확한 통계 마크업:
```html
<div class="message-stats"><div><div class="message-stat-label">라벨</div><div class="message-stat-value">값</div></div><div><div class="message-stat-label">라벨2</div><div class="message-stat-value">값2</div></div></div>
```
- `style`, event handler, URL, SVG, 이미지, 그 외 class는 금지.

## 6. QA 통과 불변식 (lint_spec.py가 검사)
브라우저 QA(`verify_demo.js`)는 인터랙션 완료를 시간 내에 확인한다. 아래를 지키면 첫 렌더에 통과한다.
- `operations.action.durationMs` ≤ **1200** (QA가 ~1300ms 후 권고문 재확인)
- `improvement.action.durationMs` ≤ **2000** (막대가 durationMs에 채워짐, QA ~2200ms 확인)
- `github.action.durationMs` ≤ **2600** (QA ~2800ms 대기)
- `operations.action.recommendationBefore` ≠ `recommendationAfter` (재최적화가 실제로 바뀌어야 함)
- `foundry.orchestration.summary`에 **"의사결정 패키지"**(또는 "decision package") 포함 (QA가 채팅 로그에서 확인)
- `appPlatform.cards[0].value` = `evaluation.initialScore`이고 `finalScore`와는 달라야 한다.
- readiness 진단은 점수를 유지하고 `gaps`를 노출하며, remediation plan 실행 후에만 projected score를 표시한다.
- `appPlatform.evaluation.gaps`에 warning/danger 상태의 미해결 Gap이 하나 이상 있어야 한다.
- Foundry 통제 증거: Entra·Purview·Content Safety, GitHub: AI Controls·Advanced Security,
  App Platform: Entra·Defender를 반드시 포함한다.
- `simulator.output.goodThreshold` > `warningThreshold` — 런타임은 **높은 output을 good/green**으로 처리하므로 output은 "신뢰 점수"처럼 **높을수록 좋은 값**으로 설계한다(부정확률처럼 높을수록 나쁜 값 금지).

## 7. 속도 팁
- spec 작성 후 **먼저 `lint_spec.py`** → 통과하면 render → 그 다음 puppeteer QA. (렌더 전에 gotcha를 <1초에 차단)
- Puppeteer·Chromium은 리서치·작성과 **병렬로** 저장소 밖 공용 캐시에 미리 설치(프리워밍)해 두면 QA 단계 대기가 사라진다.
- 모든 화면에 `● 시연 데이터` 배지 유지, 수치는 시연용 가정치로 명시.
