---
name: google-web-search
description: "최신 정보가 필요할 때 Google 웹 검색을 수행하여 실시간 정보를 수집하고 요약합니다. 학습 데이터 이후의 최신 뉴스, 기술 업데이트, 릴리스 정보, 가격 변경, 이벤트 등을 검색합니다. WHEN: 최신 정보 검색, 실시간 검색, Google 검색, 최신 뉴스, 최근 업데이트, 릴리스 노트, 최신 버전, 현재 가격, 현재 상태, latest news, recent updates, current price, what's new, release notes, changelog, web search, search the web, look up online, 오늘 날짜 기준 정보, 2024년 이후 정보, 최신 트렌드, 기술 동향, 최근 발표, 공식 발표, 최신 문서."
argument-hint: "검색하고 싶은 주제나 질문을 입력하세요"
---

# Google 웹 검색 스킬

AI 모델의 학습 데이터 컷오프 이후의 **최신 정보**가 필요할 때, 웹 검색을 통해 실시간 정보를 수집하고 정리합니다.

## When to Use

- **최신 버전/릴리스 확인**: 라이브러리, 프레임워크, 서비스의 최신 버전 정보
- **최근 뉴스/발표**: 기술 업데이트, 서비스 변경, 정책 변경 등
- **현재 가격/요금**: 클라우드 서비스, API 요금 등 실시간 가격 정보
- **최신 문서/가이드**: 공식 문서의 최신 내용 확인
- **트렌드/동향**: 최신 기술 트렌드, 시장 동향
- **이벤트/컨퍼런스**: 예정된 또는 최근 이벤트 정보
- **버그/이슈 상태**: 특정 이슈의 현재 상태 확인

## Workflow

### Step 1: 검색 쿼리 구성

사용자의 질문을 분석하여 효과적인 검색 쿼리를 구성합니다.

**쿼리 구성 원칙:**
- 핵심 키워드를 영어로 변환 (영어 결과가 더 풍부)
- 연도/날짜를 포함하여 최신 결과 유도 (예: "2025", "2026")
- 구체적인 기술 용어 사용
- 불필요한 조사/접속사 제거

**도메인 정책:**

검색 결과의 신뢰성을 보장하기 위해, **신뢰 도메인 우선 정책**을 적용합니다.

**1차 신뢰 도메인 (기본 사용):**

| 도메인 | 포함 범위 |
|----------|----------|
| `microsoft.com` | Microsoft Learn, DevBlogs, Azure 문서 등 모든 서브도메인 |
| `github.com` | GitHub Blog, Docs, 릴리스 페이지, Discussions |
| `google.com` | Google 개발자 블로그, Google Cloud 문서 |
| `youtube.com` | 공식 채널 영상, 데모, 튜토리얼 |

**2차 신뢰 도메인 (기술 공식 소스):**

| 도메인 | 용도 |
|----------|------|
| `python.org`, `pypi.org` | Python 공식 문서, 패키지 정보 |
| `nodejs.org`, `npmjs.com` | Node.js, npm 패키지 정보 |
| `kubernetes.io` | Kubernetes 공식 문서 |
| `react.dev`, `angular.dev`, `vuejs.org` | 프론트엔드 프레임워크 공식 문서 |
| `rust-lang.org`, `go.dev`, `typescriptlang.org` | 언어 공식 문서 |
| `docker.com` | Docker 공식 문서 |
| `terraform.io` | Terraform 공식 문서 |
| `stackoverflow.com` | 기술 Q&A |
| `dev.to`, `medium.com` | 기술 블로그 (교차 검증 필수) |

**사용자 지정 도메인:** 사용자가 특정 도메인을 명시적으로 요청하면 해당 도메인도 검색합니다.

**금지 도메인:** 신뢰할 수 없는 소스, 알 수 없는 개인 블로그, SEO 스팸 사이트 등에서는 정보를 가져오지 않습니다.

**검색 쿼리 예시:**

| 사용자 질문 | 최적화된 쿼리 |
|------------|-------------|
| "React 최신 버전이 뭐야?" | `React latest version 2026 site:react.dev OR site:github.com/facebook/react` |
| "Azure Functions 요금 변경됐어?" | `Azure Functions pricing changes 2026 site:microsoft.com` |
| "Python 3.13 새 기능" | `Python 3.13 new features changelog site:python.org OR site:github.com` |
| "Kubernetes 최신 동향" | `Kubernetes latest trends 2026 site:kubernetes.io OR site:github.com` |

