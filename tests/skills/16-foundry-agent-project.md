# 테스트 #16: foundry-agent-project — Foundry 에이전트 프로젝트

## 대상 스킬
`.github/skills/foundry-agent-project/SKILL.md`

## 프롬프트

```
Microsoft Foundry로 고객 문의를 자동 응답하는 에이전트를 만들고 싶어.
Azure AI Search와 Code Interpreter를 도구로 쓰고, 단일 에이전트로 시작할 거야.
프로젝트를 처음부터 세팅해줘.
```

## 검증 포인트

- [ ] **요구사항 인터뷰**: 에이전트 목적, 도구, 데이터 소스, 워크플로우 패턴 등을 확인하는가
- [ ] **커스텀 구조 설계**: 공식 샘플이 아닌 요구사항 맞춤 프로젝트 구조를 설계하는가
- [ ] **pyproject.toml 포함**: 패키지 정의와 의존성을 포함한 설정 파일이 있는가
- [ ] **Dockerfile 포함**: 컨테이너 빌드를 위한 Dockerfile을 제공하는가
- [ ] **Agent Framework SDK**: Microsoft Agent Framework Python SDK를 사용하는가
- [ ] **도구 통합**: Azure AI Search와 Code Interpreter 도구 설정이 포함되는가
- [ ] **프로젝트 디렉토리 구조**: 체계적인 디렉토리 구조를 제시하는가
- [ ] **실행 방법 안내**: 로컬에서 실행하고 테스트하는 방법을 안내하는가
