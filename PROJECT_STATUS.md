# 기하 문제 데이터베이스 프로젝트 현황

**최종 업데이트**: 2024-12-12
**현재 상태**: ✅ 기본 구축 완료 + KMO 중등부 1차 추가, 웹 UI 가동 가능

---

## 📊 현황 요약

| 항목 | 수량 | 비고 |
|------|------|------|
| 추출된 문제 | 246개 | `problems/001.tex ~ 246.tex` |
| TikZ 그림 포함 | 68개 (28%) | 기하 도형 |
| 답안 있음 | 58개 | 메타데이터에서 추출 |
| 풀이 작성 완료 | 0개 | 웹 UI로 작성 예정 |
| 원본 TeX 파일 | 43개 + 6개 KMO | 다양한 폴더에 산재 |
| KMO 중등부 1차 | 32개 (2020-2025) | 기하 문제만 추출 |

---

## ✅ 완료된 작업

### 1. 문제 추출 (완료)
- **도구**: `_scripts/extract_problems.py`
- **결과**: 43개 원본 파일 → 214개 개별 문제 파일
- **위치**: `problems/001.tex ~ 214.tex`
- **메타데이터**: `_scripts/problems_metadata.json`

### 2. 포맷 변환 (완료)
- **도구**: `_scripts/convert_to_problem_env.py`
- **변환**: `\numbering` → `\begin{problem}...\end{problem}`
- **목적**: 향후 포맷 변경 유연성

### 3. 오류 수정 (완료)
- **문제**: 105개 파일에서 짝 맞지 않는 `}` 발견
- **원인**: `\endnote{...}` 파싱 실패
- **수정**: `_scripts/fix_problem_files_v2.py` 실행
- **결과**: 0개 오류, 모든 파일 정상

### 4. TikZ 루프 수정 (완료)
- **문제**: `problems/155.tex`에서 5개 `\foreach` 루프 미종료
- **증상**: LaTeX 컴파일 실패
- **수정**: 모든 `\foreach` 루프에 `}` 추가
- **검증**: `_testing_.tex` 컴파일 성공 (4페이지 PDF 생성)

### 5. 웹 UI 개발 (완료)
- **위치**: `web_app/`
- **백엔드**: Flask (Python)
- **프론트엔드**: HTML/JavaScript + MathJax
- **기능**:
  - 246개 문제 목록 표시
  - 문제 검색 (번호, 출처, 파일명)
  - 문제 내용 보기 (수식 렌더링)
  - 풀이 작성 (LaTeX 형식)
  - 메타데이터 편집 (출처, 답안, 카테고리, 난이도, 태그)
  - 통계 대시보드

### 6. KMO 중등부 1차 문제 추가 (완료) ⭐ NEW
- **출처**: 2020-2025년 KMO 중등부 1차 시험 PDF
- **도구**: `KMO_mid/process_kmo_problems.py`
- **결과**:
  - 6개 년도별 전체 TeX 파일 생성 (`KMO_mid/KMO_202X_중등부_1차.tex`)
  - 32개 기하 문제 추출 (`problems/215.tex ~ 246.tex`)
  - 자동 카테고리 태깅 (삼각형, 원, 중심, 접선 등)
- **분류**:
  - 2020년: 7개 기하 문제
  - 2021년: 4개 기하 문제
  - 2022년: 5개 기하 문제
  - 2023년: 5개 기하 문제
  - 2024년: 5개 기하 문제
  - 2025년: 6개 기하 문제

---

## 📁 폴더 구조

```
__Geometry/
├── problems/                          # 추출된 문제 파일
│   ├── 001.tex ~ 214.tex             # 개별 문제 (TeX 조각) - 기존
│   ├── 215.tex ~ 246.tex             # KMO 중등부 1차 문제 (2020-2025)
│   └── solutions/                     # 풀이 저장 폴더 (웹 UI에서 생성)
│       └── NNN_solution.tex
│
├── KMO_mid/                           # KMO 중등부 1차 시험 문제 ⭐ NEW
│   ├── KMO_2020_중등부_1차.pdf       # 원본 PDF
│   ├── KMO_2020_중등부_1차.tex       # 변환된 TeX
│   ├── KMO_2021_중등부_1차.pdf
│   ├── KMO_2021_중등부_1차.tex
│   ├── ... (2022-2025 동일)
│   └── process_kmo_problems.py       # PDF → TeX 변환 스크립트
│
├── _scripts/                          # 스크립트 및 문서
│   ├── extract_problems.py           # 문제 추출 메인 스크립트
│   ├── convert_to_problem_env.py     # 포맷 변환
│   ├── fix_problem_files_v2.py       # 중괄호 오류 수정
│   ├── tex_to_markdown.py            # Markdown 변환 (프로토타입)
│   ├── problems_metadata.json        # 메타데이터 DB (246개 문제)
│   ├── extraction_log.txt            # 추출 로그
│   ├── README.md                     # 스크립트 사용 가이드
│   ├── KNOWN_ISSUES.md               # 알려진 문제점
│   ├── MARKDOWN_CONVERSION_NOTES.md  # Markdown 변환 가이드
│   └── FIXES_APPLIED.md              # 수정 이력
│
├── web_app/                           # 웹 애플리케이션
│   ├── app.py                        # Flask 서버
│   ├── requirements.txt              # Python 의존성
│   ├── README.md                     # 웹앱 사용법
│   └── static/
│       └── index.html                # 웹 UI
│
├── _testing_.tex                      # 테스트용 문서
└── PROJECT_STATUS.md                  # 이 파일
```

