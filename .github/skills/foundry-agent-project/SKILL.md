---
name: foundry-agent-project
description: "Microsoft Foundry로 에이전트를 정의하고, Microsoft Agent Framework(Python SDK)로 워크플로우를 구성하는 프로젝트를 처음부터 생성·가이드·배포합니다. 기존 Foundry 샘플이 아닌 커스텀 프로젝트 구조를 직접 설계합니다. WHEN: Foundry 에이전트 프로젝트 생성, Agent Framework 프로젝트 시작, Foundry 워크플로우 프로젝트, create Foundry agent project, scaffold agent project, new agent app, Foundry agent from scratch, multi-agent workflow project, create agent workflow, 에이전트 앱 만들기, 에이전트 프로젝트 초기화, Agent Framework 워크플로우, Foundry 프로젝트 세팅, 에이전트 배포 프로젝트, bootstrap agent app, init agent project, agent project template, Foundry starter project, setup agent dev environment, agent boilerplate."
argument-hint: "에이전트의 목적과 사용할 도구/데이터 소스를 설명하세요"
---

# Foundry Agent Project

Microsoft Foundry + Microsoft Agent Framework(Python SDK) 기반 에이전트 프로젝트를 처음부터 생성하고, 워크플로우를 구성하며, Foundry에 배포하는 전체 워크플로우를 안내합니다.

## When to Use

- **커스텀 프로젝트 설계**: Foundry 샘플이 아닌, 요구사항에 맞는 프로젝트 구조를 처음부터 설계할 때
- **멀티에이전트 워크플로우**: 여러 에이전트를 조합한 워크플로우 프로젝트를 구성할 때
- **기존 앱 에이전트화**: 기존 Python 앱에 에이전트 기능을 추가할 때
- **프로젝트 템플릿**: Agent Framework 프로젝트의 표준 구조가 필요할 때

> **기존 스킬과의 차이**: `microsoft-foundry` → `create`는 Foundry 공식 샘플을 다운로드하여 시작합니다. 이 스킬은 사용자 요구사항을 인터뷰하여 **커스텀 구조를 직접 설계**합니다. `microsoft-foundry-agent-framework-code-gen`은 이미 존재하는 코드의 수정/개선에 초점을 맞춥니다.

## DO NOT USE FOR

> 아래에서 참조하는 `microsoft-foundry`, `microsoft-foundry-agent-framework-code-gen`, `azure-prepare` 등은 VS Code Copilot의 내장 스킬(built-in)이며, 이 리포지토리에는 포함되어 있지 않습니다.

- 이미 코드가 있는 에이전트 배포만 → `microsoft-foundry` 스킬의 `deploy` 서브스킬 사용
- 기존 에이전트 코드의 수정/디버그/개선 → `microsoft-foundry-agent-framework-code-gen` 스킬 사용
- Foundry 공식 샘플 기반 빠른 시작 → `microsoft-foundry` → `create` 서브스킬 사용
- Foundry 리소스/RBAC/모델 관리 → `microsoft-foundry` 스킬 사용
- Azure Functions/App Service 배포 → `azure-prepare` 스킬 사용

## Workflow

### Phase 1: 요구사항 수집

사용자에게 다음을 확인합니다:

| 항목 | 설명 | 예시 |
|------|------|------|
| **에이전트 목적** | 에이전트가 수행할 핵심 작업 | "고객 문의 자동 응답", "코드 리뷰 자동화" |
| **도구(Tools)** | 에이전트가 사용할 외부 도구/API | Bing Search, Azure AI Search, Code Interpreter |
| **데이터 소스** | 참조할 데이터/지식 베이스 | Azure Blob, SharePoint, Custom API |
| **에이전트 수** | 단일 에이전트 vs 멀티에이전트 | 단일 / 2~3개 조합 |
| **워크플로우 패턴** | 에이전트 간 협업 방식 | Sequential, Parallel, Router, Handoff |
| **Foundry 프로젝트** | 기존 Foundry 프로젝트 유무 | 신규 생성 / 기존 사용 |

### Phase 2: 프로젝트 스캐폴딩

#### Step 1: 프로젝트 구조 생성

```
<project-root>/
├── pyproject.toml              # 패키지 정의 및 의존성
├── Dockerfile                  # 컨테이너 빌드
├── .env.example                # 환경변수 템플릿
├── .foundry/
│   └── agent-metadata.yaml     # Foundry 메타데이터
├── src/
│   └── <project_name>/
│       ├── __init__.py
│       ├── app.py              # HTTP 서버 엔트리포인트
│       ├── agents/
│       │   ├── __init__.py
│       │   └── <agent_name>.py # 에이전트 정의
│       ├── tools/
│       │   ├── __init__.py
│       │   └── <tool_name>.py  # 커스텀 도구 정의
│       └── workflows/
│           ├── __init__.py
│           └── <workflow>.py   # 워크플로우 오케스트레이션
└── tests/
    ├── __init__.py
    └── test_<agent_name>.py    # 에이전트 테스트
```

