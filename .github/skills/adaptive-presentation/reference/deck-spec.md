# Deck Spec Contract

`deck-spec.json`은 요청·스토리라인·Fact Ledger·템플릿·폰트·QA를 연결하는 authoritative contract다.
생성 코드와 verifier는 이 파일을 함께 사용하며, CLI 플래그가 충돌하면 spec을 우선하고 실패한다.

## 최소 구조

```json
{
  "schemaVersion": 1,
  "request": {
    "topic": "AI 운영 전략",
    "audience": "CIO",
    "purpose": "의사결정",
    "language": "ko-KR",
    "slideCount": 12,
    "output": "ai-operations.pptx"
  },
  "canvas": {"source": "default", "widthIn": 13.333, "heightIn": 7.5},
  "templateProfile": null,
  "factLedger": "fact-ledger.json",
  "languagePolicy": {
    "mode": "korean-first-technical-english",
    "targetLatinRatio": 0.40,
    "maxLatinRatio": 0.55,
    "maxSlideLatinRatio": 0.75,
    "minAnalyzedCharacters": 40,
    "preserveOfficialTerms": true,
    "requireKoreanExplanationForProtectedTerms": true,
    "minHangulCharactersPerTechnicalSlide": 24,
    "protectedTerms": [
      "GitHub Copilot",
      "Microsoft Foundry",
      "Code Review",
      "Hosted Agents"
    ],
    "allowHighLatinSlides": []
  },
  "speakerNotesPolicy": {
    "mode": "core-only",
    "required": true,
    "authoringMode": "regenerate-from-scratch",
    "requiredSections": ["핵심 메시지"],
    "coreSection": "핵심 메시지",
    "targetSeconds": 60,
    "minCharacters": 120,
    "maxCharacters": 600,
    "minCoreCharacters": 100,
    "maxCoreCharacters": 580,
    "minCoreSentences": 4,
    "maxCoreSentences": 6,
    "minTotalSentences": 4,
    "maxTotalSentences": 6,
    "forbiddenSections": ["질문", "전환"],
    "requireCoreFirst": true,
    "forbidSourceReferences": true
  },
  "fontPolicy": {
    "selected": "Apple SD Gothic Neo",
    "fallbacks": ["Malgun Gothic", "Noto Sans CJK KR", "NanumGothic"],
    "requireAvailable": true,
    "requireRenderedMatch": true,
    "requireAllTextFont": true,
    "leadingMessage": {
      "fontFamily": "Apple SD Gothic Neo",
      "sizePt": 27,
      "bold": true
    }
  },
  "slides": [
    {
      "number": 1,
      "role": "cover",
      "title": "운영 통제를 먼저 설계해야 AI가 확장됩니다",
      "claimIds": [],
      "stateLabels": []
    },
    {
      "number": 2,
      "role": "evidence",
      "title": "평가와 추적이 프로덕션 승격의 기준입니다",
      "claimIds": ["F-001"],
      "stateLabels": ["GA"]
    }
  ],
  "qa": {
    "strict": true,
    "minBodyPt": 15,
    "minTitlePt": 26,
    "maxUnmappedTextSpans": 0,
    "failRenderedOverflow": true,
    "requireVisualReview": true,
    "exceptionManifest": null
  }
}
```

한국어 덱의 repository 기본은 `Apple SD Gothic Neo`이며, 표지·section divider를 제외한 본문
리딩 메시지는 `27pt · Bold`다. `leadingMessage`를 생략하면 validator가 `selected · 27pt · Bold`로
정규화한다. 브랜드·템플릿 때문에 다른 스타일을 써야 하면 `fontFamily`는 `selected` 또는
`fallbacks` 중 하나로 명시하고, verifier가 실제 본문 title row의 family·size·weight를 검사한다.
`requireAllTextFont=true`이면 PPTX의 모든 visible text run은 `selected`를 명시해야 한다.
이때 `leadingMessage.fontFamily`도 반드시 `selected`와 같아야 한다. 브랜드·템플릿 override는
해당 글꼴을 `selected`로 바꿔 기록한다. `fallbacks`는 렌더 환경의 대체 글꼴만 허용하며 PPTX 내부의
혼용 글꼴로 사용할 수 없다.

한국어(`ko`, `ko-KR`) spec에서 `languagePolicy`를 생략하면 위 기본 임계치가 적용된다. 다만 생성자는
해당 덱에 실제로 사용하는 서비스명·공식 기능명을 `protectedTerms`에 명시해야 한다.

- `targetLatinRatio`: `protectedTerms`를 제외한 설명용 영문의 편집 목표. 낮다고 실패하지 않는다.
- `maxLatinRatio`: footer·출처·페이지 번호와 `protectedTerms`를 제외한 설명용 영문의 최대 비율.
- `maxSlideLatinRatio`: 공식 명칭이 집중된 기술 장을 위한 개별 장 최대치.
- `protectedTerms`: 번역하면 안 되는 공식 영문명. 대소문자를 무시하고 최종 PPTX 존재 여부를 검사하며
  language ratio 계산에서는 중립 처리한다.
- `requireKoreanExplanationForProtectedTerms`: 공식 기술명이 있는 장에 쉬운 한글 설명을 요구한다.
- `minHangulCharactersPerTechnicalSlide`: protected term이 등장한 장에서 최소한 확보할 한글 설명 문자 수.
  기본 24자는 최소 안전장치이며 실제 제작에서는 역할·가치·판단을 한 문장 이상 쓴다.