---

## 🚀 웹 UI 실행 방법

```bash
cd web_app
python3 app.py
```

→ 브라우저에서 **http://localhost:5000** 접속

### 사용 흐름
1. 왼쪽 목록에서 문제 선택
2. "문제 보기" 탭: 문제 확인 (수식 자동 렌더링)
3. "풀이 작성" 탭: LaTeX 형식으로 풀이 입력 → 저장
4. "메타데이터" 탭: 출처, 답안, 카테고리 등 입력 → 저장

---

## ⚠️ 알려진 문제 (미해결)

### 1. 메타데이터 추출 오류
- **증상**: 한 페이지에 두 문제가 있던 경우, 뒷 문제의 출처가 앞 문제에 포함됨
- **원인**: `\newpage`를 문제 끝으로 처리했으나, 실제로는 `\stepcounter{prob}`가 더 정확한 구분자
- **영향**: 일부 문제의 메타데이터가 부정확할 수 있음
- **상태**: 보류 (우선순위: 낮음)
- **해결 방안**: 웹 UI에서 수동 수정 가능

---

## 📋 메타데이터 구조

`_scripts/problems_metadata.json`:
```json
{
  "total_problems": 214,
  "problems": [
    {
      "id": "001",
      "filename": "001.tex",
      "source_file": "Problem Sets/contents/00_수선.tex",
      "source": "",           // 웹 UI에서 입력
      "answer": "",           // 웹 UI에서 입력
      "category": "",         // 웹 UI에서 입력
      "difficulty": "",       // 웹 UI에서 입력
      "tags": [],             // 웹 UI에서 입력
      "has_tikz": false,
      "note": ""              // 웹 UI에서 입력
    }
  ]
}
```

---

## 🎯 다음 단계 (선택사항)

### 우선순위 높음
- [ ] 웹 UI로 풀이 작성 시작
- [ ] 메타데이터 수동 입력 (출처, 답안)

### 우선순위 중간
- [ ] 메타데이터 추출 오류 수정 스크립트
- [ ] 문제 카테고리 태깅 (원, 삼각형, 사각형 등)
- [ ] 난이도 평가

### 우선순위 낮음
- [ ] Markdown 변환 자동화
- [ ] TikZ → SVG 변환
- [ ] PDF 생성 기능
- [ ] 데이터베이스 마이그레이션 (SQLite/PostgreSQL)

---

## 📝 재추출이 필요한 경우

```bash
# 기존 백업
mv problems problems_backup
mv _scripts/problems_metadata.json _scripts/problems_metadata_backup.json

# 재추출
cd _scripts
python3 extract_problems.py
python3 convert_to_problem_env.py
python3 fix_problem_files_v2.py
```

---

## 🔧 주요 명령어

### 문제 추출
```bash
cd _scripts
python3 extract_problems.py
```

### 웹 서버 실행
```bash
cd web_app
python3 app.py
```

### 테스트 컴파일
```bash
pdflatex _testing_.tex
```

### 통계 확인
```bash
curl http://localhost:5000/api/stats | python3 -m json.tool
```

---

## 📚 관련 문서

- `_scripts/README.md` - 스크립트 상세 설명
- `_scripts/KNOWN_ISSUES.md` - 알려진 문제점
- `_scripts/MARKDOWN_CONVERSION_NOTES.md` - Markdown 변환 가이드
- `web_app/README.md` - 웹 애플리케이션 사용법

---

## 💡 핵심 성과

✅ **246개 문제** 자동 추출 및 개별 파일화
✅ **KMO 중등부 1차 (2020-2025)** 32개 기하 문제 추가
✅ **자동 카테고리 태깅** (삼각형, 원, 중심, 접선 등)
✅ **모든 LaTeX 오류** 수정 (컴파일 성공)
✅ **웹 기반 관리 시스템** 구축
✅ **메타데이터 구조** 설계 및 JSON 저장
✅ **풀이 작성 워크플로우** 확립

---

## 🔍 카테고리별 문제 분류 (KMO 추가분)

| 카테고리 | 키워드 |
|---------|--------|
| 삼각형 | 삼각형, 이등변삼각형, 직각삼각형, 예각삼각형 |
| 사각형 | 사각형, 정사각형, 직사각형, 평행사변형, 등변사다리꼴 |
| 다각형 | 오각형, 정육각형 |
| 원 | 원, 반원, 외접원, 내접원 |
| 중심 | 외심, 내심, 무게중심, 중점 |
| 선 | 중선, 수선, 이등분선, 접선, 현 |
| 각 | 각, 예각, 직각, 둔각 |
| 넓이 | 넓이, 면적 |
| 접선 | 접선, 접하다 |
| 호 | 호 |

---

**다음 로그인 시**: `web_app` 폴더로 이동 후 `python3 app.py` 실행하여 풀이 작성 시작!
