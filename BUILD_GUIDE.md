# 빌드 및 배포 가이드

> **빠른 시작은 [WORKFLOW.md](WORKFLOW.md)를 참조하세요.**

## 빌드 시스템 개요 (2025-12-25 업데이트)

### 핵심 원칙
✅ **원본 파일 보존** - `.tex` 파일은 절대 수정하지 않음
✅ **증분 빌드** - 변경된 파일만 처리 (파일 해시 기반)
✅ **개별 JSON** - 문제별로 분리하여 lazy loading 지원
✅ **R2 CDN** - Cloudflare Workers를 통한 전 세계 배포
✅ **풀이 텍스트** - TikZ와 설명 텍스트 분리 추출

---

## 빌드 프로세스

### 1. 증분 빌드 (로컬)

```bash
python3 ___scripts/build_incremental.py
```

**기능**:
- 원본 `.tex` 파일 읽기 (수정 안 함)
- TikZ → SVG 변환 (solution 파일의 tikzpicture)
- solution 텍스트 추출 (TikZ 제외, 답안 제외)
- 개별 JSON 파일 생성 (`dist/problems/`)
- 파일 해시 기반 증분 처리 (변경된 파일만)

**출력**:
```
dist/
├── problems/
│   ├── 001.json      # content, solution, solution_text, svg_files
│   ├── 002.json
│   └── ...
├── svg/
│   ├── 001_fig1.svg  # TikZ → SVG 변환 결과
│   ├── 018_fig1.svg
│   ├── 018_fig2.svg  # 여러 그림 지원
│   └── ...
└── metadata.json     # 전체 문제 목록 (메타데이터만)
```

### 2. R2 업로드

#### 방법 1: 자동 스크립트 (권장)

```bash
./upload_r2.sh
```

