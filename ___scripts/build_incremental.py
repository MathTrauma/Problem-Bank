#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
증분 빌드 시스템 - troubles.xml 해결

핵심 원칙:
1. 원본 .tex 파일은 절대 수정하지 않음
2. 빌드 시점에만 tikzpicture를 SVG로 변환
3. 변경된 파일만 처리 (파일 해시 기반)
4. 개별 JSON 파일로 저장 (번들 대신)

출력:
- dist/problems/{id}.json  : 개별 문제 JSON
- dist/svg/{id}_fig*.svg   : SVG 그림
- dist/metadata.json       : 전체 메타데이터
- .build_cache.json        : 빌드 캐시 (해시)
"""

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 경로 설정
BASE_DIR = Path(__file__).parent.parent
PROBLEMS_DIR = BASE_DIR / "web_app" / "data" / "problems"
SOLUTIONS_DIR = PROBLEMS_DIR / "solutions"
METADATA_FILE = BASE_DIR / "web_app" / "data" / "problems_metadata.json"

# 출력 디렉토리
DIST_DIR = BASE_DIR / "dist"
DIST_PROBLEMS_DIR = DIST_DIR / "problems"
DIST_SVG_DIR = DIST_DIR / "svg"
DIST_METADATA_FILE = DIST_DIR / "metadata.json"

# 캐시 파일
CACHE_FILE = BASE_DIR / ".build_cache.json"

# TikZ 패턴
TIKZ_PATTERN = re.compile(
    r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',
    re.DOTALL
)

# standalone LaTeX 템플릿
STANDALONE_TEMPLATE = r"""\documentclass[tikz,border=5pt]{standalone}
\usepackage{tkz-euclide}
\usepackage{xcolor}
\begin{document}
%s
\end{document}
"""


def compute_file_hash(filepath: Path) -> str:
    """파일의 SHA256 해시 계산"""
    if not filepath.exists():
        return ""

    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_cache() -> Dict[str, str]:
    """빌드 캐시 로드"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_cache(cache: Dict[str, str]):
    """빌드 캐시 저장"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)


def compile_tikz_to_svg(tikz_code: str, output_path: Path) -> bool:
    """tikzpicture 코드를 SVG로 변환"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        tex_file = tmpdir / "figure.tex"
        pdf_file = tmpdir / "figure.pdf"

        # standalone tex 파일 생성
        tex_content = STANDALONE_TEMPLATE % tikz_code
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(tex_content)

        # pdflatex 컴파일
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', tex_file.name],
            cwd=tmpdir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0 or not pdf_file.exists():
            print(f"    ❌ pdflatex 컴파일 실패")
            return False

        # pdf2svg 변환
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ['pdf2svg', str(pdf_file), str(output_path)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"    ❌ pdf2svg 변환 실패: {result.stderr}")
            return False

        return True


def process_tikz_in_content(content: str, problem_id: str) -> Tuple[str, List[str]]:
    """
    content에서 tikzpicture를 찾아 SVG로 변환하고 마커로 대체

    Returns:
        (변환된 content, 생성된 SVG 파일명 리스트)
    """
    tikz_matches = list(TIKZ_PATTERN.finditer(content))

    if not tikz_matches:
        return content, []

    svg_files = []
    new_content = content

    # 뒤에서부터 처리 (인덱스 유지)
    for idx, match in enumerate(reversed(tikz_matches)):
        fig_num = len(tikz_matches) - idx
        svg_filename = f"{problem_id}_fig{fig_num}.svg"
        svg_path = DIST_SVG_DIR / svg_filename

        tikz_code = match.group()

        print(f"    [{fig_num}/{len(tikz_matches)}] {svg_filename} 변환 중...")

        if compile_tikz_to_svg(tikz_code, svg_path):
            # tikzpicture를 SVG 마커로 대체
            svg_marker = f"% [SVG: {svg_filename}]"
            new_content = new_content[:match.start()] + svg_marker + new_content[match.end():]
            svg_files.append(svg_filename)
            print(f"    ✅ {svg_filename} 생성 완료")
        else:
            print(f"    ⚠️  {svg_filename} 변환 실패, 원본 유지")

    return new_content, list(reversed(svg_files))


