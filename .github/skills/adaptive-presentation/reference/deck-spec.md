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
    "required": true,
    "authoringMode": "regenerate-from-scratch",
    "requiredSections": [
      "핵심 메시지",
      "전체 흐름",
      "구성 요소",
      "실제 예시",
      "검증 기준",
      "상태/조건",
      "질문/전환",
      "발표 한 문장",
      "출처"
    ],
    "explanationSection": "전체 흐름",
    "statusSection": "상태/조건",
    "exampleSection": "실제 예시",
    "validationSection": "검증 기준",
    "summarySection": "발표 한 문장",
    "targetSeconds": 180,
    "minCharacters": 1000,
    "maxCharacters": 2600,
    "minExplanationCharacters": 220,
    "minExplanationSentences": 3,
    "minStatusCharacters": 120,
    "minExampleCharacters": 100,
    "minValidationCharacters": 70,
    "minSummaryCharacters": 30,
    "maxSummaryCharacters": 180,
    "requireStateLabelsInStatusSection": true
  },
  "fontPolicy": {
    "selected": "Noto Sans CJK KR",
    "fallbacks": ["Malgun Gothic", "Apple SD Gothic Neo"],
    "requireAvailable": true,
    "requireRenderedMatch": true
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

- `requiredSections`: 각 섹션은 `섹션명:` 형태로 notes에 직접 표시한다.
- `authoringMode`: 기존 notes 문구를 이어 붙이지 않고 비운 뒤 현재 storyline·visual·근거에서 재작성한다.
- `explanationSection`: 화면 읽는 순서와 요소 간 관계를 설명하는 섹션명.
- `statusSection`: 제품 상태, 적용 범위와 예외를 정리할 섹션명.
- `exampleSection`, `validationSection`, `summarySection`: 실제 업무 예시, KPI·evidence, 발표용 한 문장을
  각각 검사할 섹션명.
- `targetSeconds`: 상세 설명을 모두 사용할 때의 목표 시간. 한국어 기본은 약 180초다.
- `minCharacters`: 결론과 질문만 적고 상세 설명·출처를 생략하는 notes를 방지한다.
- `maxCharacters`: 발표 원고처럼 과도하게 긴 notes를 방지한다.
- `minExplanationCharacters`, `minExplanationSentences`: `전체 흐름` 블록이 단순 요약이 아니라 화면 읽는
  순서·의미·조건을 전달하도록 강제한다.
- `minStatusCharacters`: `상태/조건`이 `GA` 같은 짧은 라벨만 반복하지 않고 정확한 범위와 조건을
  설명하도록 강제한다.
- `minExampleCharacters`, `minValidationCharacters`: 슬라이드 개념을 실제 고객 업무와 측정 가능한 KPI에
  연결한다.
- `minSummaryCharacters`, `maxSummaryCharacters`: `발표 한 문장`을 너무 짧거나 장황하지 않게 유지한다.
- `requireStateLabelsInStatusSection`: slide의 `stateLabels`를 `상태/조건`에도 직접 표시해 시각 라벨과
  상세 설명이 어긋나지 않게 한다.
- `상태/조건`은 `Foundry IQ — core API GA, portal·SharePoint·advanced retrieval Preview`처럼
  서비스 전체와 API·portal·source·개별 tool의 상태를 분리한다. 공식 기술명은 English로 유지하고
  역할과 조건은 쉬운 한국어로 설명한다.
- `출처`는 긴 URL 대신 `[F-001] Publisher · Document title · checked YYYY-MM-DD`처럼 짧게 쓴다.
- 외부 출처가 없는 표지·진단·실행 장은 `내부 프레임 · 고객별 검증 필요`, `ASSUMPTION`,
  `Recommendation`처럼 성격과 검증 조건을 적는다.

`slides`는 `request.slideCount`와 정확히 일치하고 1부터 연속 번호를 사용한다. `claimIds`는 공통
Fact Ledger JSON의 `Fact` ID만 참조한다. Inference는 근거 Fact ID를 연결하고 Assumption은
`stateLabels`로 표시한다. 해당 슬라이드 footer에는
`Source: [F-001] Publisher · Document title`처럼 ID를 표시한다. Preview·가정·시연 수치는
`stateLabels`에 기록하고 실제 슬라이드에도 같은 텍스트를 보여준다.

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
