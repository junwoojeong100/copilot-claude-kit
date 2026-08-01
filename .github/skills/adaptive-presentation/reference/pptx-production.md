# PPTX Production

슬라이드는 고정 생성 엔진이나 컴포넌트 라이브러리 없이 **`python-pptx`로 직접** 만든다. 매 덱마다
주제에 맞는 시각 형태를 자유롭게 구성하되, 결론이 가장 짧은 경로로 읽히는 Straightforward 구조와
아래 품질·위생 기준을 지킨다.

## 1. 도구

1. Python 환경에서 `python-pptx`를 기본으로 사용한다.
2. 대량 데이터 처리·차트 계산에는 pandas/matplotlib를 쓸 수 있으나, 발표에 들어가는 핵심 도표는
   가능하면 PowerPoint 도형/네이티브 차트로 만들어 편집 가능하게 한다.
3. 외부 이미지가 필요하면 사용권과 원본 URL을 기록한다.
4. 도구 탐색·의존성 준비는 `scripts/toolcheck.py`(soffice·PyMuPDF·Pillow·python-pptx·한글 폰트 1회
   탐지·캐시)와
   `reference/full-optimized.md`의 캐시 규칙을 따른다.

## 2. 파일 구조

```text
<output>/<deck>.pptx                 # 사용자에게 보이는 기본 산출물

<session>/<deck>-work/               # SKILL.md의 portable 세션 artifact 디렉터리 아래
  fact-ledger.md
  storyline.md
  build_<deck>.py                    # python-pptx 직접 생성 스크립트
  qa/
    contact-01-30.jpg
    slide-08.jpg                     # 선택 검수 시에만
```

생성 스크립트·QA 산출물을 저장소 루트나 최종 출력 폴더에 두지 않는다. 사용자가 요청한 경우에만 세션
작업 폴더에서 최종 출력 위치로 복사한다. 중간 PDF는 QA가 끝날 때까지만 두고 정리한다. Python은
`python3 -B` 또는 `PYTHONDONTWRITEBYTECODE=1`로 실행해 저장소에 `__pycache__`·`.pyc`가 생기지 않게 한다.

## 3. 생성 스크립트 골격

`python-pptx`를 직접 사용하는 최소 골격이다. 슬라이드마다 필요한 도형·텍스트·차트를 자유롭게 배치한다.

```python
import os
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN

OUT = Path(os.environ["PPTX_OUT"])

# 주제·브랜드에 맞게 자유롭게 정하는 값 (고정 팔레트 아님)
INK = RGBColor(0x1A, 0x1A, 0x1A)
ACCENT = RGBColor(0x0F, 0x62, 0xFE)
CANVAS = RGBColor(0xFF, 0xFF, 0xFF)
BODY_FONT = "Apple SD Gothic Neo"

def textbox(slide, text, x, y, w, h, size, *, color=INK, bold=False,
            align=PP_ALIGN.LEFT, font=BODY_FONT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = font
    run.font.color.rgb = color
    return box

def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # 슬라이드마다 정보 관계에 맞는 형태를 직접 구성한다.
    slide = prs.slides.add_slide(blank)
    textbox(slide, "결론형 제목", 0.72, 0.5, 11.9, 1.0, 34, bold=True)
    # ... 도형·차트·출처 footer 등 자유 배치 ...

    prs.save(OUT)

if __name__ == "__main__":
    build()
```

거대한 JSON 하나로 모든 장을 같은 레이아웃으로 렌더하지 않는다. 슬라이드마다 함수/구성을 나눠
정보 유형에 맞는 형태를 만든다.

### 선택: 디자인 중립 헬퍼로 보일러플레이트 줄이기

`pptx_helpers`는 색·좌표를 **인자로 받는** 기계적 프리미티브(box·text·bullets·chip·chevron·grid_table·
soft_shadow)만 제공한다. 팔레트·테마·슬라이드 유형이 없으므로 "정해진 틀 없이 자유 구성" 원칙을 그대로
지키면서 반복 코드를 줄인다.

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("<absolute-skill-dir>")))
import pptx_helpers as H

