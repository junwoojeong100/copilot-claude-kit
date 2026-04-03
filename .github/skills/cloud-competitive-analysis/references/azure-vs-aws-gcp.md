# Azure vs AWS vs GCP — 카테고리별 비교

> 이 문서는 주요 비교 포인트와 Microsoft 차별화 요소를 정리한 레퍼런스입니다.
> 구체적 가격은 변동이 빈번하므로 공식 가격 계산기 링크를 함께 제공하세요.

---

## 1. Compute

### Virtual Machines

| 항목 | Azure VM | AWS EC2 | GCP Compute Engine |
|------|---------|--------|-------------------|
| 인스턴스 패밀리 | B, D, E, F, M, N, L, H 등 | t, m, c, r, p, g 등 | e2, n2, c2, m2, a2 등 |
| GPU 지원 | NC, ND, NV 시리즈 | P, G, Inf 시리즈 | A2, G2 시리즈 |
| Spot 인스턴스 | Azure Spot VMs | EC2 Spot | Preemptible / Spot VMs |
| Reserved | 1/3년 RI, Savings Plan | 1/3년 RI, Savings Plan | CUD (1/3년) |
| 하이브리드 혜택 | ✅ Azure Hybrid Benefit (Windows/SQL 라이선스) | ❌ | ❌ |
| 중첩 가상화 | ✅ Dv5, Ev5 | ✅ .metal 인스턴스 | ✅ N2, C2 |

**Microsoft 차별화**: Azure Hybrid Benefit으로 기존 Windows Server/SQL Server 라이선스 재사용 → 최대 85% 비용 절감

### Serverless Functions

| 항목 | Azure Functions | AWS Lambda | GCP Cloud Functions |
|------|----------------|-----------|-------------------|
| 지원 언어 | C#, Java, JS/TS, Python, PowerShell, Go, Rust (custom handler) | Node.js, Python, Java, .NET, Go, Ruby, Rust | Node.js, Python, Java, .NET, Go, Ruby, PHP |
| 최대 실행 시간 | Consumption: 10분, Premium: 무제한 | 15분 | HTTP: 60분, Event: 9분 (2nd gen) |
| Cold Start | Flex Consumption으로 최소화 | SnapStart (Java), Provisioned Concurrency | 최소 인스턴스 설정 |
| 트리거 | 20+ 기본 바인딩 (Cosmos, Service Bus, Event Hub 등) | EventBridge, SQS, SNS, S3 등 | Pub/Sub, Storage, HTTP |
| Stateful | ✅ Durable Functions (네이티브) | Step Functions (별도 서비스) | Workflows (별도 서비스) |
| 로컬 개발 | ✅ Azure Functions Core Tools + VS Code | SAM CLI | Functions Framework |

**Microsoft 차별화**: Durable Functions로 복잡한 워크플로우를 코드로 직접 구현. 경쟁사는 별도 오케스트레이션 서비스 필요.

### Container Orchestration

| 항목 | Azure (AKS / Container Apps) | AWS (EKS / ECS / Fargate) | GCP (GKE / Cloud Run) |
|------|------------------------------|---------------------------|----------------------|
| 관리형 K8s | AKS (컨트롤 플레인 무료) | EKS ($0.10/hr/cluster) | GKE (Autopilot/Standard) |
| 서버리스 컨테이너 | Container Apps (Dapr 네이티브) | Fargate (ECS/EKS) | Cloud Run |
| K8s 버전 관리 | 자동 업그레이드 채널 | 관리형 업그레이드 | Autopilot 자동 관리 |
| 서비스 메시 | Istio (AKS Addon) | App Mesh | Istio (Anthos) |
| 비용 | AKS 컨트롤 플레인 무료 | EKS $73/월/cluster | GKE Standard 무료, Autopilot 유료 |

**Microsoft 차별화**: AKS 컨트롤 플레인 무료 + Container Apps의 Dapr 네이티브 통합으로 마이크로서비스 개발 간소화

