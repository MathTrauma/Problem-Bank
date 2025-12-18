#!/usr/bin/env python3
"""
problems 폴더 기반으로 metadata 재생성
"""
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
PROBLEMS_DIR = DATA_DIR / "problems"
SOLUTIONS_DIR = PROBLEMS_DIR / "solutions"
OUTPUT_FILE = DATA_DIR / "problems_metadata.json"


def extract_metadata_from_tex(problem_id: str) -> dict:
    """tex 파일에서 메타데이터 추출"""
    problem_file = PROBLEMS_DIR / f"{problem_id}.tex"

    metadata = {
        "id": problem_id,
        "source": "",
        "source_file": f"problems/{problem_id}.tex",
        "has_tikz": False,
        "tags": [],
        "difficulty": None,
        "category": "",
        "answer": "",
        "note": ""
    }

    if not problem_file.exists():
        return metadata

    with open(problem_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Source 추출 (% Source: ...)
    source_match = re.search(r'%\s*Source:\s*(.+)', content)
    if source_match:
        metadata["source"] = source_match.group(1).strip()

    # TikZ 사용 여부
    if '\\begin{tikzpicture}' in content or 'tikz' in content.lower():
        metadata["has_tikz"] = True

    # Solution 존재 여부
    solution_file = SOLUTIONS_DIR / f"{problem_id}_solution.tex"
    if solution_file.exists():
        with open(solution_file, 'r', encoding='utf-8') as f:
            sol_content = f.read()
        if '\\begin{tikzpicture}' in sol_content or '[SVG:' in sol_content:
            metadata["has_tikz"] = True

    return metadata


def main():
    print("Metadata 재생성 중...")

    # problems 폴더에서 모든 tex 파일 찾기
    problem_files = sorted(PROBLEMS_DIR.glob("[0-9][0-9][0-9].tex"))

    problems = []
    for pf in problem_files:
        problem_id = pf.stem
        metadata = extract_metadata_from_tex(problem_id)
        problems.append(metadata)
        print(f"  {problem_id}: {metadata['source'][:50] if metadata['source'] else '(출처 없음)'}")

    # 저장
    output_data = {
        "total_problems": len(problems),
        "problems": problems
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 완료! {len(problems)}개 문제")
    print(f"출력: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
