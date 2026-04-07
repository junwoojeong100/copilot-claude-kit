# 테스트 #10: refactor.prompt.md — 리팩토링

## 대상 파일
`.github/prompts/refactor.prompt.md`

## 사용법
📎 → Prompt → **refactor** 선택 후 아래 입력

## 프롬프트

```python
def process(data):
    result = []
    for item in data:
        if item['type'] == 'A':
            if item['status'] == 'active':
                if item['score'] > 80:
                    result.append({'name': item['name'], 'grade': 'excellent'})
                elif item['score'] > 50:
                    result.append({'name': item['name'], 'grade': 'good'})
                else:
                    result.append({'name': item['name'], 'grade': 'poor'})
    return result
```

현재 문제점: 중첩 if가 너무 깊고 가독성이 떨어짐
개선 목표: 가독성 향상, 테스트 용이성
유지해야 할 것: 기존 동작, 입출력 형식

## 검증 포인트

- [ ] **기존 동작 유지**: 리팩토링 후에도 동일한 입력에 동일한 출력을 보장하는가
- [ ] **변경 전후 차이 설명**: 무엇이 어떻게 바뀌었는지 명확히 설명하는가
- [ ] **변경 근거 제시**: 왜 그 변경이 필요한지 근거를 제시하는가
- [ ] **중첩 감소**: early return, guard clause, 함수 분리 등으로 중첩을 줄이는가
- [ ] **가독성 향상**: 리팩토링된 코드가 실제로 더 읽기 쉬운가
- [ ] **테스트 용이성**: 분리된 로직이 개별 테스트가 가능한 구조인가
- [ ] **과도한 추상화 없음**: 한 번만 쓰이는 로직에 불필요한 클래스/패턴을 만들지 않는가
