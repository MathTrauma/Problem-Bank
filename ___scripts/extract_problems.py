#!/usr/bin/env python3
"""
TeX 문제 추출 스크립트
기하 문제 TeX 파일들에서 개별 문제를 추출하여 데이터베이스화
"""

import re
import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class TexProblemExtractor:
    """TeX 파일에서 문제를 추출하는 클래스"""

    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.problem_count = 0
        self.problems = []
        self.metadata = []

        # 제외할 폴더
        self.exclude_dirs = {
            'tkz1', 'tkz2', 'images', 'images_3rd',
            'problems',  # 출력 폴더
            '.git', '__pycache__',
            'problems_backup'  # 백업 폴더들 (problems_backup로 시작하는 모든 폴더)
        }

        # 제외할 파일 패턴
        self.exclude_patterns = [
            'template', 'test', '_000', '_001', '_002',
            'tkz', 'logo'
        ]

    def should_process_file(self, filepath: Path) -> bool:
        """파일을 처리할지 결정"""
        # 폴더 체크
        for part in filepath.parts:
            if part in self.exclude_dirs:
                return False
            # problems_backup으로 시작하는 폴더 제외
            if part.startswith('problems_backup'):
                return False

        # 파일명 패턴 체크
        filename = filepath.stem.lower()
        for pattern in self.exclude_patterns:
            if pattern in filename:
                return False

        return True

    def collect_tex_files(self) -> List[Path]:
        """처리할 TeX 파일 목록 수집"""
        tex_files = []
        for tex_file in self.base_dir.rglob("*.tex"):
            if self.should_process_file(tex_file):
                tex_files.append(tex_file)

        # 우선순위 정렬: contents 폴더 먼저
        tex_files.sort(key=lambda p: (
            'contents' not in str(p),
            str(p)
        ))

        return tex_files

    def extract_endnote_with_braces(self, text: str) -> Tuple[str, int, int]:
        """
        중괄호 개수를 세는 방식으로 endnote 추출
        Returns: (endnote_content, start_pos, end_pos) 또는 ('', -1, -1)
        """
        # \endnote{ 패턴 찾기
        match = re.search(r'\\endnote\s*\{', text)
        if not match:
            return ('', -1, -1)

        start_pos = match.start()
        # { 다음 위치부터 시작
        pos = match.end()
        brace_count = 1  # 이미 { 하나를 열었음

        while pos < len(text) and brace_count > 0:
            if text[pos] == '{':
                brace_count += 1
            elif text[pos] == '}':
                brace_count -= 1
            pos += 1

        if brace_count == 0:
            # endnote 내용 (중괄호 안의 내용만)
            content_start = match.end()
            content_end = pos - 1
            endnote_content = text[content_start:content_end]
            return (endnote_content, start_pos, pos)
        else:
            # 매칭 실패
            return ('', -1, -1)

    def extract_endnote(self, text: str) -> Dict[str, str]:
        """endnote 및 fbox에서 메타데이터 추출"""
        metadata = {
            'source': '',
            'answer': '',
            'note': '',
            'endnote_content': ''  # solution 파일에 저장할 전체 내용
        }

        # 1. 문제 시작 부분의 \fbox{...}\\ 패턴에서 출처 추출
        # \stepcounter{prob} 직전에 있는 fbox
        fbox_before_pattern = r'\\fbox\s*\{\s*([^}]+)\s*\}\s*\\\\\s*\\stepcounter\s*\{prob\}'
        fbox_before_match = re.search(fbox_before_pattern, text)
        if fbox_before_match:
            metadata['source'] = fbox_before_match.group(1).strip()

        # 2. endnote 찾기 (중괄호 개수 세기)
        endnote_content, _, _ = self.extract_endnote_with_braces(text)

        if endnote_content:
            metadata['endnote_content'] = endnote_content

            # endnote 내부의 출처 정보 (fbox) - 위에서 찾지 못한 경우만
            if not metadata['source']:
                source_pattern = r'\\fbox\s*\{\s*([^}]+)\s*\}'
                source_match = re.search(source_pattern, endnote_content)
                if source_match:
                    metadata['source'] = source_match.group(1).strip()

            # 답안
            answer_pattern = r'답\s*[:：]\s*([^\\]+)'
            answer_match = re.search(answer_pattern, endnote_content)
            if answer_match:
                metadata['answer'] = answer_match.group(1).strip()

            # 전체 노트
            metadata['note'] = endnote_content.strip()

        return metadata

    def remove_endnote(self, text: str) -> str:
        """텍스트에서 endnote 제거 (중괄호 개수 세기)"""
        endnote_content, start_pos, end_pos = self.extract_endnote_with_braces(text)

        if start_pos >= 0:
            # endnote 전체 제거
            return text[:start_pos] + text[end_pos:]

        return text

    def clean_problem_content(self, text: str) -> str:
        """문제 내용 정리"""
        # endnote 제거
        text = self.remove_endnote(text)

        # 문제 시작 부분의 \fbox{...}\\ 패턴 제거
        text = re.sub(r'\\fbox\s*\{[^}]+\}\s*\\\\\s*', '', text)

        # \stepcounter{prob} 제거
        text = re.sub(r'\\stepcounter\s*\{prob\}', '', text)

        # 불필요한 \vfill, \newpage 제거
        text = re.sub(r'\\vfill\s*', '', text)
        text = re.sub(r'\\newpage\s*', '', text)

        # 앞뒤 공백 제거
        text = text.strip()

        return text

    def has_tikz(self, text: str) -> bool:
        """TikZ 그림 포함 여부 확인"""
        return bool(re.search(r'\\begin\{tikzpicture\}', text))

    def parse_file(self, filepath: Path) -> List[Dict]:
        """단일 TeX 파일 파싱"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # UTF-8 실패시 latin-1 시도
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()

        problems = []
        relative_path = filepath.relative_to(self.base_dir)

        # 문제 시작 위치들을 모두 찾기
        # 패턴 1: \fbox{...}\\ 다음에 \stepcounter{prob}
        # 패턴 2: \stepcounter{prob}만 있는 경우
        problem_starts = []

        # \fbox{...}\\ 바로 다음에 \stepcounter{prob}가 오는 패턴
        fbox_pattern = r'(\\fbox\s*\{[^}]*\}\s*\\\\\s*)\\stepcounter\s*\{prob\}'
        for match in re.finditer(fbox_pattern, content, re.DOTALL):
            problem_starts.append({
                'pos': match.start(),
                'end': match.end(),
                'with_fbox': True,
                'fbox_start': match.start(),
                'stepcounter_end': match.end()
            })

        # 모든 \stepcounter{prob} 위치 찾기
        stepcounter_pattern = r'\\stepcounter\s*\{prob\}'
        for match in re.finditer(stepcounter_pattern, content):
            # 이미 fbox와 함께 찾은 위치가 아닌 경우만 추가
            is_duplicate = False
            for ps in problem_starts:
                if abs(match.start() - ps['pos']) < 100:  # 근처에 이미 있으면 중복
                    is_duplicate = True
                    break

            if not is_duplicate:
                problem_starts.append({
                    'pos': match.start(),
                    'end': match.end(),
                    'with_fbox': False,
                    'stepcounter_end': match.end()
                })

        # 시작 위치 순서대로 정렬
        problem_starts.sort(key=lambda x: x['pos'])

        # 각 문제 블록 추출
        for i, start_info in enumerate(problem_starts):
            # 문제 시작 위치 결정
            if start_info['with_fbox']:
                block_start = start_info['fbox_start']
            else:
                block_start = start_info['pos']

            # 문제 끝 위치 결정
            # 1. 이 블록 내에서 \vfill 또는 \newpage 찾기
            # 2. 다음 문제 시작 위치
            # 3. 파일 끝

            # 검색 시작점: \stepcounter{prob} 이후부터
            search_start = start_info['stepcounter_end']

            # 다음 문제 시작 위치
            if i + 1 < len(problem_starts):
                next_problem_pos = problem_starts[i + 1]['pos']
            else:
                next_problem_pos = len(content)

            # \vfill 또는 \newpage를 찾되, 다음 문제 시작 전까지만 검색
            search_region = content[search_start:next_problem_pos]

            # \vfill이나 \newpage 위치 찾기
            vfill_match = re.search(r'\\vfill', search_region)
            newpage_match = re.search(r'\\newpage', search_region)

            # 가장 먼저 나오는 종료 패턴 사용
            end_positions = []
            if vfill_match:
                end_positions.append(search_start + vfill_match.end())
            if newpage_match:
                end_positions.append(search_start + newpage_match.end())

            if end_positions:
                block_end = min(end_positions)
            else:
                # \vfill이나 \newpage가 없으면 다음 문제 시작 직전까지
                block_end = next_problem_pos

            # 문제 블록 추출
            problem_text = content[block_start:block_end]

            # 너무 짧은 내용은 스킵 (주석만 있거나 비어있는 경우)
            clean_text = self.clean_problem_content(problem_text)
            if len(clean_text.strip()) < 20:
                continue

            # 메타데이터 추출
            metadata = self.extract_endnote(problem_text)

            # 문제 내용 정리
            content_clean = self.clean_problem_content(problem_text)

            problems.append({
                'content': content_clean,
                'metadata': metadata,
                'source_file': str(relative_path),
                'has_tikz': self.has_tikz(content_clean)
            })

        return problems

    def save_problem(self, problem_id: str, content: str, metadata: Dict, source_file: str) -> None:
        """개별 문제 파일 저장"""
        problems_dir = self.base_dir / "problems"
        filename = problems_dir / f"{problem_id}.tex"

        # 주석으로 메타데이터 추가
        header = f"% Problem ID: {problem_id}\n"
        if metadata.get('source'):
            header += f"% Source: {metadata['source']}\n"
        if metadata.get('answer'):
            header += f"% Answer: {metadata['answer']}\n"
        header += f"% Original file: {source_file}\n\n"

        full_content = header + content

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_content)

        # endnote 내용이 있으면 solution 파일 저장
        if metadata.get('endnote_content'):
            solutions_dir = problems_dir / "solutions"
            solutions_dir.mkdir(exist_ok=True)

            solution_filename = solutions_dir / f"{problem_id}_solution.tex"

            solution_header = f"% Solution for Problem {problem_id}\n"
            if metadata.get('source'):
                solution_header += f"% Source: {metadata['source']}\n"
            solution_header += f"% Original file: {source_file}\n\n"

            solution_content = solution_header + metadata['endnote_content']

            with open(solution_filename, 'w', encoding='utf-8') as f:
                f.write(solution_content)

    def extract_all(self) -> None:
        """모든 파일에서 문제 추출"""
        tex_files = self.collect_tex_files()

        print(f"총 {len(tex_files)}개 파일 발견")
        print("=" * 60)

        log_entries = []

        for tex_file in tex_files:
            relative_path = tex_file.relative_to(self.base_dir)
            print(f"\n처리 중: {relative_path}")

            problems = self.parse_file(tex_file)

            if not problems:
                print(f"  → 문제 없음")
                continue

            print(f"  → {len(problems)}개 문제 발견")

            for problem in problems:
                self.problem_count += 1
                problem_id = f"{self.problem_count:03d}"

                # 파일 저장
                self.save_problem(
                    problem_id,
                    problem['content'],
                    problem['metadata'],
                    problem['source_file']
                )

                # 메타데이터 수집
                self.metadata.append({
                    'id': problem_id,
                    'filename': f"{problem_id}.tex",
                    'source_file': problem['source_file'],
                    'source': problem['metadata'].get('source', ''),
                    'answer': problem['metadata'].get('answer', ''),
                    'has_tikz': problem['has_tikz'],
                    'has_solution': bool(problem['metadata'].get('endnote_content', '')),
                    'note': problem['metadata'].get('note', '')
                })

                # 로그 기록
                log_entries.append(
                    f"[{problem_id}] {relative_path} - "
                    f"{problem['metadata'].get('source', 'No source')}"
                )

        print("\n" + "=" * 60)
        print(f"총 {self.problem_count}개 문제 추출 완료")

        # 메타데이터 저장
        self.save_metadata()

        # 로그 저장
        self.save_log(log_entries)

    def save_metadata(self) -> None:
        """메타데이터 JSON 저장"""
        output = {
            'total_problems': self.problem_count,
            'problems': self.metadata
        }

        metadata_file = self.base_dir / "___scripts" / "problems_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n메타데이터 저장: {metadata_file}")

    def save_log(self, log_entries: List[str]) -> None:
        """로그 파일 저장"""
        log_file = self.base_dir / "___scripts" / "extraction_log.txt"

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("문제 추출 로그\n")
            f.write("=" * 60 + "\n\n")

            for entry in log_entries:
                f.write(entry + "\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write(f"총 {len(log_entries)}개 문제 추출 완료\n")

        print(f"로그 저장: {log_file}")


def main():
    """메인 함수"""
    print("TeX 문제 추출 스크립트 시작")
    print("=" * 60)

    # 스크립트가 ___scripts 폴더에서 실행되는 경우 상위 디렉토리 사용
    import os
    script_dir = Path(__file__).parent
    if script_dir.name == "___scripts" or script_dir.name == "_scripts":
        base_dir = script_dir.parent
    else:
        base_dir = Path(".")

    print(f"기준 디렉토리: {base_dir.absolute()}")

    extractor = TexProblemExtractor(base_dir)
    extractor.extract_all()

    print("\n" + "=" * 60)
    print("추출 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
