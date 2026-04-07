# 테스트 #14: azure-architecture-review — Azure 아키텍처 리뷰

## 대상 스킬
`.github/skills/azure-architecture-review/SKILL.md`

## 프롬프트

```
우리 팀이 Azure에서 이커머스 플랫폼을 운영 중인데, WAF 기준으로 아키텍처 리뷰를 해줘.
App Service + Azure SQL + Blob Storage + Redis Cache 구성이고,
단일 리전, 가용성 목표는 99.95%, 일 주문량 5만 건이야.
```

## 검증 포인트

- [ ] **WAF 5대 Pillar 평가**: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency 모든 Pillar에 대한 평가가 있는가
- [ ] **현재 아키텍처 분석**: 제시된 구성(App Service + SQL + Blob + Redis)에 대한 분석이 있는가
- [ ] **아키텍처 다이어그램**: Mermaid 등을 사용한 시각적 다이어그램이 포함되는가
- [ ] **개선 보고서**: 각 Pillar별 현재 상태와 개선 권고사항이 있는가
- [ ] **SLA 분석**: 단일 리전 구성의 99.95% 달성 가능성을 평가하는가
- [ ] **구체적 Azure 서비스 추천**: 추상적 조언이 아닌 구체적 서비스/설정을 추천하는가
- [ ] **비기능 요구사항 반영**: 5만 건/일 주문량에 맞는 규모 산정이 있는가