**기능**:
- wrangler를 사용한 R2 업로드
- 진행 상황 표시 (50개마다)
- metadata.json, problems/*.json, svg/*.svg 모두 업로드

#### 방법 2: Python 스크립트

**환경변수 설정 (필수)**:
```bash
export R2_ACCOUNT_ID="your_account_id"
export R2_BUCKET_NAME="your_bucket_name"
export R2_ACCESS_KEY_ID="your_access_key"
export R2_SECRET_ACCESS_KEY="your_secret_key"
```

**실행**:
```bash
python3 ___scripts/upload_to_r2.py
```

**기능**:
- 변경된 파일만 R2에 업로드
- 파일 해시 기반 증분 업로드
- (주의: SSL 에러 발생 가능 - wrangler 사용 권장)

### 3. Cloudflare Workers CDN

**배포**:
```bash
cd cloudflare-workers
npx wrangler deploy
```

**CDN URL**:
```
https://r2-cdn.painfultrauma.workers.dev/metadata.json
https://r2-cdn.painfultrauma.workers.dev/problems/001.json
https://r2-cdn.painfultrauma.workers.dev/svg/001_fig1.svg
```

---

## 환경변수 설정

### 필수 환경변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `R2_ACCOUNT_ID` | Cloudflare Account ID | c1e4805... |
| `R2_BUCKET_NAME` | R2 버킷 이름 | your-bucket |
| `R2_ACCESS_KEY_ID` | R2 Access Key | 6faa32e... |
| `R2_SECRET_ACCESS_KEY` | R2 Secret Key | 3708723... |

### 설정 방법

**macOS/Linux (임시 설정):**
```bash
export R2_ACCOUNT_ID="your_account_id"
export R2_BUCKET_NAME="your_bucket_name"
export R2_ACCESS_KEY_ID="your_access_key"
export R2_SECRET_ACCESS_KEY="your_secret_key"
```

**영구 설정 (~/.zshrc 또는 ~/.bashrc):**
```bash
# ~/.zshrc 파일에 추가
echo 'export R2_ACCOUNT_ID="your_account_id"' >> ~/.zshrc
echo 'export R2_BUCKET_NAME="your_bucket_name"' >> ~/.zshrc
echo 'export R2_ACCESS_KEY_ID="your_access_key"' >> ~/.zshrc
echo 'export R2_SECRET_ACCESS_KEY="your_secret_key"' >> ~/.zshrc

# 설정 적용
source ~/.zshrc
```

**확인:**
```bash
echo $R2_ACCOUNT_ID
echo $R2_BUCKET_NAME
```

---

## 웹앱 구조

### 데이터 로드 방식

**이전** (단일 번들):
```javascript
fetch('problems_bundle.json')  // 전체 로드 (220KB+)
```

**현재** (Lazy Loading):
```javascript
fetch('https://r2-cdn.../metadata.json')       // 메타데이터만 (63KB)
fetch('https://r2-cdn.../problems/001.json')    // 필요할 때만 로드 (~1KB)
```

### 파일 구조

```
web_app/
├── index.html
├── css/styles.css
├── js/
│   ├── app.js         # 앱 초기화
│   ├── data.js        # R2 CDN 데이터 로드
│   ├── render.js      # UI 렌더링
│   └── utils.js       # 유틸리티
└── data/
    ├── problems/      # 원본 파일 (Git 추적)
    └── problems_metadata.json
```

---

## 디렉토리 설명

| 디렉토리 | 용도 | Git 추적 |
|---------|------|---------|
| `web_app/data/problems/` | 원본 `.tex` 파일 | ✅ 추적 |
| `dist/` | 빌드 결과물 | ❌ 무시 |
| `cloudflare-workers/` | Workers 스크립트 | ✅ 추적 |
| `___scripts/` | 빌드 스크립트 | ✅ 추적 |

---

## 파일 변경 시 워크플로우

> **자세한 내용은 [WORKFLOW.md](WORKFLOW.md)를 참조하세요.**

### 문제 추가/수정 (Quick Reference)

1. **원본 파일 수정**:
   ```
   web_app/data/problems/267.tex              # 문제 본문
   web_app/data/problems/solutions/267_solution.tex  # 풀이
   ```

2. **빌드**:
   ```bash
   python3 ___scripts/build_incremental.py
   ```

3. **R2 업로드**:
   ```bash
   ./upload_r2.sh
   ```

4. **Git 푸시**:
   ```bash
   git add .
   git commit -m "feat: 새로운 문제 추가"
   git push origin main
   ```

5. **완료!**
   - CDN: 즉시 반영
   - GitHub Pages: 1-2분 후 자동 배포

---

## 주요 스크립트

| 스크립트 | 기능 |
|---------|------|
| `build_incremental.py` | 증분 빌드 (TikZ → SVG, solution_text 추출, JSON 생성) |
| `upload_r2.sh` | wrangler를 통한 R2 일괄 업로드 (권장) |
| `upload_to_r2.py` | Python boto3를 통한 R2 증분 업로드 |
| `extract_problems.py` | 원본 .tex 파일에서 문제 추출 및 메타데이터 생성 |
| `test_r2_upload.py` | R2 연결 테스트 |

---

## 캐시 파일

| 파일 | 용도 |
|------|------|
| `.build_cache.json` | 빌드 캐시 (파일 해시) |
| `.upload_cache.json` | 업로드 캐시 (파일 해시) |

**주의**: Git에서 무시됨 (`.gitignore`)

---

## 문제 해결

### Q: SVG가 안 보여요
**A**: R2 업로드 확인
```bash
curl https://r2-cdn.painfultrauma.workers.dev/svg/001_fig1.svg
```

### Q: 빌드가 너무 오래 걸려요
**A**: 증분 빌드가 작동 중입니다. 변경된 파일만 처리합니다.

### Q: 원본 파일이 수정되었어요
**A**: `.bak` 백업 파일에서 복구:
```bash
cp file.tex.bak file.tex
```

---

## 참고 문서

- **[WORKFLOW.md](WORKFLOW.md)** - 전체 워크플로우 및 할 일 목록
- **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** - 배포 가이드
- `troubles.xml` - 해결된 문제점
- `cloudflare-workers/README.md` - Workers 배포 가이드
- `.github/workflows/deploy.yml` - GitHub Actions 설정

---

**최종 업데이트**: 2025-12-25
**문의**: mathtrauma.com
