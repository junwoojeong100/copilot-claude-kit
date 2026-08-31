# Editorial Business Deck Style

`Claude Cowork처럼`, `컨설팅 덱처럼`, `전문 디자이너가 만든 임원 자료처럼`이라는 요청은 특정 회사의
브랜드를 복제하라는 의미가 아니라 아래 **템플릿 인식형 편집 원칙**으로 해석한다.

## 1. 템플릿과 브랜드가 최우선

- 사용자가 준 템플릿·샘플 덱·브랜드 가이드가 있으면 그 slide master, grid, font, color, footer를 먼저
  분석하고 그대로 따른다.
- 샘플이 없을 때만 주제에 맞는 자체 시각 언어를 만든다.
- `Cowork-like` 요청만으로 Anthropic 로고·주황색·Poppins/Lora를 자동 적용하지 않는다.

## 2. 기본 시각 언어

- 강한 결론형 제목 + 넓은 여백 + 정밀한 column/grid.
- square 또는 거의 square인 surface, hairline rule, 얇은 separator를 우선한다.
- 제목 바로 아래의 짧은 장식용 accent line, 반복되는 pill chip, 과도한 rounded card와 soft shadow는
  AI 생성물처럼 보이기 쉬우므로 기본값으로 사용하지 않는다.
- 한 가지 motif(예: 왼쪽 세로 bar, 번호 folio, 상단 band, 얇은 divider)를 정해 덱 전체에서 반복한다.

## 3. 색상

- 하나의 dominant color가 전체 시각 무게의 약 60~70%를 담당하고, support 1~2개와 sharp accent 1개만
  보조한다.
- 동일한 단계·상태·소유권은 같은 색을 유지한다.
- 브랜드가 없는 Microsoft/GitHub/Azure 임원 자료는 white canvas + near-black ink + Microsoft/Azure
  primary + optional blue-teal secondary가 안전하다.
- 색보다 위치·크기·굵기·여백으로 계층을 먼저 만든다.

## 4. 타이포그래피

- 한국어 덱의 모든 visible text: `Apple SD Gothic Neo`. 표지·본문·표·도식·footer에서 다른 글꼴을 섞지 않는다.
- 한국어 본문 리딩 메시지: `Apple SD Gothic Neo · 27pt · Bold`. 모든 본문 장에서 같은 family·size·weight를 쓴다.
- 표지·section divider title: 30~42pt, 강한 weight. 긴 제목은 2줄을 위한 전용 높이를 확보하거나 문구를 줄인다.
- Primary body: 15~19pt.
- Secondary body: 13~15pt.
- Table/diagram label: 11~13pt.
- Source/footer: 8~9.5pt.
- 한 슬라이드 안에서 title/body/caption의 크기 차이가 분명해야 한다.
- 전체 축소 요청은 역할별로 0.5~2pt 일괄 적용한다. 축소 후 생긴 여백은 근거·KPI·owner·예외 조건을
  보강하는 데 쓰고, 이미 밀도가 높은 슬라이드는 내용을 유지한다.

## 5. 레이아웃

내용 전달이 목적인 본문 슬라이드에는 정보 관계와 맞는 시각 구조를 하나 이상 둔다. 표지·section
divider·단순 마무리 장에는 장식적 visual을 억지로 추가하지 않는다.

- metric-led page: 큰 숫자 + 작은 해설 + 기준/출처
- editorial columns: hairline으로 분리한 2~4열 비교
- native table/chart: dark header, 최소 gridline, 직접 label
- architecture split: control/runtime, central/team처럼 책임을 공통 축으로 분리
- process band: 단계 번호, 동사, 산출물을 한 축에 정렬
- decision tree: 기본값과 예외를 시각적으로 구분
- roadmap: phase, 종료 기준, KPI, owner를 공통 시간축에 배치

같은 rounded-card grid를 연속 사용하지 않는다. 이미지가 없어도 chart, table, diagram, stat, timeline,
process, hierarchy 같은 **편집 가능한 native visual**이 있어야 한다.

## 6. QA

- 본문 장에 정보 관계를 설명하는 시각 구조가 있는가?
- 같은 레이아웃이 의도 없이 3장 연속 반복되는가?
- 제목 밑 장식선·pill·rounded card·shadow가 내용보다 더 눈에 띄는가?
- dominant/support/accent의 우선순위가 보이는가?
- 표와 차트가 PowerPoint native 객체이거나 편집 가능한 도형인가?
- 제목·본문·label의 위계가 thumbnail에서도 즉시 구분되는가?
- source/footer가 작지만 실제 렌더에서 읽히는가?