prs, blank = H.new_deck()                              # 16:9 치수(디자인 아님)
INK, ACCENT = H.hexc("14203A"), H.hexc("1F63D8")       # 색은 매 덱 자유
s = H.add_slide(prs, blank, bg=H.hexc("FFFFFF"))
H.text(s, "결론형 제목", 0.72, 0.6, 11.9, 1.0, 30, INK, bold=True)
H.bullets(s, ["근거 1", "근거 2"], 0.72, 1.9, 6.0, 2.0, 17, INK, marker_color=ACCENT)
prs.save(OUT)
```

### 편집형 비즈니스 덱 기본값

`Claude Cowork처럼`, `컨설팅 덱처럼`, `임원용으로 더 전문적으로`라는 요청은
[`editorial-business-style.md`](./editorial-business-style.md)를 따른다.

- 샘플 deck/template이 있으면 자체 팔레트보다 그 master·grid·font·layout을 우선한다.
- 샘플이 없으면 강한 제목, 정밀한 column/grid, 넓은 여백, hairline rule, native chart/table/diagram을
  기본 시각 언어로 사용한다.
- 내용 전달이 목적인 본문 슬라이드에는 편집 가능한 visual structure가 하나 이상 있어야 한다.
  표지·section divider·단순 마무리 장은 예외다.
- 한 화면의 primary reading path는 좌→우 또는 상→하 하나로 고정하고, 결론과 무관한 장식·중첩
  container·중복 label은 제거한다.
- 한 가지 visual motif를 반복하되 같은 layout을 반복하지 않는다.
- 제목 밑 짧은 accent line, 과도한 rounded card·pill chip·soft shadow는 기본값으로 금지한다.

## 4. 화면과 안전 영역

- 기본: 13.333 × 7.5 inch
- 좌우 여백: 0.6~0.8 inch
- 제목 영역: 상단 0.4~1.45 inch
- 본문 영역: 약 1.6~6.75 inch
- 출처/페이지: 7.0 inch 부근
- 장식 도형은 의도적으로 bleed할 수 있지만 텍스트는 안전 영역 안에 둔다
- 사용자가 `완전 흰 배경`을 요청하면 모든 슬라이드의 `slide.background.fill`을 `#FFFFFF`로 직접
  지정한다. slide 전체를 덮는 배경 도형도 흰색이어야 하며, 섹션별 `#F7F7F7` canvas 교대는 사용하지
  않는다. 카드와 강조 영역의 light neutral surface는 별도 역할이므로 유지할 수 있다.
- 제목·본문·주석·출처의 전용 행을 먼저 예약하고, 한 영역의 도형이나 텍스트가 다른 영역을 침범하지 않게
  좌표를 잡는다.
- 포함 관계가 아닌 콘텐츠 도형끼리는 bounding box가 겹치지 않게 한다. 배지·라벨처럼 의도적으로 도형
  위에 놓는 텍스트도 컨테이너 안에 완전히 들어가야 한다.
- 연결선과 화살표는 텍스트 상자 아래를 통과시키지 않는다. 공간이 부족하면 선을 우회시키거나 내용을 줄인다.

## 5. 텍스트

- `word_wrap=True`, `auto_size=NONE`
- 텍스트 프레임 margin을 명시
- 모든 run에 font name/size/color를 직접 적용
- 한글과 영문 혼용 렌더를 실제 PDF에서 확인
- 줄 간격과 paragraph spacing을 명시
- 텍스트가 들어가는 도형은 PowerPoint/LibreOffice의 폰트 메트릭 차이를 고려해 가로·세로 8~12%의
  여유를 둔다. 한 환경에서 간신히 맞는 상태는 합격이 아니다.
- 제목은 제목 전용 행 안에서 끝나야 하며 구분선·섹션 chip을 침범하지 않아야 한다. 카드 문구는 카드
  border 안에 완전히 들어가야 한다.

크기:

- 제목 30~42pt
- 주요 본문 15~19pt
- 보조 13~15pt
- 표·도식 label 11~13pt
- 출처 8~9.5pt

표지·section divider를 제외한 본문 슬라이드 title role은 덱 전체에서 한 가지 크기를 사용한다. 같은 title
row가 슬라이드마다 31/32/34pt로 달라지면 위계가 흔들린다. 긴 제목은 문구 단축, title frame 폭·높이,
명시적 줄바꿈으로 해결하고 해당 슬라이드만 축소하지 않는다. 정말 다른 위계인 슬라이드만 예외로 기록한다.

