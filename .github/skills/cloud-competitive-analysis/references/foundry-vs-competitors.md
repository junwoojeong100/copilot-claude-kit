# Microsoft Foundry vs Competitors — AI 에이전트 플랫폼 비교

> **Last Updated**: 2026-04 | AI 서비스 가격 및 기능은 빈번히 변경됩니다. 최신 정보는 각 공식 문서를 확인하세요.

> Microsoft AI Foundry(구 Azure AI Studio)와 경쟁 AI 플랫폼을 비교합니다.

---

## 1. 플랫폼 전체 비교

| 항목 | Microsoft AI Foundry | AWS Bedrock | Google Vertex AI | OpenAI Platform | Anthropic Console |
|------|---------------------|-------------|-----------------|----------------|-------------------|
| **포지셔닝** | 엔터프라이즈 AI 통합 플랫폼 | 관리형 모델 API + 에이전트 | ML 통합 + Gemini 플랫폼 | 모델 퍼스트 API 플랫폼 | 안전한 AI API 플랫폼 |
| **대상** | 엔터프라이즈 개발자 | AWS 사용 기업 | GCP 사용 기업 / 데이터 사이언티스트 | AI 네이티브 스타트업/개발자 | AI 개발자/기업 |
| **모델 접근** | OpenAI + OSS 1800+ 카탈로그 | Claude, Titan, Llama, Mistral 등 | Gemini + 서드파티 모델 | GPT-4o, o1, o3 등 OpenAI 전용 | Claude 3.5/4 등 Anthropic 전용 |
| **차별점** | 엔터프라이즈 거버넌스 + 멀티모델 | AWS 생태계 통합 | Gemini + 데이터 통합 | 최신 모델 최초 접근 | 안전성·정직성 강조 |

---

## 2. 모델 가용성

| 모델 | Microsoft Foundry | AWS Bedrock | Vertex AI | OpenAI Platform | Anthropic |
|------|-------------------|-------------|-----------|----------------|-----------|
| GPT-4o / GPT-4.1 | ✅ (Azure OpenAI) | ❌ | ❌ | ✅ | ❌ |
| o1 / o3 등 최신 추론 모델 | ✅ (Azure OpenAI) | ❌ | ❌ | ✅ | ❌ |
| Claude 3.5/4 | ⚠️ 카탈로그에서 일부 | ✅ | ✅ (일부) | ❌ | ✅ |
| Gemini 2.x | ❌ | ❌ | ✅ (독점) | ❌ | ❌ |
| Llama 3.x | ✅ 카탈로그 | ✅ | ✅ | ❌ | ❌ |
| Mistral / Mixtral | ✅ 카탈로그 | ✅ | ✅ | ❌ | ❌ |
| Phi (Microsoft) | ✅ (독점) | ❌ | ❌ | ❌ | ❌ |
| DALL·E / GPT Image | ✅ (Azure OpenAI) | ❌ | Imagen | ✅ | ❌ |
| Whisper | ✅ | ❌ | Chirp | ✅ | ❌ |
| **모델 총 수** | 1800+ (카탈로그) | 40+ | 150+ | 10+ (자사 모델) | 5+ (자사 모델) |

**Microsoft 차별화**: OpenAI 모델 독점 엔터프라이즈 접근 + 1800+ 오픈소스 모델 카탈로그 + 자사 Phi 모델. 단일 플랫폼에서 가장 넓은 모델 선택지 제공.

---

## 3. AI 에이전트 프레임워크

| 기능 | Microsoft Agent Framework | AWS Bedrock Agents | Google Agent Development Kit | OpenAI Agents SDK | Anthropic Claude MCP |
|------|--------------------------|-------------------|-------------------------------|-------------------|---------------------|
| **에이전트 생성** | 코드/선언형 YAML | 콘솔/SDK | Agent Development Kit (ADK) | Agents SDK | API 기반 |
| **도구 통합** | Azure Functions, API, MCP | Lambda, API | Cloud Functions, API | Function calling | Tool use, MCP |
| **지식 베이스** | Azure AI Search 통합 | Knowledge Bases (S3 + OpenSearch) | Vertex AI Search | Retrieval (Files) | RAG (외부) |
| **멀티 에이전트** | ✅ 오케스트레이션 네이티브 | ⚠️ 제한적 (선형) | ✅ ADK | ✅ Agent handoffs | ⚠️ 외부 구현 |
| **메모리/상태** | ✅ 대화 히스토리 + 세션 관리 | ✅ 세션 관리 | ✅ 세션 | ✅ Threads | ⚠️ API 레벨 |
| **MCP 지원** | ✅ (네이티브) | ⚠️ | ⚠️ 일부 | ⚠️ | ✅ (창시자) |
| **가드레일** | ✅ Content Safety + Prompt Shields | ✅ Guardrails | ⚠️ 기본 필터 | ⚠️ Moderation API | ✅ Constitutional AI |
| **평가(Eval)** | ✅ Foundry Evaluations | ⚠️ Model Evaluation | ✅ Vertex AI Evaluation | ✅ Evals | ⚠️ 외부 도구 |
| **추적/관찰** | ✅ Foundry Tracing (OpenTelemetry) | ✅ CloudWatch | ✅ Cloud Trace | ⚠️ 제한적 | ⚠️ 외부 도구 |
| **배포** | Azure Container Apps / App Service | Lambda + Bedrock | Cloud Run / GKE | API 직접 호스팅 | API 직접 호스팅 |

