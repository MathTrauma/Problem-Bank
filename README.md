# 기하 문제 관리 시스템

KMO 중등부 기하 문제 웹 애플리케이션

## 🌐 웹사이트

**https://mathtrauma.github.io/Problem-Bank/**

## 📚 문서

- **[WORKFLOW.md](WORKFLOW.md)** - 문제 입력/수정 및 전체 워크플로우 가이드
- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - 빌드 시스템 상세 설명
- **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** - 배포 가이드

## ✨ 주요 기능

- 📝 **문제 관리**: LaTeX 기반 문제 입력 및 관리
- 🎨 **TikZ 지원**: TikZ 그림 자동 SVG 변환
- 💡 **풀이 시스템**: 드래그 가능한 annotation box로 풀이 설명 표시
- 🔍 **검색 기능**: 문제 번호, 출처 검색
- 📂 **분류 시스템**: KMO 중등부 1차 / 출처 미분류 / 기타
- 🚀 **CDN 배포**: Cloudflare R2 + Workers를 통한 전 세계 배포

## 🛠 기술 스택

- **프론트엔드**: Vanilla JS, CSS3, MathJax
- **빌드**: Python 3, pdflatex, pdf2svg
- **배포**: GitHub Pages, Cloudflare R2/Workers
- **버전 관리**: Git, GitHub

## 🚀 빠른 시작

### 문제 추가하기

1. 문제 파일 작성: `web_app/data/problems/XXX.tex`
2. 풀이 파일 작성 (선택): `web_app/data/problems/solutions/XXX_solution.tex`
3. 빌드: `python3 ___scripts/build_incremental.py`
4. R2 업로드: `./upload_r2.sh`
5. Git 푸시: `git push origin main`

**자세한 내용은 [WORKFLOW.md](WORKFLOW.md)를 참조하세요.**

## 📊 현황

- **총 문제 수**: 265개
- **풀이 있는 문제**: ~30%
- **TikZ 그림**: 자동 SVG 변환 지원

## 📁 프로젝트 구조

```
.
├── web_app/                    # 프론트엔드
│   ├── index.html
│   ├── css/styles.css
│   ├── js/
│   │   ├── app.js
│   │   ├── data.js
│   │   ├── render.js
│   │   └── utils.js
│   └── data/
│       ├── problems/           # 원본 .tex 파일
│       │   ├── XXX.tex
│       │   └── solutions/
│       │       └── XXX_solution.tex
│       └── problems_metadata.json
├── ___scripts/                 # 빌드 스크립트
│   ├── build_incremental.py
│   ├── extract_problems.py
│   └── upload_to_r2.py
├── dist/                       # 빌드 결과 (Git 무시)
│   ├── problems/
│   ├── svg/
│   └── metadata.json
└── cloudflare-workers/         # CDN Workers
    └── src/index.js
```

## 🔧 개발 환경 설정

### 필수 도구

- Python 3.x
- pdflatex (TeX Live)
- pdf2svg
- Node.js (wrangler)

### 설치

```bash
# macOS
brew install texlive pdf2svg node

# Python 패키지
pip3 install boto3
```

## 📝 라이선스

MIT License

## 👤 문의

- **웹사이트**: https://mathtrauma.com
- **GitHub**: https://github.com/MathTrauma/Problem-Bank

---

**최종 업데이트**: 2025-12-25
