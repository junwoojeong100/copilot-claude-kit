# Microsoft Foundry vs Copilot Studio
## 초보자를 위한 완벽 비교 가이드

> 기준일: 2026년 4월 | 최신 업데이트 반영

---

## 슬라이드 1: 제목

### Microsoft Foundry vs Copilot Studio
**AI 에이전트, 어디에서 만들까?**

- Microsoft의 두 가지 핵심 AI 에이전트 플랫폼 비교
- 2026년 4월 기준 최신 정보

---

## 슬라이드 2: AI 에이전트란?

### AI 에이전트 = 똑똑한 디지털 직원

- 사람 대신 **질문에 답하고, 업무를 처리**하는 AI 프로그램
- 예시:
  - 고객 문의에 24시간 자동 응답하는 챗봇
  - 이메일을 읽고 자동으로 일정을 잡아주는 비서
  - 제조 공정 데이터를 분석해 이상을 감지하는 모니터

---

## 슬라이드 3: 한눈에 비교

| | **Copilot Studio** | **Microsoft Foundry** |
|---|---|---|
| 한마디 요약 | **"클릭으로 만드는 AI"** | **"코드로 만드는 AI"** |
| 접근 방식 | 로우코드 / 노코드 (SaaS) | 프로코드 (PaaS) |
| 비유 | 파워포인트로 발표자료 만들기 | Visual Studio로 앱 개발하기 |
| 포털 | copilotstudio.microsoft.com | ai.azure.com |

---

## 슬라이드 4: 누가 사용하나요?

### Copilot Studio 사용자
- 비즈니스 담당자 (HR, 영업, 마케팅)
- IT 관리자
- 시민 개발자 (Citizen Developer)
- **코딩 경험 불필요**

### Microsoft Foundry 사용자
- 전문 개발자 / SW 엔지니어
- 데이터 사이언티스트
- ML 엔지니어
- **Python, C#, JS 등 코딩 필수**

---

## 슬라이드 5: 개발 방식 비교

### Copilot Studio — "보이는 대로 만든다"
- 드래그 앤 드롭 비주얼 디자이너
- 자연어로 에이전트 설명 → 자동 생성
- Topics(대화 흐름) + Agent Flows(자동화)
- 프리빌트 커넥터로 빠른 연결

### Microsoft Foundry — "코드로 자유롭게"
- Python/C# SDK, CLI, VS Code 확장
- Semantic Kernel, LangChain, LangGraph, AutoGen 지원
- 1,400+ 도구 카탈로그(Tool Catalog)에서 선택
- GitHub/Azure DevOps CI/CD 완전 지원

---

## 슬라이드 6: AI 모델 선택

### Copilot Studio
- Microsoft가 관리하는 모델 사용
- GPT-4.1 (기본), GPT-5 (2025.11 GA)
- Claude Opus 4.6, Claude Sonnet 4.5 지원 (2026.2~)
- **파인튜닝 불가** → 프롬프트 수준 커스터마이징
- M365 Copilot Tuning (Preview, 2025.6~)

### Microsoft Foundry
- 광범위한 모델 카탈로그에서 **자유 선택**
  - GPT-5, GPT-4.1, Claude 시리즈
  - Llama, Mistral, Phi, FLUX(이미지) 등
  - Fireworks 커스텀 모델 임포트 (Preview)
- **파인튜닝 지원** — 모델 미세 조정 가능
- 모델 벤치마킹 & 평가 도구 내장

---

## 슬라이드 7: 인프라 & 관리

### Copilot Studio = SaaS (서비스형)
```
┌─────────────────────────┐
│   Microsoft가 전부 관리    │
│  서버, 네트워크, 업데이트   │
│     보안, 컴플라이언스     │
│                         │
│   사용자는 에이전트만 제작  │
└─────────────────────────┘
```
- 인프라 걱정 없음
- 자동 업데이트 & 패치

### Microsoft Foundry = PaaS (플랫폼형)
```
┌─────────────────────────┐
│   사용자가 직접 관리       │
│  컴퓨팅, 네트워크, 스토리지 │
│   RBAC, Key Vault 설정   │
│                         │
│  완전한 인프라 제어 가능    │
└─────────────────────────┘
```
- Azure 구독 내 리소스 직접 운영
- 데이터 주권 완벽 통제

