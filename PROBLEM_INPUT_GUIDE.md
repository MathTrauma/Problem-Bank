# 추출된 문제를 TeX 본문에서 사용하는 방법

## 📚 개요

`problems/` 폴더의 추출된 문제들(001.tex ~ 184.tex)을 효율적으로 본문에 포함하는 여러 방법을 제공합니다.

---

## 🚀 빠른 시작

### 방법 1: 매크로 사용 (추천!)

1. **프리앰블에 매크로 파일 추가:**
   ```latex
   \input{problem_macros.tex}
   ```

2. **본문에서 사용:**
   ```latex
   % 1-20번 문제
   \inputproblems{1}{20}

   % 개별 문제
   \inputproblem{15}

   % solution 포함
   \inputproblemwithsol{10}
   ```

### 방법 2: Python 스크립트로 목록 파일 생성

```bash
# 1-20번 문제 목록 생성
python3 ___scripts/generate_problem_list.py 1 20 problems_1_20.tex

# 본문에서:
# \input{problems_1_20.tex}
```

---

## 📖 상세 사용법

### 1. 매크로 사용

**`problem_macros.tex` 제공 매크로:**

```latex
% 범위 지정
\inputproblems{시작번호}{끝번호}
% 예: \inputproblems{1}{20}

% 개별 문제
\inputproblem{문제번호}
% 예: \inputproblem{15}

% solution 포함
\inputproblemwithsol{문제번호}
% 예: \inputproblemwithsol{10}
```

**완전한 예제:**

```latex
\documentclass{article}
\usepackage[korean]{babel}
\usepackage{amsmath}

% 문제 카운터 정의
\newcounter{prob}
\newcommand{\numbering}{\noindent\textbf{문제 \arabic{prob}.} }

% 매크로 파일 로드
\input{problem_macros.tex}

\begin{document}

\section{수선 문제}
\inputproblems{1}{10}

\section{특정 문제만}
\inputproblem{15}
\inputproblem{23}

\end{document}
```

---

### 2. Python 스크립트 사용

**기본 사용:**
```bash
python3 ___scripts/generate_problem_list.py 시작 끝 출력파일명
```

**옵션:**
- `--no-counter`: `\stepcounter{prob}` 제외 (numbering이 자동 증가하는 경우)
- `--with-solutions`: solution 파일도 포함
- `--macro`: 매크로 파일만 생성

**예제:**

```bash
# 1-20번 문제
python3 ___scripts/generate_problem_list.py 1 20 my_problems.tex

# solution 포함
python3 ___scripts/generate_problem_list.py 1 10 prob_with_sol.tex --with-solutions

# stepcounter 없이 (numbering이 자동으로 카운터 증가하는 경우)
python3 ___scripts/generate_problem_list.py 1 20 problems.tex --no-counter

# 매크로 파일 재생성
python3 ___scripts/generate_problem_list.py --macro
```

**생성된 파일 사용:**
```latex
\input{my_problems.tex}
```

---

### 3. 직접 입력 (소규모 작업)

**개별 입력:**
```latex
\stepcounter{prob}\input{problems/001.tex}
\stepcounter{prob}\input{problems/002.tex}
\stepcounter{prob}\input{problems/003.tex}
```

**선택적 입력:**
```latex
\stepcounter{prob}\input{problems/005.tex}
\stepcounter{prob}\input{problems/012.tex}
\stepcounter{prob}\input{problems/023.tex}
```

---

## 🛠️ 고급 사용법

### \numbering 매크로 수정

`\numbering`이 자동으로 카운터를 증가시키도록 수정하면 `\stepcounter` 불필요:

```latex
\renewcommand{\numbering}{%
    \stepcounter{prob}%
    \noindent\textbf{문제 \arabic{prob}.} %
}

% 이제 단순히:
\input{problems/001.tex}
\input{problems/002.tex}
```

### 조건부 포함

```latex
% TikZ 문제만 포함 (수동 선별 필요)
\input{problems/015.tex}  % TikZ 있음
\input{problems/017.tex}  % TikZ 있음

% 또는 메타데이터 JSON을 파싱하여 자동화
```

### 카테고리별 분류

```bash
# 메타데이터를 기반으로 카테고리별 파일 생성 (향후 구현 가능)
python3 ___scripts/generate_by_category.py --category "원" --output circle_problems.tex
```

---

## 📁 파일 구조

```
__Geometry/
├── problems/
│   ├── 001.tex ~ 184.tex          # 추출된 문제
│   └── solutions/
│       └── NNN_solution.tex        # endnote 내용
│
├── problem_macros.tex              # 매크로 파일 ⭐
├── problems_1_20.tex               # 생성된 목록 예제
├── example_usage.tex               # 사용 예제 문서
│
└── ___scripts/
    └── generate_problem_list.py    # 목록 생성 스크립트 ⭐
```

---

## 💡 팁

### 1. 문제 번호 확인
```bash
# 메타데이터에서 출처 확인
grep "Source:" problems/*.tex | grep "KMO"

# 특정 키워드 검색
grep -l "삼각형" problems/*.tex
```

### 2. 빠른 미리보기
```bash
# 문제 001-010 미리보기
for i in {1..10}; do
    echo "=== Problem $(printf %03d $i) ==="
    cat problems/$(printf %03d $i).tex | grep -v "^%"
    echo
done
```

### 3. PDF 생성
```bash
# 예제 문서 컴파일
pdflatex example_usage.tex
```

---

## ⚙️ 문제 해결

### Q: 문제 번호가 중복됩니다
A: `\setcounter{prob}{0}`으로 카운터를 초기화하세요.

### Q: 파일을 찾을 수 없습니다
A: 상대 경로를 확인하세요. TeX 파일과 problems 폴더가 같은 위치에 있어야 합니다.

### Q: 한글이 깨집니다
A: UTF-8 인코딩과 `\usepackage[korean]{babel}` 또는 `kotex`을 사용하세요.

### Q: TikZ 그림이 표시되지 않습니다
A: `\usepackage{tikz}` 및 필요한 TikZ 라이브러리를 로드하세요.

---

## 📝 예제 파일

- **`example_usage.tex`**: 모든 방법을 보여주는 완전한 예제
- **`problem_input_examples.tex`**: 다양한 방법 비교
- **`problems_1_20.tex`**: 생성된 목록 예제

---

## 🔗 관련 파일

- `PROJECT_STATUS.md` - 프로젝트 전체 현황
- `___scripts/README.md` - 스크립트 설명
- `web_app/README.md` - 웹 UI 사용법

---

**작성일**: 2024-12-14
**최종 수정**: 2024-12-14
