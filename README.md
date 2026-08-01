# GitHub Copilot Augment Kit

GitHub Copilot을 특정 모델에 종속되지 않는 **고성능 엔지니어링 에이전트**로 확장하는 경량 커스터마이징 킷입니다. 단일 지침 파일과 온디맨드 스킬, 재사용 가능한 생성 엔진으로 사고·소통·안전·코딩·Git·팩트체크·웹 조사·고객 데모·PPTX 제작 워크플로를 제공하며, 모든 결과는 결론과 다음 행동이 먼저 보이는 **Straightforward** 형식을 우선합니다.

이 리포의 `.github/` 폴더를 프로젝트에 두면 GitHub Copilot(VS Code Chat의 Agent mode·터미널 CLI)이
지침과 스킬을 자동으로 읽습니다. `.vscode/mcp.json`까지 적용하면 VS Code Agent mode에서도
Microsoft Learn MCP를 사용할 수 있습니다.

> **Augment**는 GitHub Copilot의 역량을 지침·스킬·MCP로 보강한다는 뜻입니다. 특정 모델명은 저장소 정체성에 포함하지 않으며, `/model` 또는 모델 선택기에서 현재 작업에 가장 적합한 모델로 언제든 교체할 수 있습니다.
>
> **현재 검증 기준(2026-07-15)**: 이 버전의 지침·스킬·예제 워크플로는 **GPT-5.6 Sol**로 최종 end-to-end 테스트와 품질 검증을 수행했습니다. GPT-5.6 Sol은 고정 런타임 의존성이 아닙니다. 더 적합한 최신 모델이 제공되면 계속 재검증·업데이트하되, 지침·Skills·MCP 워크플로가 특정 모델에 종속되지 않는 설계 원칙을 유지합니다.

---

## 이게 뭔가요? (3줄 요약)

- **무엇**: GitHub Copilot에 입힐 수 있는 단일 지침 + 전문 스킬 모음입니다.
- **왜**: 기반 모델이 바뀌어도 Straightforward한 결과와 일관된 품질·안전·전문 워크플로를 유지하도록 Copilot의 실행 방식을 보강합니다.
- **어떻게**: `.github/`를 두면 지침·스킬이 자동 로드되고, 생성 스킬은 실시간 조사·스토리라인 같은 의미 계층과 Golden Runtime·통합 QA Runner 같은 검증 엔진을 조합해 반복 구현 시간을 줄입니다.

---

## 무엇이 들어있나 — 3가지 빌딩 블록

| 블록 | 위치 | 동작 방식 | 내용 |
|------|------|----------|------|
| **Instructions** | `.github/copilot-instructions.md` | 매 대화 **자동 로드** | Straightforward 결과 · 페르소나 · 사고 · 소통 · 안전 · 코딩 · Git · MS/GitHub 가치 · 팩트체크 · 출처 |
| **Skills** | `.github/skills/` | 관련 질문 시 **자동 활성화** 또는 `/skill-name` | 결론 우선 실시간 검색 · 고객·산업별 AI/App Platform 데모 · 적응형 PPTX 생성 |
| **MCP (사전 번들)** | `.github/mcp.json` · `.vscode/mcp.json` | clone 후 신뢰/Start 승인 시 활성화 | Microsoft Learn MCP — 공식 문서·코드 샘플 검색 (Azure·사내 MCP는 선택 연결) |

> 상시 적용 원칙은 **단일 파일로 통합**해 중복을 줄이고, 상세 워크플로는 관련 작업에서만 스킬로 불러옵니다.

---

## 5분 빠른 시작

### 1) 먼저 체험해보기

```bash
git clone https://github.com/junwoojeong100/github-copilot-augment-kit.git
cd github-copilot-augment-kit
code .
```

VS Code에서 Copilot Chat을 **Agent mode**로 열고 **모델 선택기(Model Picker)** 에서 작업에 적합한
모델을 선택합니다. 모델이 바뀌어도 동일한 지침과 스킬이 적용됩니다.

### 2) 내 프로젝트에 적용하기

전체 킷을 적용하려면 **`.github/`와 `.vscode/mcp.json`**을 프로젝트 루트에 복사합니다.
아래 명령은 대상 프로젝트에 같은 이름의 설정 파일이 없을 때만 사용하세요.

```bash
cp -R github-copilot-augment-kit/.github /path/to/my-project/
mkdir -p /path/to/my-project/.vscode
cp github-copilot-augment-kit/.vscode/mcp.json /path/to/my-project/.vscode/mcp.json
```