### Step 2: 웹 검색 수행

`fetch_webpage` 도구를 사용하여 검색을 수행합니다.

> **⚠️ `fetch_webpage` 도구를 사용할 수 없는 경우**: MCP 도구(`mcp_microsoft_pla_browser_navigate` 등)나 `run_in_terminal`의 `curl` 명령으로 대체합니다. 어떤 웹 접근 도구도 사용할 수 없다면, 학습 데이터 기반으로 답변하되 "실시간 검색을 수행할 수 없어 학습 데이터 기준으로 답변합니다"라고 명시합니다.

**검색 전략 (용도별):**

`google.com/search`는 봇 감지로 결과를 반환하지 않는 경우가 많으므로, 용도에 맞는 검색 엔드포인트를 사용합니다.

**뉴스/최신 정보 → Google News (가장 안정적)**
```
https://news.google.com/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en
```
- 최신 뉴스, 속보, 기술 업데이트, 릴리스 발표 등에 적합

**일반 웹 문서 → DuckDuckGo HTML (봇 감지 없음)**
```
https://html.duckduckgo.com/html/?q={encoded_query}
```
- 공식 문서, 기술 블로그, 가이드, 릴리스 노트 등 일반 웹 문서 검색에 적합
- JavaScript가 불필요한 순수 HTML 버전이라 `fetch_webpage`와 100% 호환
- 검색 결과에서 URL을 추출한 뒤, **1차·2차 신뢰 도메인의 링크만 상세 fetch**

**허용 도메인 직접 접근 (URL을 이미 알거나 추론 가능한 경우)**
검색 주제에 따라 허용 도메인의 관련 페이지를 직접 fetch합니다:
- `https://github.blog/tag/{topic}/` — GitHub 관련 뉴스
- `https://learn.microsoft.com/en-us/{path}` — Microsoft/Azure 공식 문서
- `https://devblogs.microsoft.com/{path}` — Microsoft 개발자 블로그
- `https://github.com/{owner}/{repo}/releases` — 릴리스 정보

**Google 검색 (최후의 수단)**
```
https://www.google.com/search?q={encoded_query}
```
> ⚠️ `google.com/search`가 JavaScript 챌린지 페이지를 반환하면, 재시도하지 않고 즉시 다른 방법으로 전환합니다.

**⚠️ 검색 엔진 vs 결과 소스 구분:**
- **검색 엔진** (URL 발견용): Google News, DuckDuckGo HTML, Google Search 모두 사용 가능
- **결과 소스** (상세 내용 fetch용): 반드시 1차·2차 신뢰 도메인 내 URL만 fetch (비신뢰 도메인은 fetch 금지)

**검색 실행 예시:**

```
# 뉴스/최신 정보
fetch_webpage:
- urls: ["https://news.google.com/search?q={검색어}&hl=en-US&gl=US&ceid=US:en"]
- query: "찾고자 하는 정보"

# 일반 웹 문서/기술 문서
fetch_webpage:
- urls: ["https://html.duckduckgo.com/html/?q={검색어}"]
- query: "찾고자 하는 정보"
```

### Step 3: 상세 정보 수집

검색 결과에서 유망한 링크를 식별하고, 해당 페이지의 상세 내용을 가져옵니다.

```
fetch_webpage 도구를 사용:
- urls: ["발견된 관련 URL 1", "발견된 관련 URL 2"]
- query: "찾고자 하는 구체적인 정보"
```

**소스 우선순위:**
1. **공식 프로젝트 사이트** — 해당 기술의 공식 도메인 (react.dev, python.org, kubernetes.io 등)
2. **Microsoft 공식 문서** — `learn.microsoft.com`, `devblogs.microsoft.com`
3. **GitHub 공식 블로그/릴리스** — `github.blog`, `github.com/{owner}/{repo}/releases`
4. **패키지 레지스트리** — `npmjs.com`, `pypi.org` 등
5. **YouTube 공식 채널** — 데모, 튜토리얼
6. **커뮤니티** — `stackoverflow.com`, `dev.to` (교차 검증 후 사용)

> ⚠️ 비공식 소스(dev.to, medium.com, stackoverflow.com)의 정보는 공식 문서와 교차 검증하여 정확성을 확인합니다.

### Step 4: 결과 정리 및 응답

