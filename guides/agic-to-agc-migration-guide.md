# AGIC → AGC 마이그레이션 가이드

> **Application Gateway Ingress Controller(AGIC)에서 Application Gateway for Containers(AGC)로의 전환 안내**

---

## 목차

1. [한눈에 보는 요약](#1-한눈에-보는-요약)
2. [왜 마이그레이션해야 하나요?](#2-왜-마이그레이션해야-하나요)
3. [AGIC vs AGC 비교](#3-agic-vs-agc-비교)
4. [마이그레이션 전 체크리스트](#4-마이그레이션-전-체크리스트)
5. [마이그레이션 5단계 절차](#5-마이그레이션-5단계-절차)
6. [AGIC 어노테이션 → AGC 매핑표](#6-agic-어노테이션--agc-매핑표)
7. [주의사항 및 제한사항](#7-주의사항-및-제한사항)
8. [FAQ](#8-faq)
9. [참고 자료](#9-참고-자료)

---

## 1. 한눈에 보는 요약

```
┌─────────────────────────────────────────────────────────────┐
│                     현재 (AGIC)                              │
│                                                             │
│  클라이언트 → Application Gateway → AKS Pod                 │
│              (AGIC가 Ingress를 AG 설정으로 변환)              │
└─────────────────────────────────────────────────────────────┘
                          ↓ 마이그레이션
┌─────────────────────────────────────────────────────────────┐
│                     목표 (AGC)                               │
│                                                             │
│  클라이언트 → Application Gateway for Containers → AKS Pod  │
│              (ALB Controller가 Gateway/Ingress API 처리)     │
└─────────────────────────────────────────────────────────────┘
```

**핵심 메시지**: AGC는 AGIC의 **차세대 버전**입니다. Microsoft는 AGIC에서 AGC로의 전환을 공식 권장하고 있습니다. 마이그레이션은 **점진적으로, 다운타임 없이** 수행할 수 있습니다.

---

## 2. 왜 마이그레이션해야 하나요?

### 🔴 AGIC의 한계

| 문제 | 설명 |
|------|------|
| **느린 설정 반영** | Pod/경로 변경 시 ARM API를 통해 Application Gateway를 업데이트하므로 수 분이 걸릴 수 있음 |
| **Ingress API만 지원** | Kubernetes의 차세대 표준인 Gateway API를 지원하지 않음 |
| **제한된 트래픽 관리** | 트래픽 분할(Traffic Splitting), 가중치 기반 라우팅 미지원 |
| **설정 충돌 위험** | AGIC가 Application Gateway의 전체 설정을 덮어쓰며, 기존 설정이 삭제될 수 있음 |

### 🟢 AGC의 장점

| 장점 | 설명 |
|------|------|
| **실시간에 가까운 업데이트** | Pod 추가/제거, 경로 변경, 헬스 프로브 등이 거의 즉시 반영 |
| **Gateway API + Ingress API 모두 지원** | Kubernetes 표준 API를 모두 활용 가능 |
| **트래픽 분할** | 카나리 배포, Blue/Green 배포를 위한 가중치 기반 트래픽 분할 지원 |
| **Azure 또는 Kubernetes로 관리** | Azure Portal/CLI 또는 Kubernetes 리소스 두 가지 방식으로 설정 가능 |
| **자동 스케일링** | 트래픽에 따른 자동 확장/축소 |
| **가용영역 복원력** | 기본적으로 AZ 복원력 제공 |
| **mTLS 지원** | 프론트엔드, 백엔드, 또는 E2E mTLS 지원 |
| **WAF 통합** | Web Application Firewall 정책을 Gateway/HTTPRoute 단위로 세밀하게 적용 |
| **gRPC, HTTP/2, WebSocket, SSE** | 다양한 프로토콜 기본 지원 |

### 비유로 이해하기

> AGIC는 "전통적인 택배 서비스"와 같습니다. 주문(Ingress 설정)이 들어오면 본사(ARM)에 전화해서 배송 경로를 바꿔달라고 요청합니다. 시간이 걸립니다.
>
> AGC는 "실시간 내비게이션이 달린 배송 시스템"입니다. 도로 상황(Pod 변경)이 바뀌면 즉시 경로가 업데이트됩니다. 또한 하나의 화물을 여러 트럭에 나눠 실을 수도 있습니다(트래픽 분할).

---

## 3. AGIC vs AGC 비교

| 항목 | AGIC | AGC |
|------|------|-----|
| API 지원 | Ingress API만 | **Ingress API + Gateway API** |
| 설정 반영 속도 | 느림 (ARM API 경유) | **거의 실시간** |
| 트래픽 분할 | ❌ | ✅ 가중치 기반 라우팅 |
| 관리 방식 | Kubernetes만 | **Azure + Kubernetes 모두** |
| 자동 스케일링 | Application Gateway SKU 의존 | ✅ 내장 |
| mTLS | 제한적 | ✅ 프론트엔드/백엔드/E2E |
| WAF | AG WAF 정책 연결 | ✅ 리소스 단위 세밀한 적용 |
| gRPC | ❌ | ✅ |
| HTTP/2 | 제한적 | ✅ |
| WebSocket | ✅ | ✅ |
| 헬스 프로브 | 어노테이션 기반 | **HealthCheckPolicy CRD** |
| 헤더 재작성 | 어노테이션/CRD | **네이티브 필터** |
| 배포 방식 | Add-on / Helm | **AKS Add-on / Helm** |

---

## 4. 마이그레이션 전 체크리스트

마이그레이션을 시작하기 전에 아래 항목을 확인하세요:

### ✅ 호환성 확인

- [ ] **Private IP 사용 여부**: AGC는 현재 Private IP 프론트엔드를 지원하지 않습니다. Private IP를 사용 중이라면 마이그레이션을 보류하세요.
- [ ] **포트 80/443 외 사용 여부**: AGC는 포트 80과 443만 지원합니다. 다른 포트를 사용하는 서비스가 있다면 마이그레이션을 보류하세요.
- [ ] **Ingress API에서 Custom TLS Policy 사용 여부**: AGC의 Ingress API에서는 커스텀 TLS 정책이 지원되지 않습니다 (Gateway API에서는 지원).

### ✅ 인증서 관리 방식 확인

- [ ] **Azure Key Vault + CSI 드라이버 사용 여부**: AGC는 CSI 드라이버를 통한 인증서 마운트를 **지원하지 않습니다**. Key Vault의 인증서를 Kubernetes Secret으로 동기화해야 합니다.
- [ ] cert-manager + Let's Encrypt 사용 또는 수동으로 Key Vault → K8s Secret 동기화 방식으로 변경 계획 수립

### ✅ 현재 AGIC 어노테이션 목록 정리

```bash
# 현재 사용 중인 AGIC 어노테이션 확인
kubectl get ingress -A -o json | jq '.items[].metadata.annotations | to_entries[] | select(.key | startswith("appgw.ingress.kubernetes.io"))' 
```

### ✅ DNS TTL 확인

```bash
# 현재 DNS TTL 값 확인
dig +noall +answer your-domain.com
```

---

## 5. 마이그레이션 5단계 절차

> **핵심 원칙**: AGIC와 AGC가 동시에 실행되며, 검증 후에 트래픽을 전환합니다. 문제 발생 시 DNS를 되돌려 즉시 롤백할 수 있습니다.

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Step 1   │ →  │ Step 2   │ →  │ Step 3   │ →  │ Step 4   │ →  │ Step 5   │
│ ALB      │    │ Ingress  │    │ E2E      │    │ 트래픽   │    │ AGIC     │
│ 컨트롤러 │    │ 설정     │    │ 테스트   │    │ 전환     │    │ 제거     │
│ 설치     │    │ 변환     │    │          │    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                ← ─ ─ 서비스별 반복 ─ ─ →
```

---

### Step 1: ALB Controller 설치

AGIC와 **병렬로** AGC의 ALB Controller를 설치합니다. 두 컨트롤러가 같은 클러스터에서 동시 실행 가능합니다.

#### 방법 A: AKS Add-on (권장)

```bash
# AKS Add-on으로 설치 (가장 간단)
az aks update \
  -n <AKS-클러스터-이름> \
  -g <리소스-그룹-이름> \
  --enable-addons azure-application-lb-controller
```

Add-on 방식의 장점:
- 자동 업데이트 관리
- Managed Identity 자동 구성
- 서브넷 자동 프로비저닝
- RBAC 자동 설정

#### 방법 B: Helm

```bash
# Helm으로 설치
helm install alb-controller oci://mcr.microsoft.com/application-lb/charts/alb-controller \
  --version 1.3.7 \
  -n azure-alb-system --create-namespace
```

#### 설치 확인

```bash
# ALB Controller Pod가 정상 실행 중인지 확인
kubectl get pods -n azure-alb-system

# 두 개의 Pod가 Running 상태여야 합니다:
# - alb-controller-xxxxx (설정 오케스트레이션)
# - alb-controller-bootstrap-xxxxx (CRD 관리)
```

---

### Step 2: Ingress 설정 변환

기존 AGIC의 Ingress 리소스를 AGC 형식으로 변환합니다. **Gateway API** 또는 **Ingress API** 중 선택할 수 있습니다.

#### 예시: 기본 HTTP 라우팅

**기존 AGIC Ingress:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app-svc
            port:
              number: 80
```

**새 AGC Ingress (Ingress API 방식):**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    alb.networking.azure.io/alb-name: my-alb          # AGC 리소스 이름
    alb.networking.azure.io/alb-namespace: azure-alb   # AGC 네임스페이스
spec:
  ingressClassName: azure-alb-external                  # AGC IngressClass
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app-svc
            port:
              number: 80
```

**새 AGC (Gateway API 방식 — 권장):**

```yaml
# 1. Gateway 리소스 생성
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
  namespace: azure-alb
  annotations:
    alb.networking.azure.io/alb-name: my-alb
spec:
  gatewayClassName: azure-alb-external
  listeners:
  - name: http
    port: 80
    protocol: HTTP
    allowedRoutes:
      namespaces:
        from: All

---
# 2. HTTPRoute 리소스 생성
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: my-app-route
spec:
  parentRefs:
  - name: my-gateway
    namespace: azure-alb
  hostnames:
  - "myapp.example.com"
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: my-app-svc
      port: 80
```

#### 예시: HTTPS + HTTP→HTTPS 리다이렉트

**기존 AGIC:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-https
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    appgw.ingress.kubernetes.io/ssl-redirect: "true"
    appgw.ingress.kubernetes.io/appgw-ssl-certificate: "my-cert"
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app-svc
            port:
              number: 80
```

**새 AGC (Gateway API 방식):**

```yaml
# Gateway — 포트 80과 443 모두 리스닝
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
  namespace: azure-alb
spec:
  gatewayClassName: azure-alb-external
  listeners:
  - name: http
    port: 80
    protocol: HTTP
    allowedRoutes:
      namespaces:
        from: All
  - name: https
    port: 443
    protocol: HTTPS
    tls:
      mode: Terminate
      certificateRefs:
      - kind: Secret
        group: ""
        name: listener-tls-secret       # K8s Secret에 인증서 저장 필요
    allowedRoutes:
      namespaces:
        from: All

---
# HTTPRoute — HTTPS 트래픽 처리
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: my-app-https
spec:
  parentRefs:
  - name: my-gateway
    namespace: azure-alb
    sectionName: https
  hostnames:
  - "myapp.example.com"
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: my-app-svc
      port: 80

---
# HTTPRoute — HTTP→HTTPS 리다이렉트
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: my-app-redirect
spec:
  parentRefs:
  - name: my-gateway
    namespace: azure-alb
    sectionName: http
  hostnames:
  - "myapp.example.com"
  rules:
  - filters:
    - type: RequestRedirect
      requestRedirect:
        scheme: https
        statusCode: 301
```

---

### Step 3: E2E 테스트

실제 트래픽을 전환하기 전에 AGC를 통한 경로가 정상인지 검증합니다.

```bash
# 1. AGC 프론트엔드의 IP/FQDN 확인
kubectl get gateway my-gateway -n azure-alb -o jsonpath='{.status.addresses[0].value}'

# 2. 로컬 hosts 파일로 테스트 (DNS 변경 없이)
# /etc/hosts에 추가:
# <AGC-Frontend-IP>  myapp.example.com

# 3. 요청 테스트
curl -v https://myapp.example.com

# 4. 기대 결과 확인
# - HTTP 상태 코드
# - 응답 헤더
# - 리다이렉트 동작
# - 라우팅 조건
```

---

### Step 4: 트래픽 전환

테스트가 완료되면 DNS를 변경하여 실제 트래픽을 AGC로 전환합니다.

```
            기존                              목표
DNS → Application Gateway (AGIC)    DNS → AGC Frontend
         ↓                                    ↓
      AKS Pod                             AKS Pod
```

**전환 절차:**

1. **DNS TTL 확인**: 현재 DNS 레코드의 TTL을 확인합니다
2. **저트래픽 시간 선택**: 트래픽이 적은 시간에 전환합니다
3. **DNS 레코드 변경**: CNAME 또는 A 레코드를 AGC 프론트엔드로 변경합니다

```bash
# 예: Azure DNS에서 CNAME 업데이트
az network dns record-set cname set-record \
  -g <DNS-리소스-그룹> \
  -z example.com \
  -n myapp \
  -c <AGC-Frontend-FQDN>
```

4. **TTL 대기**: 이전 DNS TTL 시간만큼 기다려서 모든 클라이언트가 새 레코드를 해석하도록 합니다
5. **모니터링**: 트래픽이 정상적으로 흐르는지 확인합니다

> **롤백 방법**: 문제 발생 시 DNS 레코드를 기존 Application Gateway로 되돌리면 됩니다.

---

### Step 5: AGIC 제거

모든 서비스의 마이그레이션이 완료되면 AGIC를 정리합니다.

```bash
# 1. AGIC용 Ingress 리소스 삭제
kubectl delete ingress <ingress-이름> -n <네임스페이스>

# 2-A. AGIC가 AKS Add-on인 경우
az aks disable-addons \
  -n <AKS-클러스터-이름> \
  -g <리소스-그룹-이름> \
  -a ingress-appgw

# 2-B. AGIC가 Helm으로 설치된 경우
helm uninstall ingress-azure

# 3. Application Gateway 리소스 삭제 (Azure Portal 또는 CLI)
az network application-gateway delete \
  -n <AppGW-이름> \
  -g <리소스-그룹-이름>
```

---

## 6. AGIC 어노테이션 → AGC 매핑표

| 기능 | AGIC 어노테이션 | AGC (Gateway API) | AGC (Ingress API) |
|------|-----------------|--------------------|--------------------|
| **경로 재작성** | `backend-path-prefix` | HTTPRoute `URLRewrite` 필터 | IngressExtension `ReplacePrefixMatch` |
| **백엔드 호스트명** | `backend-hostname` | HTTPRoute `URLRewrite` 필터 | IngressExtension |
| **HTTP→HTTPS 리다이렉트** | `ssl-redirect` | HTTPRoute `RequestRedirect` 필터 | IngressExtension `requestRedirect` |
| **TLS 인증서** | `appgw-ssl-certificate` | Gateway `certificateRefs` → K8s Secret | Ingress `tls.secretName` |
| **TLS 정책** | `appgw-ssl-profile` | FrontendTLSPolicy CRD | ❌ 미지원 |
| **백엔드 TLS 신뢰** | `appgw-trusted-root-certificate` | BackendTLSPolicy CRD | BackendTLSPolicy CRD |
| **세션 어피니티** | `cookie-based-affinity` | RoutePolicy CRD | IngressExtension |
| **헬스 프로브** | `health-probe-*` | HealthCheckPolicy CRD | HealthCheckPolicy CRD |
| **헤더 재작성** | `rewrite-rule-set` | HTTPRoute `RequestHeaderModifier` | IngressExtension |
| **연결 드레이닝** | `connection-draining` | 기본 활성화 (설정 불가) | 기본 활성화 (설정 불가) |
| **요청 타임아웃** | `request-timeout` | RoutePolicy | IngressBackendSettings |
| **Private IP** | `use-private-ip` | ❌ 미지원 | ❌ 미지원 |
| **포트 오버라이드** | `override-frontend-port` | ❌ (80/443만 지원) | ❌ (80/443만 지원) |
| **WAF** | `waf-policy-for-path` | WebApplicationFirewallPolicy CRD | ❌ 미지원 |

---

## 7. 주의사항 및 제한사항

### ⚠️ 현재 AGC에서 지원되지 않는 기능

| 기능 | 상태 | 대안 |
|------|------|------|
| **Private IP 프론트엔드** | 미지원 | Private IP가 필요하면 마이그레이션 보류 |
| **80/443 외 포트** | 미지원 | 다른 포트가 필요하면 마이그레이션 보류 |
| **Ingress API Custom TLS 정책** | 미지원 | Gateway API 사용으로 전환 |
| **Ingress API WAF 정책** | 미지원 | Gateway API 사용으로 전환 |

### ⚠️ 인증서 관리 변경점

- AGIC: Azure Key Vault에서 직접 인증서 참조 가능
- **AGC: 인증서를 반드시 Kubernetes Secret으로 저장해야 함**
- Azure Key Vault + CSI 드라이버를 통한 외부 볼륨 마운트 **미지원**
- [cert-manager](https://learn.microsoft.com/azure/application-gateway/for-containers/how-to-cert-manager-lets-encrypt-gateway-api) 사용 또는 Key Vault → K8s Secret 수동 동기화 필요

### ⚠️ 연결 드레이닝 동작 차이

| 시나리오 | AGIC (설정 가능) | AGC (자동) |
|---------|-----------------|------------|
| 스케일 인 | 커스텀 타임아웃 | 5분 후 연결 종료 |
| 비정상 헬스 프로브 | 커스텀 타임아웃 | 클라이언트 연결 해제까지 유지 |
| Pod 제거 | 커스텀 타임아웃 | 클라이언트 연결 해제까지 유지 |

---

## 8. FAQ

### Q: 마이그레이션 중에 다운타임이 발생하나요?

**아닙니다.** AGIC와 AGC가 동시에 실행되며, 같은 백엔드 Pod를 바라봅니다. DNS 전환 방식이므로 다운타임 없이 트래픽을 전환할 수 있습니다. 문제 시 DNS를 되돌리면 즉시 롤백됩니다.

### Q: 모든 서비스를 한 번에 마이그레이션해야 하나요?

**아닙니다.** 서비스 단위로 점진적 마이그레이션이 가능합니다. Step 2~4를 서비스별로 반복하면 됩니다.

### Q: Gateway API와 Ingress API 중 어떤 것을 선택해야 하나요?

**Gateway API를 권장합니다.** Gateway API가 Kubernetes의 차세대 표준이며, AGC에서 더 많은 기능을 지원합니다 (커스텀 TLS 정책, WAF 정책 등). 하지만 기존 Ingress API도 계속 지원하므로, 단순한 구성이라면 Ingress API를 사용해도 됩니다.

### Q: 기존 Application Gateway 리소스는 어떻게 되나요?

마이그레이션 완료 후 **별도로 삭제해야 합니다.** AGC는 기존 Application Gateway와 완전히 별개의 Azure 리소스입니다.

### Q: Private IP를 사용하는 내부 서비스는 어떻게 하나요?

현재 AGC는 Private IP를 지원하지 않으므로, 해당 서비스는 마이그레이션을 **보류**하고 지원이 추가될 때까지 AGIC를 계속 사용하세요.

---

## 9. 참고 자료

### 출처

- [AGIC에서 AGC로 마이그레이션 (공식 가이드)](https://learn.microsoft.com/azure/application-gateway/for-containers/migrate-from-agic-to-agc) — 마이그레이션 절차, 어노테이션 매핑, 기능 비교 상세 안내
- [Application Gateway for Containers 개요](https://learn.microsoft.com/azure/application-gateway/for-containers/overview) — AGC의 아키텍처, 기능, 배포 전략
- [Application Gateway Ingress Controller 개요](https://learn.microsoft.com/azure/application-gateway/ingress-controller-overview) — AGIC 아키텍처 및 기능 설명
- [ALB Controller 설치 가이드 (AKS Add-on)](https://learn.microsoft.com/azure/application-gateway/for-containers/quickstart-deploy-application-gateway-for-containers-alb-controller-addon) — Add-on 방식 설치
- [ALB Controller 설치 가이드 (Helm)](https://learn.microsoft.com/azure/application-gateway/for-containers/quickstart-deploy-application-gateway-for-containers-alb-controller-helm) — Helm 방식 설치
- [AGC 컴포넌트 구성](https://learn.microsoft.com/azure/application-gateway/for-containers/application-gateway-for-containers-components) — 리소스 구조 및 타임아웃 기본값
- [AGC에서 WAF 사용](https://learn.microsoft.com/azure/web-application-firewall/ag/waf-application-gateway-for-containers-overview) — WAF 정책 적용 방법
