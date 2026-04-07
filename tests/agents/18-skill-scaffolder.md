# 테스트 #18: skill-scaffolder — 스킬 생성기

## 대상 에이전트
`.github/agents/skill-scaffolder.agent.md`

## 사용법
에이전트 선택기 → **skill-scaffolder** 선택 후 아래 입력

## 프롬프트

```
"api-documentation"이라는 새 스킬을 만들어줘.
REST API 문서를 자동으로 생성해주는 스킬이야.
OpenAPI spec을 읽어서 마크다운 문서로 변환하는 기능이 필요해.
```

## 검증 포인트

- [ ] **요구사항 인터뷰**: 스킬 이름, 용도, 트리거 키워드, 참조 자료 필요 여부를 확인하는가
- [ ] **기존 스킬 패턴 분석**: `.github/skills/` 아래 기존 스킬의 구조를 참고하는가
- [ ] **올바른 경로**: `.github/skills/api-documentation/` 경로에 파일을 생성하는가
- [ ] **SKILL.md 생성**: 프론트매터(`name`, `description`, `argument-hint`)를 포함한 SKILL.md를 생성하는가
- [ ] **표준 구조**: `When to Use`, `Workflow`, `Output Format` 등 표준 섹션이 포함되는가
- [ ] **기존 파일 미수정**: 기존 스킬 파일을 변경하지 않는가
- [ ] **references/ 디렉토리**: 참조 자료가 필요한 경우 `references/` 디렉토리를 함께 생성하는가
- [ ] **instruction-reviewer 연동**: 생성 후 품질 점검을 instruction-reviewer에 위임하는가
