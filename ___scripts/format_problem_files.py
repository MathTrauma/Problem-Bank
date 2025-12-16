#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
문제 파일 포맷팅 스크립트
- 마침표(.) 다음에 줄바꿈 추가
- 수식 다음에 한글/영문이 오면 공백 추가
"""

import re
from pathlib import Path
import sys


def format_problem_text(text: str) -> str:
    """
    문제 텍스트를 포맷팅합니다.
    """
    # 주석 라인 보존
    lines = text.split('\n')
    comment_lines = []
    content_lines = []

    for line in lines:
        if line.strip().startswith('%'):
            comment_lines.append(line)
        else:
            content_lines.append(line)

    # 내용만 처리
    content = '\n'.join(content_lines)

    # 1. 수식 보호 (임시 치환)
    math_expressions = []
    math_index = 0

    # Display math $$...$$ 보호
    def save_display_math(match):
        nonlocal math_index
        placeholder = f'___DISPLAYMATH_{math_index}___'
        math_expressions.append((placeholder, match.group(0)))
        math_index += 1
        return placeholder

    content = re.sub(r'\$\$[^\$]+?\$\$', save_display_math, content)

    # Inline math $...$ 보호
    def save_inline_math(match):
        nonlocal math_index
        placeholder = f'___INLINEMATH_{math_index}___'
        math_expressions.append((placeholder, match.group(0)))
        math_index += 1
        return placeholder

    content = re.sub(r'\$[^\$]+?\$', save_inline_math, content)

    # 2. 마침표 다음 줄바꿈 처리
    # 마침표 뒤에 공백 + 한글/영문이 오면 줄바꿈으로 변경
    # 단, 이미 줄바꿈이 있거나, \\가 있으면 패스
    content = re.sub(r'\.(\s+)([가-힣A-Z])', r'.\n\2', content)

    # 3. 수식 복원
    for placeholder, math_expr in math_expressions:
        content = content.replace(placeholder, math_expr)

    # 4. 수식 뒤에 한글/영문이 바로 오면 공백 추가
    # $...$다음글 -> $...$ 다음글
    content = re.sub(r'(\$[^\$]+?\$)([가-힣a-zA-Z])', r'\1 \2', content)
    content = re.sub(r'(\$\$[^\$]+?\$\$)([가-힣a-zA-Z])', r'\1 \2', content)

    # 5. 연속된 빈 줄 제거 (최대 1개)
    content = re.sub(r'\n\n+', r'\n\n', content)

    # 6. 주석과 내용 결합
    if comment_lines:
        result = '\n'.join(comment_lines) + '\n\n' + content
    else:
        result = content

    # 7. 끝에 줄바꿈 하나만
    result = result.rstrip() + '\n'

    return result


def format_problem_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    문제 파일 하나를 포맷팅합니다.

    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        formatted = format_problem_text(original)

        # 변경사항이 있는지 확인
        if original == formatted:
            return False

        if dry_run:
            print(f"[DRY RUN] Would modify: {file_path.name}")
            return True

        # 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted)

        print(f"✅ Formatted: {file_path.name}")
        return True

    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return False


def format_all_problems(problems_dir: Path, dry_run: bool = False):
    """
    모든 문제 파일을 포맷팅합니다.
    """
    # 문제 파일 찾기
    problem_files = sorted(problems_dir.glob('*.tex'))

    if not problem_files:
        print(f"No .tex files found in {problems_dir}")
        return

    print("=" * 60)
    if dry_run:
        print("DRY RUN MODE - No files will be modified")
    else:
        print("Formatting problem files...")
    print("=" * 60)

    modified_count = 0
    total_count = len(problem_files)

    for file_path in problem_files:
        if format_problem_file(file_path, dry_run):
            modified_count += 1

    print("=" * 60)
    print(f"Total files: {total_count}")
    print(f"Modified: {modified_count}")
    print(f"Unchanged: {total_count - modified_count}")
    print("=" * 60)


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='Format problem .tex files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')
    parser.add_argument('--file', type=str,
                       help='Format a single file instead of all files')

    args = parser.parse_args()

    # 경로 설정
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    problems_dir = base_dir / 'problems'

    if not problems_dir.exists():
        print(f"Error: Problems directory not found: {problems_dir}")
        sys.exit(1)

    if args.file:
        # 단일 파일 처리
        file_path = problems_dir / args.file
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        format_problem_file(file_path, args.dry_run)
    else:
        # 모든 파일 처리
        format_all_problems(problems_dir, args.dry_run)


if __name__ == '__main__':
    main()