**Microsoft 차별화**: 에이전트 개발 → 평가 → 추적 → 배포까지 단일 플랫폼에서 완결. 멀티 에이전트 오케스트레이션과 엔터프라이즈급 가드레일을 네이티브 제공.

---

## 4. RAG (Retrieval-Augmented Generation)

| 기능 | Microsoft Foundry | AWS Bedrock | Vertex AI | OpenAI Platform |
|------|-------------------|-------------|-----------|----------------|
| 벡터 검색 | ✅ Azure AI Search (하이브리드 + 시맨틱) | Knowledge Bases (OpenSearch) | Vertex AI Search | Vector Store (내장) |
| 문서 처리 | ✅ Document Intelligence (OCR + 구조 분석) | Textract | Document AI | File parsing (제한적) |
| 하이브리드 검색 | ✅ 키워드 + 벡터 + 시맨틱 리랭킹 | ⚠️ 벡터 위주 | ⚠️ 벡터 + 키워드 | ⚠️ 벡터 위주 |
| 청킹 전략 | ✅ 커스텀 + 자동 | ✅ 자동 | ⚠️ 기본 | ✅ 자동 |
| 데이터 소스 | Blob, SQL, Cosmos DB, SharePoint, OneLake 등 | S3, RDS, Confluence 등 | Cloud Storage, BigQuery 등 | Files API |
| 엔터프라이즈 데이터 | ✅ Microsoft Graph (M365 데이터) 통합 | ❌ | ❌ | ❌ |

**Microsoft 차별화**: Azure AI Search의 하이브리드 검색(키워드+벡터+시맨틱)은 업계 최고 검색 품질. Microsoft Graph 연동으로 M365 데이터(이메일, Teams, SharePoint) 기반 RAG 가능 — 경쟁사 대비 유일한 기능.

---

## 5. 엔터프라이즈 거버넌스 & 보안

| 기능 | Microsoft Foundry | AWS Bedrock | Vertex AI | OpenAI Platform |
|------|-------------------|-------------|-----------|----------------|
| 네트워크 격리 | ✅ Private Endpoint + VNet | ✅ VPC Endpoint | ✅ VPC-SC | ❌ |
| CMK 암호화 | ✅ | ✅ | ✅ | ⚠️ Enterprise 전용 |
| RBAC | ✅ Entra ID + Azure RBAC | IAM | IAM | ⚠️ 기본 |
| 감사 로그 | ✅ Azure Monitor + Purview | CloudTrail | Cloud Audit Logs | ⚠️ Enterprise 전용 |
| 데이터 주권 | ✅ 60+ 리전, 데이터 잔류 보장 | 리전 선택 | 리전 선택 | ⚠️ 제한적 리전 |
| 컴플라이언스 | ✅ SOC, ISO, HIPAA, FedRAMP 등 100+ | 98+ | 100+ | SOC 2 |
| 콘텐츠 안전 | ✅ Content Safety (세밀한 필터 + Prompt Shields) | Guardrails | 기본 필터 | Moderation API |
| 책임 있는 AI | ✅ RAI 대시보드 + 평가 메트릭 | ⚠️ 기본 | ⚠️ 기본 | ⚠️ 기본 |
| 비용 관리 | ✅ TPM 제한, 배포별 할당량 | 모델별 제한 | 할당량 | Rate Limit |

**Microsoft 차별화**: 엔터프라이즈 요구사항(네트워크 격리, RBAC, 컴플라이언스, 데이터 주권)을 가장 성숙하게 지원. 금융, 의료, 정부 등 규제 산업에 가장 적합한 AI 플랫폼.

