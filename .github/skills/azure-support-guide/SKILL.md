---
name: azure-support-guide
description: "Azure 서비스 사용 방법 안내 및 트러블슈팅 지원 스킬. 고객/파트너가 Azure 서비스를 올바르게 사용하도록 가이드하고, 문제 발생 시 체계적으로 진단·해결합니다. WHEN: Azure 사용법 문의, Azure 서비스 설정 방법, Azure 트러블슈팅, Azure 오류 해결, 배포 실패, 연결 오류, 인증 오류, 성능 저하, Azure 서비스 비교, Azure 마이그레이션 가이드, how to use Azure, Azure best practices, Azure getting started, Azure 요금 문의, Azure 리소스 설정, Azure 네트워크 문제, Azure 권한 문제, RBAC 설정 방법, Managed Identity 사용법, Azure 모니터링 설정, Azure 로그 분석."
argument-hint: "Azure 서비스 관련 질문이나 발생한 오류 메시지를 입력하세요"
---

# Azure Support Guide

고객 및 파트너의 Azure 서비스 사용법 문의와 트러블슈팅을 체계적으로 지원하는 스킬입니다.

## When to Use

- **사용법 안내**: Azure 서비스의 설정, 구성, 운영 방법을 안내할 때
- **트러블슈팅**: 서비스 오류, 배포 실패, 연결 문제 등 해결할 때
- **서비스 비교**: 유사 서비스 간 선택을 도울 때 (예: App Service vs Container Apps)
- **모범 사례**: 보안, 성능, 비용 관점의 권장 구성을 안내할 때
- **마이그레이션**: 서비스 간 전환 또는 업그레이드 가이드를 제공할 때

---

## Response Principles

### 1. 공감 먼저

고객이 겪는 불편함을 인지하고, 문제를 해결하겠다는 의지를 먼저 전달합니다.

### 2. 구조화된 답변

- **결론 먼저** (Bottom-Line Up Front): 핵심 답변을 먼저 제시
- **단계별 안내**: 번호가 매겨진 명확한 절차
- **검증 포함**: 각 단계 후 결과를 확인하는 방법 제시

### 3. 맥락에 맞는 깊이

| 고객 수준 | 응답 스타일 |
|-----------|------------|
| 입문자 | Portal UI 기반 단계별 가이드, 스크린샷 위치 설명 |
| 중급자 | CLI/PowerShell 명령어 + Portal 병행 |
| 고급자 | CLI/IaC 중심, 아키텍처 수준 조언 |

수준이 불분명하면 CLI 기반으로 안내하되, Portal 대안도 함께 제시합니다.

---

## Workflow

### Mode A: 사용법 안내 (How-To)

#### Step 1: 요구사항 파악

사용자 질문에서 다음을 식별합니다:

1. **대상 서비스**: 어떤 Azure 서비스에 대한 문의인지
2. **수행 작업**: 생성, 설정, 연동, 모니터링 등 무엇을 하려는지
3. **현재 상태**: 이미 설정된 부분과 막힌 부분
4. **환경 정보**: 구독, 리전, 기존 리소스 구성

#### Step 2: 공식 문서 기반 안내

1. MCP 도구 또는 Microsoft Learn에서 최신 공식 문서를 조회합니다
2. 문서 내용을 고객 맥락에 맞게 재구성합니다
3. 실제 실행 가능한 명령어/코드를 제공합니다

**안내 구조:**
```markdown
## 개요
[서비스명]을 [목적]으로 설정하는 방법입니다.

## 사전 요구사항
- 필요한 구독/권한
- 필요한 사전 리소스
- 필요한 CLI 도구 버전

## 단계별 가이드

### 1단계: [작업명]
```bash
az command --param value
```
**확인**: [기대 결과 설명]

### 2단계: [작업명]
...

## 다음 단계
- [추가 설정 안내]
- [관련 서비스 연동]

## 참고 문서
- [공식 문서 링크]
```

#### Step 3: 모범 사례 첨부

사용법 안내 시 해당 서비스의 핵심 Best Practices를 함께 제시합니다. [best-practices-by-service.md](./references/best-practices-by-service.md) 참조.

---

### Mode B: 트러블슈팅 (Troubleshooting)

#### Step 1: 증상 수집

다음 정보를 수집하거나 확인합니다:

