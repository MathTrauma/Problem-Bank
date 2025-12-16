# 문제 관리 가이드

새로운 문제를 추가하고 관리하는 방법을 설명합니다.

## 목차

1. [새 문제 추가하기](#새-문제-추가하기)
2. [문제 파일 직접 작성하기](#문제-파일-직접-작성하기)
3. [풀이 추가하기](#풀이-추가하기)
4. [메타데이터 관리](#메타데이터-관리)
5. [문제 포맷팅](#문제-포맷팅)
6. [웹사이트 배포](#웹사이트-배포)

---

## 새 문제 추가하기

### 방법 1: 대화형 스크립트 사용 (추천)

가장 쉬운 방법입니다. 스크립트가 모든 과정을 안내합니다.

```bash
cd /Users/_Math_\(수업\)/중등_경시수업/__Geometry/___scripts
python3 add_new_problem.py
```

스크립트가 다음을 자동으로 처리합니다:
- 문제 번호 자동 할당 (다음 번호)
- 문제 파일 생성 (`problems/NNN.tex`)
- 풀이 파일 생성 (선택적, `problems/solutions/NNN_solution.tex`)
- 메타데이터 입력 및 저장
- 백업 자동 생성

**입력 항목:**
- 출처: 예) `35회(2021) KMO 중등부 1차 4번`
- 답안: 예) `100`
- 카테고리: 예) `원, 삼각형`
- 난이도: `1-5` (1=매우 쉬움, 5=매우 어려움)
- 태그: 예) `피타고라스, 원의 성질`
- 메모: 추가 정보
- 문제 내용: LaTeX 형식

**예시:**

```
문제 번호: 217
출처: 30회(2016) KMO 중등부 1차 5번
답안: 144
카테고리: 원
난이도: 4
태그: 원의 성질, 접선
메모:

문제 내용:
반지름이 $r$ 인 원 $O$ 가 있다.
점 $P$ 에서 원에 그은 접선의 길이는 $2r$ 이다.
선분 $OP$ 의 길이를 구하여라.
```

### 방법 2: 빠른 추가 (스크립트용)

명령줄에서 직접 추가:

```bash
python3 add_new_problem.py \
  --id 217 \
  --source "30회(2016) KMO 중등부 1차 5번" \
  --content "반지름이 \$r\$ 인 원 \$O\$ 가 있다..."
```

---

## 문제 파일 직접 작성하기

### 파일 생성

```bash
cd problems
touch 217.tex
```

### 템플릿

```latex
% Problem ID: 217
% Source: 30회(2016) KMO 중등부 1차 5번
% Created: 2025-12-16

\numbering 반지름이 $r$ 인 원 $O$ 가 있다.
점 $P$ 에서 원에 그은 접선의 길이는 $2r$ 이다.
선분 $OP$ 의 길이를 구하여라.
```

### 작성 규칙

1. **수식 표기**
   - Inline math: `$...$`
   - Display math: `$$...$$`
   - 수식 뒤에 한글/영문이 오면 공백 추가: `$AB$ 의 길이`

2. **문장 구분**
   - 마침표(`.`) 다음에는 줄바꿈
   - 물음표(`?`), 느낌표(`!`) 뒤에도 줄바꿈 권장

3. **LaTeX 명령어**
   - `\numbering`: 문제 번호 표시 (자동)
   - `\\`: 줄바꿈
   - `\overline{AB}`: 선분 표기
   - `\angle ABC`: 각 표기
   - `\triangle ABC`: 삼각형 표기

4. **TikZ 그림**
   ```latex
   \begin{center}
   \begin{tikzpicture}
   % 그림 코드
   \end{tikzpicture}
   \end{center}
   ```

### 예시

```latex
% Problem ID: 217
% Source: 30회(2016) KMO 중등부 1차 5번

\numbering 반지름이 $r$ 인 원 $O$ 가 있다.
점 $P$ 에서 원에 그은 접선의 길이는 $2r$ 이다.
선분 $OP$ 의 길이를 구하여라.

\begin{center}
\begin{tikzpicture}[scale=0.8]
  \draw (0,0) circle (2);
  \draw (0,0) node[below left] {$O$};
  \draw (0,0) -- (4,0) node[right] {$P$};
\end{tikzpicture}
\end{center}
```

---

## 풀이 추가하기

### 풀이 파일 생성

```bash
cd problems/solutions
touch 217_solution.tex
```

### 템플릿

```latex
% Solution for Problem 217
% Created: 2025-12-16

원의 중심 $O$ 에서 접점까지의 거리를 $r$ 이라 하면, 피타고라스 정리에 의해
$$OP^2 = r^2 + (2r)^2 = 5r^2$$
따라서 $OP = r\sqrt{5}$ 이다.
```

### 작성 규칙

풀이도 문제와 동일한 LaTeX 규칙을 따릅니다.

---

## 메타데이터 관리

### 자동 업데이트 (스크립트 사용 시)

`add_new_problem.py` 스크립트를 사용하면 `___scripts/problems_metadata.json`이 자동으로 업데이트됩니다.

### 수동 업데이트

직접 파일을 작성한 경우, 메타데이터를 수동으로 추가해야 합니다.

**파일 위치:** `___scripts/problems_metadata.json`

**추가 예시:**

```json
{
  "total_problems": 217,
  "problems": [
    {
      "id": "217",
      "source": "30회(2016) KMO 중등부 1차 5번",
      "answer": "r√5",
      "category": "원",
      "difficulty": 4,
      "tags": ["원의 성질", "접선", "피타고라스"],
      "note": "",
      "has_tikz": true,
      "has_solution": true,
      "source_file": "manually_added_20251216"
    }
  ]
}
```

**필드 설명:**

- `id`: 문제 번호 (3자리 문자열)
- `source`: 출처
- `answer`: 답안
- `category`: 카테고리
- `difficulty`: 난이도 (1-5)
- `tags`: 태그 배열
- `note`: 메모
- `has_tikz`: TikZ 그림 포함 여부 (boolean)
- `has_solution`: 풀이 존재 여부 (boolean)
- `source_file`: 원본 파일명

---

## 문제 포맷팅

모든 문제 파일을 자동으로 포맷팅할 수 있습니다.

### 포맷팅 규칙

1. **마침표 뒤 줄바꿈**
   - `문장1. 문장2` → `문장1.\n문장2`

2. **수식 뒤 공백**
   - `$AB$의` → `$AB$ 의`

3. **연속 빈 줄 제거**
   - 최대 1개의 빈 줄만 허용

### 사용법

**Dry-run (미리보기):**

```bash
cd ___scripts
python3 format_problem_files.py --dry-run
```

**실제 포맷팅:**

```bash
python3 format_problem_files.py
```

**단일 파일만:**

```bash
python3 format_problem_files.py --file 217.tex
```

---

## 웹사이트 배포

### 로컬 테스트

1. **데이터 번들 생성**
   ```bash
   cd web_app
   python3 build_data.py
   ```

2. **로컬 서버 실행**
   ```bash
   http-server -p 8000
   ```

3. **브라우저에서 확인**
   - http://localhost:8000

### GitHub Pages 자동 배포

1. **변경사항 커밋**
   ```bash
   git add problems/217.tex
   git add problems/solutions/217_solution.tex
   git add ___scripts/problems_metadata.json
   git commit -m "Add problem 217"
   git push
   ```

2. **자동 배포**
   - GitHub Actions가 자동으로:
     - `build_data.py` 실행
     - `problems_bundle.json` 생성
     - GitHub Pages에 배포

3. **확인**
   - 몇 분 후 https://mathtrauma.github.io/Problem-Bank/ 에서 확인

---

## 전체 워크플로우 (추천)

### 새 문제 추가 → 배포

```bash
# 1. 대화형으로 문제 추가
cd ___scripts
python3 add_new_problem.py

# 2. 생성된 파일 확인 및 편집
vim ../problems/217.tex
vim ../problems/solutions/217_solution.tex

# 3. 포맷팅 (선택적)
python3 format_problem_files.py --file 217.tex

# 4. 로컬 테스트
cd ../web_app
python3 build_data.py
http-server -p 8000

# 5. Git 커밋 & 푸시
cd ..
git add problems/217.tex
git add problems/solutions/217_solution.tex
git add ___scripts/problems_metadata.json
git commit -m "Add problem 217: 원의 접선"
git push

# 6. GitHub에서 자동 배포 (몇 분 소요)
```

---

## 문제 해결

### 메타데이터 백업 복원

백업은 `___scripts/problems_metadata_backup_YYYYMMDD_HHMMSS.json` 형식으로 저장됩니다.

```bash
cd ___scripts
cp problems_metadata_backup_20251216_153045.json problems_metadata.json
```

### 문제 번호 충돌

이미 존재하는 번호로 추가하려고 하면:

```
⚠️  Problem 217 already exists in metadata
Update metadata? (y/N):
```

- `y`: 기존 메타데이터 업데이트
- `N`: 취소

### TikZ 그림 렌더링 안 됨

현재 웹 버전에서는 TikZ 그림이 렌더링되지 않습니다.
- 웹에서는 문제 텍스트만 표시
- LaTeX 컴파일 시에는 정상 표시

향후 TikZ → SVG 변환 기능 추가 예정.

---

## 참고

- 문제 파일: `problems/*.tex`
- 풀이 파일: `problems/solutions/*_solution.tex`
- 메타데이터: `___scripts/problems_metadata.json`
- 관리 스크립트: `___scripts/add_new_problem.py`
- 포맷팅 스크립트: `___scripts/format_problem_files.py`
- 배포 가이드: `DEPLOY_GUIDE.md`
