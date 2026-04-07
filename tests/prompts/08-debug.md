# 테스트 #8: debug.prompt.md — 디버깅

## 대상 파일
`.github/prompts/debug.prompt.md`

## 사용법
📎 → Prompt → **debug** 선택 후 아래 입력

## 프롬프트

```
증상: API 호출 시 간헐적으로 ConnectionResetError 발생
기대 동작: 안정적인 API 응답
실제 동작: 10번 중 2~3번 연결 끊김
에러 메시지: ConnectionResetError: [Errno 104] Connection reset by peer
환경: Python 3.11, FastAPI, uvicorn, Docker container
```

## 검증 포인트

- [ ] **증상 파악**: 에러 메시지와 재현 패턴(간헐적, 10번 중 2~3번)을 정확히 이해하는가
- [ ] **가설 수립**: 여러 가능한 원인을 가설로 제시하는가 (예: 커넥션 풀, 타임아웃, 프록시 등)
- [ ] **검증 방법**: 각 가설을 확인할 수 있는 구체적 방법을 안내하는가
- [ ] **근본 원인 지향**: 표면적 증상이 아닌 근본 원인을 찾으려 하는가
- [ ] **즉시 수정**: 바로 적용할 수 있는 해결 방안을 제공하는가
- [ ] **재발 방지**: 장기적으로 같은 문제를 예방하는 방안도 제시하는가
- [ ] **환경 고려**: Docker 컨테이너 환경 특수성을 고려하는가
