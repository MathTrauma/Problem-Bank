#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF에서 그림을 추출하고 연속된 영역의 이미지를 자동으로 병합

주요 기능:
1. PDF 페이지에서 임베디드 이미지 추출
2. 수직으로 연속된 이미지 자동 감지 및 병합
3. PNG 및 SVG 형식으로 저장
"""

import fitz  # PyMuPDF
from PIL import Image
import subprocess
from pathlib import Path
import io


def extract_images_with_positions(pdf_path, page_num):
    """
    PDF 페이지에서 이미지와 위치 정보를 함께 추출

    Args:
        pdf_path: PDF 파일 경로
        page_num: 페이지 번호 (0-based)

    Returns:
        List of dicts with keys: 'xref', 'bbox', 'image', 'width', 'height'
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
        print("⚠️  potrace가 설치되어 있지 않습니다. brew install potrace로 설치하세요.")
        return None

    # PNG를 그레이스케일로 변환 후 이진화
    img = Image.open(png_path)
    img_gray = img.convert('L')
    img_bw = img_gray.point(lambda x: 0 if x < threshold else 255, '1') # type: ignore

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
        print(f"  ✅ SVG 변환: {svg_path.name} ({svg_path.stat().st_size / 1024:.1f} KB)")
        return svg_path
    else:
        print(f"  ❌ SVG 변환 실패: {result.stderr}")
        return None


def extract_and_merge_figures(pdf_path, page_num, output_dir, base_name="figure"):
    """
    PDF 페이지에서 그림을 추출하고 연속된 이미지를 자동으로 병합

    Args:
        pdf_path: PDF 파일 경로
        page_num: 페이지 번호 (0-based)
        output_dir: 출력 디렉토리
        base_name: 출력 파일명 기본 이름

    Returns:
        List of output file paths (PNG, SVG)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📄 PDF: {Path(pdf_path).name}, 페이지: {page_num + 1}")

    # 1. 이미지 위치 정보와 함께 추출
    print("  이미지 추출 중...")
    image_info_list = extract_images_with_positions(pdf_path, page_num)
    print(f"  발견된 이미지: {len(image_info_list)}개")

    if not image_info_list:
        print("  ⚠️  이미지가 없습니다.")
        return []

    # 2. 연속된 이미지 그룹화
    print("  연속된 이미지 그룹화 중...")
    groups = group_adjacent_images(image_info_list)
    print(f"  그룹 개수: {len(groups)}개")

    # 3. 각 그룹 처리
    output_files = []

    for group_idx, group in enumerate(groups):
        print(f"\n  그룹 {group_idx + 1}: {len(group)}개 이미지")

        # 병합
        merged_img = merge_images_vertically(group)

        # 파일명 생성
        if len(groups) == 1:
            png_filename = f"{base_name}.png"
            svg_filename = f"{base_name}.svg"
        else:
            png_filename = f"{base_name}_{group_idx + 1}.png"
            svg_filename = f"{base_name}_{group_idx + 1}.svg"

        png_path = output_dir / png_filename
        svg_path = output_dir / svg_filename

        # PNG 저장
        merged_img.save(png_path)
        print(f"  ✅ PNG 저장: {png_filename} ({merged_img.width}x{merged_img.height}, {png_path.stat().st_size / 1024:.1f} KB)")
        output_files.append(png_path)

        # SVG 변환
        svg_result = png_to_svg(png_path, svg_path)
        if svg_result:
            output_files.append(svg_path)

    print(f"\n✅ 완료: {len(output_files)}개 파일 생성")
    return output_files


if __name__ == '__main__':
    # 예제: 수능 미적분 26번 문제
    BASE_DIR = Path(__file__).parent.parent
    pdf_path = BASE_DIR / "suneung-26_2.pdf"
    page_num = 13  # 페이지 14 (0-based index)
    output_dir = BASE_DIR / "___scripts" / "extracted_figures"

    extract_and_merge_figures(
        pdf_path=pdf_path,
        page_num=page_num,
        output_dir=output_dir,
        base_name="suneung_2026_calculus_26_auto"
    )