> **기존 프로젝트 주의**: `.github/copilot-instructions.md`, `.github/mcp.json`,
> `.vscode/mcp.json` 또는 같은 이름의 스킬이 이미 있으면 위 명령을 그대로 실행하지 말고 내용을
> 검토해 병합하세요. repository-wide `copilot-instructions.md`는 하나지만,
> `.github/instructions/**/*.instructions.md`와 `AGENTS.md`는 함께 사용할 수 있습니다.

---

## 어디서 쓸 수 있나 — VS Code Agent mode & 터미널(CLI)

이 킷은 **VS Code Copilot Chat의 Agent mode**와 터미널용
**[GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/copilot-cli/about-copilot-cli)**
양쪽에서 동작합니다.

### Copilot CLI 설치

활성 GitHub Copilot 구독이 필요합니다. 공식 설치 방법은
[GitHub Docs](https://docs.github.com/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli)를
기준으로 확인하세요.

```bash
# macOS / Linux (Homebrew)
brew install --cask copilot-cli

# 크로스 플랫폼 (npm, Node.js 22+)
npm install -g @github/copilot
```

설치 후 리포 디렉토리에서 `copilot`을 실행하고, 첫 실행 시 `/login`으로 인증합니다.

| 명령 | 설명 |
|------|------|
| `/model` | 작업에 사용할 AI 모델 선택 또는 Auto 설정 |
| `/diff` | 변경사항 리뷰 |
| `/plan` | 구현 계획 수립 |
| `/help` | 전체 명령 보기 |

### VS Code Agent mode vs Copilot CLI

| 항목 | VS Code Copilot Chat (Agent mode) | GitHub Copilot CLI |
|------|---------------------|-------------------|
| `copilot-instructions.md` | ✅ 자동 적용 | ✅ 자동 적용 |
| `skills/` | ✅ 자동 활성화 · `/skill-name` | ✅ 자동 활성화 · `/skill-name` |
| Microsoft Learn MCP | `.vscode/mcp.json`에서 Start | `.github/mcp.json`을 신뢰 후 자동 로드 |
| 범용 최신 웹 검색 | Copilot web search/Research capability 사용 | 내장 `/research` 또는 Research agent 사용 |

---

## 설계 원칙 — 변동 지식은 최소화하고, 필요할 때 최신 확인

이 킷의 지침·스킬은 주로 **방향(무엇을 다룰지), 형식(어떻게 정리할지), 재사용 가능한
워크플로**를 정의합니다. 서비스명과 예시는 포함하지만, 자주 바뀌는 기능 상태·가격·수치·규제
조항은 가능한 한 고정하지 않습니다.

- **왜?** 클라우드·AI·규제는 빠르게 변합니다. 박제된 내용은 금방 낡고 토큰만 소모합니다.
- **대신** 답변 시점에 공식 문서(`learn.microsoft.com` · `docs.github.com`)와 client가 제공하는 web
  search/Research 도구 또는 승인된 search MCP로 최신 정보를 확인합니다.
- **효과**: 최신성 오류와 유지보수 부담을 줄입니다. 검색 가능 여부와 원문 갱신 시점에 따라 최신성에는 한계가 있을 수 있습니다.

---

## 프로젝트 구조

```
.github/
├── copilot-instructions.md              # 단일 핵심 지침 (매 대화 자동 로드)
├── mcp.json                             # Microsoft Learn MCP 사전 번들 (CLI 워크스페이스 자동 로드)
├── mcp.enghub.example.json              # Microsoft 사내 EngHub MCP 예시 (임직원이 복사해서 사용)
└── skills/                              # 전문 스킬 (온디맨드)
    ├── web-search/                      # 실시간 웹·공식 문서 검색과 구조화 수집
    │   ├── SKILL.md
    │   ├── schema/                      # machine-readable Fact Ledger 계약
    │   ├── examples/                    # Fact Ledger JSON 예제
    │   └── tests/                       # 검색·수집 정책 계약 테스트
    ├── ai-platform-demo/                # 고객·산업별 AI·App Platform 데모(단일 HTML) 생성기
    │   ├── SKILL.md                     # 실시간 리서치→메뉴·데이터 매핑→Overlay 합성→검증
    │   ├── runtime/                     # 검증된 SPA shell·CSS·JavaScript Golden Runtime
    │   ├── packs/                       # 디자인·고객 사실을 고정하지 않는 산업별 기본 구조
    │   ├── schema/                      # 고객별 demo-spec JSON Schema
    │   ├── scripts/                     # Overlay Composer·Spec Renderer·브라우저 검증기
    │   ├── tests/                       # Composition·design 고정 검사 회귀 테스트
    │   ├── examples/                    # 전체 Spec·compact Customer Overlay 구조 예제
    │   └── reference/                   # soft-dark 기본 디자인·화면 archetype·Runtime·검증 절차
    └── adaptive-presentation/           # 주제·청중별 PPTX 생성기(조사·스토리라인 중심)
        ├── SKILL.md                     # 조사→스토리라인→자유 슬라이드 제작→빠른 렌더 검증
        ├── reference/                   # 스토리라인 패턴·레이아웃 아이디어·python-pptx 제작·검증
        ├── scripts/                     # 통합 QA Runner·구조 감사·JPEG/contact sheet 렌더링
        └── tests/                       # 검증 Runner 회귀 테스트
.vscode/
└── mcp.json                             # VS Code Copilot Agent용 MCP 번들
```

---

## 구성 요소 자세히

### Instructions — `copilot-instructions.md` (자동 적용)

매 대화에 자동 로드되는 단일 지침. 아래 원칙을 압축해 담습니다.

| 섹션 | 핵심 |
|------|------|
| 페르소나 & 사고 | 지적 겸손, 단계적 추론, 불확실성 표기 |
| 커뮤니케이션 | Straightforward 결과, 결론 우선(BLUF), 적응적 소통, 한국어 존댓말+영문 병기 |
| 안전 & 윤리 | 해로운 콘텐츠 거부, PII/시크릿 보호 |
| 코딩 | 가독성·보안(OWASP) 우선, 언어별 베스트 프랙티스 |
| Git 워크플로우 | 영어 커밋, Conventional Commits, PR 규칙 |
| MS/GitHub 가치 | 구체 서비스로 통제·가치 매핑(Foundry·Agent Framework·GitHub Platform·AKS·ACA 등) |
| 팩트체크 · 출처 | 최신·수치·논쟁·의사결정 핵심 주장만 검증 표, 실제 참조한 출처 명시 |

### [Skills](https://docs.github.com/copilot/concepts/agents/about-agent-skills) — 자연어 또는 `/skill-name`

| 스킬 | 트리거 예시 | 기능 |
|------|-----------|------|
| **web-search** | "최신 버전 알려줘", "고객·산업 기초자료 수집해줘" | 전용 검색 도구·공식 문서 검색으로 원문을 검증하고 Markdown/JSON Fact Ledger로 구조화해 downstream 스킬에 전달 |
| **ai-platform-demo** | "○○ 고객 AI 데모", "AKS/ACA App Platform 데모", "CI/CD 임원 데모" | 실시간 조사 + focus별 스토리라인 + 유연한 route Overlay → 5~8화면 soft-dark 단일 HTML SaaS 데모 생성·전체 QA |
| **adaptive-presentation** | "병원 경영진 대상 의료 AI 전략 PPT 20장", "기술 발표자료 만들어줘", "제품 소개 슬라이드" | 결론·다음 행동 우선 스토리라인 + 필요한 외부 조사 + python-pptx 자유 제작 + 통합 QA Runner → 편집 가능한 PPTX |

---

## AI · App Platform 데모 스킬 (`ai-platform-demo`)

고객사 임원 보고·영업용 **"실제로 동작하는" AI·App Platform 운영 데모를 단일 HTML 하나**로
생성합니다. AI 중심, App Platform·CI/CD 중심, 균형형 focus를 지원하며 슬라이드가 아니라 임원이 직접
클릭·질문·조작하는 SaaS 앱입니다.

**무엇을 만드나** — 사이드바 + 실시간 대시보드 + 도메인/App Platform 운영 콘솔 + GitHub 기반
개발·배포 + AI 에이전트 채팅 + 통합 거버넌스 중 **목적에 맞는 5~8개 화면 SPA**. 고객 업무
3~5개와 플랫폼 화면 2~3개를 선택하고 4~6개 핵심 시연 장면으로 동선을 압축합니다. 첫 화면에서 고객 결과·KPI·primary action이 보이고, 실시간
KPI·스트리밍 차트·움직이는 객체·토스트·멀티에이전트 협업까지 동작합니다.

**사용법** — 자연어로 고객과 산업을 알려주고, 필요하면 AI 중심 또는 App Platform·CI/CD 중심 focus를
지정하면 됩니다.

```
> 현대제철 대상으로 철강 제조 AI 운영 플랫폼 데모 만들어줘. 청중은 CDO·생산본부장.
> OO사 대상으로 GitHub Actions와 AKS/ACA 운영을 강조한 App Platform 임원 데모 만들어줘.
```

스킬이 자동 로드되어 ① **매 요청 실시간** 고객·산업 리서치 → ② Storyline·메뉴/데이터 매핑(5~8개
route, 4~6개 guided journey) →
③ compact `customer-overlay.json` 작성 → ④ Industry Pack과 합성해 Spec·HTML 생성 → ⑤ Puppeteer 전체 QA까지
수행합니다. **디자인은 GitHub Primer Dark Dimmed 계열 soft-dark를 기본값**으로 사용하고 고객별
`brand`·`accent` token만 안전하게 바꿀 수 있습니다.

검색 backend와 원문 검증은 `web-search` 계약이 결정합니다. 범용 web search, CLI의 `/research` 또는
Research agent, 공식 문서 검색을 가용성과 질문 범위에 맞게 사용하고, 메인 에이전트가 결과를 하나의
Fact Ledger로 병합해 Storyline·Overlay·최종 HTML까지 일관되게 연결합니다.

```text
실시간 Fact Ledger + Storyline + route·메뉴·데이터(soft-dark 기본 디자인)
  → Customer Overlay + Industry Pack
  → validated demo-spec.json
  → Golden Runtime (shell.tmpl + runtime.css + runtime.js)
  → 고객별 단일 HTML
  → 선택된 5~8개 화면·핵심 인터랙션 브라우저 QA
```

**Golden Runtime은 검증된 동작 엔진**입니다. 라우터, timer/listener 정리, 실시간 차트, 시뮬레이터,
에이전트 채팅, HTML escaping, 안정적인 QA ID를 재사용합니다. layout·type·motion은 Runtime이 유지하고
고객별 route 구성·KPI·공식·에이전트·서사와 선택적 brand/accent를 Spec에서 결정합니다.

**Industry Pack은 산업 terminology·KPI 공식·Agent/Platform 역할의 출발점**만 제공하며 고객명·Storyline을
포함할 수 없습니다. Composer는 Customer Overlay가 허용되지 않은 design key를 정의하거나
Fact Ledger가 오래됐거나 canonical Fact source가 2개 미만이거나 핵심 고객 path가 빠지면 실패합니다.
따라서 같은 산업이라도 고객별
운영 flow·KPI·에이전트·climax가 달라지고 soft-dark 기본값 위에 brand/accent를 선택 적용할 수 있습니다.

```bash
python3 -B .github/skills/ai-platform-demo/scripts/compose_demo_spec.py \
  --base .github/skills/ai-platform-demo/examples/precision-manufacturing.example.json \
  --pack .github/skills/ai-platform-demo/packs/renewable-energy-holdings.pack.json \
  --customer <session>/<app>-work/customer-overlay.json \
  --fact-ledger <session>/<app>-work/fact-ledger.json \
  --output <session>/<app>-work/demo-spec.json \
  --html-output <session>/<app>-work/<app>.html
```

적합한 Industry Pack이 없으면 전체 `demo-spec.json`을 직접 작성하는 기존 경로를 사용합니다. 속도를
위해 고객과 맞지 않는 Pack을 사용하지 않으며 최종 QA는 노출된 모든 화면에 적용합니다.

| 입력 | 예시 |
|------|------|
| 고객명 / 산업 | "삼표산업 / 레미콘·골재·시멘트" |
| 청중(임원) | "CIO, 재무팀장, CI팀장" |
| 데모 focus | 균형형 / AI 중심 / App Platform·CI/CD 중심 |
| 강조 서비스 | Microsoft Foundry · Microsoft Agent Framework · GitHub Copilot · GitHub Platform · AKS · Azure Container Apps |

> 산출물은 **단일 `.html`**(인라인 CSS/JS, 오프라인 동작). 모든 화면에 `● DEMO DATA` 배지로 시연 데이터임을 명시합니다.

### 개인/팀에 설치

```bash
# 팀 공유 — 같은 이름의 스킬이 없을 때
mkdir -p /path/to/my-project/.github/skills
cp -R github-copilot-augment-kit/.github/skills/ai-platform-demo \
  /path/to/my-project/.github/skills/

# 개인 — 같은 이름의 스킬이 없을 때, 모든 프로젝트에서 사용
mkdir -p ~/.copilot/skills
cp -R .github/skills/ai-platform-demo ~/.copilot/skills/
```

같은 이름의 스킬이 이미 있으면 덮어쓰지 말고 내용을 비교해 병합하세요.

확인: CLI에서 `/skills list` · `/skills info ai-platform-demo` · `/env`.

---

## 적응형 PPT 스킬 (`adaptive-presentation`)

임원 보고, 고객 제안, 제품 소개, 기술 아키텍처, 교육·세미나 등 다른 주제와 청중에도 실제 `.pptx`를
생성합니다.

이 스킬의 무게 중심은 **① 필요한 근거 수집(Fact Ledger)** 과 **② 목적에 맞는 스토리라인 설계**입니다.
슬라이드 시각화는 고정 템플릿이나 고정 생성 프레임워크에 의존하지 않고, 매 요청마다 주제에 맞게
**자유롭고 다양하게** `python-pptx`로 직접 구성하되 제작·검증 시간은 최소화합니다. 표지와 첫 본문
슬라이드에서 결론·가치·다음 행동이 보이고, 이후 장은 그 결론에 필요한 근거만 쌓는 Straightforward
구성을 최우선으로 합니다.

진행 순서: ① 외부 사실·최신 정보가 필요할 때 공식 자료 조사·Fact Ledger → ② 목적별 Storyline 설계 →
③ `python-pptx`로 슬라이드 자유 제작(정보 유형에 맞는 시각 형태를 매번 다양하게) →
④ 통합 QA Runner의 전체 렌더 및 contact sheet로 빠른 검증 순입니다.

```text
필요한 경우 Fact Ledger
  → 목적별 Storyline(슬라이드별 결론·근거·시각 형태)
  → python-pptx 자유 슬라이드 제작(고정 템플릿 없음)
  → 편집 가능한 PPTX
  → 통합 QA Runner(구조 감사 + 전체 렌더 + risk slides)
```

**슬라이드는 고정 생성 엔진 없이 `python-pptx`로 직접 만듭니다.** 정보 관계(숫자·흐름·비교·계층·사례)에
맞는 시각 형태를 슬라이드마다 자유롭게 선택하고, 같은 구조를 기계적으로 반복하지 않습니다. 색·글꼴은
주제와 (있다면) 사용자 브랜드에 맞게 정하되 본문 대비 최소 4.5:1, 주요 본문 16pt 권장·15pt 하한, 출처 footer 표기 등
가독성·편집성 기준은 지킵니다. 아이디어가 필요하면 `reference/slide-blueprints.md`의 관계형 패턴을
선택적으로 참고하되 그대로 복제하지 않습니다.

외부 사실 조사의 backend와 원문 검증은 `web-search` 계약을 따릅니다. 이전 Fact Ledger와 URL은 검색
출발점으로만 사용하며, 기능 상태·가격·규제·고객 성과는 발표 요청마다 현재 공식 원문으로 다시
확인합니다. 사용자 제공 자료만 재구성하거나 외부 사실이 없는 창작형 덱에는 웹 조사를 강제하지
않습니다.

재생성 Python 스크립트와 QA 파일은 세션 작업 폴더에 격리하며 저장소와 최종 출력 폴더에는 사용자가
요청한 최종 파일 외 중간 자산을 남기지 않습니다. 중간 PDF는 manifest의 PPTX·PDF SHA-256이 모두
일치할 때만 상세 슬라이드 렌더에 재사용합니다. 수정 후에는 변경 부분을 먼저 확인하되 완료 전 요구되는
구조·시각 검증을 다시 수행합니다.

```text
> 병원 경영진 대상 의료 AI 전략 발표자료 20장 만들어줘.
> 청중은 개발자야. 이벤트 기반 아키텍처를 교육하는 기술 PPT 15장으로 만들어줘.
> 이 기존 PPT는 내용은 유지하고, 투자위원회 대상의 절제된 디자인으로 재구성해줘.
```

슬라이드 시각화는 주제·내용에 따라 매번 다르게 구성하며 **정해진 템플릿·색상·카드 스타일을 복제하지
않습니다.**

통합 검증:

```bash
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py \
  deck.pptx --out <session>/<deck>-work --expected-slides 30 \
  --strict --min-body-pt 15
```

Runner는 구조 감사와 전체 렌더를 병렬 실행하고, 텍스트 밀도·작은 글자·title risk·group·bounds를
점수화해 위험 슬라이드를 자동으로 상세 렌더합니다. 전체 overview와 위험 슬라이드는 사람이 확인하며,
`--strict --min-body-pt 15`는 15pt 미만 본문 후보·명시적 크기가 없는 run·title risk를 실패 처리합니다. 사람이 확인한
의도적 예외에만 `--allow-small-text 4,8-9`처럼 슬라이드 번호를 지정합니다. 외부 사실을 사용하는
슬라이드가 있으면 `--require-sources <slide-list>`를 추가합니다. QA Runner는 비어 있지 않은
일반 출력 디렉터리를 덮어쓰지 않습니다.

개인 설치(같은 이름의 스킬이 없을 때):

```bash
mkdir -p ~/.copilot/skills
cp -R .github/skills/adaptive-presentation ~/.copilot/skills/
```

기존 스킬이 있으면 덮어쓰지 말고 내용을 비교해 병합하세요. 설치 후
`/skills info adaptive-presentation`으로 로드 위치를 확인할 수 있습니다.

---

## 생성 시간을 줄이는 공통 실행 구조

두 생성 스킬은 기본적으로 **FULL-OPTIMIZED** 정책을 사용합니다. 조사·스토리라인·제작·전체 QA를
생략하는 대신, 안전한 병렬화·캐시·중간 산출물 재사용과 결함 일괄 수정으로 중복 작업과 wall-clock
time을 줄입니다.

| 최적화 | `ai-platform-demo` | `adaptive-presentation` |
|---|---|---|
| **생성 메커니즘 재사용** | Golden Runtime의 SPA lifecycle·interaction·QA hook 재사용 | 고정 생성 엔진 대신 python-pptx로 직접 제작하고 조사·검증·렌더 스크립트만 재사용 |
| **요청별 변경 surface 축소** | 매번 실시간 조사 후 Industry Pack에는 없는 고객 사실·메뉴·데이터(핵심 route)만 Customer Overlay에 작성 | 외부 조사가 필요하면 Fact Ledger를 만들고, 스토리라인을 먼저 확정한 뒤 슬라이드는 주제에 맞게 자유 제작 |
| **안전한 병렬 실행** | 메인 에이전트가 공식 조사 도구를 병렬 호출하고 최종 Spec·HTML도 직접 소유 | 메인 에이전트가 공식 조사 도구를 병렬 호출하고 동일 immutable PPTX의 구조 감사·전체 렌더만 읽기 전용 병렬 실행 |
| **도구 캐시** | 저장소 밖 공용 Puppeteer·Chromium 캐시를 재사용 | 저장소 밖 Python·렌더링 도구·폰트 탐색 캐시를 재사용 |
| **중간 산출물 재사용** | 한 browser/page 세션에서 선택된 5~8개 route와 핵심 인터랙션을 연속 검증 | PPTX SHA-256이 같은 리비전에서만 중간 PDF를 상세 렌더에 재사용 |
| **수정 루프 단축** | 결함을 모아 일괄 수정 → 영향 route 확인 → 최종 전체 QA | 결함을 모아 일괄 수정 → 위험 슬라이드 확인 → 변경 시에만 최종 전체 render |
| **측정** | 단계별 시간·cache hit·repair cycle을 세션 `metrics.json`에 기록 | 단계별 시간·PDF reuse·cache hit·repair cycle을 세션 `metrics.json`에 기록 |

공용 캐시에는 고객 데이터·시크릿·생성 결과를 넣지 않으며, 검증 스크립트와 QA 파일은 세션 작업
폴더에 격리합니다. 최종 산출물 폴더에는 사용자가 요청한 `.html` 또는 `.pptx`만 남깁니다.
여기서 `<session>`은 클라이언트가 제공하는 세션 artifact 경로를 뜻합니다. 그런 경로가 없는
VS Code 환경에서는 저장소와 최종 출력 폴더 밖의 OS 임시 디렉터리를 사용합니다.

---

## MCP 서버 (사전 번들 · clone 후 승인하면 동작)

MCP(Model Context Protocol) 서버는 Copilot에 **구조화된 외부 도구 접근**(공식 문서·GitHub 이슈/PR/코드)을
붙여 줍니다. 이 킷은 **[Microsoft Learn MCP](https://learn.microsoft.com/training/support/mcp)를 사전
번들**하며, clone 후 폴더 신뢰 또는 서버 Start를 승인하면 활성화됩니다. 연결 설정만 저장하고 문서 내용은
저장소에 복제하지 않습니다.

범용 최신 웹 검색은 MCP가 아니라 GitHub Copilot CLI의 `/research`·Research agent 또는 VS Code Copilot의
web search capability를 사용합니다. 이 킷의 `web-search` 스킬은 검색 전략·검증·Fact Ledger 계약을 맡고
검색 backend 자체는 제공하지 않습니다.

### 번들된 서버

| 서버 | 역할 | 인증 | 어떻게 연결되나 |
|------|------|------|------|
| **GitHub MCP** | 이슈·PR·코드·릴리스 조회/작성 | GitHub 로그인 | **Copilot CLI에 내장** — 설정 불필요 |
| **Microsoft Learn MCP** | `learn.microsoft.com` 공식 문서·코드 샘플 조회 | **불필요 · 무료 공개 엔드포인트** | **리포에 번들** — 클라이언트 승인 후 활성화 |

> 선택 연결: Azure 리소스 작업은 **Azure MCP**(플러그인), Microsoft 사내 도구는 **EngHub MCP**(예시 파일)를
> 아래 절에서 각각 연결합니다.

### 인식과 활성화

- **Copilot CLI** — 리포의 `.github/mcp.json`을 **워크스페이스 서버**로 자동 로드. 첫 실행 시 폴더 신뢰(trust)에 동의하면 활성화됩니다.
  - 확인: `copilot mcp list` → `Workspace servers: microsoft-learn (http)`
- **VS Code (Copilot Chat · Agent)** — 리포의 `.vscode/mcp.json`을 인식. 파일 상단 **Start** 또는 명령 팔레트 → **MCP: List Servers**로 시작.
  - 확인: Agent 도구 목록에 `microsoft_docs_search` 등이 보이면 정상입니다.

### 다른 MCP 서버 추가 (선택)

- **CLI**: `/mcp add`(대화형) 또는 전역 `~/.copilot/mcp-config.json`(루트 키 `mcpServers`). 관리는 `copilot mcp list` / `/mcp show` / `/mcp disable <이름>`.
- **VS Code**: `.vscode/mcp.json`(루트 키 `servers`).
- **플러그인 경유**: 일부 플러그인은 자체 MCP 서버를 함께 설치합니다. 이 경우 `mcp-config.json`에는
  보이지 않고 플러그인 설정으로 관리합니다(아래 Azure MCP 참고).

> **보안**: MCP 서버는 외부 도구를 실행합니다. **신뢰할 수 있는 서버만** 추가하고, 추적되는
> `.github/mcp.json`이나 `.vscode/mcp.json`에 리터럴 키를 저장하지 마세요. 클라이언트가 지원하는
> 환경변수/secret/input 치환 또는 사용자 전역 설정을 사용하고, 구체 문법은 해당 클라이언트의
> 공식 문서를 따르세요.

### Azure MCP 연결 (Azure Skills 플러그인, 선택)

Azure 리소스를 실제로 조회·진단·배포하려면 **[Azure Skills 플러그인](https://github.com/microsoft/azure-skills)**
을 설치합니다. 이 플러그인은 Azure 스킬과 함께 **Azure MCP Server**(+ Foundry MCP)를 연결하므로,
이 킷의 MCP 파일에는 별도 항목을 추가하지 않습니다.

| 항목 | 내용 |
|------|------|
| 용도 | 리소스 조회, 모니터링·로그 질의, 가격 확인, 배포·진단 워크플로 실행 |
| 설치 단위 | Copilot CLI 플러그인 (사용자 전역) |
| MCP 정의 위치 | 플러그인 내부 `.mcp.json` — `npx -y @azure/mcp@latest server start` |
| 사전 조건 | Node.js 18+, Azure CLI `az login`(배포 워크플로는 `azd auth login`) |
| 인증 | 로컬 Azure 자격 증명 사용 — 리포에 키를 저장하지 않음 |

**연결 절차 (Copilot CLI)**

1. `/plugin`으로 마켓플레이스 `microsoft/azure-skills`를 추가하고 `azure` 플러그인을 설치합니다.
2. `az login`으로 대상 구독에 로그인합니다.
3. CLI를 재시작한 뒤 `azure-` 계열 도구(예: 리소스 그룹 조회)가 로드되는지 확인합니다.

> 플러그인은 사용자 전역에 설치되므로 저장소마다 다시 설정할 필요가 없습니다. 필요 없을 때는
> `~/.copilot/settings.json`의 `enabledPlugins`에서 비활성화합니다.

### Microsoft 사내 MCP 연결 (EngHub)

**EngHub MCP**(`https://mcp.eng.ms`)는 Microsoft **임직원이 사용할 수 있는 사내 Engineering Hub MCP
서버**입니다. 개인이 만든 서버가 아니라 사내 공통 엔드포인트이며, corporate 계정과 사내 인증이 있어야
연결됩니다.

이 킷은 EngHub를 **기본 로드 대상에 넣지 않고 예시 파일로만 번들**합니다. 외부 사용자가 clone했을 때
불필요한 인증 실패와 시작 지연이 생기지 않게 하기 위해서입니다.

| 항목 | 내용 |
|------|------|
| 용도 | 사내 엔지니어링 포털·내부 문서·내부 서비스 도구를 Copilot 세션에서 직접 호출 |
| 사용 대상 | Microsoft 임직원 (corporate 계정 필요) |
| 외부 사용자 | 사용 불가 — 공개 문서 조회는 Microsoft Learn MCP를 사용 |
| 번들 파일 | `.github/mcp.enghub.example.json` (예시 · 자동 로드되지 않음) |
| 적용 위치 | 워크스페이스 `.github/mcp.json` 또는 VS Code `.vscode/mcp.json` |
| 인증 | 브라우저 OAuth + corporate 인증 (사내망·VPN 연결이 필요할 수 있음) |

**연결 절차**

1. 사내 네트워크 또는 VPN에 연결하고 corporate 계정 로그인 상태를 확인합니다.
2. 예시 파일의 `EngHub` 항목을 워크스페이스 `.github/mcp.json`에 병합합니다.

   ```bash
   cd <이 킷을 적용한 프로젝트 루트>
   cp .github/mcp.json .github/mcp.json.bak
   python3 - <<'PY'
   import json
   base = json.load(open(".github/mcp.json"))
   extra = json.load(open(".github/mcp.enghub.example.json"))
   base["mcpServers"].update(extra["mcpServers"])
   json.dump(base, open(".github/mcp.json", "w"), indent=2, ensure_ascii=False)
   open(".github/mcp.json", "a").write("\n")
   PY
   ```

   결과는 다음과 같습니다. VS Code에서 쓰려면 `.vscode/mcp.json`의 `servers`에 같은 항목을 추가합니다.

   ```json
   {
     "mcpServers": {
       "microsoft-learn": {
         "type": "http",
         "url": "https://learn.microsoft.com/api/mcp",
         "tools": ["*"]
       },
       "EngHub": {
         "type": "http",
         "url": "https://mcp.eng.ms",
         "tools": ["*"]
       }
     }
   }
   ```

3. CLI를 재시작하면 OAuth 인증이 진행됩니다. 승인 후 `copilot mcp list` 또는 `/mcp show`에서
   `EngHub`가 연결 상태로 보이고 도구 목록이 로드되는지 확인합니다.

**원복 (사용을 마쳤거나 커밋 전에 되돌릴 때)**

```bash
git checkout -- .github/mcp.json     # 저장소 기본 상태로 복구
# 또는 백업 사용: mv .github/mcp.json.bak .github/mcp.json
```

임시로만 끄려면 `/mcp disable EngHub`를 사용합니다.

> 사내 전용 서버를 추가한 `.github/mcp.json` 변경은 **공개 저장소에 커밋하지 마세요.** 외부 사용자
> 환경에서는 인증이 실패하고 시작만 느려집니다. 커밋 전에 `git status`로 확인하는 것을 권장합니다.

**문제 해결**

| 증상 | 원인 | 조치 |
|------|------|------|
| 시작이 오래 걸리고 EngHub 도구가 보이지 않음 | 사내망 밖에서 인증 실패 | 사내망·VPN 연결 후 CLI 재시작 |
| 로그에 `HTTP 403 Forbidden` · `Failed to discover authorization server metadata` | corporate 인증이 없거나 만료 | 재로그인 후 재시도. 로그는 `~/.copilot/logs/`에서 확인 |
| 재인증이 계속 실패 | 만료된 OAuth 캐시 재사용 | `~/.copilot/mcp-oauth-config/`의 해당 항목을 삭제하고 다시 인증 |
| 당장 필요 없음 | — | `/mcp disable EngHub` 또는 설정에서 제거 |

> EngHub 연결 실패는 **다른 작업을 막지 않습니다.** Microsoft Learn MCP, GitHub MCP, 스킬, 셸·파일
> 작업은 그대로 동작하며 세션 시작만 지연됩니다.

> **보안**: 사내 데이터·식별자·내부 URL을 외부 서비스나 공개 산출물로 옮기지 마세요.

---

## 자주 묻는 질문

**Q. 어떤 Copilot 플랜이 필요한가요?**
이 킷은 특정 모델을 요구하지 않습니다. 사용하려는 GitHub Copilot Chat·Agent·CLI 기능을 지원하는 플랜과 최신 클라이언트를 사용하면 됩니다.

**Q. 내 프로젝트에 어떻게 적용하나요?**
지침·스킬은 `.github/`에, VS Code MCP 설정은 `.vscode/mcp.json`에 둡니다. 기존 설정이나 같은
이름의 스킬이 있으면 복사 명령으로 덮어쓰지 말고 내용을 병합하세요.

**Q. 스킬이 동작하지 않아요.**
최신 VS Code + GitHub Copilot Chat의 Agent mode를 사용하고, `SKILL.md`의 `name`이 폴더명과
일치하며 `description`에 트리거 키워드가 있는지 확인하세요.

**Q. 지침이 로드되지 않아요.**
`.github/copilot-instructions.md` 경로가 맞는지, 프로젝트 루트에 `.github/`가 있는지 확인하세요. Copilot CLI도 이 파일을 자동으로 읽습니다.

**Q. MCP 서버는 어떻게 붙이나요?**
Microsoft Learn MCP 설정은 CLI의 `.github/mcp.json`과 VS Code의 `.vscode/mcp.json`에 번들되어 있으며,
폴더 신뢰 또는 Start 승인 후 활성화됩니다. GitHub MCP는 Copilot CLI에 내장돼 있습니다. Azure MCP는
Azure Skills 플러그인으로, Microsoft 사내 EngHub MCP는 `.github/mcp.enghub.example.json` 예시로
연결합니다. 범용 최신 웹 검색은 GitHub Copilot의 web search 또는 Research capability를 사용합니다.

---

## 라이선스

[MIT](LICENSE)
