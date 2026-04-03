---
applyTo: "**/*.{py,js,ts,jsx,tsx,java,cs,go,rs,rb,php,swift,kt,c,cpp,h,hpp,sh,bash,zsh,yaml,yml,json,toml,sql}"
description: "코드 품질, 보안, 스타일 관련 코딩 지침. 모든 코드 파일에 적용됩니다."
---

# 코딩 관련 지침

## 코드 품질 원칙

### 1. 가독성 우선 (Readability First)
- 영리한 코드보다 **읽기 쉬운 코드**를 작성합니다.
- 의미 있는 변수명과 함수명을 사용합니다.
- 자기 문서화(self-documenting) 코드를 지향합니다.

### 2. 점진적 복잡성 (Progressive Complexity)
- 가장 단순한 해결책부터 시작합니다.
- 필요할 때만 복잡성을 추가합니다.
- YAGNI (You Aren't Gonna Need It) 원칙을 따릅니다.

### 3. 실용주의 (Pragmatism)
- 완벽보다 **작동하는 코드**를 먼저 목표로 합니다.
- 이론적 우아함보다 실제 유지보수성을 중시합니다.
- 팀과 프로젝트의 기존 컨벤션을 존중합니다.

## 코드 제공 방식

### 완전한 코드 제공
- 실행 가능한 완전한 코드를 제공합니다.
- 필요한 import/require 문을 포함합니다.
- 생략 없이 전체 코드를 보여줍니다.

### 코드 설명
```python
# ✅ 좋은 예: 핵심 로직에만 주석
def calculate_discount(price: float, tier: str) -> float:
    """고객 등급별 할인 금액을 계산합니다."""
    discount_rates = {
        "gold": 0.2,
        "silver": 0.1,
        "bronze": 0.05,
    }
    rate = discount_rates.get(tier, 0)
    return price * rate
```

```python
# ❌ 나쁜 예: 과도한 주석
def calculate_discount(price: float, tier: str) -> float:
    # 할인율을 저장할 딕셔너리를 생성합니다
    discount_rates = {
        "gold": 0.2,      # 골드 등급은 20% 할인
        "silver": 0.1,     # 실버는 10%
        "bronze": 0.05,    # 브론즈는 5%
    }
    # 등급에 해당하는 할인율을 가져옵니다
    rate = discount_rates.get(tier, 0)  # 없으면 0
    # 가격에 할인율을 곱하여 반환합니다
    return price * rate  # 할인 금액 반환
```

## 언어별 베스트 프랙티스

### Python
- Type hints를 활용합니다.
- f-string을 사용합니다.
- 컨텍스트 매니저(`with`)를 활용합니다.
- PEP 8 스타일을 따릅니다.
- `pathlib`를 `os.path`보다 선호합니다.

### TypeScript / JavaScript
- TypeScript를 JavaScript보다 선호합니다.
- `const`를 기본으로, 필요할 때만 `let`을 사용합니다.
- `any` 타입 사용을 최소화합니다.
- 옵셔널 체이닝(`?.`)과 널 병합 연산자(`??`)를 활용합니다.
- `async/await`를 `.then()` 체인보다 선호합니다.

### 범용 원칙
- DRY (Don't Repeat Yourself) — 단, 과도한 추상화는 지양
- SOLID 원칙을 상황에 맞게 적용
- 에러 핸들링은 시스템 경계에서 수행
- 불변성(immutability)을 기본으로

## 보안 관련 코딩

### 반드시 지키는 것
- 사용자 입력은 항상 검증/새니타이즈합니다.
- SQL 쿼리에는 파라미터 바인딩을 사용합니다.
- 시크릿/인증 정보를 코드에 하드코딩하지 않습니다.
- HTTPS를 기본으로 사용합니다.
- OWASP Top 10 취약점을 인지하고 방어합니다.

### 보안 코드 예시
```python
# ✅ 파라미터 바인딩
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ SQL 인젝션 취약
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

## 테스트 코드

### 테스트 작성 원칙
- 테스트는 **독립적**이고 **반복 가능**해야 합니다.
- 테스트명은 **무엇을 검증하는지** 명확히 표현합니다.
