#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 문제 데이터를 하나의 JSON 파일로 통합
GitHub Pages 배포용
"""

import json
from pathlib import Path

# 경로 설정
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
PROBLEMS_DIR = DATA_DIR / "problems"
SOLUTIONS_DIR = PROBLEMS_DIR / "solutions"
METADATA_FILE = DATA_DIR / "problems_metadata.json"
OUTPUT_FILE = SCRIPT_DIR / "problems_bundle.json"


def load_metadata():
    """메타데이터 로드"""
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_problem_content(problem_id):
    """문제 내용 로드"""
    problem_file = PROBLEMS_DIR / f"{problem_id}.tex"
    if problem_file.exists():
        with open(problem_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 주석 라인 제거
            lines = content.split('\n')
            content_lines = [line for line in lines if not line.strip().startswith('%')]
            return '\n'.join(content_lines).strip()
    return ""


def load_solution(problem_id):
    """풀이 내용 로드"""
    solution_file = SOLUTIONS_DIR / f"{problem_id}_solution.tex"
    if solution_file.exists():
        with open(solution_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ""


def build_bundle():
    """모든 데이터를 하나의 JSON으로 통합"""
    print("=" * 60)
    print("문제 데이터 번들 생성 중...")
    print("=" * 60)

    # 메타데이터 로드
    metadata = load_metadata()

    # 각 문제에 대해 내용과 풀이 추가
    enriched_problems = []

    for problem in metadata['problems']:
        problem_id = problem['id']
        print(f"처리 중: {problem_id}")

        # 문제 내용과 풀이 로드
        content = load_problem_content(problem_id)
        solution = load_solution(problem_id)

        # 통합 데이터 생성
        enriched_problem = {
            **problem,  # 기존 메타데이터
            'content': content,
            'solution': solution
        }

        enriched_problems.append(enriched_problem)

    # 최종 번들 데이터
    bundle = {
        'total_problems': metadata['total_problems'],
        'problems': enriched_problems
    }

    # JSON 파일로 저장
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"✅ 완료! {len(enriched_problems)}개 문제 처리")
    print(f"출력 파일: {OUTPUT_FILE}")
    print(f"파일 크기: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    print("=" * 60)


if __name__ == '__main__':
    build_bundle()
