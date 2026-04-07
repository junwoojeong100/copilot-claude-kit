# GitHub Copilot as Claude AI + Claude Code

> **Microsoft FTE를 위한 프로젝트**: Microsoft 정직원(FTE)에게 무료 제공되는 **GitHub Copilot Business** 라이센스로, **별도 Anthropic 구독 없이** Claude Opus 4.6 · Sonnet 4.6 등의 모델을 VS Code Copilot Chat에서 사용할 수 있습니다.

이 리포지토리는 여기에 **커스텀 인스트럭션을 추가**하여, 페르소나·코딩 스타일·보안 규칙과 Azure/GitHub 전문 스킬까지 갖춘 코딩 어시스턴트로 만들어 줍니다.

> **목표**: GitHub Copilot을 **Claude AI + Claude Code**처럼 사용하는 것. Anthropic 유료 구독 없이도, Copilot의 Claude 모델 + 커스텀 인스트럭션 조합으로 동일한 경험을 구현합니다.

## 왜 이 리포가 필요한가?

| 구성 요소 | 설명 |
|-----------|------|
| **GitHub Copilot Business** (MS FTE 무료) | Claude 모델 접근 권한 제공 |
| **VS Code Model Picker** | Copilot Chat에서 Claude Opus/Sonnet 모델 선택 |
| **이 리포의 Custom Instructions** | 페르소나·코딩 스타일·보안 규칙 + Azure/GitHub 전문 스킬 |

→ 결과: **무료로 Claude AI + Azure 전문가 경험**을 얻을 수 있습니다.

## 빠른 시작

### 1. 리포지토리 클론

```bash
git clone https://github.com/junwoojeong100/github-copilot-claude-ai.git
cd github-copilot-claude-ai
```

### 2. VS Code로 열기

```bash
code .
```

### 3. Claude 모델 선택

VS Code에서 Copilot Chat 패널을 열고, 하단의 **모델 선택기(Model Picker)** 에서 `Claude Opus 4.6` 또는 `Claude Sonnet 4.6`를 선택합니다.

### 4. 바로 사용

별도 설정 없이 Copilot Chat에서 대화하면 모든 지침이 자동으로 적용됩니다.

- **일반 대화**: `copilot-instructions.md` + `instructions/` 자동 적용
- **코드 작업**: `instructions/` 파일이 패턴 매칭으로 자동 로드
- **프롬프트 템플릿**: `prompts/` 파일을 VS Code 프롬프트 선택기에서 선택
- **전문 스킬**: 관련 질문 시 자동 활성화

---

## 프로젝트 구조

```
.github/
├── copilot-instructions.md                          # 핵심 지침 (매 대화 자동 로드)
│
├── agents/                                           # 커스텀 에이전트 (온디맨드)
│   ├── instruction-reviewer.agent.md                # 커스터마이징 파일 품질 점검
│   └── skill-scaffolder.agent.md                    # 새 스킬 표준 구조 생성
│
├── instructions/                                     # 자동 적용 지침 (applyTo 패턴)
│   ├── coding.instructions.md                       # 코드 품질·보안·스타일
│   ├── safety.instructions.md                       # 안전·윤리 가이드라인
│   ├── persona.instructions.md                      # AI 페르소나 정의
│   ├── thinking.instructions.md                     # 사고방식·추론 프로세스
│   └── communication.instructions.md                # 커뮤니케이션 스타일
│
├── prompts/                                          # 재사용 프롬프트 (온디맨드)
│   ├── code-review.prompt.md                        # 코드 리뷰 요청
│   ├── debug.prompt.md                              # 버그 디버깅
│   ├── architecture.prompt.md                       # 아키텍처 설계
│   ├── explain.prompt.md                            # 학습/설명 요청
│   └── refactor.prompt.md                           # 리팩토링 요청
│
└── skills/                                           # 전문 스킬 (온디맨드)
    ├── azure-architecture-review/                   # Azure 아키텍처 설계 & WAF 리뷰
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── architecture-patterns.md
    │   │   ├── service-selection-guide.md
    │   │   └── waf-review-checklist.md
    │   └── assets/
    │       └── review-report-template.md
    │
    ├── azure-support-guide/                         # Azure 사용법 안내 & 트러블슈팅
    │   ├── SKILL.md
    │   └── references/
    │       ├── troubleshooting-flowchart.md
    │       ├── common-issues.md
    │       └── best-practices-by-service.md
    │
    ├── cloud-competitive-analysis/                  # Azure/GitHub 경쟁사 비교 분석
    │   ├── SKILL.md
    │   └── references/
    │       ├── azure-vs-aws-gcp.md
    │       ├── github-vs-competitors.md
    │       ├── foundry-vs-competitors.md
    │       ├── copilot-vs-claude-code.md
    │       └── service-mapping.md
    │
    ├── fact-check/                                  # 모든 답변 팩트체크 (항상 적용)
    │   └── SKILL.md
    │
    └── google-web-search/                           # Google 웹 검색으로 최신 정보 수집
        └── SKILL.md
```