#### Step 2: 핵심 파일 생성

**pyproject.toml** — 최신 SDK 버전 핀 포함:
```toml
[project]
name = "<project-name>"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "microsoft-agents-core",
    "microsoft-agents-ai-agents",
    "aiohttp",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio"]
```

> ⚠️ 반드시 `aitk-get_agent_code_gen_best_practices` 도구를 호출하여 최신 SDK 버전과 패턴을 확인합니다.

**Dockerfile** — Foundry 호스팅 호환:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY src/ src/
EXPOSE 8080
CMD ["python", "-m", "src.<project_name>.app"]
```

**.env.example** — 필수 환경변수 문서화:
```env
# Azure AI Foundry
AZURE_AI_PROJECT_CONNECTION_STRING=
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME=

# Optional: Custom tool endpoints
# SEARCH_ENDPOINT=
# SEARCH_API_KEY=
```

#### Step 3: 에이전트 정의

> ⚠️ 아래는 구조 참고용 의사코드입니다. 실제 생성 시 반드시 `aitk-get_agent_code_gen_best_practices` 결과의 최신 SDK 패턴을 우선 적용합니다.

단일 에이전트 패턴:
```python
# src/<project_name>/agents/<agent_name>.py
from microsoft.agents.core import Agent, AgentContext
from microsoft.agents.ai_agents import AIAgent

async def create_agent(context: AgentContext) -> AIAgent:
    agent = AIAgent(
        name="<agent-name>",
        instructions="""
        <에이전트 역할과 지침을 여기에 정의>
        """,
        model=context.config.model_deployment_name,
        tools=[...],  # Phase 1에서 결정한 도구
    )
    return agent
```

#### Step 4: 워크플로우 구성 (멀티에이전트 시)

> ⚠️ 아래는 워크플로우 패턴별 구조 참고용 의사코드입니다. 실제 생성 시 반드시 `aitk-get_agent_code_gen_best_practices` 결과의 최신 SDK 패턴을 우선 적용합니다.

워크플로우 패턴별 코드 생성:

| 패턴 | 설명 | 사용 시기 |
|------|------|----------|
| **Sequential** | A → B → C 순차 실행 | 단계별 처리가 필요한 파이프라인 |
| **Parallel** | A, B, C 동시 실행 후 집계 | 독립적 하위 작업 병렬 처리 |
| **Router** | 입력에 따라 적절한 에이전트 선택 | 의도 분류 후 라우팅 |
| **Handoff** | 에이전트 간 대화 컨텍스트 전달 | 에스컬레이션, 전문가 위임 |

**Sequential 워크플로우 예시:**
```python
# src/<project_name>/workflows/sequential.py
from microsoft.agents.ai_agents import SequentialWorkflow

async def run_pipeline(context, user_input: str):
    """A → B → C 순차 파이프라인"""
    researcher = await create_researcher_agent(context)
    writer = await create_writer_agent(context)
    reviewer = await create_reviewer_agent(context)

    workflow = SequentialWorkflow(
        agents=[researcher, writer, reviewer],
    )
    result = await workflow.run(user_input)
    return result
```

**Router 워크플로우 예시:**
```python
# src/<project_name>/workflows/router.py
from microsoft.agents.ai_agents import RouterWorkflow

async def run_router(context, user_input: str):
    """입력 의도에 따라 적절한 에이전트로 라우팅"""
    faq_agent = await create_faq_agent(context)
    billing_agent = await create_billing_agent(context)
    tech_agent = await create_tech_support_agent(context)

    workflow = RouterWorkflow(
        router_instructions="사용자 질문의 의도를 분류하여 적절한 에이전트로 전달합니다.",
        agents={
            "faq": faq_agent,
            "billing": billing_agent,
            "tech_support": tech_agent,
        },
    )
    result = await workflow.run(user_input)
    return result
```

**Handoff 워크플로우 예시:**
```python
# src/<project_name>/workflows/handoff.py
from microsoft.agents.ai_agents import HandoffWorkflow

async def run_handoff(context, user_input: str):
    """에이전트 간 대화 컨텍스트를 유지하며 전달"""
    triage_agent = await create_triage_agent(context)
    specialist_agent = await create_specialist_agent(context)

    workflow = HandoffWorkflow(
        entry_agent=triage_agent,
        handoff_targets={
            "escalate": specialist_agent,
        },
    )
    result = await workflow.run(user_input)
    return result
