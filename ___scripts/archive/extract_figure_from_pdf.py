#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF에서 특정 그림 영역을 추출하여 SVG로 변환
"""

import fitz  # PyMuPDF
from PIL import Image
import io
import subprocess
from pathlib import Path

def extract_figure_from_pdf(pdf_path, page_num, output_dir):
    """
    PDF에서 그림을 추출

    Args:
        pdf_path: PDF 파일 경로
        page_num: 페이지 번호 (0-based)
        output_dir: 출력 디렉토리
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # PDF 열기
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    print(f"페이지 {page_num + 1} 처리 중...")
    print(f"페이지 크기: {page.rect}")

    # 페이지의 모든 이미지 추출
    image_list = page.get_images()
    print(f"발견된 이미지 개수: {len(image_list)}")

    # 이미지 추출
    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]

        # PNG로 저장
        output_path = output_dir / f"page{page_num + 1}_image{img_index + 1}.png"
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"  이미지 저장: {output_path}")

    # 페이지 전체를 고해상도 이미지로 렌더링 (그림이 벡터인 경우)
    mat = fitz.Matrix(3.0, 3.0)  # 3배 확대
    pix = page.get_pixmap(matrix=mat, alpha=False)

    # 전체 페이지 PNG 저장
    full_page_path = output_dir / f"page{page_num + 1}_full.png"
    pix.save(str(full_page_path))
    print(f"  전체 페이지 저장: {full_page_path}")

    doc.close()

    return full_page_path


def extract_figure_region(pdf_path, page_num, bbox, output_path):
    """
    PDF의 특정 영역만 추출

    Args:
        pdf_path: PDF 파일 경로
        page_num: 페이지 번호 (0-based)
        bbox: 추출할 영역 (x0, y0, x1, y1) - 포인트 단위
        output_path: 출력 파일 경로
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    # 지정된 영역만 렌더링
    rect = fitz.Rect(bbox)
    mat = fitz.Matrix(4.0, 4.0)  # 4배 확대 for better quality
    pix = page.get_pixmap(matrix=mat, clip=rect, alpha=False)

    # PNG로 저장
    pix.save(str(output_path))
    print(f"영역 추출 완료: {output_path}")
    print(f"  크기: {pix.width} x {pix.height}")

    doc.close()
    return output_path


def png_to_svg(png_path, svg_path):
    """
    PNG를 SVG로 변환 (potrace 사용)

    Args:
        png_path: PNG 파일 경로
        svg_path: 출력 SVG 파일 경로
    """
    # potrace가 설치되어 있는지 확인
    try:
        subprocess.run(['potrace', '--version'],
                      capture_output=True, check=True)
    except:
        print("potrace가 설치되어 있지 않습니다. brew install potrace로 설치하세요.")
        return None

    # PNG를 PBM으로 변환 (potrace는 bitmap 형식 필요)
    img = Image.open(png_path)

    # 그레이스케일로 변환
    img_gray = img.convert('L')

    # 임시 PBM 파일
    pbm_path = png_path.with_suffix('.pbm')
    img_gray.save(pbm_path)

    # potrace로 SVG 변환
    result = subprocess.run(
        ['potrace', '-s', '-o', str(svg_path), str(pbm_path)],
        capture_output=True,
        text=True
    )

    # 임시 파일 삭제
    pbm_path.unlink()

    if result.returncode == 0:
        print(f"SVG 변환 완료: {svg_path}")
        return svg_path
    else:
        print(f"SVG 변환 실패: {result.stderr}")
        return None


if __name__ == '__main__':
    # 설정
    pdf_path = "/Users/_Math_(수업)/중등_경시수업/__Geometry/suneung-26_2.pdf"
    output_dir = Path("/Users/_Math_(수업)/중등_경시수업/__Geometry/___scripts/extracted_figures")

    # 미적분 26번 문제는 페이지 14 (0-based index: 13)
    page_num = 13

    # 1. 전체 페이지 추출
    full_page = extract_figure_from_pdf(pdf_path, page_num, output_dir)

    # 2. 그림 영역만 추출 (bbox 좌표는 PDF 좌표계 기준)
    # 페이지를 먼저 확인한 후 그림 위치를 찾아야 함
    # 대략적인 위치 추정 (미적분 26번 문제의 그림)
    # 이 값들은 실제 PDF를 보고 조정해야 함
    figure_bbox = (100, 400, 500, 650)  # (x0, y0, x1, y1)

    figure_path = output_dir / f"calculus_26_figure.png"
    extract_figure_region(pdf_path, page_num, figure_bbox, figure_path)

    # 3. PNG를 SVG로 변환 (선택적)
    svg_path = output_dir / f"calculus_26_figure.svg"
    # png_to_svg(figure_path, svg_path)