---

## 구성 요소 설명

### `copilot-instructions.md` — 핵심 지침

Copilot이 **매 대화마다** 자동으로 읽는 파일입니다.  
정직성, 깊이 있는 사고, 안전 우선 등 핵심 원칙과 전체 파일 구조 참조를 포함합니다.

### `agents/` — 커스텀 에이전트

특정 워크플로우에 특화된 에이전트입니다. Chat에서 `@` 또는 에이전트 선택기로 호출합니다.

| 에이전트 | 도구 | 설명 |
|----------|------|------|
| `instruction-reviewer` | 읽기, 검색 | instructions/prompts/skills 파일의 품질·일관성·중복을 점검하고 보고서 제공 |
| `skill-scaffolder` | 읽기, 편집, 검색, 에이전트 | 새 스킬을 표준 디렉토리 구조로 생성 (instruction-reviewer 연동) |

### `instructions/` — 자동 적용 지침

| 파일 | 적용 범위 | 설명 |
|------|----------|------|
| `coding` | 코드·설정 파일 | 가독성 우선, 언어별 베스트 프랙티스 |
| `safety` | 모든 파일 | OWASP Top 10 대응, 보안 코딩, 윤리적 AI 사용 |
| `persona` | 모든 파일 | 지적 겸손, 호기심, 균형 잡힌 시각 등 AI 성격 |
| `thinking` | 모든 파일 | 단계적 사고, 불확실성 인정, 메타인지 |
| `communication` | 모든 파일 | 결론 우선, 적응적 소통, 톤 가이드라인 |

> **적용 범위 상세**: `coding`은 `*.{py,js,ts,jsx,tsx,java,cs,go,...}` 등 주요 코드·설정 파일에 적용되고, 나머지는 모든 파일(`**`)에 적용됩니다.

> `.instructions.md` 파일은 `applyTo` 프론트매터 패턴에 매칭되는 파일을 열거나 편집할 때 자동으로 Copilot 컨텍스트에 추가됩니다.

### `prompts/` — 재사용 프롬프트

VS Code 프롬프트 선택기(📎 → Prompt)에서 선택하여 사용하는 템플릿입니다.

| 프롬프트 | 역할 | 사용 예시 |
|---------|------|----------|
| `code-review` | 보안·성능·가독성 관점 코드 리뷰 | 현재 파일의 코드 품질 점검 |
| `debug` | 증상 파악 → 근본 원인 분석 | 에러 메시지와 함께 원인 추적 |
| `architecture` | 요구사항 → 트레이드오프 → 추천 | 시스템 설계 방향 결정 |
| `explain` | 사용자 수준에 맞춤 개념 설명 | 코드나 개념을 쉽게 이해 |
| `refactor` | 기존 동작 유지하며 품질 개선 | 복잡한 코드 정리 |

### `skills/` — 전문 스킬

슬래시 명령(`/`) 또는 관련 키워드 질문 시 자동 활성화되는 온디맨드 워크플로우입니다.

| 스킬 | 트리거 예시 | 기능 |
|------|-----------|------|
| **azure-architecture-review** | "Azure 아키텍처 설계해줘", "WAF 리뷰" | 아키텍처 설계 + Mermaid 다이어그램 + WAF 5 Pillar 평가 보고서 |
| **azure-support-guide** | "App Service 502 에러", "Azure 사용법" | 체계적 트러블슈팅 + 서비스별 Best Practices + 서비스 비교 |
| **cloud-competitive-analysis** | "Azure vs AWS", "Copilot vs Claude Code" | 서비스 매핑 + 기능/가격 비교 + Microsoft 차별화 포인트 |
| **fact-check** | 모든 답변에 자동 적용 | 답변 내 사실적 주장 검증 + 신뢰도 표시 |
| **google-web-search** | "최신 버전 알려줘", "최근 업데이트", "web search" | Google 검색으로 최신 정보 수집 + 출처 기반 요약 |

> **검색 도메인 정책**: `google-web-search` 스킬은 **신뢰 도메인 우선 정책**을 적용합니다.
> - **1차 신뢰**: `microsoft.com`, `github.com`, `google.com`, `youtube.com`
> - **2차 신뢰**: 공식 프로젝트 사이트(`python.org`, `react.dev`, `kubernetes.io` 등), 패키지 레지스트리(`npmjs.com`, `pypi.org`)
> - 사용자가 특정 도메인을 요청하면 해당 도메인도 검색합니다.
> - 출처 불명 개인 블로그, SEO 스팸 사이트 등 신뢰할 수 없는 소스는 사용하지 않습니다.

