# GitHub vs Competitors — DevOps 플랫폼 비교

---

## 1. 전체 플랫폼 비교

| 항목 | GitHub | GitLab | Bitbucket | Azure DevOps |
|------|--------|--------|-----------|-------------|
| **포지셔닝** | AI-powered 개발자 플랫폼 | 올인원 DevSecOps 플랫폼 | Atlassian 생태계 통합 | 엔터프라이즈 DevOps |
| **소유** | Microsoft | 독립 (상장) | Atlassian | Microsoft |
| **호스팅** | SaaS + GHES | SaaS + Self-managed | SaaS + Data Center | SaaS + Server |
| **핵심 강점** | Copilot, 커뮤니티, Actions | 단일 플랫폼 통합 | Jira 연동 | 엔터프라이즈 거버넌스 |
| **오픈소스 생태계** | ✅ 최대 (100M+ repos) | ⚠️ 중간 | ⚠️ 소규모 | ❌ |

---

## 2. Source Control (Git)

| 기능 | GitHub | GitLab | Bitbucket |
|------|--------|--------|-----------|
| 무료 프라이빗 리포 | ✅ 무제한 | ✅ 무제한 | ✅ (5 사용자 무료) |
| 대규모 파일 (LFS) | ✅ | ✅ | ✅ |
| 코드 리뷰 | PR + Copilot 리뷰 | MR + AI 리뷰 | PR |
| 브랜치 보호 | ✅ Rulesets | ✅ Protected branches | ✅ Branch permissions |
| 코드 소유자 | ✅ CODEOWNERS | ✅ Code Owners | ❌ |
| 머지 큐 | ✅ Merge Queue | ✅ Merge Trains | ❌ |
| 모노레포 지원 | ⚠️ 개선 중 | ⚠️ | ⚠️ |

**GitHub 차별화**: 세계 최대 오픈소스 커뮤니티 + Copilot 코드 리뷰로 PR 품질 자동 향상

---

## 3. CI/CD

| 기능 | GitHub Actions | GitLab CI/CD | Bitbucket Pipelines | Azure Pipelines |
|------|---------------|-------------|--------------------|-----------------| 
| 구성 파일 | YAML (.github/workflows/) | YAML (.gitlab-ci.yml) | YAML (bitbucket-pipelines.yml) | YAML (azure-pipelines.yml) |
| 마켓플레이스 | ✅ 20,000+ Actions | ⚠️ CI/CD Components | ⚠️ Pipes | ⚠️ Tasks |
| 무료 tier | 2,000분/월 (퍼블릭 무제한) | 400분/월 | 50분/월 | 1,800분/월 (퍼블릭 무제한) |
| Self-hosted 러너 | ✅ 무료 | ✅ 무료 | ❌ | ✅ 무료 |
| 매트릭스 빌드 | ✅ | ✅ | ⚠️ 제한적 | ✅ |
| 재사용 워크플로우 | ✅ Reusable Workflows | ✅ Include/Extends | ⚠️ | ✅ Templates |
| OIDC 지원 | ✅ (Azure, AWS, GCP) | ✅ | ⚠️ | ✅ |
| GPU 러너 | ✅ (GitHub-hosted) | ⚠️ Self-hosted만 | ❌ | ⚠️ Self-hosted만 |

**GitHub 차별화**: 20,000+ 마켓플레이스 Actions 생태계 + 퍼블릭 리포 무제한 무료 + Copilot Workspace에서 Actions 자동 생성

---

## 4. Security (DevSecOps)

| 기능 | GitHub Advanced Security | GitLab Ultimate | Bitbucket |
|------|------------------------|----------------|-----------|
| 코드 스캐닝 (SAST) | ✅ CodeQL (시맨틱 분석) | ✅ SAST | ⚠️ 서드파티 연동 |
| 시크릿 스캐닝 | ✅ 200+ 패턴, Push Protection | ✅ Secret Detection | ⚠️ 제한적 |
| 의존성 스캐닝 | ✅ Dependabot (자동 PR) | ✅ Dependency Scanning | ⚠️ Snyk 연동 |
| 컨테이너 스캐닝 | ✅ | ✅ | ⚠️ |
| 라이선스 컴플라이언스 | ⚠️ 제한적 | ✅ | ❌ |
| SBOM | ✅ 내보내기 지원 | ✅ | ❌ |
| 보안 개요 대시보드 | ✅ Security Overview | ✅ Security Dashboard | ❌ |
| Copilot 자동 수정 | ✅ Copilot Autofix | ❌ | ❌ |
| AI 기반 취약점 설명 | ✅ | ⚠️ AI Explain | ❌ |

**GitHub 차별화**: CodeQL의 시맨틱 코드 분석은 업계 최고 수준. Copilot Autofix로 보안 취약점 자동 수정 PR 생성.

---

## 5. AI & Copilot