| 항목 | 수집 방법 |
|------|----------|
| **오류 메시지** | 사용자 제공 또는 로그에서 추출 |
| **발생 시점** | 언제부터? 간헐적? 지속적? |
| **영향 범위** | 전체 서비스? 특정 기능? 특정 사용자? |
| **최근 변경사항** | 배포, 설정 변경, SKU 변경 등 |
| **재현 조건** | 특정 조건에서만 발생하는지 |

정보가 부족하면 핵심 항목만 추가 질문합니다 (최대 3개).

#### Step 2: 체계적 진단

[troubleshooting-flowchart.md](./references/troubleshooting-flowchart.md)에 따라 진단합니다.

**진단 순서:**

```
1. Azure 서비스 상태 확인 (Azure Status / Resource Health)
   ↓ 서비스 정상
2. 리소스 상태 확인 (Resource Health, Activity Log)
   ↓ 리소스 정상
3. 구성 검증 (설정, 네트워크, 권한)
   ↓ 구성 정상
4. 애플리케이션 레벨 진단 (로그, 메트릭, 트레이스)
   ↓ 원인 식별
5. 해결책 적용 및 검증
```

**진단 도구:**

| 도구 | 용도 | 명령 / MCP |
|------|------|-----------|
| Resource Health | 리소스 가용성 | `mcp_azure_mcp_resourcehealth` |
| Activity Log | 관리 영역 변경 이력 | `az monitor activity-log list` |
| Diagnostic Logs | 서비스별 상세 로그 | `mcp_azure_mcp_monitor` (logs_query) |
| Application Insights | APM, 요청/예외 추적 | `mcp_azure_mcp_applicationinsights` |
| Azure Advisor | AI 기반 권고사항 | `az advisor recommendation list` |
| AppLens | AI 기반 진단 | `mcp_azure_mcp_applens` |
| Network Watcher | 네트워크 진단 | `az network watcher` |

#### Step 3: 원인 분석 및 해결

[common-issues.md](./references/common-issues.md)에서 서비스별 알려진 문제와 해결법을 참조합니다.

**응답 구조:**
```markdown
## 문제 요약
[증상 1줄 요약]

## 원인 분석
[근본 원인 설명]

## 해결 방법

### 즉시 조치 (Quick Fix)
```bash
# 즉시 적용 가능한 명령
```

### 근본 해결 (Permanent Fix)
1. [단계별 해결 절차]
2. ...

### 확인 방법
```bash
# 해결 확인 명령
```

## 재발 방지
- [예방 조치 안내]
- [모니터링/알림 설정 제안]
```

#### Step 4: 에스컬레이션 판단

다음 조건에 해당하면 Microsoft 지원 티켓 생성을 안내합니다:

- Azure 플랫폼 장애로 확인된 경우
- 서비스 제한/쿼터 증가가 필요한 경우
- 알려지지 않은 오류로 자체 해결이 어려운 경우
- 데이터 손실 또는 보안 사고인 경우

```markdown
## 지원 요청 안내
위 방법으로 해결되지 않는 경우, Azure 지원 요청을 생성해주세요:
1. Azure Portal → **도움말 + 지원** → **지원 요청 만들기**
2. 서비스 유형: [해당 서비스]
3. 문제 유형: [해당 유형]
4. 첨부 정보: [수집한 진단 정보]
```

---

### Mode C: 서비스 비교 및 선택 가이드

고객이 유사 서비스 간 선택을 요청하면 다음 구조로 비교합니다:

```markdown
## [서비스 A] vs [서비스 B]

| 기준 | 서비스 A | 서비스 B |
|------|---------|---------|
| 적합한 워크로드 | | |
| 관리 수준 | | |
| 확장 방식 | | |
| 가격 모델 | | |
| SLA | | |

### 추천
- **[서비스 A] 선택**: [조건]
- **[서비스 B] 선택**: [조건]
```

---

## Service-Specific Quick Reference

### Compute

| 문의 유형 | 핵심 진단/안내 포인트 |
|-----------|---------------------|
| App Service 배포 실패 | Deployment Center 로그, SCM 로그, `az webapp log` |
| Functions 실행 안됨 | Host 로그, Application Insights, 바인딩 설정 |
| Container Apps 시작 안됨 | 이미지 풀, 포트 설정, health probe, 환경 변수 |
| AKS Pod 장애 | `kubectl describe pod`, events, resource limits |
| VM 연결 불가 | NSG, RDP/SSH 포트, NIC, Boot diagnostics |