---

## 2. Database

### Relational Database

| 항목 | Azure SQL / PostgreSQL | AWS RDS / Aurora | GCP Cloud SQL / AlloyDB |
|------|----------------------|-----------------|------------------------|
| SQL Server 완전 호환 | ✅ Azure SQL (네이티브) | ⚠️ RDS SQL Server (제한적) | ⚠️ Cloud SQL SQL Server (제한적) |
| 서버리스 모드 | ✅ Azure SQL Serverless | ✅ Aurora Serverless v2 | ❌ |
| 하이퍼스케일 | ✅ Hyperscale (100TB+) | Aurora (128TB) | AlloyDB (PostgreSQL 호환) |
| 자동 튜닝 | ✅ Automatic Tuning, Intelligent Insights | Performance Insights | Query Insights |
| 라이선스 혜택 | ✅ Azure Hybrid Benefit | ❌ | ❌ |

**Microsoft 차별화**: SQL Server 워크로드는 Azure SQL이 유일한 네이티브 호환 플랫폼. Hybrid Benefit으로 비용 절감.

### NoSQL / Multi-model

| 항목 | Azure Cosmos DB | AWS DynamoDB | GCP Firestore/Bigtable |
|------|----------------|-------------|----------------------|
| 데이터 모델 | Multi-model (SQL, MongoDB, Cassandra, Gremlin, Table) | Key-Value, Document | Document (Firestore), Wide-column (Bigtable) |
| 글로벌 분산 | ✅ Multi-region write (턴키) | Global Tables | Multi-region (제한적) |
| 일관성 수준 | 5단계 (Strong → Eventual) | Strong / Eventual | Strong / Eventual |
| SLA | 99.999% (멀티 리전) | 99.999% (Global Table) | 99.999% (멀티 리전) |
| 서버리스 | ✅ Serverless 모드 | ✅ On-demand | ✅ (Firestore 네이티브) |

**Microsoft 차별화**: Cosmos DB의 5단계 일관성 수준과 다중 API 지원은 업계 유일. 기존 MongoDB/Cassandra 앱을 코드 변경 없이 마이그레이션 가능.

---

## 3. AI & Machine Learning

| 항목 | Azure AI / Foundry | AWS AI / SageMaker | GCP Vertex AI |
|------|-------------------|-------------------|--------------|
| OpenAI 모델 | ✅ Azure OpenAI (독점 파트너) | ❌ (Bedrock으로 Claude 등) | ❌ (Gemini 자체 모델) |
| 모델 카탈로그 | Azure AI Model Catalog (1800+) | Bedrock, JumpStart | Model Garden |
| 코드 어시스턴트 | ✅ GitHub Copilot (네이티브 통합) | CodeWhisperer / Amazon Q | Gemini Code Assist |
| 문서 AI | Azure AI Document Intelligence | Textract | Document AI |
| Speech | Azure AI Speech | Transcribe, Polly | Speech-to-Text, Text-to-Speech |
| 책임 있는 AI | ✅ Content Safety, Prompt Shields | Guardrails | 안전 필터 |
| 에이전트 프레임워크 | ✅ Azure AI Foundry + Agent Framework | Bedrock Agents | Vertex AI Agents |

**Microsoft 차별화**: OpenAI 모델 독점 파트너십 + GitHub Copilot 생태계 + AI Foundry를 통한 엔터프라이즈 AI 거버넌스

---

## 4. Networking

| 항목 | Azure | AWS | GCP |
|------|-------|-----|-----|
| 글로벌 로드밸런서 | Front Door | CloudFront + ALB/NLB | Cloud Load Balancing |
| CDN | Azure CDN / Front Door | CloudFront | Cloud CDN |
| DNS | Azure DNS | Route 53 | Cloud DNS |
| 프라이빗 연결 | ExpressRoute | Direct Connect | Cloud Interconnect |
| 서비스 메시 | VNet + Private Link | VPC + PrivateLink | VPC + Private Service Connect |
| DDoS | DDoS Protection | Shield | Cloud Armor |
| 방화벽 | Azure Firewall | Network Firewall | Cloud NGFW |