---

## 사용법

### Instructions — 자동 적용

**별도 조작 없이 자동으로 동작합니다.** `.github/instructions/` 의 지침 파일들은 `applyTo` 패턴에 매칭되는 파일을 열거나 편집할 때 Copilot 컨텍스트에 자동 로드됩니다.

- 코드 파일(`.py`, `.ts`, `.java` 등)을 열면 → `coding` 지침 자동 적용
- 어떤 파일이든 열면 → `persona`, `thinking`, `communication`, `safety` 지침 자동 적용

> 사용자가 직접 호출할 필요가 없습니다. Copilot이 알아서 적용합니다.

### Prompts — 프롬프트 선택기

1. Copilot Chat 입력창의 📎 (Attach) 버튼을 클릭합니다.
2. **Prompt...** 항목을 선택하면 사용 가능한 프롬프트 목록이 표시됩니다.
3. 원하는 프롬프트를 선택하고, 입력창에 질문이나 요청을 입력해 전송합니다.

```
📎 → Prompt → code-review 선택 → "이 파일 봐줘"
📎 → Prompt → debug 선택 → "TypeError: Cannot read property 'map' of undefined"
📎 → Prompt → architecture 선택 → "실시간 알림 시스템을 설계하고 싶어"
📎 → Prompt → refactor 선택 → "이 함수가 너무 길어"
📎 → Prompt → explain 선택 → "이 코드가 뭘 하는 건지 설명해줘"
```

> **참고**: 프롬프트 내용은 입력창에 텍스트로 나타나지 않습니다. Copilot이 배후에서 프롬프트 지침과 사용자 입력을 합쳐서 처리합니다.

### Skills — 슬래시 명령 또는 자연어

**방법 1: 슬래시 명령**

Copilot Chat에서 `/`를 입력하면 사용 가능한 스킬 목록이 표시됩니다.

```
/azure-architecture-review 전자상거래 플랫폼 아키텍처를 설계해줘
/azure-support-guide Container Apps에서 502 에러가 발생합니다
/cloud-competitive-analysis Azure Functions vs AWS Lambda 비교해줘
/google-web-search React 최신 버전과 변경사항 알려줘
```

**방법 2: 자연어 질문 (자동 활성화)**

스킬의 `description`에 포함된 키워드로 질문하면 자동으로 해당 스킬이 로드됩니다.

```
"Azure 아키텍처 리뷰해줘"              → azure-architecture-review 활성화
"Redis 연결이 끊기는데 어떻게 해야 해?"  → azure-support-guide 활성화
"GitHub vs GitLab 비교해줘"            → cloud-competitive-analysis 활성화
"Foundry vs Bedrock 차이가 뭐야?"      → cloud-competitive-analysis 활성화
"Python 3.13 최신 변경사항 알려줘"       → google-web-search 활성화
"Azure 최근 업데이트가 뭐야?"            → google-web-search 활성화
```

### Agents — 에이전트 선택기

Copilot Chat 상단의 에이전트 선택기에서 원하는 에이전트를 선택하거나, `@`로 호출합니다.

```
에이전트 선택기 → instruction-reviewer → "현재 instructions 파일들 점검해줘"
에이전트 선택기 → skill-scaffolder → "azure-monitoring 스킬을 만들어줘"
```

> 에이전트는 허용된 도구만 사용할 수 있어, 일반 Copilot Chat보다 **제한된 범위에서 안전하게** 동작합니다.

---

## 자주 묻는 질문

### Q: 이 프로젝트를 내 리포에 적용하려면?

`.github/` 폴더 전체를 원하는 프로젝트의 루트에 복사하면 됩니다.  
Copilot이 자동으로 `copilot-instructions.md`를 인식합니다.

### Q: 스킬이 동작하지 않습니다

- VS Code Insiders + GitHub Copilot Chat 최신 버전이 필요합니다.
- `SKILL.md`의 `name` 필드가 폴더명과 일치하는지 확인하세요.
- `description`에 트리거 키워드가 포함되어 있는지 확인하세요.

### Q: instructions 파일이 로드되지 않습니다

- 파일 확장자가 `.instructions.md`인지 확인하세요.
- `applyTo` 패턴이 올바른 glob 형식인지 확인하세요.
- `.github/instructions/` 경로에 위치하는지 확인하세요.

### Q: 기존 copilot-instructions.md와 충돌하나요?

`copilot-instructions.md`는 프로젝트당 하나만 인식됩니다. 기존 파일이 있다면 내용을 병합하세요.

---

## 라이선스

MIT
