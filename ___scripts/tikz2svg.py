#!/usr/bin/env python3
"""
TikZ to SVG 변환 스크립트

solution 파일들의 tikzpicture 환경을 SVG로 변환하고,
원본 파일에서는 SVG 참조로 대체합니다.

사용법:
    python3 tikz2svg.py                    # 모든 solution 파일 처리
    python3 tikz2svg.py 245                # 245_solution.tex만 처리
    python3 tikz2svg.py 245 246            # 여러 파일 처리
    python3 tikz2svg.py --check            # 변환 필요한 파일 확인만
"""

import argparse
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


# 기준 디렉토리
BASE_DIR = Path(__file__).parent.parent
PROBLEMS_DIR = BASE_DIR / "problems"
SOLUTIONS_DIR = PROBLEMS_DIR / "solutions"
SVG_OUTPUT_DIR = BASE_DIR / "web_app" / "data" / "svg"

# standalone LaTeX 템플릿
STANDALONE_TEMPLATE = r"""\documentclass[tikz,border=5pt]{standalone}
\usepackage{tkz-euclide}
\usepackage{xcolor}
\begin{document}
%s
\end{document}
"""

# tikzpicture 환경 패턴
TIKZ_PATTERN = re.compile(
    r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',
    re.DOTALL
)


def find_tikz_in_file(filepath: Path) -> list[tuple[int, str]]:
    """파일에서 모든 tikzpicture 환경을 찾아 반환"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    matches = []
    for i, match in enumerate(TIKZ_PATTERN.finditer(content)):
        matches.append((i, match.group()))

    return matches


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
            print(f"  ❌ pdflatex 컴파일 실패")
            print(f"     에러: {result.stdout[-500:] if result.stdout else result.stderr[-500:]}")
            return False

        # pdf2svg 변환
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ['pdf2svg', str(pdf_file), str(output_path)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  ❌ pdf2svg 변환 실패: {result.stderr}")
            return False

        return True


def get_svg_reference(svg_filename: str, for_web: bool = True) -> str:
    """SVG 참조 코드 생성"""
    if for_web:
        # 웹앱용: HTML img 태그로 변환될 마커
        return f"% [SVG: {svg_filename}]"
    else:
        # LaTeX용: includegraphics (SVG 지원 패키지 필요)
        return f"\\includegraphics{{{svg_filename}}}"


def process_solution_file(problem_id: str, dry_run: bool = False) -> dict:
    """단일 solution 파일 처리"""
    solution_file = SOLUTIONS_DIR / f"{problem_id}_solution.tex"

    if not solution_file.exists():
        return {"status": "not_found", "file": str(solution_file)}

    tikz_matches = find_tikz_in_file(solution_file)

    if not tikz_matches:
        return {"status": "no_tikz", "file": str(solution_file)}

    if dry_run:
        return {
            "status": "needs_conversion",
            "file": str(solution_file),
            "tikz_count": len(tikz_matches)
        }

    # 파일 내용 읽기
    with open(solution_file, 'r', encoding='utf-8') as f:
        content = f.read()

    results = []
    new_content = content

    for idx, tikz_code in tikz_matches:
        svg_filename = f"{problem_id}_fig{idx + 1}.svg"
        svg_path = SVG_OUTPUT_DIR / svg_filename

        print(f"  [{idx + 1}/{len(tikz_matches)}] {svg_filename} 변환 중...")

        if compile_tikz_to_svg(tikz_code, svg_path):
            # tikzpicture를 SVG 참조로 대체
            svg_ref = get_svg_reference(svg_filename)
            new_content = new_content.replace(tikz_code, svg_ref, 1)
            results.append({"svg": svg_filename, "success": True})
            print(f"  ✅ {svg_filename} 생성 완료")
        else:
            results.append({"svg": svg_filename, "success": False})

    # 수정된 내용 저장
    if any(r["success"] for r in results):
        # 백업 생성
        backup_file = solution_file.with_suffix('.tex.bak')
        shutil.copy(solution_file, backup_file)

        with open(solution_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return {
        "status": "processed",
        "file": str(solution_file),
        "results": results
    }


def find_all_solutions_with_tikz() -> list[str]:
    """tikzpicture가 포함된 모든 solution 파일의 problem_id 반환"""
    problem_ids = []

    for tex_file in SOLUTIONS_DIR.glob("*_solution.tex"):
        tikz_matches = find_tikz_in_file(tex_file)
        if tikz_matches:
            # 파일명에서 problem_id 추출
            problem_id = tex_file.stem.replace("_solution", "")
            problem_ids.append(problem_id)

    return sorted(problem_ids)


def main():
    parser = argparse.ArgumentParser(
        description='TikZ to SVG 변환 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python3 tikz2svg.py                    # 모든 solution 파일 처리
  python3 tikz2svg.py 245                # 245_solution.tex만 처리
  python3 tikz2svg.py 245 246            # 여러 파일 처리
  python3 tikz2svg.py --check            # 변환 필요한 파일 확인만
  python3 tikz2svg.py --list             # tikz 포함 파일 목록
        """
    )

    parser.add_argument('problem_ids', nargs='*', help='처리할 문제 번호')
    parser.add_argument('--check', action='store_true', help='변환 필요한 파일 확인만')
    parser.add_argument('--list', action='store_true', help='tikz 포함 파일 목록 출력')

    args = parser.parse_args()

    # SVG 출력 디렉토리 생성
    SVG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.list:
        print("tikzpicture 포함 solution 파일:")
        problem_ids = find_all_solutions_with_tikz()
        for pid in problem_ids:
            tikz_count = len(find_tikz_in_file(SOLUTIONS_DIR / f"{pid}_solution.tex"))
            print(f"  {pid}_solution.tex ({tikz_count}개 tikz)")
        print(f"\n총 {len(problem_ids)}개 파일")
        return

    # 처리할 파일 결정
    if args.problem_ids:
        problem_ids = args.problem_ids
    else:
        problem_ids = find_all_solutions_with_tikz()

    if not problem_ids:
        print("처리할 tikzpicture가 포함된 파일이 없습니다.")
        return

    print(f"{'[확인 모드]' if args.check else '[변환 모드]'}")
    print(f"처리 대상: {len(problem_ids)}개 파일")
    print(f"SVG 출력: {SVG_OUTPUT_DIR}\n")

    total_success = 0
    total_fail = 0

    for problem_id in problem_ids:
        print(f"📄 {problem_id}_solution.tex 처리 중...")
        result = process_solution_file(problem_id, dry_run=args.check)

        if result["status"] == "not_found":
            print(f"  ⚠️  파일 없음")
        elif result["status"] == "no_tikz":
            print(f"  ℹ️  tikzpicture 없음")
        elif result["status"] == "needs_conversion":
            print(f"  📊 {result['tikz_count']}개 tikzpicture 발견")
        elif result["status"] == "processed":
            for r in result["results"]:
                if r["success"]:
                    total_success += 1
                else:
                    total_fail += 1
        print()

    if not args.check:
        print("=" * 40)
        print(f"완료: 성공 {total_success}개, 실패 {total_fail}개")
        if total_success > 0:
            print(f"SVG 파일 위치: {SVG_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