---

## 슬라이드 8: 데이터 연결 & 통합

### Copilot Studio — M365 생태계 중심
- **네이티브 통합**: SharePoint, Teams, Outlook, OneDrive
- Power Platform 커넥터 (1,000+ SaaS 연결)
- Microsoft Graph 커넥터 (ServiceNow, Azure DevOps 등)
- Tenant Graph Grounding으로 문서 검색 향상

### Microsoft Foundry — Azure 생태계 중심
- Azure 서비스 직접 연결 (SQL, Cosmos DB, AKS 등)
- Azure AI Search + Foundry IQ 기반 고급 RAG
- SharePoint, Fabric Data Agent 연결 지원
- 온프레미스/멀티클라우드 커스텀 코드로 연결

---

## 슬라이드 9: 에이전트 배포 채널

### Copilot Studio
| 채널 | 지원 |
|------|------|
| Microsoft Teams | ✅ 원클릭 |
| Microsoft 365 Copilot | ✅ 네이티브 |
| 웹챗/웹사이트 | ✅ 임베딩 코드 |
| WhatsApp | ✅ (2025.7~) |
| Outlook/이메일 | ✅ |
| 모바일 앱 (iOS/Android) | ✅ Client SDK (2025.9~) |

### Microsoft Foundry
| 채널 | 지원 |
|------|------|
| REST API | ✅ 기본 |
| 웹앱/컨테이너 배포 | ✅ |
| Azure Functions | ✅ |
| M365/Teams 게시 | ✅ (M365 Agents SDK 통해) |
| Private Endpoint | ✅ 기업 내부 전용 |
| A2A (Agent-to-Agent) | ✅ |

---

## 슬라이드 10: 2026년 최신 기능 하이라이트

### Copilot Studio 최신 업데이트
| 시기 | 주요 기능 |
|------|----------|
| 2025.9 | Computer-Using Agents (CUA) — 데스크톱 앱 자동화 |
| 2025.10 | MCP 서버 지원, 에이전트 평가 테스트셋 |
| 2025.11 | 멀티에이전트 오케스트레이션, GPT-5 GA |
| 2026.1 | VS Code 확장 GA, Cloud PC 풀링 |
| 2026.2 | Claude Opus 4.6/Sonnet 4.5 선택, 콘텐츠 필터 세밀 설정 |
| 2026.3 | Work IQ 도구 (Preview) — M365 작업 인사이트 연결 |

