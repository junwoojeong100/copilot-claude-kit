# Verification

생성 성공은 완료가 아니다. PPTX는 **구조 감사 + 전체 렌더 + 시각 확인**을 거친 뒤에야 완료다.
목표는 **한 번의 전체 패스**로 결함을 찾아 일괄 수정하고, 변경이 있을 때만 다시 렌더하는 것이다.

기본 실행:

```bash
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py \
  deck.pptx --out <work-dir> --expected-slides 30 --strict \
  --min-body-pt 15
```

Runner가 구조 감사와 전체 렌더를 읽기 전용으로 병렬 실행하고, risk score가 높은 슬라이드를 같은 PDF로
상세 렌더한다. `verification-report.json`, `qa/contact-*.jpg`, `qa-detail/slide-*.jpg`를 확인한 뒤
결함을 일괄 수정한다. `--strict --min-body-pt 15`는 15pt 미만의 likely body 후보, 명시적 크기가 없는 run, title risk,
본문 title row의 font-size 불일치, 승인되지 않은 geometry overlap, 서로 다른 text frame에서 실제
렌더된 글자의 충돌을 실패 처리한다.
Storyline에서 Fact Ledger의 외부 사실을 사용하는 슬라이드가 있으면
`--require-sources <slide-list>`를 추가해 모두 전달한다.
해당 슬라이드의 footer 영역에 `Source:` 또는 `출처:`가 없으면 strict 검증이 실패한다. 외부 사실을
사용하지 않는 덱에서만 이 옵션을 생략한다.
사람이 확인한 의도적 예외가 있을 때만 `--allow-small-text 4,8-9` 또는
`--allow-overlap 6,8`, `--allow-title-size 12`처럼 슬라이드 번호를 명시한다. footer와 짧은
label/chip은 별도로 분류된다.

## 1. 구조 감사

```bash
python3 -B .github/skills/adaptive-presentation/scripts/audit_pptx.py deck.pptx
```

검사 항목(임의 PPTX 대상, 생성 방식과 무관):

- 슬라이드 장수와 화면비
- PowerPoint 압축 구조(ZIP integrity)
- 슬라이드·layout·master 등 package XML의 중복 shape-property child(PowerPoint repair risk)
- 슬라이드 경계를 벗어난 도형
- 텍스트 상자·도형·그룹 자식·표 셀의 사용 글꼴과 크기 분포
- 출처를 제외한 작은 텍스트 후보
- 슬라이드별 텍스트 문자 수
- 비어 있는 텍스트 상자(장식용 auto shape는 제외)
- 명시적 글자 크기가 없는 non-empty run
- 표지·section divider를 자동 제외한 본문 title row의 기준 크기와 슬라이드별 편차
- text/text frame 교차, 비텍스트 shape/shape 교차, text frame의 후보 container 이탈

제목 일관성 결과:

- `content_title_reference_pt`: 본문 title row의 기준 크기
- `content_title_size_range_pt`: 승인되지 않은 본문 제목의 최대-최소 크기 차이
- `unexpected_title_size_inconsistencies`: 기준 크기에서 벗어난 미승인 슬라이드

긴 제목 때문에 특정 슬라이드만 축소하지 말고 title frame 높이·폭이나 문구를 조정한다. 표지·section
divider처럼 실제 위계가 다른 예외만 확대 확인 후 `--allow-title-size`로 승인한다.

구조 검사 결과의 `overlap_candidates`는 좌표 기반이다. `--strict`에서는
`unexpected_overlap_candidates`가 0이어야 한다. connector나 포함 관계처럼 의도적인 겹침은 개별
슬라이드를 확대 확인한 뒤에만 `--allow-overlap`으로 승인한다.

감사 스크립트는 주요 본문과 짧은 label/chip 후보를 분리해 보고한다. label 경고는 시각 검토 대상이며
그 자체가 실패는 아니다. 그룹 도형이 있으면 내부 텍스트는 검사하지만 자식 좌표의 시각적 경계는 렌더로
확인한다. 차트 축·데이터 레이블처럼 별도 객체에 그려지는 텍스트도 렌더로 확인한다. 장식 도형의
intentional bleed는 허용할 수 있다. 감사 결과를 맹목적으로 통과시키지 말고 항목별로 판단한다.