```

> 📌 `workflows/` 디렉토리는 에이전트 간 오케스트레이션 로직을 담당합니다. 각 파일은 Agent Framework의 워크플로우 API를 사용하여 `agents/`에 정의된 에이전트들을 조합합니다.

#### Step 5: HTTP 서버 엔트리포인트

```python
# src/<project_name>/app.py
from aiohttp import web
from microsoft.agents.core import AgentRuntime

async def handle_message(request: web.Request) -> web.Response:
    # 메시지 수신 → 에이전트 실행 → 응답 반환
    ...

app = web.Application()
app.router.add_post("/api/messages", handle_message)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
```

### Phase 3: 로컬 개발 및 테스트

#### Step 1: 환경 설정

```bash
# 가상환경 생성 및 의존성 설치
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 환경변수 설정
cp .env.example .env
# .env 파일에 실제 값 입력
```

#### Step 2: 로컬 실행

```bash
python -m src.<project_name>.app
```

#### Step 3: 테스트

```bash
pytest tests/ -v
```

### Phase 4: Foundry 배포

> 이 단계에서는 `microsoft-foundry` 스킬의 서브스킬들을 순서대로 활용합니다.

#### Step 1: Foundry 프로젝트 준비

기존 프로젝트가 없으면 `microsoft-foundry` → `project/create` 서브스킬로 생성합니다.

#### Step 2: `.foundry/agent-metadata.yaml` 설정

```yaml
project:
  subscription_id: "<subscription-id>"
  resource_group: "<resource-group>"
  project_name: "<foundry-project-name>"

agent:
  name: "<agent-name>"
  description: "<에이전트 설명>"

registry:
  acr_name: "<acr-name>"
  image_name: "<project-name>"
  image_tag: "latest"
```

#### Step 3: 빌드 및 배포

`microsoft-foundry` → `deploy` 서브스킬을 호출하여 다음을 수행합니다:

1. Docker 이미지 빌드
2. ACR에 푸시
3. Foundry 에이전트 생성/업데이트
4. 컨테이너 시작

#### Step 4: 배포 검증

`microsoft-foundry` → `invoke` 서브스킬로 배포된 에이전트를 테스트합니다.

### Phase 5: 평가 및 최적화 (선택)

배포 후 에이전트 품질 개선이 필요하면:

1. `microsoft-foundry` → `observe` 서브스킬로 평가 실행
2. 프롬프트 최적화 수행
3. 재배포

## Error Handling

| 상황 | 처리 방법 |
|------|----------|
| `aitk-*` 도구 사용 불가 | SKILL.md의 의사코드 기반으로 생성하되, "최신 SDK 패턴은 `aitk-get_agent_code_gen_best_practices` 도구로 확인하세요"라고 안내 |
| Foundry 프로젝트 접근 불가 | 로컬 개발 환경(pyproject.toml, src/, tests/)까지만 구성하고, 배포 단계는 Foundry 접근 확보 후 진행하도록 안내 |
| Docker 미설치 | Dockerfile은 생성하되, 로컬 실행(`python -m`)까지만 안내. 컨테이너 빌드·배포는 Docker 설치 후 진행 |
| SDK 호환성 문제 | pyproject.toml에 버전을 핀하지 않고, 사용자에게 최신 호환 버전 확인을 요청 |

## Output Format

프로젝트 생성 완료 시 아래 형식으로 요약합니다:

```markdown
## ✅ 프로젝트 생성 완료

**프로젝트명**: <project-name>
**에이전트**: <에이전트 이름 및 역할>
**워크플로우**: <패턴 유형>
**언어**: Python (Microsoft Agent Framework)

### 생성된 파일
- `pyproject.toml` — 패키지 및 의존성
- `Dockerfile` — 컨테이너 빌드
- `src/<project_name>/agents/` — 에이전트 정의
- `src/<project_name>/workflows/` — 워크플로우 구성
- `.foundry/agent-metadata.yaml` — Foundry 메타데이터

### 다음 단계
1. `.env` 파일에 Azure AI Foundry 연결 정보 입력
2. `pip install -e ".[dev]"` 로 의존성 설치
3. 로컬에서 테스트 후 Foundry 배포
```

## 사전 조건

| 항목 | 설명 |
|------|------|
| Python | 3.10 이상 |
| Azure 구독 | Azure AI Foundry 프로젝트 접근 가능 |
| Docker | 컨테이너 빌드용 (배포 시 필요) |
| Azure CLI | `az login` 완료 상태 |
