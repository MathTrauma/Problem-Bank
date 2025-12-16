#!/usr/bin/env python3
"""
문제 파일의 \numbering을 \begin{problem}...\end{problem} 환경으로 변환
"""

import re
from pathlib import Path


def convert_file(filepath: Path) -> None:
    """개별 파일 변환"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 주석 부분과 본문 분리
    lines = content.split('\n')

    # 주석 부분 (% 로 시작하는 줄들)
    comment_lines = []
    content_start_idx = 0

    for i, line in enumerate(lines):
        if line.strip().startswith('%') or line.strip() == '':
            comment_lines.append(line)
        else:
            content_start_idx = i
            break

    # 본문 부분
    problem_content = '\n'.join(lines[content_start_idx:])

    # \numbering 제거
    problem_content = re.sub(r'\\numbering\s*', '', problem_content)

    # 앞뒤 공백 정리
    problem_content = problem_content.strip()

    # problem 환경으로 감싸기
    new_content = '\n'.join(comment_lines) + '\n\n'
    new_content += '\\begin{problem}\n'
    new_content += problem_content + '\n'
    new_content += '\\end{problem}\n'

    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)


def main():
    """메인 함수"""
    problems_dir = Path('problems')

    if not problems_dir.exists():
        print("problems/ 폴더가 없습니다.")
        return

    tex_files = sorted(problems_dir.glob('*.tex'))

    print(f"총 {len(tex_files)}개 파일 변환 시작")
    print("=" * 60)

    for i, tex_file in enumerate(tex_files, 1):
        convert_file(tex_file)

        if i % 50 == 0:
            print(f"{i}개 파일 처리 완료...")

    print("=" * 60)
    print(f"총 {len(tex_files)}개 파일 변환 완료!")


if __name__ == "__main__":
    main()