전체 렌더가 끝나면 verifier는 PDF text span을 원본 text frame에 다시 매핑한다.

- `rendered_text_overlaps`: 서로 다른 text frame에서 실제 글리프 bounding box가 겹친 항목
- `unexpected_rendered_text_overlaps`: 승인되지 않아 strict 실패를 만드는 항목
- `rendered_text_overflow_candidates`: 줄바꿈·폰트 metric으로 frame 밖에 렌더된 후보

overflow candidate 자체는 인접 객체와 충돌하지 않을 수 있으므로 위험 슬라이드 우선순위에 반영하고
확대 확인한다. 다른 frame의 글자와 충돌한 항목은 수정하거나 명시적으로 승인해야 한다.

## 2. 전체 렌더

필요 도구: LibreOffice `soffice`, PyMuPDF `fitz`, Pillow.
`--out`에는 이 작업만 사용하는 빈 디렉터리나 Runner가 소유 표시한 기존 QA 디렉터리를 지정한다.
비어 있지 않은 일반 디렉터리는 기존 파일 삭제를 막기 위해 거부한다.

```bash
# 기본: 30장 단위 overview JPEG만 남김
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  deck.pptx --out <session>/<deck>-work/qa --keep-pdf
```

결과:

- 30장 단위 `contact-01-30.jpg`
- 개별 slide JPEG는 contact sheet 생성 후 삭제
- 중간 PDF도 렌더 후 삭제(위 예시는 `--keep-pdf`로 상세 검사 동안만 유지)

기본 JPEG는 파일당 900KiB 이하로 압축된다. PPTX와 PDF는 렌더 입력/중간 산출물일 뿐 `view`로 열지 않는다.

## 3. contact sheet 검사

전체 흐름은 compact overview JPEG **한 장씩** 본다.

- 섹션 리듬이 있는가?
- 모든 장이 같은 카드 그리드처럼 보이지 않는가? (같은 구조 반복이면 일부를 다른 관계형 형태로 교체)
- 제목 길이와 위치가 안정적인가?
- 같은 역할의 본문 제목이 모두 동일한 크기로 보이는가? 긴 제목만 작아진 슬라이드가 없는가?
- 시각적 밀도가 한 구간에 몰리지 않는가?
- 임원 자료의 색상 계열이 3~4개 안에서 일관되는가? 여러 카드가 빨강·초록·보라·노랑으로 각각
  구분되는 rainbow palette가 아닌가?
- 같은 의미가 슬라이드마다 다른 색으로 바뀌지 않는가?
- 본문 슬라이드에 stat·chart·table·process·hierarchy·timeline 등 편집 가능한 visual structure가
  있는가? 표지·section divider·단순 마무리 장에는 장식적 visual을 강제하지 않았는가?
- 제목·본문·caption의 위계가 thumbnail에서도 즉시 보이는가?
- 제목 바로 아래 장식선, pill chip, rounded-card grid, soft shadow가 반복되는 AI 생성물 패턴은 아닌가?
- dominant/support/accent의 우선순위가 보이고 모든 색이 같은 비중으로 경쟁하지 않는가?
- `완전 흰 배경` 요청 시 모든 slide canvas가 동일한 순백색인가? 섹션 교대를 위해 연회색 canvas가
  섞이지 않았는가?

## 4. 위험 슬라이드 확인

의심 슬라이드만 기존 PDF를 재사용해 개별 JPEG로 다시 렌더한다.

```bash
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  deck.pptx --reuse-pdf <session>/<deck>-work/qa/<deck>.pdf \
  --slides 8,16,22 --keep-slide-images \
  --out <session>/<deck>-work/qa-detail
```

이 상세 검사는 PPTX를 수정하기 전에 수행한다. `--reuse-pdf`는 manifest의 PPTX와 PDF SHA-256을 모두
검사하며, 어느 파일이든 달라지면 실패하므로 오래되거나 부분 생성된 PDF를 쓸 수 없다. 한 응답에서
full-slide 이미지는 최대 2~3개만 확인한다.

확인:

