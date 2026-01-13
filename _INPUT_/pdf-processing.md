# PDF에서 LaTeX 형식 문제 추출 - 완전 가이드

## ✅ 기본 원칙

**Claude는 PDF를 시각적으로 읽을 수 있습니다** (multimodal capability)
- OCR 도구 불필요
- Claude가 PDF 내용을 보고 직접 LaTeX 형식으로 작성
- 수학 기호를 정확하게 변환 (`$...$`, `\mathrm{...}`, `\angle`, etc.)

---

## 📋 전체 작업 순서

### 1단계: PDF 파일 확인 및 분석

```bash
# PDF 파일 확인
ls -la _INPUT_/

# 파일명으로 구분:
# - 문제 파일: 2025_3.pdf (또는 *_sol이 아닌 파일)
# - 해설 파일: 2025_3_sol.pdf (또는 *_solution.pdf)
```

**⚠️ 주의사항:**
- 문제 파일과 해설 파일을 정확히 구분할 것
- 페이지 수와 내용을 먼저 확인

### 2단계: Claude가 PDF 읽고 LaTeX 작성

```python
# Read tool로 PDF 파일 읽기
Read(file_path="/path/to/2025_3.pdf")
```

**Claude가 직접 수행:**
1. PDF 내용을 시각적으로 확인
2. 문제 텍스트를 LaTeX 형식으로 변환
   - 수학 기호: `$...$` 또는 `\[...\]`
   - 점 이름: `\mathrm{A}`, `\mathrm{BC}` 등
   - 각도: `\angle\mathrm{ABC}`
   - 분수: `\dfrac{...}{...}`
3. Write tool로 .tex 파일 작성
   - 위치: `_OUTPUT_/`
   - 파일명: `{문제번호}.tex`

**❌ 피해야 할 실수:**
- `extract_geometry_problem.py` 스크립트를 실행하면 Claude가 만든 좋은 tex 파일이 자동 추출된 텍스트로 덮어써짐
- **LaTeX 파일은 Claude가 직접 작성하고, 스크립트는 그림 추출만 사용**

### 3단계: 이미지 위치 분석

```python
# 각 문제가 있는 페이지의 이미지 위치 확인
import fitz

pdf_path = "_INPUT_/2025_3.pdf"
doc = fitz.open(pdf_path)

for page_num in range(len(doc)):
    page = doc[page_num]
    page_dict = page.get_text("dict")

    # 이미지 위치 정보 출력
    for block in page_dict["blocks"]:
        if block["type"] == 1:  # 이미지 블록
            bbox = block["bbox"]
            print(f"bbox: ({bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f})")
            print(f"y위치: {bbox[1]:.1f} ~ {bbox[3]:.1f}")
```

**⚠️ 중요:**
- 한 페이지에 여러 문제가 있을 수 있음
- 각 문제의 그림을 y좌표로 구분
- 같은 문제에 속하는 연속된 이미지는 병합 필요

### 4단계: bbox 기반 정확한 그림 추출

```python
import fitz
from PIL import Image
import io
from pathlib import Path

def extract_image_from_bbox(page, bbox_list, output_path):
    """여러 bbox의 이미지를 추출하여 수직으로 병합"""
    images = []

    for bbox in bbox_list:
        # bbox 영역을 픽셀 이미지로 렌더링
        pix = page.get_pixmap(clip=fitz.Rect(bbox), matrix=fitz.Matrix(2, 2))  # 2배 해상도
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    # 이미지가 하나면 그대로 저장
    if len(images) == 1:
        images[0].save(output_path)
        return

    # 여러 이미지를 수직으로 병합
    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    merged = Image.new('RGB', (max_width, total_height), 'white')
    y_offset = 0
    for img in images:
        x_offset = (max_width - img.width) // 2
        merged.paste(img, (x_offset, y_offset))
        y_offset += img.height

    merged.save(output_path)

# 사용 예시
doc = fitz.open("_INPUT_/2025_3.pdf")
page = doc[6]  # 페이지 7 (0-based)

# 17번 문제: 단일 이미지
extract_image_from_bbox(
    page,
    [(164.9, 256.3, 344.7, 433.8)],
    Path("_OUTPUT_/2025_3_problem_17_figure.png")
)

# 18번 문제: 연속된 2개 이미지 병합
extract_image_from_bbox(
    page,
    [
        (467.1, 273.0, 724.8, 347.4),
        (467.1, 347.4, 724.8, 421.7)
    ],
    Path("_OUTPUT_/2025_3_problem_18_figure.png")
)
```

**장점:**
- 각 문제의 그림을 정확하게 분리
- 수직으로 연속된 이미지 자동 병합
- 고해상도 (2배 스케일)

### 5단계: LaTeX 파일에 그림 참조 추가

```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.5\textwidth]{2025_3_problem_17_figure.png}
\end{figure}
```

**⚠️ 중요 - 파일 형식:**
- ✅ **PNG 사용** - LaTeX에서 기본 지원
- ❌ **SVG 사용 금지** - LaTeX에서 기본적으로 SVG 지원 안함
- SVG가 필요하면 별도 패키지(`svg` package) 설정 필요하지만 복잡함

