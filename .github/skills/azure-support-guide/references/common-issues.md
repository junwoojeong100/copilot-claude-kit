# Common Issues & Solutions

Azure 서비스별 자주 발생하는 문제와 해결 방법입니다.

---

## App Service

### 배포 후 502 Bad Gateway
**원인**: 앱 시작 실패, 포트 미스매치, health check 실패
**해결**:
```bash
# 로그 확인
az webapp log tail -n <APP_NAME> -g <RG>

# 시작 명령 확인 (Linux)
az webapp config show -n <APP_NAME> -g <RG> --query "linuxFxVersion"

# health check 경로 확인
az webapp config show -n <APP_NAME> -g <RG> --query "healthCheckPath"
```
**조치**: `WEBSITES_PORT` 환경변수 설정, 시작 명령 수정, health check 경로 확인

### 앱 느려짐 / 간헐적 타임아웃
**원인**: ARR Affinity, 리소스 부족, 콜드 스타트
**해결**:
```bash
# 메트릭 확인
az monitor metrics list --resource <RESOURCE_ID> --metric "CpuPercentage,MemoryPercentage" --interval PT5M

# Always On 설정 확인
az webapp config show -n <APP_NAME> -g <RG> --query "alwaysOn"
```
**조치**: 스케일 업 또는 Auto-scale 설정, Always On 활성화

---

## Azure Functions

### Function 실행 안됨 (트리거 미동작)
**원인**: 바인딩 설정 오류, 연결 문자열 누락, 스케일 컨트롤러 문제
**해결**:
```bash
# 앱 설정 확인
az functionapp config appsettings list -n <FUNC_NAME> -g <RG> -o table

# host.json 확인
az functionapp config show -n <FUNC_NAME> -g <RG>
```
**체크리스트**:
- [ ] `AzureWebJobsStorage` 설정이 올바른지
- [ ] 트리거 연결 문자열이 앱 설정에 있는지
- [ ] function.json 바인딩 설정이 정확한지

### Cold Start 지연
**원인**: Consumption plan 특성, 큰 패키지 크기
**해결**:
- Premium plan 또는 Flex Consumption으로 전환
- 패키지 크기 최소화
- `WEBSITE_RUN_FROM_PACKAGE=1` 설정

---

## Container Apps

### 컨테이너 시작 실패
**원인**: 이미지 풀 실패, 포트 미스매치, 환경 변수 누락
**해결**:
```bash
# 시스템 로그 확인
az containerapp logs show -n <APP_NAME> -g <RG> --type system

# revision 상태 확인
az containerapp revision list -n <APP_NAME> -g <RG> -o table
```
**체크리스트**:
- [ ] ACR 자격 증명이 올바른지 (Managed Identity 또는 Admin)
- [ ] 이미지 태그가 존재하는지
- [ ] `targetPort`가 컨테이너의 리스닝 포트와 일치하는지
- [ ] 필수 환경 변수가 설정되었는지

### Ingress 502/503
**원인**: Health probe 실패, 앱 시작 미완료
**해결**:
```bash
# ingress 설정 확인
az containerapp ingress show -n <APP_NAME> -g <RG>
```
**조치**: startup probe 시간 증가, health check 엔드포인트 구현

---

## Azure SQL Database

### 연결 실패 ("Cannot open server")
**원인**: 방화벽 규칙 미설정, VNet 서비스 엔드포인트 미설정
**해결**:
```bash
# 방화벽 규칙 확인
az sql server firewall-rule list -g <RG> -s <SERVER_NAME> -o table

# 클라이언트 IP 추가
az sql server firewall-rule create -g <RG> -s <SERVER_NAME> -n AllowMyIP --start-ip-address <IP> --end-ip-address <IP>

# Azure 서비스 접근 허용
az sql server firewall-rule create -g <RG> -s <SERVER_NAME> -n AllowAzure --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
```

