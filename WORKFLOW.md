# 기하 문제 관리 시스템 - 워크플로우 가이드

> 최종 업데이트: 2025-12-25

## 목차
1. [문제 입력하기](#문제-입력하기)
2. [풀이 작성하기](#풀이-작성하기)
3. [빌드 및 배포](#빌드-및-배포)
4. [할 일 목록](#할-일-목록)

---

## 문제 입력하기

### 1. 파일 위치
```
web_app/data/problems/
├── 001.tex          # 문제 본문
├── 002.tex
├── ...
└── solutions/
    ├── 001_solution.tex  # 풀이 (선택)
    ├── 002_solution.tex
    └── ...
```

### 2. 문제 파일 형식 (`XXX.tex`)

```latex
% Problem ID: 001
% Source: 제35회(2021) KMO 중등부 1차 4번
% Answer: 73
% Original file: problems/001.tex

\numbering 선분 $AB$가 지름인 반원의 호 위에 점 $C$와 $D$가 있다.
선분 $CD$를 지름으로 하는 원이 점 $E$에서 선분 $AB$에 접한다.
선분 $AB$의 중점 $O$에서 $E$까지 거리는 1이다.
$\overline{CD}=12$일 때, $(\overline{AB})^2$의 값을 구하여라.\\
```

**주요 명령어:**
- `\numbering`: 문제 번호 (자동 렌더링: "**문제.**")
- `\\`: 줄바꿈
- `$...$`: 인라인 수식
- `$$...$$`: 디스플레이 수식

### 3. 메타데이터 업데이트

문제를 추가하거나 수정한 후에는 메타데이터를 업데이트해야 합니다:

```bash
cd ___scripts
python3 extract_problems.py  # 원본 .tex 파일에서 문제 추출
```

이 스크립트는 자동으로:
- `web_app/data/problems_metadata.json` 생성/업데이트
- 출처, 답안, TikZ 사용 여부 등 메타데이터 추출

---

## 풀이 작성하기

### 1. 풀이 파일 위치
```
web_app/data/problems/solutions/001_solution.tex
```

### 2. 풀이 파일 구조

풀이 파일은 **3가지 요소**로 구성됩니다:

```latex
% Solution for Problem 001

답 73 \\


\begin{tikzpicture}[scale=0.8]
% TikZ 그림 코드
\tkzDefPoint(0,0){O}
\tkzDefPoint(-8.54,0){A}
...
\end{tikzpicture}


접점에서 접선에 수직인 직선은 원의 중심을 지난다.\\
즉, $E$ 에서 $AB$ 에 수직인 직선은 $CD$ 의 중점(원의 중심, 현의 중점)을 지난다. \\
$\overline{CD}$ 의 중점을 $M$ 이라 하자. $\overline{OM} = \sqrt{6^2 + 1}$ 을 얻는다.\\
선분 $OM$ 은 원 $O$ 의 현 $CD$ 에 수직이므로 $\overline{OC} = \sqrt{37 + 6^2}$ 을 얻는다. \\
```

#### ① 답안 (선택)
```latex
답 73 \\
```

#### ② TikZ 그림 (선택)
```latex
\begin{tikzpicture}[scale=0.8]
% 그림 코드
\end{tikzpicture}
```

**TikZ 그림은 자동으로 SVG로 변환됩니다:**
- 빌드 시 `dist/svg/001_fig1.svg` 생성
- 웹에서 "그림 보기" 버튼으로 표시

#### ③ 설명 텍스트 (핵심!)
```latex
접점에서 접선에 수직인 직선은 원의 중심을 지난다.\\
즉, $E$ 에서 $AB$ 에 수직인 직선은...
```

**설명 텍스트는 드래그 가능한 Annotation Box로 표시됩니다:**
- 💡 아이콘이 있는 황금색 박스
- 마우스로 드래그해서 위치 이동 가능
- LaTeX 수식 자동 렌더링

### 3. 여러 그림이 있는 경우

```latex
% Solution for Problem 018

두 가지 예시.

첫번째
\begin{tikzpicture}[scale=1.2]
% 첫 번째 그림
\end{tikzpicture}

두번째
\begin{tikzpicture}[scale=1.2]
% 두 번째 그림
\end{tikzpicture}
```

**결과:**
- `018_fig1.svg`, `018_fig2.svg` 생성
- "그림 1 보기", "그림 2 보기" 버튼으로 표시

---

## 빌드 및 배포

### 전체 워크플로우

```
┌─────────────┐
│ .tex 파일   │ (원본 - Git 추적)
│ 수정/추가   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 증분 빌드   │ python3 ___scripts/build_incremental.py
│             │ - TikZ → SVG 변환
│             │ - solution_text 추출
│             │ - JSON 생성
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ dist/       │ (빌드 결과물 - Git 무시)
│ problems/   │
│ svg/        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ R2 업로드   │ ./upload_r2.sh
│             │ 또는 wrangler
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ CDN 배포    │ https://r2-cdn.painfultrauma.workers.dev
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ GitHub Push │ git push origin main
│             │ → GitHub Pages 자동 배포
└─────────────┘
```

### 1. 빌드

```bash
cd /Users/_Math_\(수업\)/중등_경시수업/__Geometry

# 증분 빌드 (변경된 파일만 처리)
python3 ___scripts/build_incremental.py
```

**출력:**
```
dist/
├── problems/
│   ├── 001.json    # content, solution, solution_text, svg_files
│   ├── 002.json
│   └── ...
├── svg/
│   ├── 001_fig1.svg
│   ├── 018_fig1.svg
│   ├── 018_fig2.svg
│   └── ...
└── metadata.json   # 전체 문제 메타데이터
```

**JSON 구조 예시:**
```json
{
  "id": "001",
  "source": "35회(2021) KMO 중등부 1차 4번",
  "content": "\\numbering 선분 $AB$가...",
  "solution": "% Solution for...",
  "solution_text": "접점에서 접선에 수직인...",  ← 새로 추가!
  "svg_files": ["001_fig1.svg"]
}
```

### 2. R2 업로드 (데이터)

```bash
# 방법 1: 자동 스크립트 (권장)
./upload_r2.sh

# 방법 2: wrangler 수동 업로드
npx wrangler r2 object put kmo-geometry/metadata.json --file=dist/metadata.json
npx wrangler r2 object put kmo-geometry/problems/001.json --file=dist/problems/001.json
```

### 3. GitHub 푸시 (프론트엔드)

```bash
git add .
git commit -m "feat: 새로운 문제 추가"
git push origin main
```

**자동 배포:**
- GitHub Actions가 자동으로 실행
- `web_app/` 폴더의 HTML/CSS/JS를 GitHub Pages에 배포
- 약 1-2분 소요

### 4. 확인

- **웹사이트**: https://mathtrauma.github.io/Problem-Bank/
- **CDN**: https://r2-cdn.painfultrauma.workers.dev/metadata.json

---

## 할 일 목록

### 🔴 긴급 (High Priority)

- [ ] **문제 데이터 정리**
  - [ ] 출처 미분류 문제들 출처 확인 및 입력
  - [ ] 답안 누락된 문제들 답안 입력
  - [ ] 풀이 작성 (현재 약 30% 완료)

- [ ] **UI/UX 개선**
  - [ ] Annotation box 위치 저장 기능 (localStorage)
  - [ ] 모바일 반응형 디자인 개선
  - [ ] 다크 모드 추가

### 🟡 중요 (Medium Priority)

- [ ] **검색 기능 강화**
  - [ ] 태그 검색 추가
  - [ ] 난이도 필터링
  - [ ] 전문 검색 (문제 본문 내용 검색)

- [ ] **문제 추가 기능**
  - [ ] 웹 UI에서 직접 문제 추가 기능
  - [ ] LaTeX 미리보기 기능
  - [ ] 이미지 업로드 지원

- [ ] **통계 대시보드**
  - [ ] 연도별/카테고리별 문제 분포
  - [ ] 풀이 완료율 시각화
  - [ ] 사용자 학습 진행도 추적

### 🟢 개선 (Low Priority)

- [ ] **성능 최적화**
  - [ ] 이미지 lazy loading 개선
  - [ ] SVG 파일 압축
  - [ ] JSON 번들 최적화

- [ ] **문서화**
  - [ ] API 문서 작성
  - [ ] 기여 가이드 작성
  - [ ] 비디오 튜토리얼 제작

- [ ] **백업 시스템**
  - [ ] 자동 백업 스크립트
  - [ ] 버전 관리 개선
  - [ ] 복구 절차 문서화

### 💡 아이디어 (Future)

- [ ] **AI 기능**
  - [ ] AI 풀이 힌트 생성
  - [ ] 유사 문제 추천
  - [ ] 자동 난이도 평가

- [ ] **협업 기능**
  - [ ] 다중 사용자 지원
  - [ ] 댓글 시스템
  - [ ] 풀이 공유 기능

- [ ] **학습 도구**
  - [ ] 오답 노트
  - [ ] 학습 일정 관리
  - [ ] 성취도 배지 시스템

---

## 빠른 참조

### 자주 쓰는 명령어

```bash
# 문제 추출 (원본 .tex에서)
python3 ___scripts/extract_problems.py

# 빌드
python3 ___scripts/build_incremental.py

# R2 업로드
./upload_r2.sh

# Git 커밋 & 푸시
git add .
git commit -m "..."
git push origin main

# 로컬 웹서버 실행 (테스트용)
cd web_app
python3 -m http.server 8000
# → http://localhost:8000
```

### 파일 경로 요약

| 파일 | 경로 | Git 추적 |
|------|------|---------|
| 문제 원본 | `web_app/data/problems/XXX.tex` | ✅ |
| 풀이 원본 | `web_app/data/problems/solutions/XXX_solution.tex` | ✅ |
| 메타데이터 | `web_app/data/problems_metadata.json` | ✅ |
| 빌드 결과 | `dist/` | ❌ |
| 프론트엔드 | `web_app/index.html`, `web_app/css/`, `web_app/js/` | ✅ |
| 빌드 스크립트 | `___scripts/` | ✅ |

### 유용한 링크

- **GitHub 저장소**: https://github.com/MathTrauma/Problem-Bank
- **웹사이트**: https://mathtrauma.github.io/Problem-Bank/
- **CDN**: https://r2-cdn.painfultrauma.workers.dev
- **Cloudflare Dashboard**: https://dash.cloudflare.com

---

## 문제 해결 (Troubleshooting)

### Q1: 빌드가 안 돼요
```bash
# 캐시 삭제 후 재시도
rm .build_cache.json
python3 ___scripts/build_incremental.py
```

### Q2: SVG가 웹에서 안 보여요
```bash
# R2 업로드 확인
curl https://r2-cdn.painfultrauma.workers.dev/svg/001_fig1.svg

# 재업로드
./upload_r2.sh
```

### Q3: Annotation box가 안 나타나요
- solution 파일에 설명 텍스트가 있는지 확인
- 빌드 후 `dist/problems/XXX.json`에서 `solution_text` 필드 확인
- R2에 새 JSON 파일 업로드 확인

### Q4: LaTeX 수식이 깨져요
- MathJax 로딩 확인 (브라우저 콘솔)
- `$` 기호가 올바르게 이스케이프되었는지 확인
- 백슬래시(`\`) 두 번 사용: `\\overline` 대신 `\overline`

---

## 변경 이력

### 2025-12-25
- ✅ 풀이 설명 텍스트를 드래그 가능한 annotation box로 표시
- ✅ `solution_text` 필드 추가 (TikZ 코드 제외)
- ✅ wrangler를 통한 R2 업로드 스크립트 작성

### 2025-12-24
- ✅ 증분 빌드 시스템 구축
- ✅ TikZ → SVG 자동 변환
- ✅ Cloudflare R2 + Workers CDN 연동

### 2025-12-18
- ✅ CSS/JS 분리 및 모듈화
- ✅ 문제 분류 시스템 구축 (KMO 중등부 1차 / 출처 미분류 / 기타)

---

**문의**: mathtrauma.com