---

## 6. Prompt 관리 & 최적화

| 기능 | Microsoft Foundry | AWS Bedrock | Vertex AI | OpenAI Platform |
|------|-------------------|-------------|-----------|----------------|
| 프롬프트 관리 | ✅ Prompt Flow | ⚠️ Prompt Management | ⚠️ Prompt Gallery | ⚠️ Playground |
| 프롬프트 최적화 | ✅ Prompt Optimizer (자동) | ❌ | ❌ | ❌ |
| A/B 테스트 | ✅ 평가 기반 비교 | ⚠️ | ✅ | ⚠️ |
| 버전 관리 | ✅ | ⚠️ | ⚠️ | ❌ |
| 시각적 편집 | ✅ Prompt Flow (DAG 기반) | ❌ | ❌ | ❌ |

**Microsoft 차별화**: Prompt Flow의 시각적 DAG 기반 오케스트레이션 + 자동 Prompt Optimizer는 업계 유일.

---

## 7. 가격 비교 (주요 모델)

> 가격은 1M 토큰 기준, 변동 가능. 공식 가격 페이지 참조.

| 모델 | Azure OpenAI | OpenAI API | Bedrock | Vertex AI |
|------|-------------|-----------|---------|-----------|
| GPT-4o (Input) | ~$2.50 | $2.50 | N/A | N/A |
| GPT-4o (Output) | ~$10.00 | $10.00 | N/A | N/A |
| GPT-4.1 (Input) | ~$2.00 | $2.00 | N/A | N/A |
| Claude 3.5 Sonnet (Input) | 카탈로그 가격 | N/A | $3.00 | $3.00 |
| Gemini 2.0 (Input) | N/A | N/A | N/A | $변동 |
| Llama 3.1 70B (Input) | 카탈로그 (서버리스) | N/A | ~$2.65 | N/A |

**참고**: Azure OpenAI는 PTU(Provisioned Throughput Units) 모델로 대규모 사용 시 비용 예측 가능성이 높음.

---

## 8. 선택 가이드

| 시나리오 | 추천 플랫폼 | 근거 |
|---------|-----------|------|
| 엔터프라이즈 AI (규제 산업) | **Microsoft Foundry** | 네트워크 격리, 컴플라이언스, Entra ID |
| OpenAI 모델 + 엔터프라이즈 | **Microsoft Foundry** | GPT-4o/o1 + 엔터프라이즈 보안 |
| Microsoft 365 데이터 활용 RAG | **Microsoft Foundry** | Microsoft Graph + AI Search |
| 기존 AWS 인프라 확장 | AWS Bedrock | AWS 서비스 통합 |
| Google Workspace 통합 | Vertex AI | Gemini + Google 에코시스템 |
| 스타트업, 빠른 프로토타입 | OpenAI Platform | 최신 모델 최초 접근, 간단한 API |
| 안전성 최우선 AI | Anthropic | Constitutional AI, RLHF |
| 멀티모델 비교/선택 필요 | **Microsoft Foundry** | 1800+ 모델 카탈로그 |
| AI 에이전트 복잡 워크플로우 | **Microsoft Foundry** | Agent Framework + Prompt Flow |
| 코스트 최적화 (OSS 모델) | **Microsoft Foundry** / Bedrock | 서버리스 OSS 모델 배포 |

---

## 9. Microsoft Foundry 통합 생태계

```
┌─────────────────────────────────────────────────────┐
│              Microsoft AI Foundry                    │
│                                                      │
│  Model Catalog ─→ Prompt Flow ─→ Agent Framework    │
│  (1800+ models)   (오케스트레이션)  (멀티 에이전트)     │
│       ↕                ↕               ↕             │
│  AI Search        Evaluations      Tracing          │
│  (RAG/검색)       (품질 평가)       (관찰 가능성)      │
│       ↕                ↕               ↕             │
│  Content Safety   Prompt Optimizer  Azure Monitor   │
│  (가드레일)        (자동 최적화)     (운영 모니터링)    │
└─────────────────────────────────────────────────────┘
        ↕                    ↕                ↕
   Azure (인프라)      GitHub (개발)    Microsoft 365 (데이터)
   - Container Apps    - Copilot         - Graph API
   - AKS              - Actions          - SharePoint
   - Functions         - Codespaces      - Teams
```

경쟁사는 개별 기능을 제공하지만, Microsoft는 **모델 선택 → 개발 → 평가 → 배포 → 운영**의 전체 AI 생명주기를 단일 플랫폼에서 통합 관리합니다.
