#!/usr/bin/env python3
"""
문제 파일의 잘못된 중괄호 제거 - 개선 버전
"""

import re
from pathlib import Path


def fix_problem_content_v2(content: str) -> str:
    """문제 내용 수정 - 개선 버전"""

    # \begin{problem}과 \end{problem} 사이의 내용 추출
    pattern = r'(\\begin\{problem\})(.*?)(\\end\{problem\})'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return content

    prefix = match.group(1)
    problem_content = match.group(2)
    suffix = match.group(3)

    # 패턴 1: 줄 시작에 } 하나만 있는 경우 제거
    problem_content = re.sub(r'^\s*\}\s*$', '', problem_content, flags=re.MULTILINE)

    # 패턴 2: }로 시작하는 텍스트 (} 제거, 나머지 유지)
    problem_content = re.sub(r'^\s*\}(.*)', r'\1', problem_content, flags=re.MULTILINE)

    # 패턴 3: endnote 잔여물 제거 (\\ 답: ... } 패턴)
    problem_content = re.sub(
        r'^\s*\\\\\s*\n\s*답\s*[:：].*?\n\s*\}',
        '',
        problem_content,
        flags=re.DOTALL | re.MULTILINE
    )

    # 패턴 4: {숫자}$ } 같은 잔여물
    problem_content = re.sub(
        r'\{[0-9]+\}\$\s*\n\s*\}',
        '',
        problem_content
    )

    # 앞뒤 공백 정리
    problem_content = problem_content.strip()

    # 주석 부분
    comments = content[:content.find('\\begin{problem}')]

    # 재구성
    fixed = comments + '\n' + prefix + '\n' + problem_content + '\n' + suffix + '\n'

    return fixed


def fix_file_v2(filepath: Path) -> tuple[bool, str]:
    """개별 파일 수정 v2"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 문제 확인
        problem_pattern = r'\\begin\{problem\}(.*?)\\end\{problem\}'
        match = re.search(problem_pattern, content, re.DOTALL)

        if not match:
            return False, "problem 환경 없음"

        problem_content = match.group(1)

        # } 로 시작하는 줄이 있는지 확인
        has_brace_issue = bool(re.search(r'^\s*\}', problem_content, re.MULTILINE))

        if not has_brace_issue:
            return False, "문제 없음"

        # 수정
        fixed_content = fix_problem_content_v2(content)

        # 검증: 여전히 문제가 있는지
        match_after = re.search(problem_pattern, fixed_content, re.DOTALL)
        if match_after:
            still_has_issue = bool(re.search(r'^\s*\}', match_after.group(1), re.MULTILINE))
            if still_has_issue:
                return False, "수정 실패 (복잡한 케이스)"

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

    print(f"총 {len(tex_files)}개 파일 검사 (v2)")
    print("=" * 60)

    fixed_count = 0
    failed_files = []

    for tex_file in tex_files:
        fixed, msg = fix_file_v2(tex_file)

        if fixed:
            fixed_count += 1
        elif "실패" in msg or "복잡한" in msg:
            failed_files.append((tex_file.name, msg))

    print(f"수정 완료: {fixed_count}개")

    if failed_files:
        print(f"\n수동 확인 필요: {len(failed_files)}개")
        for filename, msg in failed_files[:10]:
            print(f"  - {filename}: {msg}")

    # 최종 확인
    remaining = 0
    for tex_file in tex_files:
        with open(tex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'\\begin\{problem\}(.*?)\\end\{problem\}', content, re.DOTALL)
        if match and re.search(r'^\s*\}', match.group(1), re.MULTILINE):
            remaining += 1

    print("=" * 60)
    print(f"남은 문제: {remaining}개 파일")


if __name__ == "__main__":
    main()
