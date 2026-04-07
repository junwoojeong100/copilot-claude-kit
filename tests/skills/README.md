# Skills 테스트 프롬프트

`.github/skills/` 아래의 6개 스킬이 올바르게 활성화되고 동작하는지 검증하기 위한 테스트 프롬프트입니다.

## 테스트 목록

| # | 대상 스킬 | 테스트 | 핵심 검증 |
|---|----------|--------|----------|
| 11 | `fact-check` | [팩트체크 테스트](11-fact-check.md) | 🔍 팩트체크 표 존재, 검증 결과 |
| 12 | `google-web-search` | [웹 검색 테스트](12-google-web-search.md) | 최신 정보, 출처 섹션 |
| 13 | `cloud-competitive-analysis` | [경쟁 분석 테스트](13-cloud-competitive-analysis.md) | 객관적 비교, 차별화 포인트 |
| 14 | `azure-architecture-review` | [Azure 아키텍처 리뷰 테스트](14-azure-architecture-review.md) | WAF 5 Pillar, 다이어그램 |
| 15 | `azure-support-guide` | [Azure 지원 가이드 테스트](15-azure-support-guide.md) | 공감, 단계별 안내 |
| 16 | `foundry-agent-project` | [Foundry 에이전트 프로젝트 테스트](16-foundry-agent-project.md) | 커스텀 구조, SDK 사용 |

## 활성화 방법

스킬은 두 가지 방법으로 활성화됩니다:
1. **슬래시 명령**: `/스킬이름 질문` 형태로 직접 호출
2. **자연어**: 스킬의 `description`에 포함된 키워드로 질문 시 자동 활성화
