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
