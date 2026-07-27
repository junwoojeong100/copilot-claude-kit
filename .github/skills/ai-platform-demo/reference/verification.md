# Verification (puppeteer 자동 검증)

데모는 **반드시 자동 검증**한다. macOS에 Chrome이 없을 수 있으므로 puppeteer와 자체 Chromium을
저장소 밖 공용 캐시에 설치하고 재사용한다. 고객별 검증 스크립트와 screenshots만 세션 작업 폴더에
두며, 저장소나 최종 HTML 출력 폴더에서 `npm install`을 실행하지 않는다.

이 문서의 `<session>`은 client가 제공하는 session artifact directory다. 제공되지 않으면 저장소와
최종 출력 폴더 밖의 OS temporary directory에 고유 root를 만든다.

## 0. 전제 — Spec validation + Golden Runtime

브라우저를 열기 전에 Customer Overlay composition, 최종 Spec, 공통 Runtime을 먼저 검사한다.

```bash
python3 -B .github/skills/ai-platform-demo/scripts/compose_demo_spec.py \
  --base .github/skills/ai-platform-demo/examples/precision-manufacturing.example.json \
  --pack .github/skills/ai-platform-demo/packs/<industry>.pack.json \
  --customer <session>/<app>-work/customer-overlay.json \
  --fact-ledger <session>/<app>-work/fact-ledger.json \
  --output <session>/<app>-work/demo-spec.json \
  --html-output <session>/<app>-work/<app>.html

python3 -B .github/skills/ai-platform-demo/scripts/render_demo.py \
  --spec <session>/<app>-work/demo-spec.json \
  --validate-only

node --check .github/skills/ai-platform-demo/runtime/runtime.js
```

## 0.1 해시 라우팅 + `hashchange`
앱은 `location.hash`로 라우팅하고 `addEventListener('hashchange',navigate)`가 있어야 한다.
그래야 검증 스크립트가 `location.hash=route`로 각 화면을 띄울 수 있다.

## 1. 공용 캐시 준비
```bash
CACHE_ROOT="${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}"
PUPPETEER_HOME="$CACHE_ROOT/ai-platform-demo/puppeteer"
WORK_DIR="<session>/<app>-work"

mkdir -p "$PUPPETEER_HOME" "$WORK_DIR"
if [ ! -f "$PUPPETEER_HOME/package.json" ]; then
  (cd "$PUPPETEER_HOME" && npm init -y)
fi
if [ ! -d "$PUPPETEER_HOME/node_modules/puppeteer" ]; then
  (cd "$PUPPETEER_HOME" && \
    PUPPETEER_CACHE_DIR="$PUPPETEER_HOME/chromium" \
    npm install --save-exact puppeteer)
fi
```

공용 캐시는 작업 종료 시 삭제하지 않는다. `node_modules`, Chromium, package lock은 이 경로에만
두고 고객 HTML·스크린샷·브라우저 프로필은 저장하지 않는다.

## 2. 검증 스크립트

기본은 skill의 재사용 verifier를 실행한다. 고객별 `verify.js`를 매번 다시 작성하지 않는다.

```bash
CACHE_ROOT="${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}"
PUPPETEER_HOME="$CACHE_ROOT/ai-platform-demo/puppeteer"
WORK_DIR="<session>/<app>-work"

NODE_PATH="$PUPPETEER_HOME/node_modules" \
PUPPETEER_CACHE_DIR="$PUPPETEER_HOME/chromium" \
APP_HTML="$WORK_DIR/<app>.html" \
SHOTS_DIR="$WORK_DIR/shots" \
FULL_QA=1 \
node .github/skills/ai-platform-demo/scripts/verify_demo.js
```

Verifier는 기본 Chromium sandbox를 유지한다. sandbox를 제공할 수 없는 신뢰된 격리 CI 컨테이너에서만
위험을 검토한 뒤 `PUPPETEER_NO_SANDBOX=1`을 명시적으로 설정한다.

아래는 verifier contract의 요약이다. 실제 source of truth는 `scripts/verify_demo.js`이며 복사본을
세션 폴더에 만들지 않는다.
```js
const allRoutes=['dashboard','operations','simulator','improvement','finance','github','foundry','appPlatform'];
const fullQa=process.env.FULL_QA!=='0';
const activeRoutes=qaSpec.story.routeScope || allRoutes;
const routes=fullQa
  ? activeRoutes // FULL_QA는 노출된 route를 모두 검사
  : validatedVerifyRoutes;
// 각 route의 required DOM ID, 시연 데이터, overflow, click handler, 안정화 후 screenshot 검사
// FULL_QA: guided journey, dashboard CTA, 공통 scenario trace, service buyer action,
// App Platform 진단→Gap→개선계획, 빠른 route 전환, console/page error 검사
```
```bash
CACHE_ROOT="${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}"
PUPPETEER_HOME="$CACHE_ROOT/ai-platform-demo/puppeteer"
WORK_DIR="<session>/<app>-work"
REPO_ROOT="<repo-root>"

mkdir -p "$WORK_DIR/shots"
NODE_PATH="$PUPPETEER_HOME/node_modules" \
PUPPETEER_CACHE_DIR="$PUPPETEER_HOME/chromium" \
APP_HTML="$WORK_DIR/<APP>.html" \
SHOTS_DIR="$WORK_DIR/shots" \
FULL_QA=1 \
node "$REPO_ROOT/.github/skills/ai-platform-demo/scripts/verify_demo.js"
```

