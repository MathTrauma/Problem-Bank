# GitHub Pages 배포 가이드

## 개요

이 프로젝트는 GitHub Pages에 배포할 수 있는 순수 정적 웹사이트입니다.
Flask 백엔드를 사용하지 않고, 모든 데이터를 JSON 파일로 번들링하여 클라이언트 사이드에서 렌더링합니다.

## 프로젝트 구조

```
web_app/
├── index.html                  # 메인 HTML 파일
├── problems_bundle.json        # 모든 문제 데이터 (번들)
├── build_data.py              # 데이터 번들 생성 스크립트
├── data/                      # 원본 데이터 (배포하지 않음)
│   ├── problems/
│   │   ├── 001.tex ~ 184.tex
│   │   └── solutions/
│   │       └── *_solution.tex
│   └── problems_metadata.json
├── app.py                     # 로컬 개발용 Flask 앱 (배포하지 않음)
└── README_GITHUB.md           # 이 파일
```

## 배포 전 준비

### 1. 데이터 번들 생성

문제 데이터를 업데이트했다면, 다시 번들을 생성해야 합니다:

```bash
cd web_app
python3 build_data.py
```

이 명령어는 `problems_bundle.json` 파일을 생성합니다 (약 176KB).

### 2. 로컬 테스트

로컬에서 테스트하려면 간단한 HTTP 서버를 실행하세요:

```bash
# Python 3 사용
cd web_app
python3 -m http.server 8000

# 브라우저에서 http://localhost:8000 열기
```

또는 Flask 앱으로 테스트:

```bash
python3 app.py
# http://localhost:5000
```

## GitHub Pages 배포 방법

### 방법 1: GitHub UI 사용

1. **GitHub 저장소 생성**
   - GitHub에 새 저장소 생성 (예: `geometry-problems`)

2. **파일 업로드**
   ```bash
   cd web_app
   git init
   git add index.html problems_bundle.json
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/[USERNAME]/geometry-problems.git
   git push -u origin main
   ```

3. **GitHub Pages 설정**
   - 저장소 Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main` / `/ (root)`
   - Save

4. **배포 완료**
   - 몇 분 후 `https://[USERNAME].github.io/geometry-problems/` 에서 접근 가능

### 방법 2: 서브 디렉토리로 배포

기존 저장소의 서브 디렉토리로 배포하려면:

1. **루트에 필요한 파일만 복사**
   ```bash
   # 프로젝트 루트로 이동
   cd /Users/_Math_\(수업\)/중등_경시수업/__Geometry

   # docs 폴더 생성 (GitHub Pages가 docs 폴더를 지원)
   mkdir -p docs
   cp web_app/index.html docs/
   cp web_app/problems_bundle.json docs/
   ```

2. **GitHub에 푸시**
   ```bash
   git add docs/
   git commit -m "Add GitHub Pages site"
   git push
   ```

3. **GitHub Pages 설정**
   - Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main` / `/docs`
   - Save

### 방법 3: GitHub Actions 사용 (자동 배포 - 추천!)

가장 편리한 방법입니다. 문제 데이터가 변경되면 자동으로 빌드하고 배포합니다.

1. **전체 프로젝트를 GitHub에 푸시**
   ```bash
   cd /Users/_Math_\(수업\)/중등_경시수업/__Geometry
   git init
   git add .
   git commit -m "Initial commit with GitHub Actions"
   git branch -M main
   git remote add origin https://github.com/[USERNAME]/[REPO].git
   git push -u origin main
   ```

2. **GitHub Pages 설정**
   - 저장소 Settings → Pages
   - Source: **"GitHub Actions"** 선택 (중요!)
   - Save

3. **완료!**
   - 푸시하면 자동으로 workflow가 실행됩니다
   - Actions 탭에서 배포 진행 상황 확인 가능
   - 몇 분 후 `https://[USERNAME].github.io/[REPO]/` 에서 접근 가능

**자동 트리거:**
- `problems/` 폴더 변경 시
- `___scripts/problems_metadata.json` 변경 시
- `web_app/` 폴더 변경 시
- 수동 실행 (Actions 탭에서 "Run workflow" 클릭)

**장점:**
- 로컬에서 `build_data.py` 실행 불필요
- 문제 파일만 수정하고 푸시하면 자동 빌드
- 항상 최신 상태 유지

## 중요 사항

### ✅ 장점
- 서버 없이 무료 호스팅
- 빠른 로딩 속도 (정적 파일)
- 안정적인 서비스 (GitHub 인프라)
- HTTPS 자동 지원

### ⚠️ 제한사항
- **읽기 전용**: 데이터 수정 불가
- 문제 데이터 업데이트 시 다음 과정 필요:
  1. 로컬에서 `build_data.py` 실행
  2. `problems_bundle.json` 재생성
  3. Git push

### 💡 데이터 업데이트 방법

#### GitHub Actions 사용 시 (추천)

1. **로컬에서 문제 수정**
   ```bash
   # problems/ 폴더에서 .tex 파일 수정
   # 또는 ___scripts/problems_metadata.json 수정
   ```

2. **Git push만 하면 끝!**
   ```bash
   git add .
   git commit -m "Update problems"
   git push
   ```

3. **자동으로 빌드 & 배포** (몇 분 소요)
   - GitHub Actions가 자동으로 `build_data.py` 실행
   - `problems_bundle.json` 생성
   - GitHub Pages에 자동 배포

#### 수동 배포 시

1. **로컬에서 문제 수정**
   ```bash
   # problems/ 폴더에서 .tex 파일 수정
   ```

2. **번들 재생성**
   ```bash
   cd web_app
   python3 build_data.py
   ```

3. **Git push**
   ```bash
   git add .
   git commit -m "Update problems"
   git push
   ```

## 커스터마이징

### 1. 스타일 변경

`index.html`의 `<style>` 태그 안에서 CSS 수정

### 2. 기능 추가

`index.html`의 `<script>` 태그 안에서 JavaScript 수정

### 3. MathJax 설정

현재 MathJax 3를 사용 중입니다. 설정을 변경하려면 `<head>` 섹션 수정.

## 문제 해결

### 1. 404 Error

- GitHub Pages 설정에서 올바른 브랜치와 폴더를 선택했는지 확인
- `index.html`이 루트 또는 `/docs` 폴더에 있는지 확인

### 2. JSON 로딩 실패

- `problems_bundle.json`이 `index.html`과 같은 폴더에 있는지 확인
- 브라우저 콘솔(F12)에서 네트워크 탭 확인

### 3. MathJax 렌더링 안 됨

- 인터넷 연결 확인 (MathJax CDN 사용)
- 브라우저 콘솔에서 에러 확인

### 4. 한글 깨짐

- `index.html`의 `<meta charset="UTF-8">` 확인
- 파일이 UTF-8로 저장되어 있는지 확인

## 로컬 개발

로컬에서 Flask 앱으로 개발하고 싶다면:

```bash
cd web_app
python3 app.py
```

이렇게 하면 문제 편집, 풀이 저장 등의 기능을 사용할 수 있습니다.
(단, GitHub Pages에 배포된 버전에서는 이 기능들이 작동하지 않습니다)

## 참고 링크

- [GitHub Pages 문서](https://docs.github.com/en/pages)
- [MathJax 문서](https://docs.mathjax.org/)
- [JSON 데이터 검증](https://jsonlint.com/)
