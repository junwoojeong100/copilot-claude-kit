# Claude AI — GitHub Copilot Custom Instructions

GitHub Copilot을 **Claude AI의 원칙과 전문 스킬**로 커스터마이징한 프로젝트입니다.  
이 리포지토리를 클론하면 VS Code에서 Copilot이 자동으로 지침을 로드하여, 일관된 코딩 스타일과 Azure/GitHub 전문 지식을 제공합니다.

## 빠른 시작

### 1. 리포지토리 클론

```bash
git clone https://github.com/junwoojeong/claude-ai.git
cd claude-ai
```

### 2. VS Code로 열기

```bash
code .
```

### 3. 바로 사용

별도 설정 없이 Copilot Chat에서 대화하면 모든 지침이 자동으로 적용됩니다.

- **일반 대화**: `copilot-instructions.md` + `guides/` 자동 적용
- **코드 작업**: `instructions/` 파일이 패턴 매칭으로 자동 로드
- **전문 스킬**: `/azure-architecture-review` 등 슬래시 명령 또는 관련 질문 시 자동 활성화

---

## 프로젝트 구조

```
.github/
├── copilot-instructions.md                          # 핵심 지침 (매 대화 자동 로드)
│
├── instructions/                                     # 자동 적용 지침 (applyTo 패턴)
│   ├── coding.instructions.md                       # 코드 품질·보안·스타일
│   └── safety.instructions.md                       # 안전·윤리 가이드라인
│
├── guides/                                           # 페르소나 & 소통 가이드
│   ├── persona.md                                   # AI 페르소나 정의
│   ├── thinking.md                                  # 사고방식·추론 프로세스
│   ├── communication.md                             # 커뮤니케이션 스타일
│   └── prompts.md                                   # 프롬프트 활용 가이드
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

guides/                                               # 기술 가이드 문서
├── agic-to-agc-migration-guide.md                   # AGIC → AGC 마이그레이션 가이드
└── foundry-vs-copilot-studio-slides.md              # Foundry vs Copilot Studio 비교 슬라이드

tests/                                                # 테스트 및 유틸리티 스크립트
├── requirements.txt                                 # Python 의존성
├── youtube_korean_subtitle.py                       # YouTube 한국어 자막 생성 (배치)
└── youtube_realtime_subtitle.py                     # YouTube 실시간 자막 생성 (스트리밍)
```

---

## 구성 요소 설명

### `copilot-instructions.md` — 핵심 지침

Copilot이 **매 대화마다** 자동으로 읽는 파일입니다.  
정직성, 깊이 있는 사고, 안전 우선 등 핵심 원칙과 전체 파일 구조 참조를 포함합니다.

### `instructions/` — 자동 적용 지침

| 파일 | 적용 범위 | 설명 |
|------|----------|------|
| `coding.instructions.md` | `*.py, *.ts, *.js, *.go` 등 모든 코드 파일 | 가독성 우선, 보안 코딩, 언어별 베스트 프랙티스 |
| `safety.instructions.md` | 모든 파일 (`**`) | OWASP Top 10 대응, 윤리적 AI 사용, 거부 기준 |

> `.instructions.md` 파일은 `applyTo` 프론트매터 패턴에 매칭되는 파일을 열거나 편집할 때 자동으로 Copilot 컨텍스트에 추가됩니다.

### `guides/` — 페르소나 & 소통 가이드

| 파일 | 역할 |
|------|------|
| `persona.md` | 지적 겸손, 호기심, 균형 잡힌 시각 등 AI 성격 정의 |
| `thinking.md` | 단계적 사고, 불확실성 인정, 메타인지 프로세스 |
| `communication.md` | 결론 우선, 적응적 소통, 톤 가이드라인 |
| `prompts.md` | 코드 리뷰, 디버깅, 아키텍처 설계 등 프롬프트 템플릿 |

### `skills/` — 전문 스킬