def load_problem_content(problem_id: str) -> str:
    """문제 내용 로드 (원본 유지)"""
    problem_file = PROBLEMS_DIR / f"{problem_id}.tex"
    if problem_file.exists():
        with open(problem_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 주석 라인 제거
            lines = content.split('\n')
            content_lines = [line for line in lines if not line.strip().startswith('%')]
            return '\n'.join(content_lines).strip()
    return ""


def load_solution_content(problem_id: str) -> str:
    """풀이 내용 로드 (원본 유지)"""
    solution_file = SOLUTIONS_DIR / f"{problem_id}_solution.tex"
    if solution_file.exists():
        with open(solution_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ""


def build_problem_json(problem_id: str, metadata: dict, cache: Dict[str, str]) -> Optional[dict]:
    """
    단일 문제의 JSON 파일 생성

    Returns:
        변경사항이 있으면 문제 데이터 dict, 없으면 None
    """
    print(f"\n📄 문제 {problem_id} 처리 중...")

    # 파일 경로
    problem_file = PROBLEMS_DIR / f"{problem_id}.tex"
    solution_file = SOLUTIONS_DIR / f"{problem_id}_solution.tex"
    output_file = DIST_PROBLEMS_DIR / f"{problem_id}.json"

    # 파일 해시 계산
    problem_hash = compute_file_hash(problem_file)
    solution_hash = compute_file_hash(solution_file)
    combined_hash = hashlib.sha256(f"{problem_hash}{solution_hash}".encode()).hexdigest()

    cache_key = f"problem_{problem_id}"

    # 캐시 확인 (증분 빌드)
    if cache.get(cache_key) == combined_hash and output_file.exists():
        print(f"  ⏭️  변경 없음, 스킵")
        return None

    # 문제 내용 로드
    content = load_problem_content(problem_id)
    solution = load_solution_content(problem_id)

    # 풀이에서 tikzpicture 처리
    if solution:
        solution, svg_files = process_tikz_in_content(solution, problem_id)
    else:
        svg_files = []

    # 메타데이터 찾기
    problem_meta = next(
        (p for p in metadata['problems'] if p['id'] == problem_id),
        {'id': problem_id}
    )

    # 통합 데이터
    problem_data = {
        **problem_meta,
        'content': content,
        'solution': solution,
        'svg_files': svg_files
    }

    # JSON 파일 저장
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(problem_data, f, ensure_ascii=False, indent=2)

    # 캐시 업데이트
    cache[cache_key] = combined_hash

    print(f"  ✅ {output_file.name} 생성 완료")

    return problem_data


def build_all():
    """전체 빌드 프로세스"""
    print("=" * 70)
    print("증분 빌드 시스템 - 원본 보존 방식")
    print("=" * 70)

    # 출력 디렉토리 생성
    DIST_DIR.mkdir(exist_ok=True)
    DIST_PROBLEMS_DIR.mkdir(parents=True, exist_ok=True)
    DIST_SVG_DIR.mkdir(parents=True, exist_ok=True)

    # 메타데이터 로드
    print(f"\n📋 메타데이터 로드: {METADATA_FILE}")
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # 캐시 로드
    cache = load_cache()
    print(f"📦 빌드 캐시 로드: {len(cache)} 항목")

    # 각 문제 처리
    built_problems = []
    skipped_count = 0

    for problem in metadata['problems']:
        problem_id = problem['id']
        result = build_problem_json(problem_id, metadata, cache)

        if result:
            built_problems.append(result)
        else:
            skipped_count += 1

    # 전체 메타데이터 저장
    dist_metadata = {
        'total_problems': metadata['total_problems'],
        'problems': [
            {k: v for k, v in p.items() if k != 'content' and k != 'solution'}
            for p in metadata['problems']
        ]
    }

    with open(DIST_METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dist_metadata, f, ensure_ascii=False, indent=2)

    # 캐시 저장
    save_cache(cache)

    # 결과 출력
    print("\n" + "=" * 70)
    print(f"✅ 빌드 완료!")
    print(f"  처리: {len(built_problems)}개")
    print(f"  스킵: {skipped_count}개 (변경 없음)")
    print(f"  총 문제: {metadata['total_problems']}개")
    print(f"\n출력 디렉토리:")
    print(f"  {DIST_PROBLEMS_DIR}/")
    print(f"  {DIST_SVG_DIR}/")
    print("=" * 70)


if __name__ == '__main__':
    build_all()
