# Azure Service Selection Guide

워크로드 특성에 따른 Azure 서비스 선택 가이드입니다.

## Compute

| 서비스 | 적합한 경우 | 비적합한 경우 |
|--------|------------|--------------|
| **App Service** | 웹 앱/API, 관리형 원함, .NET/Java/Node/Python | GPU 필요, 커스텀 OS |
| **Container Apps** | 컨테이너 워크로드, 서버리스 원함, Dapr 활용 | K8s 전체 기능 필요 |
| **AKS** | 대규모 마이크로서비스, K8s 전문성 보유 | 소규모, K8s 경험 없음 |
| **Functions** | 이벤트 트리거, 짧은 실행, 간헐적 워크로드 | 장시간 실행, 상시 가동 |
| **Virtual Machines** | 레거시 앱, 특수 소프트웨어, OS 수준 제어 | 클라우드 네이티브 앱 |
| **Static Web Apps** | SPA, JAMstack, 정적 사이트 | 서버 사이드 렌더링 |

### Compute Decision Matrix

```
컨테이너 사용?
├── No
│   ├── 이벤트 기반? → Functions
│   ├── 정적 콘텐츠? → Static Web Apps
│   ├── OS 제어 필요? → VM
│   └── 웹 앱/API → App Service
└── Yes
    ├── K8s 필수 기능 필요? → AKS
    └── 관리형 원함? → Container Apps
```

## Database

| 서비스 | 데이터 모델 | 적합한 워크로드 | SLA |
|--------|-----------|---------------|-----|
| **Azure SQL** | Relational | OLTP, 기존 SQL Server 앱 | 99.99% |
| **Cosmos DB** | Multi-model | 글로벌 분산, 낮은 지연시간 | 99.999% |
| **PostgreSQL Flexible** | Relational | 오픈소스 선호, PostGIS | 99.99% |
| **MySQL Flexible** | Relational | 오픈소스, WordPress 등 | 99.99% |
| **Redis Cache** | Key-Value | 캐싱, 세션 스토어 | 99.9% |
| **Cosmos DB for MongoDB** | Document | MongoDB 호환 필요 | 99.999% |

### Database Decision Matrix

```
데이터 모델?
├── 관계형
│   ├── SQL Server 호환 → Azure SQL
│   ├── PostgreSQL 필요 → PostgreSQL Flexible
│   └── MySQL 필요 → MySQL Flexible
├── 문서형
│   ├── 글로벌 분산 → Cosmos DB
│   └── MongoDB 호환 → Cosmos DB for MongoDB
├── Key-Value → Redis Cache
└── 분석용 → Synapse / Data Explorer
```

## Messaging & Events

| 서비스 | 용도 | 메시지 크기 | 처리량 |
|--------|------|-----------|--------|
| **Service Bus** | 엔터프라이즈 메시징, 트랜잭션 | 256KB~100MB | 중간 |
| **Event Hub** | 대량 이벤트 스트리밍 | 1MB | 매우 높음 |
| **Event Grid** | 이벤트 라우팅, 리액티브 | 1MB | 높음 |
| **Queue Storage** | 단순 큐, 저비용 | 64KB | 중간 |

### Messaging Decision Matrix

```
요구사항?
├── 대량 스트리밍 (IoT, 로그) → Event Hub
├── 이벤트 알림/라우팅 → Event Grid
├── 엔터프라이즈 메시징 (순서, 트랜잭션) → Service Bus
└── 단순 큐, 저비용 → Queue Storage
```

## Networking

| 서비스 | 용도 |
|--------|------|
| **Front Door** | 글로벌 로드밸런싱, WAF, CDN | 
| **Application Gateway** | 리전 L7 로드밸런싱, WAF |
| **Load Balancer** | L4 로드밸런싱 |
| **Traffic Manager** | DNS 기반 글로벌 라우팅 |
| **VPN Gateway** | Site-to-Site / Point-to-Site VPN |
| **ExpressRoute** | 전용 프라이빗 연결 |
| **Private Link** | 프라이빗 엔드포인트 |
| **Azure Firewall** | 중앙 집중 네트워크 보안 |

### Load Balancer Decision Matrix

```
글로벌 분산?
├── Yes
│   ├── HTTP(S)? → Front Door
│   └── Non-HTTP? → Traffic Manager
└── No (리전 내)
    ├── HTTP(S)? → Application Gateway
    └── TCP/UDP? → Load Balancer
```

## Security & Identity

| 서비스 | 용도 |
|--------|------|
| **Entra ID** | 인증, SSO, 조건부 액세스 |
| **Key Vault** | 비밀, 키, 인증서 관리 |
| **Managed Identity** | 서비스 간 비밀번호 없는 인증 |
| **Defender for Cloud** | CSPM, 위협 탐지 |
| **DDoS Protection** | DDoS 공격 방어 |

## Monitoring & Operations

| 서비스 | 용도 |
|--------|------|
| **Application Insights** | APM, 분산 추적, 성능 모니터링 |
| **Log Analytics** | 중앙 로그 수집/분석 |
| **Azure Monitor** | 메트릭, 경고, 대시보드 |
| **Azure Advisor** | 모범 사례 권고 |

## SKU/Tier 선택 가이드

### 환경별 권장 SKU

| 서비스 | Dev/Test | Production | Enterprise |
|--------|----------|------------|------------|
| App Service | B1 | S1/P1v3 | P2v3/P3v3 |
| Azure SQL | Basic/S0 | S3/P1 | P4+/BC |
| Redis Cache | Basic C0 | Standard C1 | Premium P1+ |
| Container Apps | Consumption | Consumption/Dedicated | Dedicated |
| AKS | Standard_B2s | Standard_D4s_v5 | Standard_D8s_v5+ |