### Microsoft Foundry 최신 업데이트
| 시기 | 주요 기능 |
|------|----------|
| 2025~ | Responses API (Agents v2) 전환 |
| 2026.Q1 | 멀티에이전트 워크플로우 SDK (Python/C#) |
| 2026.Q1 | Memory — 대화 맥락 유지 기능 |
| 2026.Q1 | Foundry IQ 지식 통합 (인용 기반 답변) |
| 2026.Q1 | A2A 에이전트 엔드포인트 |
| 2026.4 | Task Adherence 가드레일, LangChain/LangGraph 통합 |
| 2026.4 | Prompt Optimizer, Fireworks 커스텀 모델 임포트 |

---

## 슬라이드 11: 멀티에이전트 비교

### 여러 AI 에이전트가 협업하는 시대

**Copilot Studio**
- 에이전트 간 연결 (authoring-add-other-agents)
- Microsoft Fabric Data Agent 연결
- 로우코드 방식으로 에이전트 조합
- A2A 프로토콜 지원

**Microsoft Foundry**
- SDK 기반 멀티에이전트 워크플로우
- Semantic Kernel / AutoGen / LangGraph 활용
- 복잡한 분기/병렬 처리 로직 구현
- A2A, MCP 프로토콜 완전 지원

---

## 슬라이드 12: 보안 & 거버넌스

### Copilot Studio
- M365 Admin Center 통합 관리
- Microsoft Entra ID 기반 인증
- **Entra Agent Identity** 자동 생성 (2025.11~)
- Microsoft Purview 연동 (DLP, 감사, 민감도 라벨)
- MIP(정보보호) 라벨 자동 표시 (2025.7~)

### Microsoft Foundry
- Azure RBAC 세밀한 역할 관리
- Key Vault, Private Endpoint, VNet 보안
- Foundry Control Plane 중앙 거버넌스
- Azure Policy 통합
- Microsoft Purview 연동 (Defender for Cloud 통해)
- Task Adherence 가드레일로 에이전트 행동 제어

---

## 슬라이드 13: 비용 구조

### Copilot Studio
- **라이선스 기반** 과금
  - 사용자당 월 구독 또는 메시지 팩 구매
  - 예측 가능한 비용 구조
- 인프라 비용 없음 (Microsoft가 관리)

### Microsoft Foundry
- **종량제 (Pay-as-you-go)**
  - 플랫폼 자체는 무료
  - 사용한 Azure 서비스별 비용 발생 (모델 API 호출, 컴퓨팅 등)
  - 사용량에 따라 가변적

### 통합 옵션
- **Microsoft Agent Pre-Purchase Plan (P3)**
  - 양쪽 플랫폼 크레딧을 하나로 통합 구매
  - 대규모 에이전트 프로젝트 시 비용 절감

---

## 슬라이드 14: 이런 상황엔 이것!

### Copilot Studio를 선택하세요
- ✅ 개발자 없이 빠르게 에이전트를 만들고 싶다
- ✅ Teams, Outlook 등 M365에서 바로 사용할 에이전트가 필요하다
- ✅ HR 문의 챗봇, 고객 FAQ 봇 같은 대화형 에이전트를 원한다
- ✅ Power Automate로 업무 자동화를 연결하고 싶다
- ✅ 인프라 관리 없이 AI를 도입하고 싶다

### Microsoft Foundry를 선택하세요
- ✅ 기존 앱/웹사이트에 AI 에이전트를 깊이 통합하고 싶다
- ✅ 모델을 파인튜닝하거나 자체 모델을 사용하고 싶다
- ✅ 복잡한 멀티에이전트 시스템을 구축해야 한다
- ✅ 데이터가 Azure 내 VNet에서만 처리되어야 한다
- ✅ GitHub CI/CD와 연동된 전문 DevOps 파이프라인이 필요하다

---

## 슬라이드 15: Better Together — 함께 쓰면 더 강력

```
┌───────────────────────────────────────────────┐
│                                               │
│  ┌─────────────┐          ┌─────────────────┐ │
│  │  Copilot     │  연결    │  Microsoft      │ │
│  │  Studio      │◄───────►│  Foundry         │ │
│  │              │  A2A    │                  │ │
│  │ 사용자 대면   │         │ 백엔드 AI 로직   │ │
│  │ 대화 인터페이스│         │ 커스텀 모델/도구  │ │
│  └─────────────┘          └─────────────────┘ │
│                                               │
│        ↓ 배포                    ↓ 처리        │
│  Teams, M365, 웹챗         Azure 인프라        │
│                                               │
└───────────────────────────────────────────────┘
```

### 하이브리드 패턴
1. **개발자**는 Foundry에서 전문 에이전트/도구 구축
2. **비즈니스 팀**은 Copilot Studio에서 사용자 대면 워크플로우 조립
3. 에이전트 간 A2A/MCP 프로토콜로 실시간 협업

---

## 슬라이드 16: 실제 시나리오 예시

### 시나리오 A: 고객 서비스 센터
| 단계 | 플랫폼 | 역할 |
|------|--------|------|
| 1. 고객 문의 접수 | Copilot Studio | Teams/웹챗으로 대화 |
| 2. FAQ 자동 응답 | Copilot Studio | SharePoint 기반 지식으로 답변 |
| 3. 복잡한 기술 분석 | Foundry | 커스텀 모델로 로그 분석 |
| 4. 답변 전달 | Copilot Studio | 분석 결과를 사용자에게 전달 |

### 시나리오 B: 제조 공정 최적화
| 단계 | 플랫폼 | 역할 |
|------|--------|------|
| 1. 센서 데이터 수집 | Foundry | IoT 데이터 실시간 처리 |
| 2. 이상 감지 | Foundry | 멀티모달 AI로 영상+수치 분석 |
| 3. 알림 & 보고 | Copilot Studio | Teams로 담당자에게 알림 |
| 4. 조치 승인 | Copilot Studio | 관리자 승인 워크플로우 |

---

## 슬라이드 17: 시작하기 가이드

### Copilot Studio 시작하기
1. [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com) 접속
2. "에이전트 만들기" 클릭
3. 자연어로 에이전트 목적 설명
4. 지식 소스 연결 (SharePoint, 웹사이트 등)
5. 테스트 → 게시 (Teams, 웹 등)

### Microsoft Foundry 시작하기
1. [ai.azure.com](https://ai.azure.com) 접속 (Azure 계정 필요)
2. Foundry 리소스 & 프로젝트 생성
3. 모델 배포 (GPT-5, Claude 등)
4. SDK로 에이전트 코드 작성 (Python/C#)
5. 테스트 → API/컨테이너로 배포

---

## 슬라이드 18: 의사결정 플로우차트

```
                    AI 에이전트를 만들고 싶다
                           │
                    코딩 경험이 있나요?
                      /          \
                   아니오          예
                    │              │
            M365 통합이           커스텀 모델/
            주요 목적?            파인튜닝 필요?
              /    \              /       \
            예     아니오        예        아니오
             │       │           │          │
        Copilot   Copilot    Foundry    복잡한 멀티
        Studio    Studio               에이전트?
                                       /      \
                                      예      아니오
                                       │        │
                                   Foundry   Copilot
                                             Studio
                                             (우선)
```

---

## 슬라이드 19: 핵심 요약

| 관점 | Copilot Studio | Microsoft Foundry |
|------|:---:|:---:|
| 진입 장벽 | 낮음 | 높음 |
| 개발 속도 | 빠름 | 보통 |
| 커스터마이징 | 제한적 | 무제한 |
| M365 통합 | 최고 | 가능 |
| 모델 선택권 | 제한적 | 광범위 |
| 인프라 관리 | 불필요 | 필요 |
| 비용 예측 | 쉬움 | 가변적 |
| 엔터프라이즈 제어 | 관리형 | 완전 제어 |

---

## 슬라이드 20: 마무리

### 핵심 메시지

> **"둘 중 하나가 아니라, 상황에 맞게 선택하고 함께 쓰세요"**

- **빠르게 시작** → Copilot Studio
- **깊이 있게 구축** → Microsoft Foundry
- **최대 효과** → Better Together (하이브리드)

### 참고 자료
- [Copilot Studio 공식 문서](https://learn.microsoft.com/en-us/microsoft-copilot-studio/)
- [Microsoft Foundry 공식 문서](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Copilot Studio vs Foundry 비교 블로그](https://techcommunity.microsoft.com/blog/microsoft-security-blog/microsoft-copilot-studio-vs-microsoft-foundry-building-ai-agents-and-apps/4483160)
- [Microsoft Agent Pre-Purchase Plan](https://learn.microsoft.com/en-us/azure/cost-management-billing/reservations/agent-pre-purchase)

---

> **출처**
> - [Microsoft Copilot Studio vs. Microsoft Foundry: Building AI Agents and Apps](https://techcommunity.microsoft.com/blog/microsoft-security-blog/microsoft-copilot-studio-vs-microsoft-foundry-building-ai-agents-and-apps/4483160) — Microsoft Security Blog
> - [Navigating AI Solutions: Copilot Studio vs. Azure AI Foundry](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/navigating-ai-solutions-microsoft-copilot-studio-vs-azure-ai-foundry/4411678) — Microsoft Foundry Blog
> - [What is Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-ai-foundry) — Microsoft Learn (2026.3.14 업데이트)
> - [Copilot Studio Overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio) — Microsoft Learn (2026.2.9 업데이트)
> - [What's new in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new) — Microsoft Learn (2026.3.6 업데이트)
> - [What's new in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/whats-new-foundry) — Microsoft Learn (2026.4.3 업데이트)
