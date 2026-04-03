# Azure Architecture Patterns Reference

아키텍처 패턴별 적용 가이드입니다. 요구사항에 따라 적절한 패턴을 선택하세요.

## N-Tier Architecture

**적합한 경우**: 전통적 웹 애플리케이션, 기존 On-premise 앱 마이그레이션
**Azure 서비스**: App Service + Azure SQL + Redis Cache

```
Client → Front Door → App Service (Web) → App Service (API) → SQL Database
                                                             → Redis Cache
```

| 장점 | 단점 |
|------|------|
| 단순하고 이해하기 쉬움 | 계층 간 강결합 |
| 팀 역할 분리 용이 | 수평 확장 제한적 |
| 기존 팀 역량 활용 | 배포 단위가 큼 |

---

## Microservices Architecture

**적합한 경우**: 대규모 팀, 독립 배포 필요, 복잡한 도메인
**Azure 서비스**: Container Apps / AKS + Service Bus + Cosmos DB

```
API Gateway → Service A → DB A
            → Service B → DB B
            → Service C ←→ Event Bus
```

| 장점 | 단점 |
|------|------|
| 독립 배포/확장 | 운영 복잡도 높음 |
| 기술 다양성 허용 | 분산 트랜잭션 어려움 |
| 장애 격리 | 서비스 간 통신 오버헤드 |

**선택 기준: Container Apps vs AKS**

| 기준 | Container Apps | AKS |
|------|---------------|-----|
| 운영 오버헤드 | 낮음 (서버리스) | 높음 (클러스터 관리) |
| Kubernetes 전문성 | 불필요 | 필요 |
| 커스터마이징 | 제한적 | 완전한 제어 |
| 비용 (소규모) | 낮음 | 높음 |
| 비용 (대규모) | 중간 | 최적화 가능 |

---

## Event-Driven Architecture

**적합한 경우**: 비동기 처리, 느슨한 결합, 실시간 데이터 처리
**Azure 서비스**: Event Grid + Functions + Service Bus

```
Producer → Event Grid → Function A → Storage
                      → Function B → Database
         → Service Bus → Consumer Service
```

| 장점 | 단점 |
|------|------|
| 느슨한 결합 | 디버깅 어려움 |
| 높은 확장성 | 이벤트 순서 보장 복잡 |
| 실시간 반응 | 멱등성 보장 필요 |

---

## Serverless Architecture

**적합한 경우**: 이벤트 기반 워크로드, 가변적 트래픽, 빠른 개발
**Azure 서비스**: Functions + Logic Apps + API Management + Cosmos DB

```
Client → API Management → Functions → Cosmos DB
                                    → Blob Storage
       → Logic Apps → External APIs
```

| 장점 | 단점 |
|------|------|
| 인프라 관리 없음 | Cold start 지연 |
| 사용량 기반 과금 | 실행 시간 제한 |
| 빠른 개발/배포 | 벤더 종속성 |

---

## Hub-Spoke Network Topology

**적합한 경우**: 엔터프라이즈 네트워킹, 멀티 워크로드, 중앙 집중 보안
**Azure 서비스**: VNet + Azure Firewall + VPN Gateway + Private DNS

```
On-Premise ←→ VPN Gateway
                  ↓
            Hub VNet (Firewall, DNS, Bastion)
           /    |    \
     Spoke1  Spoke2  Spoke3
     (Web)   (API)   (Data)
```

| 장점 | 단점 |
|------|------|
| 중앙 집중 보안 | 네트워크 복잡도 |
| 워크로드 격리 | Hub 단일 장애점 가능 |
| 정책 일관성 | 추가 비용 (Firewall) |

---

## CQRS + Event Sourcing

**적합한 경우**: 높은 읽기/쓰기 비율 차이, 이벤트 히스토리 필요, 복잡한 도메인
**Azure 서비스**: Cosmos DB (Event Store) + SQL/Redis (Read Store) + Service Bus

```
Command → API → Event Store (Cosmos DB) → Event Bus
                                         → Projection → Read Store (SQL/Redis)
Query → API → Read Store
```

---

## Big Data / Analytics

**적합한 경우**: 대량 데이터 처리, BI/리포팅, 데이터 레이크
**Azure 서비스**: Data Factory + Data Lake + Synapse + Power BI

```
Sources → Data Factory → Data Lake (Raw)
                       → Synapse (Curated)
                       → Power BI (Serve)
```

---

## Pattern Selection Decision Tree

```
워크로드 유형?
├── 웹 앱/API
│   ├── 단순, 소규모 팀 → N-Tier
│   ├── 복잡 도메인, 대규모 팀 → Microservices
│   └── 가변 트래픽, 빠른 개발 → Serverless
├── 데이터 처리
│   ├── 실시간 → Event-Driven
│   ├── 배치 → Big Data
│   └── 혼합 → Lambda Architecture
├── IoT
│   └── IoT Hub → Stream Analytics → Event-Driven
└── 엔터프라이즈 네트워킹
    └── Hub-Spoke
```