---

## 🔧 사용 가능한 스크립트

### 1. `extract_and_merge_figures.py`

**용도:** 페이지 전체 이미지를 자동으로 추출하고 병합
- 연속된 이미지 자동 감지
- PNG + SVG 출력

**한계:**
- 같은 페이지에 여러 문제가 있으면 분리 불가
- bbox 지정이 더 정확함

**사용법:**
```python
from extract_and_merge_figures import extract_and_merge_figures

extract_and_merge_figures(
    pdf_path='_INPUT_/2025_3.pdf',
    page_num=6,  # 0-based
    output_dir='_OUTPUT_/',
    base_name='page_07_figure'
)
```

### 2. `extract_geometry_problem.py`

**⚠️ 주의:** 이 스크립트는 **그림 추출에만 사용**
- **LaTeX 파일 작성 기능은 사용하지 말 것**
- Claude가 작성한 tex 파일을 덮어씀

**권장하지 않음** - bbox 기반 추출이 더 정확함

---

## 📂 최종 산출물

`_OUTPUT_/` 디렉토리에 저장:

```
_OUTPUT_/
├── 2025_3_problem_17.tex          # Claude가 작성한 문제 LaTeX
├── 2025_3_problem_17_figure.png   # bbox로 추출한 그림
├── 2025_3_problem_18.tex
├── 2025_3_problem_18_figure.png
├── 2025_3_solution_17.tex         # Claude가 작성한 풀이 LaTeX
├── 2025_3_solution_18.tex
└── ...
```

---

## ✅ 체크리스트

### 시작 전
- [ ] PDF 파일 확인 (문제 파일 vs 해설 파일)
- [ ] 페이지 수와 내용 확인
- [ ] 추출할 문제 번호 목록 작성

### LaTeX 파일 작성
- [ ] Claude가 PDF를 읽고 직접 LaTeX로 변환
- [ ] 수학 기호가 올바르게 변환되었는지 확인
- [ ] **스크립트로 덮어쓰지 않도록 주의**

### 그림 추출
- [ ] 각 문제의 페이지 번호 확인
- [ ] 이미지 bbox 좌표 확인
- [ ] bbox 기반으로 정확하게 추출
- [ ] 연속된 이미지는 병합
- [ ] **PNG 형식으로 저장** (SVG 아님)

### 최종 확인
- [ ] LaTeX 파일에 올바른 그림 파일명 참조
- [ ] 그림 크기 조정 (`width=0.5\textwidth` 등)
- [ ] 불필요한 임시 파일 삭제

---

## 🚨 흔한 실수와 해결법

### 1. "같은 페이지에 여러 문제가 있어요"
**해결:** bbox를 정확하게 지정하여 각 문제의 그림을 개별 추출

### 2. "LaTeX에서 SVG 파일을 못 찾아요"
**해결:** PNG 파일 사용. `\includegraphics{file.png}`

### 3. "자동 추출 스크립트가 그림을 잘못 분리했어요"
**해결:** 스크립트 사용 중단하고 bbox 기반 수동 추출

### 4. "Claude가 만든 tex 파일이 덮어써졌어요"
**해결:**
- LaTeX 파일은 Claude가 직접 작성
- 스크립트는 그림 추출만 사용
- 백업 필수

### 5. "연속된 이미지가 분리되어 나왔어요"
**해결:** bbox_list에 여러 좌표를 넣어서 자동 병합

---

## 💡 Best Practices

1. **항상 PDF를 먼저 분석**
   - 페이지 구조 파악
   - 문제 위치 확인
   - 이미지 개수와 위치 확인

2. **Claude의 PDF 읽기 능력 활용**
   - 가장 정확한 LaTeX 변환
   - 수학 기호 자동 처리
   - 문맥 이해

3. **bbox 기반 정확한 추출**
   - 자동화보다 정확도 우선
   - 각 문제별로 개별 처리
   - 좌표 기록 보관

4. **PNG 사용**
   - LaTeX 호환성
   - 고해상도 (2x matrix)
   - 파일 크기 적절

5. **버전 관리**
   - 중요 파일은 백업
   - 스크립트 실행 전 확인
   - Git 커밋 활용

---

## 📝 예제: 2025년 3월 고1 수학 (실제 작업 사례)

### 파일 확인
```bash
_INPUT_/2025_3.pdf         # 문제 파일 (12페이지)
_INPUT_/2025_3_sol.pdf     # 해설 파일 (5페이지)
```

### 문제 위치
- 17번, 18번: 페이지 7 (0-based: 6)
- 21번: 페이지 9 (0-based: 8)
- 27번, 28번: 페이지 11 (0-based: 10)
- 30번: 페이지 12 (0-based: 11)

### 그림 추출
각 문제별로 bbox 좌표를 정확히 지정하여 추출

### 결과물
- 6개 문제 LaTeX 파일 (Claude 작성)
- 6개 풀이 LaTeX 파일 (Claude 작성)
- 6개 그림 PNG 파일 (bbox 추출)

**성공 요인:**
- Claude가 LaTeX 직접 작성
- bbox 기반 정확한 그림 추출
- PNG 형식 사용
