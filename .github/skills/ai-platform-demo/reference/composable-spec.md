# Composable Demo Spec

고객별 전체 `demo-spec.json`을 매번 다시 쓰지 않고 다음 세 layer를 합성한다.

```text
Validated Base Spec
  + Industry Pack
  + Customer Overlay
  → demo-spec.json
  → Golden Runtime HTML
```

Industry Pack은 산업 용어·공식·Agent 역할의 출발점만 제공하며, 고객 Overlay가 `meta`, `story`와
메뉴·데이터(핵심 route·Agent)를 소유한다. **디자인은 GitHub Primer Dark Dimmed 계열 soft-dark로
고정**되어 base spec이 제공하므로
Overlay는 `design`을 넣지 않는다.

## 1. 실시간 리서치는 매번 수행

Composition은 조사 캐시의 대체 수단이 아니다.

- 고객 Overlay의 `_customer.research.mode`는 `live`여야 한다.
- `checkedAt`은 timezone이 포함된 ISO 8601 timestamp다.
- 공식·권위 소스 URL을 2개 이상 기록한다.
- 기본 Composer는 24시간보다 오래된 research metadata를 거부한다.
- `--allow-stale-research`는 repository `examples/`·`tests/` 아래 입력에만 허용되며 다른 경로에서는 Composer가 거부한다.
- 기본 생성 경로에서는 `web-search`의 machine-readable `fact-ledger.json`을 `--fact-ledger`로 전달한다.
  Composer가 `checkedAt`, `sourceUrls`, Ledger ID를 생성하므로 Overlay에 research metadata를 중복
  작성하지 않는다. 기존 metadata가 있으면 Ledger와 정확히 일치해야 한다.

## 2. Layer 책임

### Base Spec

- Renderer가 요구하는 모든 필드를 가진 검증된 전체 Spec
- 안전한 interaction copy, QA ID와 일치하는 구조
- 고객명·현재 사실을 담지 않는 것이 이상적

### Industry Pack

파일 형태:

```json
{
  "_pack": {
    "id": "renewable-energy-holdings",
    "name": "Renewable Energy Holdings",
    "requiredCustomerPaths": [
      "dashboard.hero",
      "operations.flow.nodes",
      "simulator.inputs",
      "foundry.profiles"
    ],
    "forbidOutputTerms": ["SPI", "First-Pass Yield", "Example Customer"]
  },
  "spec": {}
}
```

Industry Pack이 제공할 수 있는 것:

- 산업 route 명칭과 terminology
- KPI·simulator·finance formula의 기본 범위
- 운영 flow와 improvement factor
- Foundry Agent 역할·질문 구조
- GitHub·App Platform 화면의 산업별 workload terminology

Industry Pack에 금지되는 것:

- `meta`
- `design`
- `story`
- 특정 고객명·공식 수치·최신 프로젝트 사실

### Customer Overlay

파일 형태:

```json
{
  "_customer": {
    "research": {
      "mode": "live",
      "checkedAt": "2026-07-15T10:30:00+09:00",
      "sourceUrls": [
        "https://customer.example/official",
        "https://learn.microsoft.com/..."
      ]
    },
    "forbidTerms": ["Example Customer", "__CUSTOMER__"]
  },
  "spec": {
    "meta": {},
    "story": {}
  }
}
```

Customer Overlay가 반드시 새로 결정하는 것:

- 고객명·앱명·audience
- `DEMO_FOCUS`에 맞는 Storyline·핵심 4~6개 시연 동선·climax
- Pack의 `requiredCustomerPaths`
- 고객 공식 사실·KPI 현실 범위·GitHub/Foundry/App Platform 답변과 가정

## 3. Merge 규칙

- object는 recursive merge
- array는 전체 replace
- scalar는 뒤 layer가 replace
- `{"$delete": true}`는 해당 key 삭제
- `{"$replace": <value>}`는 object를 recursive merge하지 않고 전체 교체
- 순서: base → pack 순서대로 → customer
- 최종 output에는 `_pack`, `_customer` metadata를 포함하지 않는다.
- `meta`, `story`와 Pack의 `requiredCustomerPaths`는 Customer Overlay 값으로 **전체 교체**해
  base/pack 하위 값이 조용히 남지 않게 한다.
- `design`은 GitHub soft-dark로 고정이므로 Overlay가 정의하지 않는다. Overlay에 `design`이 있으면
  Composer가 실패한다.

## 4. Composer

```bash
python3 -B .github/skills/ai-platform-demo/scripts/compose_demo_spec.py \
  --base .github/skills/ai-platform-demo/examples/precision-manufacturing.example.json \
  --pack .github/skills/ai-platform-demo/packs/renewable-energy-holdings.pack.json \
  --customer <session>/<app>-work/customer-overlay.json \
  --fact-ledger <session>/<app>-work/fact-ledger.json \
  --output <session>/<app>-work/demo-spec.json \
  --html-output <session>/<app>-work/<app>.html
```

Composer는 다음 순서로 실패를 조기에 차단한다.

1. Pack이 customer identity 또는 `design`을 포함하는지 + Overlay가 `design`을 정의하는지 검사(디자인 고정)
2. Customer Overlay의 live research metadata 검사
3. Pack이 요구하는 customer path가 Overlay에 있는지 검사
4. layer deep merge
5. 금지어·placeholder 누출 검사
6. `render_demo.py`의 full semantic/security validation
7. 선택적으로 단일 HTML까지 한 번에 생성

Composer는 최종 Spec의 `meta.research`와 HTML의 inline Spec에 `checkedAt`, canonical source,
Ledger ID를 보존한다. 따라서 최종 artifact에서도 Fact Ledger provenance를 추적할 수 있다.

누출 검사는 HTML entity와 inline rich-text tag를 렌더된 텍스트로 정규화하고, acronym은 token
boundary로 검사한다. Research source URL은 fragment를 제거해 canonicalize한 뒤 서로 다른 2개 이상의
HTTP(S) 원문인지 확인한다.

## 5. 품질 유지 원칙

- Pack은 초안 가속 장치이며 고객의 storyline을 대신하지 않는다.
- Hero는 제품 소개가 아니라 고객 결과를 바로 말한다. route마다 임원 질문 하나와 primary action 하나를
  유지한다.
- 앞의 5개 고객 주요사업 Hero·flow·simulator·finance와 Foundry Agent profiles, focus별 climax는 고객
  Overlay에서 새로 작성한다.
- GitHub·Foundry·App Platform의 안정적인 interaction copy는 재사용 가능하지만 KPI와 고객 가치 매핑은 갱신한다.
- Microsoft Foundry·Microsoft Agent Framework, GitHub Copilot·GitHub Platform, AKS·Azure Container
  Apps는 제품 catalog가 아니라 지능·delivery·runtime 역할로 연결한다.
- 최종 browser QA는 고객 주요사업 5개 + 플랫폼 서비스 3개의 8개 route를 모두 검사한다.
