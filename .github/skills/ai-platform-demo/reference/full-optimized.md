# FULL-OPTIMIZED Execution

리서치·스토리라인·화면 설계·빌드·전체 검증을 모두 유지하면서 반복 설치와 중복 검증을 줄이는
기본 실행 방식이다.

## 1. 불변 원칙

- 5단계 순서를 유지하며 리서치가 합쳐지기 전에는 스토리라인을 시작하지 않는다.
- 스토리라인, 화면 계약, 고객 Demo Spec, 최종 단일 HTML은 한 에이전트가 소유한다(디자인은 고정).
- 공통 shell·CSS·JavaScript는 Golden Runtime에서 재사용하며 고객별로 다시 작성하지 않는다.
- 조사 backend 선택과 원문 검증은 `web-search` 계약을 따른다. 이 가이드에서 특정 backend를 추가로
  금지하거나 강제하지 않는다.
- 수정 중에는 변경 화면만 빠르게 확인할 수 있지만, 완료 전에는 `story.routeScope`에 노출된 모든
  화면·스트레스 전환·에이전트 전환·채팅을 포함한 전체 검증을 다시 수행한다.
- 저장소와 최종 출력 폴더에는 결과 HTML 하나만 남긴다.

## 2. 세션 작업 계약

`<session>`은 client가 제공하는 session artifact directory다. 제공되지 않으면 저장소와 최종 출력
폴더 밖의 OS temporary directory에 고유 root를 만든다. 후자를 사용하면 요청된 최종 HTML을 출력
위치에 복사한 뒤 `<app>-work` 전체를 삭제한다.

```text
<session>/<app>-work/
  fact-ledger.md
  storyline.md
  view-contract.md
  customer-overlay.json
  demo-spec.json
  defects.md
  metrics.json                  # 성능 측정이 필요한 경우만
  shots/
```

`view-contract.md`에는 각 route의 KPI, 필수 DOM ID, 클릭 동작, 시뮬레이터 입력, 예상 결과,
에이전트 전환 조건을 기록한다. 이 view-contract(메뉴·데이터)를 실시간 Fact Ledger와 함께
`customer-overlay.json`으로 합친다(디자인은 고정이라 `design`은 넣지 않는다). Composer가 Industry
Pack과 Overlay를 `demo-spec.json`으로 만들며 이후 수정 surface는 HTML이나 전체 Spec보다 Overlay를 우선한다.

## 3. 리서치 병렬화

다음 세 축은 같은 리서치 단계 안에서 동시에 수행할 수 있다.

1. 고객 사업·제품·규모 수치
2. 고객의 DX·AI 현황과 최근 이슈
3. Microsoft·GitHub 서비스의 현재 상태

각 검색 결과는 `web-search`의 공통 Fact Ledger 계약으로 기록하고 데모 매핑은 Customer Overlay에 둔다. 메인
에이전트가 결과를 하나의 Fact Ledger로 합치고 충돌을 해결한 뒤에만 스토리라인을 시작한다. 기존
원장이 있으면 안정적인 회사 사실은 출처를 찾는 참고로만 사용하고, **고객 요청마다 공식 원문을
실시간으로 다시 확인한다.** 이전 Fact Ledger나 Industry Pack의 사실이 새 조사를 대체하면 안 된다.
AI 데모 빌드 전에는 같은 내용을 `web-search/schema/fact-ledger.schema.json`에 맞춘
`fact-ledger.json`으로 저장하고, timezone이 포함된 `checkedAt`과 서로 다른 canonical Accepted Fact source URL
2개 이상을 확인한다.

## 4. Puppeteer 공용 캐시

```text
${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}/ai-platform-demo/puppeteer/
  package.json
  package-lock.json
  node_modules/
  chromium/
```

- 공용 캐시는 저장소 밖에 두며 작업 종료 시 삭제하지 않는다.
- Puppeteer와 Chromium은 캐시에 없을 때만 설치한다.
- `verify.js`, screenshots, 고객별 HTML은 캐시하지 않고 세션 작업 폴더에 둔다.
- 캐시에 고객 데이터, 시크릿, 브라우저 프로필을 보관하지 않는다.
- 도구 사전 준비는 콘텐츠를 만들지 않으므로 리서치와 병렬로 실행할 수 있다.

## 5. Golden Runtime 기반 단일 소유 빌드

- 화면별 HTML/CSS/JS를 여러 실행 주체에 분산하지 않는다.
- 메인 에이전트가 잠긴 storyline·view contract(메뉴·데이터)를 `customer-overlay.json`으로 작성하고,
  실시간 research metadata는 `fact-ledger.json`에서 주입한다(디자인은 고정이라 넣지 않는다).
- `scripts/compose_demo_spec.py`가 base + Industry Pack + Customer Overlay를 합치고
  `scripts/render_demo.py` validation을 거쳐 단일 HTML까지 생성한다.
- Industry Pack은 `meta`, `story`, `design`을 소유하지 않으며, 고객 Overlay가 `design`을
  정의하면 Composer가 실패한다(디자인은 base가 고정 제공).
- 고객 콘텐츠·브랜드 표현·산업 공식·Agent는 spec에서 새로 매핑하고 runtime engine은 재사용한다.
- 기본 수정은 Overlay→재합성으로 수행한다. 핵심 장면이 runtime variant로 표현되지 않을 때만 해당
  route를 bespoke patch한다.
- 여러 에이전트가 같은 spec·HTML을 동시에 편집하지 않는다.

## 6. 검증 최적화

1. 최초 빌드 후 `FULL_QA=1`로 고정 8개 화면, 스트레스 전환, 모든 에이전트, 채팅을 한 브라우저
   세션에서 검사한다.
2. 노출 route의 스크린샷과 오류를 모두 검토해 `defects.md`에 모은다.
3. 결함을 한 번에 수정한다.
4. 수정 중에는 `VERIFY_ROUTES`와 `FULL_QA=0`으로 영향받은 화면만 빠르게 확인한다.
5. 완료 전에는 다시 `FULL_QA=1`로 전체 검증한다. 수정이 없으면 최초 전체 검증이 최종 검증이다.

화면마다 브라우저를 새로 시작하지 않는다. 한 번의 검증 실행에서 같은 browser/page를 재사용하고,
route만 전환한다.

## 7. 선택적 시간 측정

반복 최적화나 benchmark가 필요한 작업에서만 `metrics.json`을 기록한다. 일반 데모 생성의 완료 조건은
아니다.

```json
{
  "research_seconds": 0,
  "storyline_design_seconds": 0,
  "customer_overlay_seconds": 0,
  "spec_compose_seconds": 0,
  "build_seconds": 0,
  "runtime_render_seconds": 0,
  "bespoke_extension_routes": 0,
  "first_full_qa_seconds": 0,
  "repair_cycles": 0,
  "targeted_qa_seconds": 0,
  "final_full_qa_seconds": 0,
  "puppeteer_cache_hit": false
}
```

기록한 `metrics.json`은 세션 작업 폴더에만 두고 다음 최적화의 근거로 사용한다.
