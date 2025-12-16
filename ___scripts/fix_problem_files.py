#!/usr/bin/env python3
"""
문제 파일의 잘못된 중괄호 및 endnote 잔여물 제거
"""

import re
from pathlib import Path


def fix_problem_content(content: str) -> str:
    """문제 내용 수정"""

    # \begin{problem}과 \end{problem} 사이의 내용 추출
    pattern = r'(\\begin\{problem\})(.*?)(\\end\{problem\})'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return content

    prefix = match.group(1)  # \begin{problem}
    problem_content = match.group(2)  # 실제 문제 내용
    suffix = match.group(3)  # \end{problem}

    # 문제 내용 정리
    # 1. \begin{problem} 직후의 \\부터 } 포함 줄까지 제거
    # 패턴: \\ 로 시작, 여러 줄, } 로 시작하는 줄까지
    problem_content = re.sub(
        r'^\s*\\\\\s*\n.*?\n\s*\}',  # \\ ... }
        '',
        problem_content,
        flags=re.DOTALL
    )

    # 2. 혹시 남아있는 단독 } 제거
    problem_content = re.sub(r'^\s*\}\s*$', '', problem_content, flags=re.MULTILINE)

    # 3. 앞뒤 공백 정리
    problem_content = problem_content.strip()

    # 주석 부분 (파일 시작 ~ \begin{problem} 전까지)
    comments = content[:content.find('\\begin{problem}')]

    # 재구성
    fixed = comments + '\n' + prefix + '\n' + problem_content + '\n' + suffix + '\n'

    return fixed


def fix_file(filepath: Path) -> tuple[bool, str]:
    """개별 파일 수정"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # } 로 시작하는 줄이 있는지 확인
        has_issue = bool(re.search(r'^\s*\}', content, re.MULTILINE))

        if not has_issue:
            return False, "문제 없음"

        # 수정
        fixed_content = fix_problem_content(content)

        # 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        return True, "수정 완료"

    except Exception as e:
        return False, f"오류: {e}"


def main():
    """메인 함수"""
    problems_dir = Path('problems')

    if not problems_dir.exists():
        print("problems/ 폴더가 없습니다.")
        return

    tex_files = sorted(problems_dir.glob('*.tex'))

    print(f"총 {len(tex_files)}개 파일 검사 시작")
    print("=" * 60)

    fixed_count = 0
    issue_files = []

    for tex_file in tex_files:
        fixed, msg = fix_file(tex_file)

        if fixed:
            fixed_count += 1
            issue_files.append(tex_file.name)

        if fixed_count > 0 and fixed_count % 10 == 0:
            print(f"{fixed_count}개 파일 수정 완료...")

    print("=" * 60)
    print(f"\n수정된 파일: {fixed_count}개")

    if fixed_count > 0:
        print(f"\n첫 10개 예시:")
        for filename in issue_files[:10]:
            print(f"  - {filename}")


if __name__ == "__main__":
    main()
