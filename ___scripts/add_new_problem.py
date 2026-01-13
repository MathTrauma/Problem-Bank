#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새 문제 추가 및 관리 스크립트
- 문제 파일 생성
- 메타데이터 입력
- 풀이 파일 생성
- JSON 메타데이터 자동 업데이트
"""

import json
from pathlib import Path
import sys
from datetime import datetime


class ProblemManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.problems_dir = base_dir / 'web_app' / 'data' / 'problems'
        self.solutions_dir = self.problems_dir / 'solutions'
        self.metadata_file = base_dir / 'web_app' / 'data' / 'problems_metadata.json'

        # 디렉토리 생성
        self.problems_dir.mkdir(exist_ok=True)
        self.solutions_dir.mkdir(exist_ok=True)

    def get_next_problem_id(self) -> str:
        """다음 문제 번호 자동 계산"""
        existing_files = list(self.problems_dir.glob('*.tex'))
        if not existing_files:
            return '001'

        # 파일명에서 숫자 추출
        numbers = []
        for f in existing_files:
            try:
                num = int(f.stem)
                numbers.append(num)
            except ValueError:
                continue

        if numbers:
            next_num = max(numbers) + 1
            return f'{next_num:03d}'
        else:
            return '001'

    def load_metadata(self) -> dict:
        """메타데이터 로드"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'total_problems': 0, 'problems': []}

    def save_metadata(self, data: dict):
        """메타데이터 저장"""
        # 백업 생성
        if self.metadata_file.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.metadata_file.parent / f'problems_metadata_backup_{timestamp}.json'
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                with open(backup_file, 'w', encoding='utf-8') as fb:
                    fb.write(f.read())
            print(f"📦 Backup created: {backup_file.name}")

        # 저장
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_problem_file(self, problem_id: str, source: str = '', content: str = '') -> Path:
        """문제 파일 생성"""
        problem_file = self.problems_dir / f'{problem_id}.tex'

        if problem_file.exists():
            print(f"⚠️  File already exists: {problem_file}")
            overwrite = input("Overwrite? (y/N): ").strip().lower()
            if overwrite != 'y':
                return problem_file

        # 템플릿
        template = f"""% Problem ID: {problem_id}
% Source: {source}
% Created: {datetime.now().strftime('%Y-%m-%d')}

\\numbering {content}
"""

        with open(problem_file, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"✅ Problem file created: {problem_file}")
        return problem_file

    def create_solution_file(self, problem_id: str, solution: str = '') -> Path:
        """풀이 파일 생성"""
        solution_file = self.solutions_dir / f'{problem_id}_solution.tex'

        if solution_file.exists():
            print(f"⚠️  Solution file already exists: {solution_file}")
            overwrite = input("Overwrite? (y/N): ").strip().lower()
            if overwrite != 'y':
                return solution_file

        # 템플릿
        template = solution if solution else f"""% Solution for Problem {problem_id}
% Created: {datetime.now().strftime('%Y-%m-%d')}

% 풀이를 여기에 작성하세요
"""

        with open(solution_file, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"✅ Solution file created: {solution_file}")
        return solution_file

    def add_to_metadata(self, problem_id: str, metadata: dict):
        """메타데이터에 문제 추가"""
        data = self.load_metadata()

        # 중복 체크
        for p in data['problems']:
            if p['id'] == problem_id:
                print(f"⚠️  Problem {problem_id} already exists in metadata")
                update = input("Update metadata? (y/N): ").strip().lower()
                if update == 'y':
                    p.update(metadata)
                    self.save_metadata(data)
                    print("✅ Metadata updated")
                return

        # 새 문제 추가
        data['problems'].append({
            'id': problem_id,
            **metadata
        })
        data['total_problems'] = len(data['problems'])

        self.save_metadata(data)
        print("✅ Metadata added")

    def interactive_add(self):
        """대화형으로 문제 추가"""
        print("=" * 60)
        print("새 문제 추가")
        print("=" * 60)

        # 문제 ID
        problem_id = self.get_next_problem_id()
        print(f"\n📝 문제 번호: {problem_id}")

        custom_id = input(f"다른 번호를 사용하시겠습니까? (Enter를 누르면 {problem_id} 사용): ").strip()
        if custom_id:
            problem_id = custom_id.zfill(3)

        # 메타데이터 입력
        print("\n📋 메타데이터 입력 (Enter를 누르면 비워둠)")
        print("-" * 60)

        source = input("출처 (예: 29회(2015) KMO 중등부 1차 3번): ").strip()
        answer = input("답안: ").strip()
        category = input("카테고리 (예: 원, 삼각형): ").strip()
        difficulty = input("난이도 (1-5): ").strip()
        tags = input("태그 (쉼표로 구분): ").strip()
        note = input("메모: ").strip()

        # 문제 내용
        print("\n📝 문제 내용 입력")
        print("-" * 60)
        print("문제 내용을 입력하세요 (여러 줄 가능, 완료하려면 빈 줄에서 Ctrl+D):")

        content_lines = []
        try:
            while True:
                line = input()
                content_lines.append(line)
        except EOFError:
            pass

        content = '\n'.join(content_lines).strip()

        # 풀이 여부
        add_solution = input("\n풀이 파일을 생성하시겠습니까? (y/N): ").strip().lower() == 'y'

        # 파일 생성
        print("\n" + "=" * 60)
        print("파일 생성 중...")
        print("=" * 60)

        self.create_problem_file(problem_id, source, content)

        has_solution = False
        if add_solution:
            self.create_solution_file(problem_id)
            has_solution = True

        # 메타데이터 구성
        metadata = {
            'source': source,
            'answer': answer,
            'category': category,
            'difficulty': int(difficulty) if difficulty.isdigit() else None,
            'tags': [t.strip() for t in tags.split(',') if t.strip()],
            'note': note,
            'has_tikz': False,  # 수동으로 확인 필요
            'has_solution': has_solution,
            'source_file': f'manually_added_{datetime.now().strftime("%Y%m%d")}'
        }

        # None 값 제거
        metadata = {k: v for k, v in metadata.items() if v not in (None, '', [])}

        self.add_to_metadata(problem_id, metadata)

        print("\n" + "=" * 60)
        print("✅ 완료!")
        print("=" * 60)
        print(f"문제 파일: problems/{problem_id}.tex")
        if has_solution:
            print(f"풀이 파일: problems/solutions/{problem_id}_solution.tex")
        print(f"메타데이터: {self.metadata_file}")
        print("\n다음 단계:")
        print("1. 문제 파일을 편집기로 열어 내용 확인/수정")
        if has_solution:
            print("2. 풀이 파일에 풀이 작성")
        print("3. TikZ 그림이 있다면 메타데이터의 has_tikz를 true로 수정")
        print("4. git add 및 commit")

    def quick_add(self, problem_id: str, source: str, content: str):
        """빠른 추가 (스크립트용)"""
        self.create_problem_file(problem_id, source, content)

        metadata = {
            'source': source,
            'has_tikz': False,
            'has_solution': False,
            'source_file': f'manually_added_{datetime.now().strftime("%Y%m%d")}'
        }

        self.add_to_metadata(problem_id, metadata)


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='Add new geometry problem')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive mode (default)')
    parser.add_argument('--id', type=str, help='Problem ID (for quick mode)')
    parser.add_argument('--source', type=str, help='Problem source (for quick mode)')
    parser.add_argument('--content', type=str, help='Problem content (for quick mode)')

    args = parser.parse_args()

    # 경로 설정
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent

    manager = ProblemManager(base_dir)

    if args.id and args.source and args.content:
        # Quick mode
        manager.quick_add(args.id, args.source, args.content)
    else:
        # Interactive mode
        manager.interactive_add()


if __name__ == '__main__':
    main()
