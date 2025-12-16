#!/usr/bin/env python3
"""
TeX 문제 파일을 Markdown으로 변환 (프로토타입)
"""

import re
import json
from pathlib import Path


def extract_metadata_from_comments(tex_content: str) -> dict:
    """주석에서 메타데이터 추출"""
    metadata = {
        'id': '',
        'source_file': '',
        'source': '',
        'answer': ''
    }

    # Problem ID
    id_match = re.search(r'%\s*Problem ID:\s*(\d+)', tex_content)
    if id_match:
        metadata['id'] = id_match.group(1)

    # Original file
    file_match = re.search(r'%\s*Original file:\s*(.+)', tex_content)
    if file_match:
        metadata['source_file'] = file_match.group(1).strip()

    # Source
    source_match = re.search(r'%\s*Source:\s*(.+)', tex_content)
    if source_match:
        metadata['source'] = source_match.group(1).strip()

    # Answer
    answer_match = re.search(r'%\s*Answer:\s*(.+)', tex_content)
    if answer_match:
        metadata['answer'] = answer_match.group(1).strip()

    return metadata


def extract_problem_content(tex_content: str) -> str:
    """problem 환경에서 본문 추출"""
    pattern = r'\\begin\{problem\}(.*?)\\end\{problem\}'
    match = re.search(pattern, tex_content, re.DOTALL)

    if match:
        return match.group(1).strip()
    return ""


def has_tikz(content: str) -> bool:
    """TikZ 포함 여부 확인"""
    return bool(re.search(r'\\begin\{tikzpicture\}', content))


def convert_basic_latex_to_markdown(content: str, problem_id: str) -> str:
    """기본 LaTeX 요소를 Markdown으로 변환"""

    # 1. 줄바꿈 제거 (LaTeX의 \\는 Markdown에서 불필요)
    content = re.sub(r'\\\\\s*$', '', content, flags=re.MULTILINE)

    # 2. center 환경 변환
    def replace_center(match):
        inner = match.group(1)
        return f'\n<div align="center">\n\n{inner}\n\n</div>\n'

    content = re.sub(
        r'\\begin\{center\}(.*?)\\end\{center\}',
        replace_center,
        content,
        flags=re.DOTALL
    )

    # 3. TikZ를 이미지 플레이스홀더로 변환
    tikz_count = [0]  # 클로저용 카운터

    def replace_tikz(match):
        tikz_count[0] += 1
        suffix = '' if tikz_count[0] == 1 else f'_{tikz_count[0]}'
        return f'\n![도형](./images/problem_{problem_id}{suffix}.svg)\n'

    content = re.sub(
        r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',
        replace_tikz,
        content,
        flags=re.DOTALL
    )

    # 4. figure/subfigure 환경 간소화
    # 복잡한 레이아웃은 수동 처리 필요하다는 주석 추가
    if re.search(r'\\begin\{figure\}', content):
        content = re.sub(
            r'\\begin\{figure\}.*?\\end\{figure\}',
            '\n<!-- 복잡한 그림 레이아웃: 수동 변환 필요 -->\n',
            content,
            flags=re.DOTALL
        )

    # 5. 불필요한 LaTeX 커맨드 제거
    content = re.sub(r'\\vfill\s*', '', content)
    content = re.sub(r'\\newpage\s*', '', content)

    # 6. 과도한 빈 줄 정리
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content.strip()


def tex_to_markdown(tex_file: Path, metadata_file: Path) -> str:
    """단일 TeX 파일을 Markdown으로 변환"""

    # TeX 파일 읽기
    with open(tex_file, 'r', encoding='utf-8') as f:
        tex_content = f.read()

    # 메타데이터 추출
    metadata = extract_metadata_from_comments(tex_content)

    # JSON 메타데이터 읽기 (추가 정보)
    with open(metadata_file, 'r', encoding='utf-8') as f:
        all_metadata = json.load(f)

    # 해당 문제의 메타데이터 찾기
    problem_meta = None
    for p in all_metadata['problems']:
        if p['id'] == metadata['id']:
            problem_meta = p
            break

    if problem_meta:
        metadata['source'] = problem_meta.get('source', '')
        metadata['answer'] = problem_meta.get('answer', '')
        has_image = problem_meta.get('has_tikz', False)
    else:
        has_image = False

    # 문제 본문 추출
    problem_content = extract_problem_content(tex_content)

    # Markdown 변환
    md_content = convert_basic_latex_to_markdown(problem_content, metadata['id'])

    # YAML front matter 생성
    front_matter = f"""---
id: "{metadata['id']}"
source_file: "{metadata['source_file']}"
source: "{metadata['source']}"
answer: "{metadata['answer']}"
has_image: {str(has_image).lower()}
---

"""

    # 최종 Markdown
    markdown = front_matter
    markdown += f"# 문제 {metadata['id']}\n\n"
    markdown += md_content
    markdown += "\n\n---\n\n"
    markdown += f"**출처**: {metadata['source'] or '-'}\n"
    markdown += f"**답안**: {metadata['answer'] or '-'}\n"

    return markdown


def convert_all(limit: int = 5):
    """전체 변환 (샘플로 처음 N개만)"""
    problems_dir = Path('problems')
    output_dir = Path('problems_markdown')
    output_dir.mkdir(exist_ok=True)

    metadata_file = Path('problems_metadata.json')

    tex_files = sorted(problems_dir.glob('*.tex'))[:limit]

    print(f"샘플 변환: 처음 {limit}개 파일")
    print("=" * 60)

    for tex_file in tex_files:
        try:
            markdown = tex_to_markdown(tex_file, metadata_file)

            # 저장
            md_file = output_dir / f"{tex_file.stem}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown)

            print(f"✓ {tex_file.name} → {md_file.name}")

        except Exception as e:
            print(f"✗ {tex_file.name}: {e}")

    print("=" * 60)
    print(f"변환 완료: {output_dir}/ 폴더 확인")


if __name__ == "__main__":
    convert_all(limit=10)