- 텍스트가 도형 밖으로 넘치는가?
- 텍스트 프레임 높이가 줄 수를 수용하는가?
- 제목이 전용 제목 행을 넘거나 구분선을 침범하는가?
- 텍스트와 컨테이너 경계 사이에 렌더링 차이를 견딜 여유가 있는가?
- 도형-도형, 도형-텍스트, 텍스트-텍스트가 의도치 않게 겹치는가?
- 두 자리 단계 번호나 짧은 영문 라벨이 좁은 frame 때문에 2줄로 깨지지 않는가?
- chevron·arrow가 카드 사이 gap을 넘어 카드 아래로 숨어 들어가지 않는가?
- 배지·예외 문장·주석이 인접 카드나 결정 영역을 침범하는가?
- 연결선이 글자를 가리는가?
- source와 page number가 겹치는가?
- 한글 조사와 영문 혼용이 이상하게 줄바꿈되는가?
- 대비가 충분한가?
- 정렬이 흔들리지 않는가?

## 5. 합격 임계치

| 항목 | 기준 |
|---|---|
| Slide count | 요청과 정확히 일치 |
| Bounds | 의도하지 않은 out-of-bounds 0 |
| Overlap | `unexpected_overlap_candidates` 0 + `unexpected_rendered_text_overlaps` 0 |
| Content title size | `unexpected_title_size_inconsistencies` 0 |
| Primary body | 원칙적으로 16pt+, 최소 15pt |
| Automated body floor | canonical QA에서 likely body 15pt 미만 실패; compact label/secondary annotation은 별도 보고 |
| Source/footer | 8~9.5pt 허용 |
| Editorial hierarchy | title 30~42pt, primary body 15~19pt, secondary 13~15pt, label 11~13pt |
| Density after reduction | 여백이 생긴 장만 근거·KPI·owner·예외 조건을 1~2개 보강하고, 고밀도 장은 유지 |
| Native visual | 본문 장에 편집 가능한 visual structure 1개 이상; 표지·section divider·단순 마무리 제외 |
| Repetition | 같은 layout이 의도 없이 3장 연속되지 않음 |
| Requested white canvas | 모든 slide background와 전체 화면 canvas 도형이 `#FFFFFF` |
| Executive palette | 브랜드가 없으면 neutral + primary + optional secondary의 3~4개 색상 계열 |
| 다양성 | 같은 구조를 기계적으로 반복하지 않음(정보 유형에 맞게 형태를 바꿈) |
| Claims | 숫자·상태·고객 성과에 source |
| Preview/demo | 텍스트 라벨 존재 |
| Render | 전체 compact overview 생성 + 위험 슬라이드 선택 렌더 |
| Integrity | `unzip -t` 오류 0 |

## 6. 수정 루프 (시간 최소화)

1. 결함을 슬라이드 번호와 유형으로 기록한다.
2. 원인을 구분한다: content density / geometry / typography / contrast / narrative.
3. 오버플로 수정은 내용·레이아웃을 우선하되, 전체 축소 요청은 역할별 0.5~2pt 일괄 조정한다.
4. 모든 결함을 모아 세션 작업 폴더의 `build_<deck>.py`를 **한 번에** 수정한다.
5. PPTX를 재생성하고 새 PPTX에서 PDF를 다시 변환한다.
6. `--strict`를 다시 실행해 geometry/render overlap이 0인지 확인한다. 의도적 예외는 확대 검토 근거가
   있을 때만 `--allow-overlap`으로 남긴다.
7. **국소(단일·소수 슬라이드, 비구조) 수정이면 `--slides`로 변경 슬라이드만 이미지화해 확인하고 전체
   contact sheet는 다시 만들지 않는다.**
8. 여러 슬라이드·구조가 바뀐 경우에만 전체 contact sheet를 다시 열람한다. 변경이 없으면 최초 전체
   렌더가 최종 검증이다.

## 7. 정리

```bash
WORK_DIR="<session>/<deck>-work" python3 -B -c \
  'import os,shutil; from pathlib import Path; w=Path(os.environ["WORK_DIR"]).resolve(); [shutil.rmtree(w/n, ignore_errors=True) for n in ("qa","qa-detail")]'
```

재생성 스크립트는 세션 작업 폴더에만 둔다. 저장소와 최종 출력 폴더에는 사용자가 요청한 최종 PPTX/PDF만
남기며, `.py`, `.pyc`, `__pycache__`, 중간 PDF, QA 이미지는 남기지 않는다.