| 기능 | GitHub Copilot | GitLab Duo | Bitbucket |
|------|---------------|-----------|-----------|
| 코드 자동 완성 | ✅ (IDE 네이티브) | ✅ Code Suggestions | ❌ |
| 채팅 어시스턴트 | ✅ Copilot Chat (IDE + Web) | ✅ Duo Chat | ❌ |
| PR 요약 | ✅ Copilot PR Summary | ✅ MR Summary | ❌ |
| 코드 리뷰 | ✅ Copilot Code Review | ✅ Duo Code Review | ❌ |
| 보안 자동 수정 | ✅ Copilot Autofix | ❌ | ❌ |
| CLI 어시스턴트 | ✅ Copilot CLI | ❌ | ❌ |
| IDE 지원 | VS Code, JetBrains, Neovim, Xcode | VS Code, JetBrains, Web IDE | ❌ |
| 에이전트 모드 | ✅ Copilot Agent (멀티-스텝 작업) | ⚠️ 프리뷰 | ❌ |
| 커스텀 모델/지식 | ✅ Copilot Extensions, Knowledge Bases | ⚠️ 제한적 | ❌ |
| Workspace | ✅ Copilot Workspace (이슈→PR 자동화) | ❌ | ❌ |

**GitHub 차별화**: 개발 전 주기를 커버하는 AI 어시스턴트. 코드 완성 → 리뷰 → 보안 → 문서화 → 배포까지 Copilot 통합.

---

## 6. Project Management

| 기능 | GitHub | GitLab | Bitbucket (+ Jira) |
|------|--------|--------|-------------------|
| 이슈 트래킹 | ✅ Issues + Projects | ✅ Issues + Boards | ✅ Jira (별도 제품) |
| 프로젝트 보드 | ✅ Projects (v2, 테이블/보드/로드맵) | ✅ Issue Boards | ✅ Jira Boards |
| 로드맵 | ✅ Project Roadmap | ✅ Roadmap | ✅ Jira Plans |
| 마일스톤 | ✅ | ✅ | ✅ (Jira Versions) |
| 시간 추적 | ❌ | ✅ | ✅ (Jira) |
| 에픽 | ⚠️ 레이블/타입으로 대체 | ✅ Epics | ✅ (Jira Epics) |

---

## 7. Packages & Registry

| 기능 | GitHub Packages | GitLab Packages | Bitbucket |
|------|----------------|----------------|-----------|
| 컨테이너 레지스트리 | ✅ ghcr.io | ✅ 내장 | ❌ |
| npm | ✅ | ✅ | ❌ |
| Maven | ✅ | ✅ | ❌ |
| NuGet | ✅ | ✅ | ❌ |
| PyPI | ✅ | ✅ | ❌ |
| 무료 용량 | 500MB (무료), 2GB (Pro) | 5GB | ❌ |

---

## 8. Pricing Comparison

### 사용자당 월 비용 (2024 기준)

| Tier | GitHub | GitLab | Bitbucket |
|------|--------|--------|-----------|
| 무료 | $0 (무제한 퍼블릭/프라이빗) | $0 (5 사용자) | $0 (5 사용자) |
| 기본 유료 | $4/user (Team) | $29/user (Premium) | $3/user (Standard) |
| 엔터프라이즈 | $21/user (Enterprise) | $99/user (Ultimate) | $6/user (Premium) |

### Copilot 추가 비용

| Tier | 비용 | 포함 기능 |
|------|------|----------|
| Copilot Free | $0 | 월 2,000 자동완성, 50 채팅 |
| Copilot Pro | $10/월 | 무제한 자동완성/채팅 |
| Copilot Business | $19/user/월 | 조직 관리, 정책 제어 |
| Copilot Enterprise | $39/user/월 | Knowledge Bases, Bing 검색 |

**GitHub 차별화**: GitLab Ultimate ($99/user) 대비 GitHub Enterprise + Copilot Business ($21 + $19 = $40/user)로 AI 기능 포함 시에도 경쟁력 있는 가격.

---

## 9. GitHub vs Azure DevOps — Microsoft 내부 비교

고객이 GitHub과 Azure DevOps 중 선택을 고민할 때:

| 기준 | GitHub 추천 | Azure DevOps 추천 |
|------|------------|------------------|
| 팀 특성 | 개발자 중심, 오픈소스 문화 | PM/운영 포함 대규모 팀 |
| AI 도구 | Copilot 전 기능 필요 | AI는 부수적 |
| 이슈 관리 | 가벼운 프로젝트 관리 | 복잡한 백로그, 스프린트 관리 |
| 패키지 관리 | GitHub Packages 충분 | Azure Artifacts (NuGet/npm/Maven) |
| 테스트 관리 | 서드파티 연동 | ✅ Test Plans 내장 |
| 위키 | GitHub Wiki, Discussions | ✅ Azure Wiki (계층형) |
| 보안 스캐닝 | ✅ GHAS (CodeQL, Dependabot) | 서드파티 또는 GHAS 연동 |
| 마이그레이션 방향 | **Microsoft 전략적 방향** | 레거시 유지보수 |

> **Microsoft의 전략적 방향**: GitHub이 Microsoft의 주력 개발자 플랫폼. 신규 프로젝트는 GitHub 권장.

---

## 10. 통합 생태계 강점

```
GitHub + Microsoft Ecosystem
├── VS Code + Copilot (최고의 개발 경험)
├── Azure (클라우드 배포 대상)
│   ├── GitHub Actions → Azure 원클릭 배포
│   ├── OIDC 페더레이션 (시크릿 없는 배포)
│   └── Azure Developer CLI (azd) 연동
├── Microsoft 365 (협업)
│   ├── Teams + GitHub 통합
│   └── Copilot (M365) ↔ Copilot (GitHub)
├── Entra ID (통합 인증)
│   └── GitHub EMU (Enterprise Managed Users)
└── Microsoft Defender for DevOps (보안)
    └── GitHub + Azure DevOps 통합 CSPM
```
