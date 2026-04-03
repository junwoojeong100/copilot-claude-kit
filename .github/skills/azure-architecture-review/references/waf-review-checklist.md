# WAF Review Checklist

Well-Architected Framework 5대 Pillar별 리뷰 체크리스트입니다.

---

## 1. Reliability (안정성)

### 가용성
- [ ] 단일 장애점(SPOF)이 존재하는가?
- [ ] 각 서비스의 SLA를 확인하고 복합 SLA를 계산했는가?
- [ ] 가용성 영역(Availability Zone)을 활용하고 있는가?
- [ ] 멀티 리전 배포가 필요한 워크로드인가?

### 복원력
- [ ] 재시도 정책(retry policy)이 구현되어 있는가?
- [ ] Circuit breaker 패턴이 적용되어 있는가?
- [ ] 서비스 간 타임아웃이 적절히 설정되어 있는가?
- [ ] Graceful degradation 전략이 있는가?

### 재해 복구
- [ ] RPO/RTO 요구사항이 정의되어 있는가?
- [ ] 백업 정책이 수립되어 있는가? (빈도, 보존 기간)
- [ ] 지역 간 복제(geo-replication)가 설정되어 있는가?
- [ ] DR 훈련을 정기적으로 실시하는가?

### Health Monitoring
- [ ] 서비스별 health check 엔드포인트가 있는가?
- [ ] 의존 서비스 장애 시 감지가 가능한가?
- [ ] 자동 복구(auto-healing) 메커니즘이 있는가?

---

## 2. Security (보안)

### Identity & Access
- [ ] Managed Identity를 사용하고 있는가? (connection string 대신)
- [ ] RBAC가 최소 권한 원칙으로 구성되어 있는가?
- [ ] MFA가 관리 화면 접근에 적용되어 있는가?
- [ ] Service Principal 키의 만료 정책이 있는가?

### 네트워크 보안
- [ ] Private Endpoint / Private Link를 사용하고 있는가?
- [ ] NSG 규칙이 최소한으로 열려 있는가?
- [ ] 공용 인터넷 노출이 최소화되어 있는가?
- [ ] WAF(Web Application Firewall)가 적용되어 있는가?
- [ ] DDoS Protection이 활성화되어 있는가?

### 데이터 보호
- [ ] 저장 데이터 암호화(encryption at rest)가 적용되어 있는가?
- [ ] 전송 중 데이터 암호화(encryption in transit, TLS 1.2+)가 적용되어 있는가?
- [ ] 민감 데이터가 Key Vault에 저장되어 있는가?
- [ ] 고객 관리 키(CMK)가 필요한가?

### 위협 탐지
- [ ] Defender for Cloud가 활성화되어 있는가?
- [ ] 보안 경고 알림이 설정되어 있는가?
- [ ] 진단 로그가 중앙 집중 수집되고 있는가?

---

## 3. Cost Optimization (비용 최적화)

### Right-sizing
- [ ] 리소스 SKU가 실제 사용량에 적합한가?
- [ ] 과도한 프로비저닝이 있는가?
- [ ] Dev/Test 환경에 낮은 SKU를 사용하고 있는가?

### 비용 모델
- [ ] Reserved Instances / Savings Plan 적용 가능한 서비스가 있는가?
- [ ] Spot VM 활용 가능한 워크로드가 있는가?
- [ ] 서버리스/소비 기반 과금 모델이 적합한 서비스가 있는가?

### 자동 확장
- [ ] Auto-scaling이 설정되어 있는가?
- [ ] Scale-down 정책이 적절한가?
- [ ] 야간/주말 비사용 시 축소 또는 중지하는가?

### 모니터링
- [ ] 비용 경고(Budget Alert)가 설정되어 있는가?
- [ ] 리소스 태그로 비용 추적이 가능한가?
- [ ] 미사용/고아 리소스가 있는가?

---

## 4. Operational Excellence (운영 우수성)

### IaC & 배포
- [ ] 인프라가 코드(Bicep/Terraform)로 관리되는가?
- [ ] CI/CD 파이프라인이 구축되어 있는가?
- [ ] Blue/Green 또는 Canary 배포 전략이 있는가?
- [ ] 롤백 절차가 정의되어 있는가?

### 모니터링 & 가시성
- [ ] Application Insights가 설정되어 있는가?
- [ ] 구조화된 로깅을 사용하고 있는가?
- [ ] 분산 추적(distributed tracing)이 활성화되어 있는가?
- [ ] KPI 기반 대시보드가 있는가?

### 경보 & 대응
- [ ] 핵심 메트릭에 대한 경보(Alert)가 설정되어 있는가?
- [ ] On-call 프로세스가 정의되어 있는가?
- [ ] Runbook/Playbook이 문서화되어 있는가?
- [ ] 사고 대응(Incident Response) 프로세스가 있는가?

### 구성 관리
- [ ] 환경별 설정이 분리되어 있는가? (App Configuration)
- [ ] Feature flag 관리 체계가 있는가?
- [ ] 비크리티컬 의존성에 대한 degradation 계획이 있는가?

---

## 5. Performance Efficiency (성능 효율성)

### Scaling
- [ ] 수평 확장(scale-out)이 가능한 아키텍처인가?
- [ ] 상태 비저장(stateless) 설계가 되어 있는가?
- [ ] Auto-scaling 규칙이 적절한가?

### Caching
- [ ] 적절한 캐싱 계층이 있는가? (Redis, CDN)
- [ ] 캐시 무효화 전략이 정의되어 있는가?
- [ ] CDN이 정적 콘텐츠에 적용되어 있는가?

### 데이터베이스 성능
- [ ] 인덱스가 적절히 설정되어 있는가?
- [ ] 읽기 복제본(read replica)을 활용하고 있는가?
- [ ] 연결 풀링이 적절히 구성되어 있는가?
- [ ] N+1 쿼리 등 비효율 패턴이 없는가?

### 네트워크 성능
- [ ] 리소스들이 같은 리전에 배치되어 있는가?
- [ ] 글로벌 사용자를 위한 CDN/Front Door가 있는가?
- [ ] 대역폭 병목이 있는가?

### 비동기 처리
- [ ] 장시간 작업이 비동기로 처리되는가?
- [ ] 메시지 큐를 통한 작업 분산이 되어 있는가?
- [ ] 배치 처리가 적절히 최적화되어 있는가?

---

## 복합 SLA 계산

### 공식

직렬 (모든 서비스가 동작해야 함):
```
복합 SLA = SLA₁ × SLA₂ × ... × SLAₙ
```

병렬 (하나만 동작하면 됨):
```
복합 SLA = 1 - (1 - SLA₁) × (1 - SLA₂)
```

### 예시
| 구성 | 개별 SLA | 복합 SLA |
|------|---------|---------|
| Front Door → App Service → SQL | 99.99% × 99.95% × 99.99% | 99.93% |
| 위 + Redis Cache | × 99.9% | 99.83% |
| SQL (Primary + Secondary) | 1-(1-0.9999)² | 99.999999% |

---

## 평가 등급 기준

| 등급 | 기준 |
|------|------|
| 🟢 Good | 체크리스트 항목 80% 이상 충족 |
| 🟡 Needs Improvement | 체크리스트 항목 50-80% 충족 |
| 🔴 Critical | 체크리스트 항목 50% 미만 또는 치명적 문제 존재 |
