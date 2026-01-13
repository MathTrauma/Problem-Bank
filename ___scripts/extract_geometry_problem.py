#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF에서 도형(기하) 문제 추출 - 텍스트와 그림 모두 추출

주요 기능:
1. PDF 페이지에서 문제 텍스트 추출
2. LaTeX 형식(.tex)으로 저장
3. 그림 자동 추출 및 병합 (PNG + SVG)
4. 모든 파일을 지정된 디렉토리에 저장
"""

import fitz  # PyMuPDF
from PIL import Image
import subprocess
from pathlib import Path
import io
import re


def extract_text_from_page(pdf_path, page_num):
    """
    PDF 페이지에서 텍스트 추출

    Args:
        pdf_path: PDF 파일 경로
        page_num: 페이지 번호 (0-based)

    Returns:
        str: 추출된 텍스트
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    # 텍스트 추출
    text = page.get_text("text")

    doc.close()

    return text


def parse_problem_text(text, problem_number=None):
    """
    추출된 텍스트를 파싱하여 문제 내용 추출

    Args:
        text: 추출된 원본 텍스트
        problem_number: 문제 번호 (선택)

    Returns:
        dict: {'number': str, 'content': str}
    """
    # 줄바꿈 정리
    lines = text.strip().split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    # 문제 번호 찾기
    if problem_number is None:
        # 첫 줄에서 문제 번호 찾기 (예: "26.", "26번", "문제 26")
        number_pattern = r'(\d+)[.\)번]'
        for line in cleaned_lines[:5]:  # 처음 5줄에서 찾기
            match = re.search(number_pattern, line)
            if match:
                problem_number = match.group(1)
                break

    # 문제 내용 추출 (전체 텍스트 사용)
    content = '\n'.join(cleaned_lines)

    return {
        'number': problem_number or 'unknown',
        'content': content
    }


def create_tex_file(problem_data, figure_filenames, output_path):
    """
    문제 데이터를 LaTeX 파일로 저장

    Args:
        problem_data: parse_problem_text()의 결과
        figure_filenames: 그림 파일명 리스트 (확장자 제외)
        output_path: 출력 .tex 파일 경로
    """
    content = problem_data['content']

    # LaTeX 특수 문자 이스케이프 (선택적)
    # content = content.replace('\\', '\\\\').replace('_', '\\_')

    # .tex 파일 생성
    tex_content = f"""% 문제 번호: {problem_data['number']}
% 추출 날짜: {Path(output_path).stat().st_mtime if output_path.exists() else 'N/A'}

\\begin{{problem}}
{content}
\\end{{problem}}
"""

    # 그림 참조 추가
    if figure_filenames:
        tex_content += "\n% 첨부 그림:\n"
        for fig_name in figure_filenames:
            tex_content += f"% \\includegraphics{{{fig_name}.svg}}\n"

    # 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tex_content)

    print(f"  ✅ TEX 저장: {output_path.name} ({len(content)} 문자)")


