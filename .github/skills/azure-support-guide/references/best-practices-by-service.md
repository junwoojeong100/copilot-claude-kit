# Best Practices by Service

Azure 서비스별 핵심 모범 사례 요약입니다. 사용법 안내 시 함께 제시합니다.

---

## App Service

| 영역 | 권장 사항 |
|------|----------|
| **보안** | Managed Identity 사용, HTTPS Only 활성화, TLS 1.2 최소 |
| **가용성** | Always On 활성화, Health Check 설정, 최소 2 인스턴스 |
| **성능** | Auto-scale 규칙 설정, ARR Affinity 비활성화 (stateless 앱) |
| **운영** | Deployment Slots 활용, App Insights 연동, 진단 로그 활성화 |
| **비용** | Dev/Test에 B1, Prod에 S1+ 사용, Reserved Instance 검토 |

---

## Azure Functions

| 영역 | 권장 사항 |
|------|----------|
| **보안** | Managed Identity로 바인딩 인증, Function Key를 Key Vault에 저장 |
| **성능** | Durable Functions으로 장시간 작업 관리, 종속성 최소화 |
| **비용** | Consumption Plan (가변 트래픽), Flex Consumption (예측 가능 트래픽) |
| **운영** | Application Insights 필수, Retry Policy 설정 |
| **설계** | 함수당 단일 책임, Idempotent 설계, 실행 시간 최소화 |

---

## Container Apps

| 영역 | 권장 사항 |
|------|----------|
| **보안** | ACR + Managed Identity, 시크릿은 Key Vault 참조, Private ingress 검토 |
| **가용성** | 최소 replica 2+, health probe (startup/liveness/readiness) 설정 |
| **성능** | 적절한 CPU/Memory 설정, Scale rules (HTTP/KEDA) 구성 |
| **운영** | Revision 모드 Single/Multiple 선택, Log Analytics 연동 |
| **네트워킹** | VNet 통합, Private Endpoint로 백엔드 서비스 접근 |

---

## Azure SQL Database

| 영역 | 권장 사항 |
|------|----------|
| **보안** | AAD 인증, TDE 활성화 (기본), 감사(Auditing) 활성화, Private Endpoint |
| **가용성** | Auto-failover Group (리전 간), Zone Redundancy (리전 내) |
| **성능** | Automatic Tuning 활성화, 인덱스 권고 적용, Read Replica 활용 |
| **비용** | Elastic Pool (다수 DB), Serverless tier (간헐적 사용), Reserved Capacity |
| **운영** | Long-term Backup Retention 설정, DTU → vCore 마이그레이션 검토 |

---

## Cosmos DB

| 영역 | 권장 사항 |
|------|----------|
| **설계** | 파티션 키 신중히 선택 (높은 카디널리티, 균등 분포), 읽기 패턴에 맞는 데이터 모델링 |
| **성능** | Point Read 우선, 크로스 파티션 쿼리 최소화, Autoscale RU 활용 |
| **가용성** | Multi-region write 검토, Consistency level 적절히 선택 |
| **비용** | Autoscale (가변 부하), Reserved Capacity (안정 부하) |
| **보안** | RBAC (데이터 플레인), 네트워크 격리 (Private Endpoint) |

---

## Storage Account

| 영역 | 권장 사항 |
|------|----------|
| **보안** | HTTPS만 허용, 기본 공용 액세스 비활성화, SAS 대신 RBAC 사용 |
| **가용성** | GRS/GZRS (중요 데이터), LRS (비중요/Dev) |
| **성능** | Premium tier (높은 IOPS), Hot/Cool/Archive 적절히 분류 |
| **비용** | Lifecycle Management Policy 설정, 불필요한 스냅샷 정리 |
| **운영** | Soft Delete 활성화, 버전 관리 활성화 (중요 데이터) |

---

## Key Vault

| 영역 | 권장 사항 |
|------|----------|
| **보안** | RBAC 모드 사용 (Access Policy보다 권장), Soft Delete + Purge Protection |
| **운영** | 비밀/인증서 만료 알림 설정, 자동 인증서 갱신 (통합 CA 사용 시) |
| **접근** | Managed Identity 사용, 네트워크 규칙 + Private Endpoint |
| **설계** | 환경별 별도 Vault, 공유 Vault 지양 |

---

## AKS

| 영역 | 권장 사항 |
|------|----------|
| **보안** | AAD 통합, Azure Policy, Workload Identity (구 Pod Identity), Private API Server |
| **가용성** | 프로덕션 최소 3 노드 (Dev/Test는 2 가능), Availability Zone 분산, PDB(Pod Disruption Budget) 설정 |
| **성능** | HPA(Horizontal Pod Autoscaler), KEDA, 적절한 resource requests/limits |
| **비용** | Spot Node Pool (비중요 워크로드), Cluster Autoscaler, AKS Cost Analysis |
| **운영** | Managed Prometheus + Grafana, Container Insights, 자동 업그레이드 채널 설정 |

---

## VNet / Networking

| 영역 | 권장 사항 |
|------|----------|
| **설계** | 주소 공간 미래 확장 고려, 서브넷 역할별 분리 (App, Data, Mgmt) |
| **보안** | NSG를 서브넷 레벨 적용, Azure Firewall 중앙 집중, DDoS Protection |
| **연결** | Private Endpoint (PaaS 서비스), Service Endpoint (레거시 호환) |
| **관리** | Network Watcher 활성화, NSG Flow Logs, Traffic Analytics |

---

## Monitoring (Application Insights + Log Analytics)

| 영역 | 권장 사항 |
|------|----------|
| **수집** | 모든 Prod 앱에 App Insights 연동, 구조화된 로깅 사용 |
| **경보** | SLA 기반 Alert 설정, Action Group으로 알림 채널 구성 |
| **대시보드** | Azure Workbooks 또는 Grafana로 운영 대시보드 구성 |
| **비용** | 샘플링 비율 조정, 데이터 보존 기간 최적화 (기본 90일) |
| **분석** | 분산 추적 활성화, 가용성 테스트(Availability Tests) 구성 |