슬래시 명령(`/`) 또는 관련 키워드 질문 시 자동 활성화되는 온디맨드 워크플로우입니다.

| 스킬 | 트리거 예시 | 기능 |
|------|-----------|------|
| **azure-architecture-review** | "Azure 아키텍처 설계해줘", "WAF 리뷰" | 아키텍처 설계 + Mermaid 다이어그램 + WAF 5 Pillar 평가 보고서 |
| **azure-support-guide** | "App Service 502 에러", "Azure 사용법" | 체계적 트러블슈팅 + 서비스별 Best Practices + 에스컬레이션 가이드 |
| **cloud-competitive-analysis** | "Azure vs AWS", "Copilot vs Claude Code" | 서비스 매핑 + 기능/가격 비교 + Microsoft 차별화 포인트 |
| **fact-check** | 모든 답변에 자동 적용 | 답변 내 사실적 주장 검증 + 신뢰도 표시 |
| **google-web-search** | "최신 버전 알려줘", "최근 업데이트", "web search" | Google 검색으로 최신 정보 수집 + 출처 기반 요약 |

> **검색 도메인 제한 정책**: `google-web-search` 스킬은 신뢰할 수 있는 소스만 참조하도록 아래 4개 도메인으로 검색이 제한됩니다.
> | 허용 도메인 | 포함 범위 |
> |------------|----------|
> | `google.com` | Google 개발자 블로그, Google Cloud 문서 등 |
> | `youtube.com` | 공식 채널 영상, 데모, 튜토리얼 등 |
> | `microsoft.com` | Microsoft Learn, DevBlogs, Azure 문서 등 모든 서브도메인 |
> | `github.com` | GitHub Blog, Docs, 릴리스 페이지 등 모든 서브도메인 |
>
> 이 제한은 생략하거나 우회할 수 없으며, 모든 검색 쿼리에 `site:` 연산자가 자동 포함됩니다.

---

## 스킬 사용법

### 방법 1: 슬래시 명령 (명시적 호출)

Copilot Chat에서 `/`를 입력하면 사용 가능한 스킬 목록이 표시됩니다.

```
/azure-architecture-review 전자상거래 플랫폼 아키텍처를 설계해줘
/azure-support-guide Container Apps에서 502 에러가 발생합니다
/cloud-competitive-analysis Azure Functions vs AWS Lambda 비교해줘
/google-web-search React 최신 버전과 변경사항 알려줘
```

### 방법 2: 자연어 질문 (자동 활성화)

스킬의 `description`에 포함된 키워드로 질문하면 Copilot이 자동으로 해당 스킬을 로드합니다.

```
"Azure 아키텍처 리뷰해줘"              → azure-architecture-review 활성화
"Redis 연결이 끊기는데 어떻게 해야 해?"  → azure-support-guide 활성화
"GitHub vs GitLab 비교해줘"            → cloud-competitive-analysis 활성화
"Foundry vs Bedrock 차이가 뭐야?"      → cloud-competitive-analysis 활성화
"Python 3.13 최신 변경사항 알려줘"       → google-web-search 활성화
"Azure 최근 업데이트가 뭐야?"            → google-web-search 활성화
```

---

## 커스터마이징

### 새로운 Instructions 추가

`.github/instructions/` 폴더에 `*.instructions.md` 파일을 만들고 프론트매터를 설정합니다:

```yaml
---
applyTo: "**/*.py"
description: "Python 프로젝트 전용 지침"
---

# Python 지침
...
```

### 새로운 Skill 추가

`.github/skills/<skill-name>/SKILL.md` 파일을 만듭니다:

```yaml
---
name: my-new-skill
description: "이 스킬의 용도와 트리거 키워드. WHEN: keyword1, keyword2."
---

# My New Skill

## When to Use
...

## Workflow
...
```

### 새로운 Guide 추가

`.github/guides/` 폴더에 `.md` 파일을 만들고, `copilot-instructions.md`에서 참조합니다.

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
