# Troubleshooting Flowchart

서비스별 체계적 진단 흐름입니다.

---

## 공통 진단 흐름

```
문제 발생
│
├─ 1. Azure 서비스 상태 확인
│  └─ https://status.azure.com 또는 Service Health
│     ├─ 장애 발생 중 → 대기 또는 지원 요청
│     └─ 정상 → 다음 단계
│
├─ 2. 리소스 헬스 확인
│  └─ Resource Health 조회
│     ├─ Unavailable → 플랫폼 이슈, 지원 요청
│     ├─ Degraded → 부분 장애, 상세 진단
│     └─ Available → 다음 단계
│
├─ 3. 최근 변경 이력 확인
│  └─ Activity Log 조회 (최근 24h)
│     ├─ 실패한 작업 발견 → 해당 작업 상세 분석
│     └─ 변경 없음 → 다음 단계
│
├─ 4. 카테고리별 진단
│  ├─ 연결 문제 → 네트워크 진단 흐름
│  ├─ 인증/권한 → ID/접근 진단 흐름
│  ├─ 성능 문제 → 성능 진단 흐름
│  ├─ 배포 실패 → 배포 진단 흐름
│  └─ 데이터 문제 → 데이터 진단 흐름
│
└─ 5. 해결 또는 에스컬레이션
```

---

## 네트워크 진단 흐름

```
연결 실패
│
├─ DNS 해석 확인
│  └─ nslookup / dig <hostname>
│     ├─ 해석 실패 → DNS 설정 / Private DNS Zone 확인
│     └─ 해석 성공 → 다음
│
├─ 포트 연결 확인
│  └─ Network Watcher / telnet / curl
│     ├─ 차단됨 → NSG, Firewall, 서비스 방화벽 확인
│     └─ 열림 → 다음
│
├─ TLS/SSL 확인
│  └─ 인증서 유효성, TLS 버전
│     ├─ 인증서 만료/불일치 → 인증서 갱신
│     └─ 정상 → 다음
│
└─ 애플리케이션 레벨
   └─ 연결 문자열, SDK 설정, 타임아웃 값 확인
```

---

## 인증/권한 진단 흐름

```
403 Forbidden / 401 Unauthorized
│
├─ 인증 방식 확인
│  ├─ Managed Identity
│  │  ├─ ID 활성화 여부 확인
│  │  ├─ 역할 할당 확인 (az role assignment list)
│  │  └─ 역할 전파 대기 (최대 10분)
│  │
│  ├─ Service Principal / App Registration
│  │  ├─ client ID, tenant ID 확인
│  │  ├─ 비밀/인증서 만료 확인
│  │  └─ API 권한 (admin consent 여부)
│  │
│  └─ SAS Token / Access Key
│     ├─ 토큰 만료 시간 확인
│     ├─ 허용된 서비스/리소스 범위 확인
│     └─ IP 제한 확인
│
├─ 대상 서비스 접근 정책 확인
│  ├─ Key Vault → 액세스 정책 vs RBAC 모드
│  ├─ Storage → 네트워크 규칙 + RBAC
│  ├─ SQL → 방화벽 규칙 + AAD Admin
│  └─ Cosmos DB → RBAC 또는 키 기반
│
└─ 네트워크 레벨 차단
   └─ Private Endpoint / VNet 규칙으로 차단될 수 있음
```

---

## 성능 진단 흐름

```
느린 응답 / 타임아웃
│
├─ 메트릭 확인
│  ├─ CPU / 메모리 사용률 → 리소스 부족 시 스케일 업/아웃
│  ├─ 연결 수 / 스레드 수 → 풀 고갈 시 설정 조정
│  └─ 큐 길이 / 대기 시간 → 병목 식별
│
├─ Application Insights (APM)
│  ├─ 느린 요청 식별 (duration > threshold)
│  ├─ 의존성 호출 지연 (DB, 외부 API)
│  ├─ 예외 빈도 확인
│  └─ 분산 추적으로 병목 구간 식별
│
├─ 데이터베이스
│  ├─ 쿼리 성능 (Query Performance Insight)
│  ├─ DTU/vCore 사용률
│  ├─ 인덱스 누락
│  └─ 연결 풀 고갈
│
└─ 네트워크
   ├─ 리전 간 지연 (cross-region latency)
   ├─ 대역폭 제한
   └─ DNS 해석 지연
```

---

## 배포 진단 흐름

```
배포 실패
│
├─ 배포 로그 확인
│  ├─ ARM 배포 → az deployment group show
│  ├─ App Service → Deployment Center / SCM 로그
│  ├─ Container Apps → System 로그, Revision 로그
│  └─ AKS → kubectl rollout status / describe deployment
│
├─ 공통 원인
│  ├─ 리소스 제한/쿼터 초과 → 쿼터 증가 요청
│  ├─ 이미지 풀 실패 → ACR 인증, 이미지 태그 확인
│  ├─ 설정 오류 → 환경 변수, 연결 문자열 확인
│  ├─ 포트 미스매치 → EXPOSE / ingress 포트 확인
│  └─ Health probe 실패 → probe 경로/포트 확인
│
└─ IaC 배포 실패
   ├─ Bicep → az bicep build로 syntax 확인
   ├─ Terraform → terraform validate / plan
   └─ What-if → az deployment group what-if
```

---

## KQL 진단 쿼리 예시

### 실패한 요청 분석
```kql
requests
| where timestamp > ago(1h)
| where success == false
| summarize count() by resultCode, name
| order by count_ desc
```

### 느린 의존성 호출
```kql
dependencies
| where timestamp > ago(1h)
| where duration > 1000
| summarize avg(duration), count() by target, type
| order by avg_duration desc
```

### 예외 추적
```kql
exceptions
| where timestamp > ago(1h)
| summarize count() by type, outerMessage
| order by count_ desc
```

### 리소스 사용량
```kql
performanceCounters
| where timestamp > ago(1h)
| where category == "Process" and name == "% Processor Time"
| summarize avg(value) by bin(timestamp, 5m)
| render timechart
```