수정 중 영향 route만 빠르게 확인:

```bash
NODE_PATH="$PUPPETEER_HOME/node_modules" \
PUPPETEER_CACHE_DIR="$PUPPETEER_HOME/chromium" \
APP_HTML="<absolute-path>/<APP>.html" \
SHOTS_DIR="<session>/<app>-work/shots-targeted" \
VERIFY_ROUTES="finance,foundry" \
FULL_QA=0 \
node "<repo-root>/.github/skills/ai-platform-demo/scripts/verify_demo.js"
```

완료 전에는 `FULL_QA=1`로 다시 실행한다. 이 모드에서는 `VERIFY_ROUTES`가 설정돼 있어도
`story.routeScope`의 모든 route를 검사하므로 최종 gate가 실수로 축소되지 않는다. `SHOTS_DIR`는
필수이며 session 작업 폴더 밖을 가리키면 verifier가 거부한다.

## 3. 합격 기준
- Verifier JSON 결과의 `errors`와 `failures`가 모두 빈 배열(콘솔/페이지 오류 0건) — 빠른 전환 후에도.
- `foundry`의 `agentTitles`에 **모든 에이전트가 서로 다르게** 찍힘(클릭 전환 정상).
- `github`에는 일반 issue와 high-risk issue가 각각 하나 이상 있어야 하며, 일반 issue는 결과를
  만들고 high-risk issue는 human-led plan으로 남음.
- `journeySelect`와 `nextScene`이 guided journey 순서를 따르고 `dashPrimaryAction`이 첫 업무 장면으로 이동.
- `scenarioTrace`가 operations/foundry/github/appPlatform에서 같은 ID와 4단계를 표시.
- App Platform assessment 후 점수는 유지되고 Gap이 보이며, `planRemediation` 후에만 예상 점수가 변경.
- 노출 route의 스크린샷을 **이미지로 직접 확인**: 텍스트 잘림/겹침, 차트·게이지·맵·도넛 렌더,
  KPI에 `NaN`/`undefined` 없음, 토프바·사이드바·푸터 겹침 없음.

위 합격 기준은 `FULL_QA=1` 결과에만 적용한다. `FULL_QA=0`은 수정 중 회귀 확인용이며 완료 판정에
사용하지 않는다.

## 4. 자주 나오는 실패 → 원인
| 증상 | 원인/수정 |
|---|---|
| 모든 화면이 첫 화면과 동일 | puppeteer가 hash-only 변경을 리로드 안 함 → `hashchange` 리스너 필수, 또는 스크립트에서 `page.evaluate(()=>navigate())` 호출 |
| `KPI: NaN` | `countUp`은 `data-count`, 트윈은 `data-from/to` — 헬퍼와 속성 불일치 |
| `Cannot set properties of null` | 전환 후 비동기 콜백의 DOM 접근 → `if(!el)return` 가드 + `addTimer` |
| 차트 곡선 안 보임 | 인라인 `stroke-dashoffset`이 CSS를 덮음 → JS로 직접 `el.style.strokeDashoffset='0'` |
| 컨트롤·푸터 겹침 | 고정 UI는 화면 가장자리/빈 영역에 배치, z-index 정리 |

## 5. 정리 (필수)
client-provided session artifact directory를 사용했다면 무거운 검증 부산물만 삭제하고 Fact Ledger와
metrics는 세션 폴더에 유지한다:
```bash
rm -rf <session>/<app>-work/shots
```
OS temporary directory fallback을 사용했다면 요청된 최종 HTML을 출력 위치에 복사한 후 work
directory 전체를 삭제한다:
```bash
rm -rf <session>/<app>-work
```
> 시각 검증용 스크린샷이 사용자에게 유용하면 보여준 뒤 정리한다. 저장소와 최종 출력 폴더에는
> **결과 `.html` 하나만** 남긴다. Python 보조 스크립트가 필요하면 같은 세션 작업 폴더에서
> `python3 -B`로 실행하고 저장소에는 `.py`, `.pyc`, `__pycache__`를 만들지 않는다.
> 공용 Puppeteer 캐시는 삭제하지 않는다. 단계별 시간과 `puppeteer_cache_hit`, `repair_cycles`는
> 세션 작업 폴더의 `metrics.json`에 기록한다.