수집된 정보를 다음 형식으로 정리합니다:

```markdown
## 검색 결과: {주제}

**검색일**: {현재 날짜}
**검색 쿼리**: `{사용된 쿼리}`

### 핵심 요약
{1-3문장으로 핵심 답변}

### 상세 내용
{구조화된 상세 정보}

### 출처
- [출처 제목 1](URL1) — {간략 설명}
- [출처 제목 2](URL2) — {간략 설명}

> ⚠️ 웹 검색 결과는 검색 시점 기준이며, 정확성을 보장하지 않습니다.
> 중요한 의사결정에는 공식 문서를 직접 확인하시기 바랍니다.
```

## 검색 전략

### 기본 검색
단일 쿼리로 빠르게 결과를 얻습니다.

### 심화 검색
하나의 주제에 대해 허용 도메인 내에서 여러 각도로 검색합니다:
1. **일반 검색**: 4개 허용 도메인 전체에서 주제 개요 파악
2. **Microsoft 공식 문서 검색**: `site:microsoft.com` 한정
3. **GitHub 소스 검색**: `site:github.com` 한정 (블로그, 문서, 릴리스)
4. **영상 콘텐츠 검색**: `site:youtube.com` 한정 (데모, 튜토리얼)

### 비교 검색
두 가지 이상의 대안을 비교할 때:
1. 각 대안별 개별 검색
2. 비교 키워드로 통합 검색 (`A vs B 2026`)
3. 벤치마크/리뷰 검색

## Google 검색 고급 연산자

유용한 검색 연산자를 활용합니다:

| 연산자 | 용도 | 예시 |
|--------|------|------|
| `site:` | 특정 사이트 내 검색 | `site:github.com kubernetes release` |
| `"exact phrase"` | 정확한 문구 검색 | `"breaking changes" React 19` |
| `after:` | 특정 날짜 이후 결과 | `Azure updates after:2025-01-01` |
| `filetype:` | 파일 유형 필터 | `kubernetes best practices filetype:pdf` |
| `-keyword` | 특정 키워드 제외 | `python web framework -django` |
| `OR` | 여러 키워드 중 하나 | `(React OR Vue) state management 2026` |

## Error Handling

| 상황 | 처리 방법 |
|------|----------|
| 검색 엔진 접근 불가 | Google News → DuckDuckGo HTML → 허용 도메인 직접 접근 순으로 폴백. 모두 실패 시 학습 데이터 기반으로 답변하되 "실시간 검색을 수행할 수 없어 학습 데이터 기준으로 답변합니다"라고 명시 |
| 검색 결과 없음 | 쿼리를 재구성(키워드 변경, 범위 확대)하여 1회 재시도. 그래도 없으면 "해당 주제에 대한 최신 검색 결과를 찾지 못했습니다"라고 안내 |
| 비신뢰 소스만 반환 | 비공식 소스의 정보를 사용하지 않고, "신뢰할 수 있는 공식 소스에서 관련 정보를 찾지 못했습니다. 공식 문서를 직접 확인하시기 바랍니다"라고 안내 |
| JavaScript 챌린지/봇 차단 | 해당 엔드포인트를 재시도하지 않고 즉시 다른 검색 방법으로 전환 |
| 검색 결과 상충 | 출처 간 정보가 상충할 경우 양쪽 정보를 모두 제시하고, 공식 소스를 우선하여 어느 쪽이 더 신뢰할 수 있는지 표시 |

## 주의사항

1. **공식 소스 우선**: 해당 기술의 공식 사이트 → 공식 문서 → 패키지 레지스트리 → 커뮤니티 순으로 우선합니다.
2. **교차 검증**: 단일 출처에 의존하지 않고, 가능한 여러 출처를 교차 검증합니다. 비공식 소스는 반드시 공식 문서와 대조합니다.
3. **날짜 확인**: 검색 결과의 게시 날짜를 확인하여 최신성을 판단합니다. 1년 이상 된 정보는 변경 여부를 재확인합니다.
4. **불확실성 표시**: 검색 결과가 상충하거나 불확실할 경우 명시합니다.
5. **개인정보 보호**: 검색 쿼리에 사용자의 개인정보를 포함하지 않습니다.
6. **신뢰할 수 없는 소스 회피**: 출처가 불명한 개인 블로그, SEO 스팸 사이트, 클릭베이트 사이트의 정보는 사용하지 않습니다.
