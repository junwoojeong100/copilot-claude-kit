# 테스트 #7: code-review.prompt.md — 코드 리뷰

## 대상 파일
`.github/prompts/code-review.prompt.md`

## 사용법
📎 → Prompt → **code-review** 선택 후 아래 입력

## 프롬프트

```python
def get_user(request):
    user_id = request.GET.get('id')
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    password = result[0]['password']
    return JsonResponse({'user': result[0], 'token': generate_token(password)})
```

## 검증 포인트

- [ ] **좋은 점 먼저**: 잘 작성된 부분(예: 함수 분리 등)을 먼저 인정하는가
- [ ] **SQL 인젝션 지적**: f-string을 이용한 쿼리 생성의 위험을 지적하는가
- [ ] **민감 데이터 노출**: 비밀번호를 응답에 포함하지 않도록 지적하는가
- [ ] **"~하면 더 좋겠습니다" 형식**: 개선점을 제안 형식으로 전달하는가
- [ ] **수정된 코드 예시**: 지적사항을 반영한 수정 코드를 함께 제공하는가
- [ ] **이유 설명**: 각 개선점에 대해 왜 그 변경이 필요한지 근거를 제시하는가
- [ ] **보안 관점**: 인증·인가, 입력 검증 등 보안 관점의 리뷰가 포함되는가