- `allowHighLatinSlides`: 코드·API 중심으로 개별 장 최대치를 의도적으로 넘는 장. 전체 contact sheet와
  확대 화면을 검토한 뒤에만 사용한다.

한국어 spec에서 `speakerNotesPolicy`를 생략하면 위 기본값이 적용된다.

- `mode`: 기본은 `core-only`다. 사용자가 workshop 진행 질문과 장표 전환 cue를 명시적으로 요청한
  경우에만 `guided-flow`를 사용한다.
- `requiredSections`: 각 섹션은 `섹션명:` 형태로 notes에 직접 표시한다.
- `authoringMode`: 기존 notes 문구를 이어 붙이지 않고 비운 뒤 현재 storyline·visual·근거에서 재작성한다.
- `coreSection`: 발표자가 그대로 말할 핵심 메시지 약 5문장을 담는 섹션명. 현재 visual의 핵심 요소
  2~4개가 어떻게 연결되어 결론, 작동 방식, 고객 의미와 판단 또는 행동을 만드는지 설명한다.
- `targetSeconds`: 한 장의 핵심을 전달하는 목표 시간. 한국어 기본은 약 60초다.
- `minCharacters`, `maxCharacters`: cue가 지나치게 빈약하거나 상세 원고로 길어지는 것을 방지한다.
- `minCoreCharacters`, `maxCoreCharacters`: 핵심 메시지 블록의 길이를 제한한다.
- `minCoreSentences`, `maxCoreSentences`: 기본 4~6문장으로 제한해 약 5문장 분량을 유지한다.
- `minTotalSentences`, `maxTotalSentences`: notes 전체 문장 수도 같은 범위로 검증한다.
- `forbiddenSections`: `core-only`에서 허용하지 않는 `질문`, `전환` 같은 섹션명이다.
- `requireCoreFirst`: notes가 `핵심 메시지:`로 시작하도록 한다.
- `forbidSourceReferences`: notes의 `출처:`·`Source:` 블록, Fact ID, URL을 금지한다.
- verifier는 section·길이·문장 수와 금지 섹션을 검사한다. visual 설명의 충분성과 구어체 품질은
  storyline 검토와 최종 editorial review에서 별도로 확인한다.
- `guided-flow`는 기존 `questionSection`, `transitionSection`, 질문·전환 길이와 문장 수,
  `requireQuestionFirst`, `requireQuestionMark` 필드를 사용한다. 기존 deck spec은 이 필드가 있으면
  `mode`가 없어도 `guided-flow`로 자동 인식한다.
- GA/Preview, 적용 범위, 예외는 slide visual·footer·`stateLabels`에 명확히 표시한다. 발표 결론을
  바꾸는 조건만 `핵심 메시지`에 압축하고 notes에 별도 상세 블록을 만들지 않는다.
- Fact ID와 출처는 speaker notes가 아니라 machine contract와 Fact Ledger에만 기록한다. 슬라이드에
  보이는 footer에는 Fact ID를 제거하고 `출처: Publisher · Document title (YYYY-MM-DD 확인)`처럼
  사람이 읽을 수 있게 표시한다.
- 외부 출처가 없는 표지·진단·실행 장은 `내부 프레임 · 고객별 검증 필요`, `ASSUMPTION`,
  `Recommendation`처럼 성격과 검증 조건을 적는다.

`slides`는 `request.slideCount`와 정확히 일치하고 1부터 연속 번호를 사용한다. `claimIds`는 공통
Fact Ledger JSON의 `Fact` ID만 참조한다. Inference는 근거 Fact ID를 연결하고 Assumption은
`stateLabels`로 표시한다. `claimIds`는 machine contract와 Fact Ledger에만 남기며 speaker notes에는
넣지 않는다. 해당 슬라이드 footer에는 `출처: Publisher · Document title`처럼 발행자와 문서명을
표시한다. Preview·가정·시연 수치는 `stateLabels`에 기록하고 실제 슬라이드에도 같은 텍스트를 보여준다.

## 템플릿

템플릿이 있으면 먼저 profile을 만든다.

```bash
python3 -B .github/skills/adaptive-presentation/scripts/inspect_template.py template.pptx \
  --out <work>/template-profile.json
```

`canvas.source`를 `template`로 두고 `templateProfile`을 지정한다. 생성기는 템플릿을 열어 기존
master·layout·theme·canvas를 보존하고 필요한 경우 기존 예시 슬라이드만 제거한다. verifier는 최종
deck의 canvas와 theme fingerprint가 profile과 일치하는지 확인한다.

## QA 증거

첫 verifier 실행은 finding ID와 contact sheet를 만든다. 자동 매핑이 불가능한 chart·SmartArt 또는
의도적 overlap만 전체 화면에서 확인하고 `qa-exceptions.json`에 정확한 `findingId`와 이유를 적는다.
슬라이드 전체를 허용하는 예외는 레거시 호환용이며 새 작업에서는 사용하지 않는다.

contact sheet와 위험 슬라이드를 모두 확인한 뒤 최종 deck SHA-256에 묶인 evidence를 생성한다.

```bash
python3 -B .github/skills/adaptive-presentation/scripts/visual_review.py create deck.pptx \
  --out <work>/visual-review.json --reviewer Copilot \
  --notes "전체 contact sheet와 위험 슬라이드의 잘림·대비·정렬을 확인했습니다."
```

PPTX가 바뀌면 이 증거는 무효가 되므로 새 revision을 다시 렌더하고 검토한다.
