# 지침 테스트 프롬프트

이 디렉토리는 `.github/` 아래의 모든 커스터마이징 파일(instructions, prompts, skills, agents, 글로벌 규칙)이 올바르게 동작하는지 검증하기 위한 **테스트 프롬프트 모음**입니다.

## 구조

```
tests/
├── README.md                          # 이 파일
├── instructions/                      # Instructions 테스트 (#1~#5)
│   ├── README.md
│   ├── 01-coding.md
│   ├── 02-communication.md
│   ├── 03-persona.md
│   ├── 04-safety.md
│   └── 05-thinking.md
├── prompts/                           # Prompts 테스트 (#6~#10)
│   ├── README.md
│   ├── 06-architecture.md
│   ├── 07-code-review.md
│   ├── 08-debug.md
│   ├── 09-explain.md
│   └── 10-refactor.md
├── skills/                            # Skills 테스트 (#11~#16)
│   ├── README.md
│   ├── 11-fact-check.md
│   ├── 12-google-web-search.md
│   ├── 13-cloud-competitive-analysis.md
│   ├── 14-azure-architecture-review.md
│   ├── 15-azure-support-guide.md
│   └── 16-foundry-agent-project.md
├── agents/                            # Agents 테스트 (#17~#18)
│   ├── README.md
│   ├── 17-instruction-reviewer.md
│   └── 18-skill-scaffolder.md
└── global-rules/                      # 글로벌 규칙 테스트 (#19~#20)
    ├── README.md
    ├── 19-fact-check-rule.md
    └── 20-source-citation-rule.md
```

## 전체 테스트 요약

| # | 카테고리 | 대상 | 프롬프트 요약 |
|---|---------|------|-------------|
| 1 | Instructions | `coding` | Python DB 검색 + 할인 계산 함수 |
| 2 | Instructions | `communication` | useEffect vs useLayoutEffect 설명 |
| 3 | Instructions | `persona` | AI 정체성, 감정, 인간 비교 |
| 4 | Instructions | `safety` | 로그인 우회 + 평문 비밀번호 저장 |
| 5 | Instructions | `thinking` | Node.js 서비스 응답 시간 10배 저하 |
| 6 | Prompts | `architecture` | 실시간 채팅 서비스 설계 |
| 7 | Prompts | `code-review` | SQL 인젝션 취약 코드 리뷰 |
| 8 | Prompts | `debug` | 간헐적 ConnectionResetError |
| 9 | Prompts | `explain` | Event-Driven Architecture 초보 설명 |
| 10 | Prompts | `refactor` | 깊은 중첩 if문 리팩토링 |
| 11 | Skills | `fact-check` | Python 3.12 변경사항 |
| 12 | Skills | `google-web-search` | GitHub Copilot 최신 업데이트 |
| 13 | Skills | `cloud-competitive-analysis` | Container Apps vs Fargate vs Cloud Run |
| 14 | Skills | `azure-architecture-review` | 이커머스 WAF 리뷰 |
| 15 | Skills | `azure-support-guide` | App Service 502 에러 해결 |
| 16 | Skills | `foundry-agent-project` | Foundry 에이전트 프로젝트 생성 |
| 17 | Agents | `instruction-reviewer` | 전체 커스터마이징 파일 점검 |
| 18 | Agents | `skill-scaffolder` | api-documentation 스킬 생성 |
| 19 | Global Rules | 팩트체크 | Kubernetes vs Docker Swarm 비교 |
| 20 | Global Rules | 출처 표시 | Azure Functions Flex Consumption |

## 사용 방법

1. 각 카테고리 폴더의 테스트 파일을 엽니다.
2. **프롬프트** 섹션의 내용을 Copilot Chat에 입력합니다.
3. 응답을 받은 후 **검증 포인트** 체크리스트로 지침 적용 여부를 확인합니다.
4. 모든 체크박스가 충족되면 해당 지침이 정상 동작하는 것입니다.

## 카테고리별 통계

| 카테고리 | 파일 수 | 테스트 수 |
|---------|--------|----------|
| Instructions | 5 | #1 ~ #5 |
| Prompts | 5 | #6 ~ #10 |
| Skills | 6 | #11 ~ #16 |
| Agents | 2 | #17 ~ #18 |
| Global Rules | 2 | #19 ~ #20 |
| **합계** | **20** | **20** |