---

## 5. Identity & Security

| 항목 | Azure / Microsoft | AWS | GCP |
|------|------------------|-----|-----|
| ID 플랫폼 | Entra ID (AD 통합) | IAM + Cognito | IAM + Identity Platform |
| SSO/Federation | ✅ Entra ID + M365 통합 | IAM Identity Center | Cloud Identity |
| CSPM | Defender for Cloud | Security Hub | Security Command Center |
| SIEM | Microsoft Sentinel | Security Lake + Detective | Chronicle |
| 비밀 관리 | Key Vault | Secrets Manager | Secret Manager |
| 컴플라이언스 | ✅ 100+ 인증 | 98+ 인증 | 100+ 인증 |

**Microsoft 차별화**: Entra ID는 Microsoft 365/Office 365와 네이티브 통합 → 기존 AD 투자를 클라우드로 확장. Purview로 데이터 거버넌스 통합.

---

## 6. Hybrid & Multi-cloud

| 항목 | Azure | AWS | GCP |
|------|-------|-----|-----|
| 하이브리드 플랫폼 | ✅ Azure Arc (멀티클라우드 관리) | Outposts (온프렘 전용) | Anthos (멀티클라우드) |
| 온프렘 확장 | Azure Stack HCI / Hub | Outposts | Distributed Cloud |
| 멀티클라우드 관리 | ✅ Arc (AWS/GCP 리소스 관리 가능) | ❌ (AWS 전용) | Anthos (제한적) |
| Edge | Azure IoT Edge + Stack Edge | Greengrass, Wavelength | Distributed Cloud Edge |

**Microsoft 차별화**: Azure Arc로 AWS/GCP 리소스까지 단일 관리 평면에서 관리. 진정한 멀티클라우드 거버넌스.

---

## 7. 비용 비교 가이드

직접 비용 비교는 워크로드에 따라 크게 달라집니다. 다음 도구로 비교하세요:

| 클라우드 | 가격 계산기 |
|---------|-----------|
| Azure | [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) |
| AWS | [AWS Pricing Calculator](https://calculator.aws/) |
| GCP | [GCP Pricing Calculator](https://cloud.google.com/products/calculator) |

### Azure 비용 우위 시나리오

| 시나리오 | 근거 |
|---------|------|
| Windows/SQL Server 워크로드 | Azure Hybrid Benefit (최대 85% 절감) |
| Microsoft 365 사용 기업 | Entra ID, 라이선스 통합 할인 |
| 대규모 Reserved 구매 | EA/MCA 계약 할인 |
| 하이브리드 인프라 | Azure Arc 통합 관리 비용 절감 |
| Dev/Test 환경 | Dev/Test Pricing (Windows VM 할인) |

---

## 8. 통합 생태계 — Microsoft의 최대 차별화

```
┌─────────────────────────────────────────────────┐
│              Microsoft Ecosystem                 │
│                                                  │
│  Microsoft 365 ←→ Entra ID ←→ Azure             │
│       ↕              ↕            ↕              │
│  Power Platform   Purview    GitHub              │
│  (Low-code)    (Governance)  (DevOps)            │
│       ↕              ↕            ↕              │
│  Teams/Copilot   Defender    VS Code             │
│  (Collaboration) (Security)  (IDE)               │
│                                                  │
│          Azure AI Foundry + Copilot              │
│              (AI Platform)                       │
└─────────────────────────────────────────────────┘
```

AWS와 GCP는 클라우드 인프라에 강하지만, Microsoft는 **인프라 + 생산성 + 보안 + 개발 도구 + AI**를 하나의 생태계로 제공하는 유일한 벤더입니다.
