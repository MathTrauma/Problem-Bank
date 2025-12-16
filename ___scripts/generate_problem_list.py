#!/usr/bin/env python3
"""
문제 목록 파일 생성 스크립트
지정한 범위의 문제들을 포함하는 TeX 파일 생성
"""
import argparse
from pathlib import Path


def generate_problem_list(start: int, end: int, output_file: str,
                         include_stepcounter: bool = True,
                         include_solutions: bool = False,
                         base_dir: str = None):
    """
    문제 목록 파일 생성

    Args:
        start: 시작 문제 번호
        end: 끝 문제 번호
        output_file: 출력 파일명
        include_stepcounter: \stepcounter{prob} 포함 여부
        include_solutions: solution 파일도 포함할지 여부
        base_dir: 기준 디렉토리
    """
    if base_dir:
        base_path = Path(base_dir)
    else:
        base_path = Path(__file__).parent.parent

    output_path = base_path / output_file

    lines = []

    # 헤더
    lines.append(f"% 문제 {start}번 ~ {end}번")
    lines.append(f"% 자동 생성 파일 - generate_problem_list.py")
    lines.append("")

    # 각 문제에 대해
    for n in range(start, end + 1):
        problem_id = f"{n:03d}"
        problem_file = f"problems/{problem_id}.tex"

        # 문제가 실제로 존재하는지 확인
        if not (base_path / problem_file).exists():
            lines.append(f"% Warning: {problem_file} not found!")
            continue

        # 구분선 (선택적)
        if n > start:
            lines.append("")

        # \stepcounter 추가 (선택적)
        if include_stepcounter:
            lines.append(f"\\stepcounter{{prob}}")

        # 문제 파일 입력
        lines.append(f"\\input{{{problem_file}}}")

        # solution 파일 포함 (선택적)
        if include_solutions:
            solution_file = f"problems/solutions/{problem_id}_solution.tex"
            if (base_path / solution_file).exists():
                lines.append(f"% Solution:")
                lines.append(f"\\input{{{solution_file}}}")

    # 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✅ 생성 완료: {output_path}")
    print(f"   문제 범위: {start} ~ {end} ({end - start + 1}개)")


def generate_macro_file(output_file: str = "problem_macros.tex"):
    """문제 입력용 매크로 파일 생성"""

    content = r"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 문제 입력용 매크로
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\usepackage{pgffor}  % \foreach 사용

% 문제 범위 입력 매크로
\newcommand{\inputproblems}[2]{%
    % #1: 시작 번호, #2: 끝 번호
    \foreach \n in {#1,...,#2}{%
        \stepcounter{prob}%
        \edef\filename{problems/\ifnum\n<10 00\the\n\else\ifnum\n<100 0\the\n\else\the\n\fi\fi.tex}%
        \IfFileExists{\filename}{%
            \input{\filename}%
        }{%
            \PackageWarning{problems}{File \filename\space not found!}%
        }%
    }%
}

% 개별 문제 입력 (자동 번호 증가)
\newcommand{\inputproblem}[1]{%
    % #1: 문제 번호
    \stepcounter{prob}%
    \edef\filename{problems/\ifnum#1<10 00\the\numexpr#1\relax\else\ifnum#1<100 0\the\numexpr#1\relax\else\the\numexpr#1\relax\fi\fi.tex}%
    \input{\filename}%
}

% solution 포함 문제 입력
\newcommand{\inputproblemwithsol}[1]{%
    % #1: 문제 번호
    \stepcounter{prob}%
    \edef\probfile{problems/\ifnum#1<10 00\the\numexpr#1\relax\else\ifnum#1<100 0\the\numexpr#1\relax\else\the\numexpr#1\relax\fi\fi.tex}%
    \edef\solfile{problems/solutions/\ifnum#1<10 00\the\numexpr#1\relax\else\ifnum#1<100 0\the\numexpr#1\relax\else\the\numexpr#1\relax\fi\fi_solution.tex}%
    \input{\probfile}%
    \IfFileExists{\solfile}{%
        \vspace{1em}
        \textbf{풀이:}\\
        \input{\solfile}%
    }{}%
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 사용 예제:
%
% \inputproblems{1}{20}           % 1-20번 문제
% \inputproblem{15}               % 15번 문제만
% \inputproblemwithsol{10}        % 10번 문제와 풀이
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

    output_path = Path(__file__).parent.parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 매크로 파일 생성: {output_path}")
    print(f"   TeX 프리앰블에 \\input{{{output_file}}}를 추가하세요.")


def main():
    parser = argparse.ArgumentParser(
        description='문제 목록 파일 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예제:
  # 1-20번 문제 목록 생성
  python3 generate_problem_list.py 1 20 problems_1_20.tex

  # \stepcounter 없이 생성 (\numbering에서 자동 증가하는 경우)
  python3 generate_problem_list.py 1 20 problems_1_20.tex --no-counter

  # solution 포함
  python3 generate_problem_list.py 1 20 problems_1_20.tex --with-solutions

  # 매크로 파일 생성
  python3 generate_problem_list.py --macro
        """
    )

    parser.add_argument('start', type=int, nargs='?', help='시작 문제 번호')
    parser.add_argument('end', type=int, nargs='?', help='끝 문제 번호')
    parser.add_argument('output', nargs='?', default='problems_list.tex',
                       help='출력 파일명 (기본: problems_list.tex)')
    parser.add_argument('--no-counter', action='store_true',
                       help='\\stepcounter{prob}를 포함하지 않음')
    parser.add_argument('--with-solutions', action='store_true',
                       help='solution 파일도 포함')
    parser.add_argument('--macro', action='store_true',
                       help='매크로 파일만 생성')

    args = parser.parse_args()

    if args.macro:
        generate_macro_file()
        return

    if args.start is None or args.end is None:
        parser.print_help()
        return

    generate_problem_list(
        args.start,
        args.end,
        args.output,
        include_stepcounter=not args.no_counter,
        include_solutions=args.with_solutions
    )


if __name__ == "__main__":
    main()