### Data

| 문의 유형 | 핵심 진단/안내 포인트 |
|-----------|---------------------|
| SQL 연결 실패 | 방화벽 규칙, VNet 서비스 엔드포인트, 연결 문자열 |
| Cosmos DB 높은 RU | 쿼리 메트릭, 인덱싱 정책, 파티션 키 |
| Storage 접근 거부 | SAS 토큰, RBAC, 네트워크 규칙, 익명 액세스 설정 |
| Redis 연결 끊김 | 타임아웃 설정, 클라이언트 연결 수, 메모리 사용량 |

### Networking

| 문의 유형 | 핵심 진단/안내 포인트 |
|-----------|---------------------|
| VNet 통신 안됨 | NSG 흐름 로그, 라우팅 테이블, 피어링 상태 |
| Private Endpoint 연결 안됨 | DNS 해석, 프라이빗 DNS 존, NIC 상태 |
| Application Gateway 502 | 백엔드 health, NSG, 경로 기반 라우팅 |
| Front Door 라우팅 오류 | 라우팅 규칙, 원본 그룹, 캐시 설정 |

### Identity & Security

| 문의 유형 | 핵심 진단/안내 포인트 |
|-----------|---------------------|
| RBAC 권한 부족 | 역할 할당 확인, 범위(scope), 조건부 액세스 |
| Managed Identity 안됨 | 시스템/사용자 할당 확인, 역할 전파 시간 (~10분) |
| Key Vault 접근 거부 | 액세스 정책 vs RBAC 모드, 네트워크 규칙 |
| Entra ID 인증 실패 | 앱 등록, redirect URI, 토큰 만료 |

---

## MCP Tools

| Tool | 용도 |
|------|------|
| `mcp_azure_mcp_resourcehealth` | 리소스 가용성 및 상태 확인 |
| `mcp_azure_mcp_applens` | AI 기반 자동 진단 |
| `mcp_azure_mcp_monitor` | 로그 및 메트릭 쿼리 (KQL) |
| `mcp_azure_mcp_applicationinsights` | APM 데이터 조회 |
| `mcp_azure_mcp_documentation` | Azure 문서 검색 |
| `microsoft_docs_search` | Microsoft Learn 검색 |
| `microsoft_docs_fetch` | 문서 전문 조회 |
| `mcp_azure_mcp_get_bestpractices` | Azure 모범 사례 조회 |

---

## Common CLI Commands

```bash
# 리소스 상태 확인
az resource show --ids <RESOURCE_ID>

# 활동 로그 (최근 변경사항)
az monitor activity-log list -g <RG> --max-events 20 --query "[].{Time:eventTimestamp, Op:operationName.localizedValue, Status:status.localizedValue}" -o table

# 진단 설정 확인
az monitor diagnostic-settings list --resource <RESOURCE_ID>

# Application Insights 로그 쿼리
az monitor app-insights query --app <AI_NAME> --analytics-query "requests | where timestamp > ago(1h) | where success == false | summarize count() by resultCode"

# 네트워크 연결 테스트
az network watcher test-connectivity --source-resource <VM_ID> --dest-address <TARGET> --dest-port <PORT>

# Advisor 권고사항 확인
az advisor recommendation list --category Security,HighAvailability,Performance -o table
```

---

## Output Format

| 문의 유형 | 출력 형식 |
|-----------|----------|
| 사용법 안내 | 단계별 가이드 (inline) |
| 트러블슈팅 | 진단 → 원인 → 해결 (inline) |
| 서비스 비교 | 비교 테이블 (inline) |
| 복잡한 가이드 | `<service>-guide.md` 파일 생성 |

---

## Error Handling

| 상황 | 대응 |
|------|------|
| 오류 메시지 불명확 | 오류 재현 방법 또는 전체 로그 요청 |
| 구독/리소스 접근 불가 | 증상 기반으로 가능한 원인 목록 제시 |
| MCP 도구 사용 불가 | CLI 명령 또는 Portal 절차로 대체 안내 |
| 알 수 없는 문제 | 수집해야 할 진단 정보 안내 + 에스컬레이션 경로 제시 |
| 여러 서비스 관련 문제 | 의존성 순서대로 하나씩 진단 |
