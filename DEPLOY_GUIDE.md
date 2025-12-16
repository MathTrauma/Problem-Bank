# GitHub Actions 배포 가이드

이 가이드는 GitHub Actions를 사용하여 기하 문제 웹사이트를 GitHub Pages에 자동 배포하는 방법을 설명합니다.

## 빠른 시작 (5분 완료)

### 1. GitHub 저장소 생성 및 푸시

```bash
cd /Users/_Math_\(수업\)/중등_경시수업/__Geometry

# Git 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Initial commit"

# GitHub 저장소와 연결
git remote add origin https://github.com/[USERNAME]/[REPO].git
git branch -M main
git push -u origin main
```

### 2. GitHub Pages 설정

1. GitHub 저장소로 이동
2. **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Pages** 클릭
4. **Source** 섹션에서:
   - ⚠️ **중요!** "GitHub Actions" 선택 (Branch가 아님)
5. Save

### 3. 배포 확인

1. **Actions** 탭으로 이동
2. "Deploy to GitHub Pages" workflow 실행 확인
3. 완료되면 녹색 체크 표시
4. `https://[USERNAME].github.io/[REPO]/` 에서 확인

## Workflow 동작 방식

### 자동 트리거

다음 파일/폴더가 변경되어 `main` 브랜치에 푸시되면 자동 실행:

- `problems/**` - 문제 파일들
- `___scripts/problems_metadata.json` - 메타데이터
- `web_app/**` - 웹 앱 파일들
- `.github/workflows/deploy.yml` - Workflow 파일 자체

### 수동 실행

GitHub 웹사이트에서:
1. Actions 탭
2. "Deploy to GitHub Pages" 선택
3. "Run workflow" 버튼 클릭
4. "Run workflow" 확인

## Workflow 상세 단계

### Build Job

1. **Checkout repository** - 코드 다운로드
2. **Setup Python** - Python 3.11 설치
3. **Copy data to web_app** - 문제 데이터 복사
   - `problems/` → `web_app/data/problems/`
   - `___scripts/problems_metadata.json` → `web_app/data/`
4. **Build data bundle** - `build_data.py` 실행
   - 모든 문제를 `problems_bundle.json`으로 통합
5. **Prepare deployment files** - 배포 파일 준비
   - `index.html`
   - `problems_bundle.json`
6. **Upload artifact** - 빌드 결과 업로드

### Deploy Job

1. **Deploy to GitHub Pages** - 빌드된 파일을 GitHub Pages에 배포

## 일반적인 사용 시나리오

### 시나리오 1: 새 문제 추가

```bash
# 1. 문제 파일 생성 (___scripts/extract_problems.py 사용)
cd ___scripts
python3 extract_problems.py

# 2. Git commit & push
cd ..
git add problems/
git add ___scripts/problems_metadata.json
git commit -m "Add new problems"
git push

# 3. GitHub Actions가 자동으로 배포!
```

### 시나리오 2: 문제 수정

```bash
# 1. 문제 파일 수정
vim problems/042.tex

# 2. Git commit & push
git add problems/042.tex
git commit -m "Fix problem 42"
git push

# 3. 자동 배포!
```

### 시나리오 3: 웹 UI 수정

```bash
# 1. index.html 수정
vim web_app/index.html

# 2. Git commit & push
git add web_app/index.html
git commit -m "Update UI design"
git push

# 3. 자동 배포!
```

### 시나리오 4: 풀이 추가/수정

```bash
# 1. 풀이 파일 수정
vim problems/solutions/042_solution.tex

# 2. Git commit & push
git add problems/solutions/042_solution.tex
git commit -m "Add solution for problem 42"
git push

# 3. 자동 배포!
```

## 문제 해결

### Workflow가 실행되지 않음

**원인**: GitHub Pages 설정이 "Branch"로 되어 있음

**해결**:
1. Settings → Pages
2. Source를 "GitHub Actions"로 변경

### 403 Error: Resource not accessible by integration

**원인**: Workflow 권한 부족

**해결**:
1. Settings → Actions → General
2. "Workflow permissions" 섹션에서
3. "Read and write permissions" 선택
4. Save

### Build 성공했지만 페이지에 접속 안 됨

**원인**: 배포 URL 확인 필요

**해결**:
1. Actions 탭에서 최근 workflow 클릭
2. Deploy job → Deploy to GitHub Pages 단계
3. 출력에서 배포 URL 확인
4. 일반적으로: `https://[USERNAME].github.io/[REPO]/`

### Python 스크립트 오류

**원인**: `build_data.py`에서 에러 발생

**해결**:
1. 로컬에서 먼저 테스트:
   ```bash
   cd web_app
   python3 build_data.py
   ```
2. 에러 수정 후 다시 푸시

## Workflow 커스터마이징

### Python 버전 변경

`.github/workflows/deploy.yml`:

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'  # 원하는 버전
```

### 배포 파일 추가

추가 파일이 필요하면:

```yaml
- name: Prepare deployment files
  run: |
    mkdir -p _site
    cp web_app/index.html _site/
    cp web_app/problems_bundle.json _site/
    cp web_app/custom.css _site/  # 추가 파일
    cp -r web_app/images _site/   # 폴더 추가
```

### 트리거 경로 추가

다른 파일 변경 시에도 트리거하려면:

```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'problems/**'
      - '___scripts/problems_metadata.json'
      - 'web_app/**'
      - 'custom_folder/**'  # 추가 경로
```

## 비용

GitHub Actions는 **공개 저장소에서 무료**입니다.
- 무제한 실행 시간
- 무제한 저장 공간 (artifacts)
- GitHub Pages 호스팅도 무료

비공개 저장소는 월 2,000분 무료 (개인 계정 기준).

## 참고 링크

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [GitHub Pages 문서](https://docs.github.com/en/pages)
- [actions/deploy-pages](https://github.com/actions/deploy-pages)
- [actions/upload-pages-artifact](https://github.com/actions/upload-pages-artifact)