긴 제목은 2줄 전용 높이를 확보하거나 문구를 줄인다. 28~29pt는 의미를 훼손하지 않고 줄일 수 없을 때만
허용한다. 컨테이너 오버플로는
문구 단축·도형 높이/폭·명시적 줄바꿈을 먼저 조정한다. 사용자가 글자 축소를 요청했거나 소폭 축소로
해결되는 경우에는 역할별 기준을 먼저 0.5~2pt 일관되게 낮춘다. 그래도 남는 문제 frame만 0.5pt 단위로
줄이되, 주요 본문 15pt·보조 13pt 아래로 내리지 않는다.

밀도: 일반 슬라이드는 주요 본문 40~65단어를 기본 범위로 삼고, 기술 슬라이드도 문장 수를 제한한다.
글자 축소로 생긴 여백에는 검증 근거, KPI, owner, 예외 조건처럼 발표자의 설명력을 높이는 정보만
1~2개 보강한다. 이미 밀도가 높은 슬라이드는 내용을 늘리지 않으며, 표/부록은 필요하면 명확히
Appendix로 구분한다.

## 6. 한글 폰트

실행 환경에서 폰트를 검색한다.

```bash
python3 -B .github/skills/adaptive-presentation/scripts/toolcheck.py \
  --strict --require-korean-font

(fc-list 2>/dev/null || true) | grep -Ei 'Noto Sans|Apple SD Gothic|Malgun|Aptos|Segoe'
```

예시 폴백:

- macOS: Apple SD Gothic Neo
- Windows: Malgun Gothic
- 공통 배포 환경: Noto Sans CJK KR 설치 여부 확인

폰트를 PPTX에 임베드할 수 있다고 가정하지 않는다.

## 7. 색과 대비

- 색은 주제와 (있다면) 사용자 브랜드에서 자유롭게 정한다. 고정 팔레트를 강제하지 않되, 먼저
  `canvas / surface / ink / primary / optional secondary` 역할을 정하고 덱 전체에서 재사용한다.
- 브랜드·템플릿이 없는 CIO/임원 자료의 기본값은 Microsoft Fluent 계열의 white/light neutral canvas,
  dark neutral ink, Microsoft Blue primary, 선택적 blue-teal secondary다.
- 임원 자료는 neutral을 포함해 **3~4개 색상 계열**로 제한한다. 같은 hue의 tint/shade는 한 계열로 보며,
  채도가 높은 accent는 최대 2계열만 쓴다.
- dominant color 하나가 약 60~70%의 시각 무게를 담당하고 support 1~2개와 sharp accent 1개만 보조한다.
- 카드·단계·팀마다 서로 다른 accent를 배정하지 않는다. 구분은 우선 위치·여백·크기·선 굵기·타이포
  계층으로 만들고, 색은 선택·강조·흐름에만 사용한다.
- 같은 의미와 상태는 덱 전체에서 같은 색을 사용한다.
- 본문과 배경 대비 최소 4.5:1
- 제목은 크더라도 낮은 대비 회색으로 두지 않는다
- 색만으로 상태를 전달하지 않고 GA/PREVIEW/위험 텍스트를 병기
- 상태색이 꼭 필요하면 해당 슬라이드의 국소 예외로 제한하고, 구조 색상 체계를 rainbow palette로
  확장하지 않는다.
- PDF 변환에서 색이 달라질 수 있으므로 렌더를 확인
- 흰 canvas 요청은 렌더뿐 아니라 PPTX 구조에서도 각 slide background가 `FFFFFF`인지 확인한다.

## 8. 도형과 연결선

- 도형은 정보 계층을 표현해야 한다
- 선은 시작과 끝의 의미가 명확해야 한다
- 교차선 최소화
- 화살표 방향은 발표 흐름과 일치
- 포함 관계와 연결 관계를 다른 스타일로 표현
- 의도하지 않은 도형 겹침은 금지한다. 그림자와 얇은 border 접촉은 허용하지만, 콘텐츠 면적이나 텍스트가
  다른 객체를 가리면 결함이다.
- chevron·arrow·connector는 인접 카드 사이의 명시적 gap 안에 들어가야 한다. connector 폭이 gap보다
  크거나 대상 카드 아래로 숨어 들어가면 폭·간격을 다시 잡는다.
- 단계 번호·짧은 라벨도 예상보다 자주 강제 줄바꿈된다. `01`·`02` 같은 두 자리 숫자는 실제 글꼴에서
  한 줄로 들어가는 폭과 높이를 확보하고, 다음 본문 행과 독립된 frame을 사용한다.