### DTU/vCore 제한 초과
**원인**: 리소스 부족, 비효율적 쿼리
**해결**:
```bash
# 메트릭 확인
az monitor metrics list --resource <RESOURCE_ID> --metric "dtu_consumption_percent,cpu_percent" --interval PT5M
```
**조치**: Query Performance Insight 확인, 인덱스 추가, 티어 업그레이드

---

## Azure Storage

### 403 AuthorizationFailure
**원인**: SAS 만료, RBAC 미설정, 네트워크 규칙 차단
**해결**:
```bash
# 네트워크 규칙 확인
az storage account show -n <ACCOUNT_NAME> -g <RG> --query "networkRuleSet"

# RBAC 할당 확인
az role assignment list --scope "/subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>" -o table
```
**체크리스트**:
- [ ] 네트워크 규칙에서 접근이 허용되는지 (기본: 모든 네트워크 거부)
- [ ] 적절한 RBAC 역할이 할당되었는지 (Storage Blob Data Contributor 등)
- [ ] SAS 토큰 사용 시 만료 시간, 허용 서비스, IP 범위 확인

---

## Key Vault

### 403 Forbidden (SecretGet)
**원인**: 액세스 정책 미설정 또는 RBAC 권한 부족
**해결**:
```bash
# 액세스 모드 확인 (vault access policy vs RBAC)
az keyvault show -n <KV_NAME> --query "properties.enableRbacAuthorization"

# RBAC 모드: 역할 할당 확인
az role assignment list --scope "/subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.KeyVault/vaults/<KV_NAME>" -o table

# Access Policy 모드: 정책 확인
az keyvault show -n <KV_NAME> --query "properties.accessPolicies"
```

---

## Cosmos DB

### 429 Too Many Requests (RU 초과)
**원인**: 프로비저닝된 RU 초과, 비효율적 쿼리, Hot Partition
**해결**:
```bash
# 현재 RU 설정 확인
az cosmosdb sql container throughput show --account-name <ACCOUNT> -g <RG> -d <DB> -n <CONTAINER>
```
**조치**:
- Autoscale 모드 활성화
- 쿼리 최적화 (point read 사용, 크로스 파티션 쿼리 제거)
- 파티션 키 재설계 검토

---

## VNet / Private Endpoint

### Private Endpoint 연결 후 접근 불가
**원인**: DNS 해석이 여전히 공용 IP를 가리킴
**해결**:
```bash
# DNS 해석 확인
nslookup <service>.database.windows.net
# Private Endpoint 적용 시 privatelink 주소로 해석되어야 함

# Private DNS Zone 연결 확인
az network private-dns zone list -g <RG> -o table
az network private-dns link vnet list -g <RG> -z <ZONE_NAME> -o table
```
**체크리스트**:
- [ ] Private DNS Zone이 생성되었는지 (예: `privatelink.database.windows.net`)
- [ ] DNS Zone이 VNet에 링크되었는지
- [ ] A 레코드가 Private Endpoint의 IP를 가리키는지

---

## Managed Identity

### "ManagedIdentityCredential authentication failed"
**원인**: ID 미활성화, 역할 미할당, 전파 지연
**해결**:
```bash
# 시스템 할당 ID 확인
az webapp identity show -n <APP_NAME> -g <RG>

# 역할 할당 확인
az role assignment list --assignee <PRINCIPAL_ID> -o table
```
**핵심**: 역할 할당 후 **최대 10분** 전파 시간이 필요합니다. 할당 직후 실패해도 잠시 대기하세요.

---

## AKS

### kubectl 연결 실패
**원인**: kubeconfig 미설정, API 서버 접근 차단
**해결**:
```bash
# 자격 증명 가져오기
az aks get-credentials -n <CLUSTER_NAME> -g <RG>

# 클러스터 상태 확인
az aks show -n <CLUSTER_NAME> -g <RG> --query "powerState,provisioningState"
```

### Pod Pending 상태
**원인**: 리소스 부족, node 가용성, PVC 미바인딩
**해결**:
```bash
kubectl describe pod <POD_NAME> -n <NAMESPACE>
kubectl get events -n <NAMESPACE> --sort-by='.lastTimestamp'
kubectl top nodes
```