def extract_images_with_positions(pdf_path, page_num):
    """
    PDF 페이지에서 이미지와 위치 정보를 함께 추출

    Args:
        pdf_path: PDF 파일 경로
        page_num: 페이지 번호 (0-based)

    Returns:
        List of dicts with keys: 'number', 'bbox', 'image', 'width', 'height'
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    image_info_list = []

    # 페이지의 텍스트와 이미지 정보를 딕셔너리로 추출
    page_dict = page.get_text("dict")

    # 이미지 추출
    for block in page_dict["blocks"]:
        if block["type"] == 1:  # 이미지 블록
            # 이미지 위치 정보 (bbox)
            bbox = fitz.Rect(block["bbox"])

            # 이미지 데이터 (이미 bytes 형태)
            image_bytes = block["image"]

            # PIL Image로 변환
            pil_image = Image.open(io.BytesIO(image_bytes))

            image_info = {
                'number': block.get("number", 0),
                'bbox': bbox,  # fitz.Rect object (x0, y0, x1, y1)
                'image': pil_image,
                'width': pil_image.width,
                'height': pil_image.height
            }

            image_info_list.append(image_info)

    doc.close()

    return image_info_list


def group_adjacent_images(image_info_list, y_threshold=10, x_threshold=10):
    """
    수직으로 인접한 이미지들을 그룹화

    Args:
        image_info_list: extract_images_with_positions()의 결과
        y_threshold: 수직 간격 임계값 (포인트 단위)
        x_threshold: 수평 위치 차이 허용 범위

    Returns:
        List of groups, 각 그룹은 image_info 리스트
    """
    if not image_info_list:
        return []

    # y좌표(상단) 기준으로 정렬
    sorted_images = sorted(image_info_list, key=lambda x: x['bbox'].y0)

    groups = []
    current_group = [sorted_images[0]]

    for i in range(1, len(sorted_images)):
        prev_img = current_group[-1]
        curr_img = sorted_images[i]

        prev_bbox = prev_img['bbox']
        curr_bbox = curr_img['bbox']

        # 이전 이미지의 하단과 현재 이미지의 상단 사이의 간격
        y_gap = curr_bbox.y0 - prev_bbox.y1

        # x좌표 차이 (좌측 정렬 기준)
        x_diff = abs(curr_bbox.x0 - prev_bbox.x0)

        # 너비 차이
        width_diff = abs(curr_bbox.width - prev_bbox.width)

        # 수직으로 인접하고, x좌표와 너비가 유사하면 같은 그룹
        if (y_gap < y_threshold and
            x_diff < x_threshold and
            width_diff < x_threshold):
            current_group.append(curr_img)
        else:
            # 새로운 그룹 시작
            groups.append(current_group)
            current_group = [curr_img]

    # 마지막 그룹 추가
    groups.append(current_group)

    return groups


def merge_images_vertically(image_group):
    """
    이미지 그룹을 수직으로 병합

    Args:
        image_group: group_adjacent_images()의 각 그룹

    Returns:
        PIL Image (병합된 이미지)
    """
    if len(image_group) == 1:
        return image_group[0]['image']

    # 정렬 (y좌표 기준)
    sorted_group = sorted(image_group, key=lambda x: x['bbox'].y0)

    # 최대 너비 계산
    max_width = max(img['width'] for img in sorted_group)

    # 총 높이 계산
    total_height = sum(img['height'] for img in sorted_group)

    # 새 이미지 생성 (흰색 배경)
    merged_img = Image.new('RGB', (max_width, total_height), 'white')

    # 이미지 붙이기
    y_offset = 0
    for img_info in sorted_group:
        img = img_info['image']
        # 중앙 정렬
        x_offset = (max_width - img.width) // 2
        merged_img.paste(img, (x_offset, y_offset))
        y_offset += img.height

    return merged_img


def png_to_svg(png_path, svg_path, threshold=200):
    """
    PNG를 SVG로 변환 (potrace 사용)

    Args:
        png_path: PNG 파일 경로
        svg_path: 출력 SVG 파일 경로
        threshold: 이진화 임계값 (0-255)

    Returns:
        SVG 파일 경로 또는 None
    """
    # potrace 설치 확인
    try:
        subprocess.run(['potrace', '--version'],
                      capture_output=True, check=True)
    except:
        print("  ⚠️  potrace가 설치되어 있지 않습니다. brew install potrace로 설치하세요.")
        return None

    # PNG를 그레이스케일로 변환 후 이진화
    img = Image.open(png_path)
    img_gray = img.convert('L')
    img_bw = img_gray.point(lambda x: 0 if x < threshold else 255, '1')  # type: ignore

    # PBM으로 저장
    pbm_path = png_path.with_suffix('.pbm')
    img_bw.save(pbm_path)

    # potrace로 SVG 변환
    result = subprocess.run(
        ['potrace', '-s', '-o', str(svg_path), str(pbm_path)],
        capture_output=True,
        text=True
    )

    # 임시 PBM 파일 삭제
    pbm_path.unlink()

    if result.returncode == 0:
        print(f"    ✅ SVG 변환: {svg_path.name} ({svg_path.stat().st_size / 1024:.1f} KB)")
        return svg_path
    else:
        print(f"    ❌ SVG 변환 실패: {result.stderr}")
        return None


def extract_geometry_problem(pdf_path, page_num, output_dir, base_name=None, problem_number=None):
    """
    PDF 페이지에서 도형 문제 전체 추출 (텍스트 + 그림)

    Args:
        pdf_path: PDF 파일 경로
        page_num: 페이지 번호 (0-based)
        output_dir: 출력 디렉토리
        base_name: 출력 파일명 기본 이름 (선택)
        problem_number: 문제 번호 (선택, 자동 감지 가능)

    Returns:
        dict: {'tex': Path, 'figures': List[Path]}
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📄 PDF: {Path(pdf_path).name}, 페이지: {page_num + 1}")

    # 1. 텍스트 추출
    print("  📝 텍스트 추출 중...")
    text = extract_text_from_page(pdf_path, page_num)
    problem_data = parse_problem_text(text, problem_number)

    # base_name이 없으면 문제 번호 사용
    if base_name is None:
        base_name = f"problem_{problem_data['number']}"

    # 2. 이미지 추출
    print("  🖼️  이미지 추출 중...")
    image_info_list = extract_images_with_positions(pdf_path, page_num)
    print(f"    발견된 이미지: {len(image_info_list)}개")

    figure_files = []
    figure_names = []  # 확장자 제외 이름

    if image_info_list:
        # 연속된 이미지 그룹화
        print("    연속된 이미지 그룹화 중...")
        groups = group_adjacent_images(image_info_list)
        print(f"    그룹 개수: {len(groups)}개")

        # 각 그룹 처리
        for group_idx, group in enumerate(groups):
            print(f"\n    그룹 {group_idx + 1}: {len(group)}개 이미지")

            # 병합
            merged_img = merge_images_vertically(group)

            # 파일명 생성
            if len(groups) == 1:
                png_filename = f"{base_name}_figure.png"
                svg_filename = f"{base_name}_figure.svg"
                fig_name = f"{base_name}_figure"
            else:
                png_filename = f"{base_name}_figure_{group_idx + 1}.png"
                svg_filename = f"{base_name}_figure_{group_idx + 1}.svg"
                fig_name = f"{base_name}_figure_{group_idx + 1}"

            png_path = output_dir / png_filename
            svg_path = output_dir / svg_filename

            # PNG 저장
            merged_img.save(png_path)
            print(f"    ✅ PNG 저장: {png_filename} ({merged_img.width}x{merged_img.height}, {png_path.stat().st_size / 1024:.1f} KB)")
            figure_files.append(png_path)

            # SVG 변환
            svg_result = png_to_svg(png_path, svg_path)
            if svg_result:
                figure_files.append(svg_path)

            figure_names.append(fig_name)

    # 3. TEX 파일 생성
    print(f"\n  📄 TEX 파일 생성 중...")
    tex_path = output_dir / f"{base_name}.tex"
    create_tex_file(problem_data, figure_names, tex_path)

    # 결과 반환
    result = {
        'tex': tex_path,
        'figures': figure_files,
        'problem_number': problem_data['number']
    }

    print(f"\n✅ 완료: {1 + len(figure_files)}개 파일 생성")
    print(f"  - TEX: {tex_path.name}")
    for fig in figure_files:
        print(f"  - 그림: {fig.name}")

    return result


if __name__ == '__main__':
    # 예제: 수능 미적분 26번 문제
    BASE_DIR = Path(__file__).parent.parent
    pdf_path = BASE_DIR / "suneung-26_2.pdf"
    page_num = 13  # 페이지 14 (0-based index)
    output_dir = BASE_DIR / "___scripts" / "extracted_figures"

    extract_geometry_problem(
        pdf_path=pdf_path,
        page_num=page_num,
        output_dir=output_dir,
        base_name="suneung_2026_calculus_26",
        problem_number="26"
    )
