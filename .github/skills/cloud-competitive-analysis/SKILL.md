---
name: cloud-competitive-analysis
description: "Microsoft Azure 및 GitHub 서비스를 경쟁사(AWS, GCP, GitLab, Bitbucket 등)와 비교 분석하는 스킬. 서비스 매핑, 기능 비교, 마이그레이션 포인트, 차별화 요소를 체계적으로 제시합니다. WHEN: Azure vs AWS, Azure vs GCP, GitHub vs GitLab, GitHub vs Bitbucket, 클라우드 서비스 비교, 경쟁사 비교, 서비스 매핑, cloud comparison, competitive analysis, service equivalent, 경쟁 분석, 마이그레이션 비교, 비용 비교, 기능 비교, DevOps 도구 비교, CI/CD 비교, 컨테이너 서비스 비교, 서버리스 비교, AI 서비스 비교, 데이터베이스 비교, Microsoft Foundry vs Bedrock, Foundry vs Vertex AI, AI 에이전트 플랫폼 비교, GitHub Copilot vs Claude Code, Copilot vs Cursor, AI 코딩 어시스턴트 비교, coding assistant comparison, Copilot vs Amazon Q, Copilot vs Gemini Code Assist."
argument-hint: "비교할 서비스나 카테고리를 입력하세요 (예: Azure Functions vs AWS Lambda)"
---

# Cloud & DevOps Competitive Analysis

Microsoft Azure / GitHub 서비스를 경쟁사 제품과 비교 분석하는 스킬입니다. 고객·파트너에게 객관적이고 공정한 비교 정보를 제공하면서, Microsoft 솔루션의 차별화 포인트를 명확히 전달합니다.

## When to Use

- **서비스 비교**: Azure vs AWS/GCP, GitHub vs GitLab/Bitbucket 등 직접 비교 요청
- **서비스 매핑**: "AWS의 S3에 해당하는 Azure 서비스는?" 등 매핑 질문
- **마이그레이션 검토**: 경쟁 클라우드에서 Azure/GitHub로 전환 시 비교 정보 필요
- **의사결정 지원**: 다중 클라우드 전략에서 서비스 선택 근거 필요
- **RFP/제안서 지원**: 경쟁 입찰 시 비교 자료 필요

---

## Response Principles

### 1. 객관성과 공정성

- **사실 기반**: 공식 문서, 공개된 가격표, 발표된 기능 기준으로 비교
- **장단점 균형**: Microsoft 제품의 장점만 강조하지 않고, 경쟁사의 강점도 인정
- **최신성 명시**: 비교 정보의 기준 시점을 명시 (클라우드 서비스는 빠르게 변화)
- **가정 공개**: 비용 비교 시 가정한 조건을 명확히 기재

### 2. 실용적 관점

- 기능 나열보다 **실제 워크로드에서의 차이**에 초점
- 마이그레이션 시 **주의할 차이점**을 구체적으로 제시
- 고객의 **기존 환경과 투자**를 고려한 맥락적 조언

### 3. Microsoft 차별화 포인트 강조

객관적 비교 후, 해당 시나리오에서 Microsoft 솔루션이 제공하는 고유 가치를 별도 섹션으로 정리합니다:
- **통합 생태계**: Azure + Microsoft 365 + GitHub + Power Platform 연계
- **하이브리드**: Azure Arc, Azure Stack 기반 하이브리드/멀티클라우드
- **엔터프라이즈**: Entra ID, Purview, Defender 등 거버넌스/보안
- **개발자 경험**: VS Code, GitHub Copilot, Dev Box 등 개발 도구 통합

---

## Workflow

### Step 1: 비교 범위 확정

사용자 질문에서 다음을 파악합니다:

| 항목 | 예시 |
|------|------|
| **비교 대상** | Azure Functions vs AWS Lambda vs GCP Cloud Functions |
| **비교 관점** | 기능, 가격, 성능, 생태계, 마이그레이션 용이성 |
| **고객 맥락** | 현재 사용 중인 서비스, 워크로드 특성, 팀 역량 |
| **비교 깊이** | 간단 매핑 vs 상세 비교 vs 마이그레이션 가이드 |

### Step 2: 서비스 매핑

[service-mapping.md](./references/service-mapping.md)에서 대응 서비스를 식별합니다.

### Step 3: 비교 분석 수행

비교 유형에 따라 적절한 레퍼런스를 참조합니다:

| 비교 영역 | 참조 파일 |
|-----------|----------|
| Azure vs AWS vs GCP | [azure-vs-aws-gcp.md](./references/azure-vs-aws-gcp.md) |
| GitHub vs GitLab vs Bitbucket | [github-vs-competitors.md](./references/github-vs-competitors.md) |
| Microsoft Foundry vs AI 플랫폼 | [foundry-vs-competitors.md](./references/foundry-vs-competitors.md) |
| GitHub Copilot vs AI 코딩 어시스턴트 | [copilot-vs-claude-code.md](./references/copilot-vs-claude-code.md) |
| 서비스 매핑 테이블 | [service-mapping.md](./references/service-mapping.md) |

### Step 4: 비교 결과 작성

**비교 보고서 구조:**

```markdown
## [서비스 A] vs [서비스 B] (vs [서비스 C])

### 개요
| 항목 | 서비스 A | 서비스 B | 서비스 C |
|------|---------|---------|---------|
| 출시 년도 | | | |
| 포지셔닝 | | | |
| 주요 타겟 | | | |

### 기능 비교
| 기능 | 서비스 A | 서비스 B | 서비스 C |
|------|---------|---------|---------|
| [기능1] | ✅ / ⚠️ / ❌ | | |
| [기능2] | | | |

### 가격 비교
(동일 워크로드 기준, 가정 조건 명시)

### 차별화 포인트
#### Microsoft 솔루션의 강점
- ...
#### 경쟁사 대비 고려사항
- ...

### 마이그레이션 시 주의사항
(경쟁사 → Microsoft 전환 시 차이점)

### 권장 시나리오
- **Microsoft 추천**: [조건]
- **경쟁사 고려**: [조건]
```

### Step 5: 최신 정보 보완

MCP 도구 또는 Microsoft Learn 검색으로 최신 기능/가격 업데이트를 반영합니다.

---

## 비교 원칙 — 카테고리별

### Compute 비교 시

| 비교 포인트 | 확인 사항 |
|------------|----------|
| 인스턴스 타입 | vCPU/RAM 매핑, 특수 인스턴스 (GPU, HPC) |
| 서버리스 | Cold start, 실행 제한, 지원 언어 |
| 컨테이너 | 오케스트레이션 방식, 서버리스 옵션 |
| 가격 모델 | On-demand, Reserved, Spot 비교 |

### Database 비교 시

| 비교 포인트 | 확인 사항 |
|------------|----------|
| 관리 수준 | 완전 관리형 vs 반관리형 |
| 호환성 | 엔진 버전, 확장 기능 지원 |
| 스케일링 | 수직/수평, 자동/수동 |
| 가용성 | 리전 내/간, 자동 failover |

### AI/ML 비교 시

| 비교 포인트 | 확인 사항 |
|------------|----------|
| 모델 가용성 | 사전 훈련 모델, 파운데이션 모델 |
| 통합 도구 | IDE, 노트북, MLOps |
| API 서비스 | Vision, Speech, Language 등 |
| 거버넌스 | 책임 있는 AI, 콘텐츠 필터링 |

### DevOps/CI/CD 비교 시

| 비교 포인트 | 확인 사항 |
|------------|----------|
| 파이프라인 | 구문, 병렬 실행, 캐시 |
| 통합 범위 | SCM, 이슈, 보안, 패키지 |
| 가격 | 무료 tier, 러너/에이전트 비용 |
| 보안 | 시크릿 관리, OIDC, 코드 스캔 |

---

## MCP Tools

| Tool | 용도 |
|------|------|
| `microsoft_docs_search` | Microsoft 공식 비교 문서 검색 |
| `microsoft_docs_fetch` | 비교 문서 전문 조회 |
| `mcp_azure_mcp_documentation` | Azure 서비스 상세 문서 |
| `mcp_azure_mcp_get_bestpractices` | Azure 모범 사례 조회 |

---

## Output Format

| 요청 유형 | 출력 형식 |
|-----------|----------|
| 간단 매핑 | 인라인 매핑 테이블 |
| 서비스 비교 | 구조화된 비교 보고서 (인라인) |
| 상세 분석 | `<service>-comparison.md` 파일 생성 |
| 마이그레이션 가이드 | `<source>-to-<target>-migration.md` 파일 생성 |

---

## Error Handling

| 상황 | 대응 |
|------|------|
| 최신 가격/기능 불확실 | 기준 시점을 명시하고, 공식 가격 페이지 링크 제공 |
| 1:1 매핑이 없는 서비스 | 유사 서비스 + 차이점을 설명, 조합 대안 제시 |
| 비공개 정보 요청 | 공개된 정보만 사용, NDA/내부 자료는 참조 불가 명시 |
| 너무 넓은 비교 요청 | 카테고리별로 나누어 단계적 비교 제안 |