- 최종 좌표 검사는 text/text, shape/shape, text/container를 모두 포함한다. frame 좌표가 겹치지 않아도
  줄바꿈된 글리프가 frame 밖으로 렌더될 수 있으므로 PDF text-span 검사까지 통과해야 한다.
- 편집형 비즈니스 덱은 square surface와 hairline separator를 우선한다. rounded rectangle·pill·shadow는
  의미가 있을 때만 국소적으로 사용하고 반복 motif로 삼지 않는다.

## 9. 표

- 6행×5열을 기본 상한으로 권장
- 공통 비교 축을 왼쪽에 고정
- 숫자 정렬과 단위 통일
- 긴 문장을 셀에 넣지 않는다
- 표가 핵심 메시지를 숨기면 비교 카드·dot plot·decision tree로 전환

## 10. 차트

- 실제 데이터와 기준일을 사용
- 차트 제목은 데이터 이름이 아니라 결론
- 단위, 축 범위, 표본/출처 표시
- 선택 계열 1개만 강한 색
- 단순 막대·선·dot plot을 우선
- 파이/도넛은 5개 이하의 구성비에서만
- 3D 차트 금지

편집 가능성이 중요하면 PowerPoint 기본 chart API 또는 도형 기반 차트를 사용한다.

## 11. 이미지

- 낮은 해상도 이미지를 늘리지 않는다
- 크롭 비율을 통일
- 텍스트 위에 복잡한 이미지를 직접 깔지 않는다
- 공식 제품 UI 스크린샷은 날짜와 버전을 확인
- 고객 로고는 공식 자산만 사용

## 12. 출처

주장 슬라이드의 footer에 직접 표시한다.

```text
Source: Organization · Document title (accessed YYYY-MM-DD)
```

- 긴 URL은 제목에 hyperlink를 걸거나 짧은 경로로 표시
- 여러 출처는 2개를 넘기지 않도록 핵심 근거를 선택
- 생성형 AI로 만든 그림이나 DEMO DATA는 명시

## 13. 상태·불확실성

- GA: neutral/primary style + `GA`
- Partial GA: secondary 또는 outline style + `PARTIAL GA`
- Preview: secondary accent + `PREVIEW`
- 가정: `ASSUMPTION`
- 시연 수치: `DEMO DATA`

상태마다 새 hue를 추가하지 않는다. 경고색이 꼭 필요한 위험 정보만 국소 예외로 쓰고, 텍스트 라벨은
반드시 유지한다.

## 14. 완성 직전

```bash
# 문법 검사 (.pyc를 만들지 않도록 py_compile 대신 ast.parse 사용)
python3 -B -c 'import ast,pathlib; ast.parse(pathlib.Path("<work-dir>/build_<deck>.py").read_text(encoding="utf-8"))'

# 생성
PPTX_OUT="<absolute-output>/<deck>.pptx" python3 -B <work-dir>/build_<deck>.py

# canonical QA: 구조 감사, 전체 렌더, rendered overlap, 위험 슬라이드, ZIP 검사를 통합 실행
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py \
  <absolute-output>/<deck>.pptx --out <work-dir>/verify \
  --expected-slides <count> --strict --min-body-pt 15
# 외부 사실을 사용한 슬라이드가 있으면 --require-sources <slide-list> 추가

# 추가 확대가 필요할 때만 canonical QA의 PDF를 재사용
python3 -B .github/skills/adaptive-presentation/scripts/render_pptx.py \
  <absolute-output>/<deck>.pptx --reuse-pdf <work-dir>/verify/qa/<deck>.pdf \
  --slides 8,16 --keep-slide-images --out <work-dir>/qa-detail

unzip -t <absolute-output>/<deck>.pptx
```

`--reuse-pdf`는 sibling manifest의 PPTX·PDF SHA-256과 현재 파일이 모두 일치할 때만 PDF를 재사용한다.
PPTX를 수정하거나 PDF가 달라진 뒤에는 기존 PDF를 재사용하지 않는다. 새 PDF로 변환한 뒤 수정 영향에
맞는 범위를 다시 렌더한다.
렌더러는 비어 있지 않은 일반 `--out` 디렉터리를 덮어쓰지 않는다. 각 QA 단계에는 전용 디렉터리를
사용하고, 기존 Runner 소유 디렉터리만 안전하게 초기화한다.
