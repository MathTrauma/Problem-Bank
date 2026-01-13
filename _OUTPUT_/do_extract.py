#!/usr/bin/env python3
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path

def extract_image_from_bbox(pdf_path, page_num, bbox_list, output_path):
    """bbox 기반으로 이미지 추출"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    images = []

    for bbox in bbox_list:
        # bbox 영역을 픽셀 이미지로 렌더링 (2배 해상도)
        pix = page.get_pixmap(clip=fitz.Rect(bbox), matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    # 이미지가 하나면 그대로 저장
    if len(images) == 1:
        images[0].save(output_path)
        print(f"저장됨: {output_path}")
    else:
        # 여러 이미지를 수직으로 병합
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images)

        merged = Image.new('RGB', (max_width, total_height), 'white')
        y_offset = 0
        for img in images:
            x_offset = (max_width - img.width) // 2
            merged.paste(img, (x_offset, y_offset))
            y_offset += img.height

        merged.save(output_path)
        print(f"병합 저장됨: {output_path}")

    doc.close()

# area.pdf - 문제 1
extract_image_from_bbox(
    "_INPUT_/area.pdf",
    0,
    [(22.5, 98.2, 265.5, 224.2)],
    "_OUTPUT_/area_problem_01_figure.png"
)

# plain0.pdf
# 페이지 1
extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    0,
    [(22.5, 98.2, 265.5, 241.5)],
    "_OUTPUT_/plain0_problem_01_figure.png"
)

extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    0,
    [(22.5, 443.2, 265.5, 590.2)],
    "_OUTPUT_/plain0_problem_02_figure.png"
)

extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    0,
    [(320.2, 98.2, 562.5, 195.8)],
    "_OUTPUT_/plain0_problem_03_figure.png"
)

extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    0,
    [(320.2, 443.2, 562.5, 600.8)],
    "_OUTPUT_/plain0_problem_04_figure.png"
)

# 페이지 2
extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    1,
    [(22.5, 98.2, 265.5, 230.2)],
    "_OUTPUT_/plain0_problem_05_figure.png"
)

extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    1,
    [(22.5, 438.0, 265.5, 555.8)],
    "_OUTPUT_/plain0_problem_06_figure.png"
)

extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    1,
    [(320.2, 98.3, 562.5, 217.5)],
    "_OUTPUT_/plain0_problem_07_figure.png"
)

extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    1,
    [(320.2, 438.0, 562.5, 657.0)],
    "_OUTPUT_/plain0_problem_08_figure.png"
)

# 페이지 3
extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    2,
    [(22.5, 98.2, 265.5, 258.0)],
    "_OUTPUT_/plain0_problem_09_figure.png"
)

extract_image_from_bbox(
    "_INPUT_/plain0.pdf",
    2,
    [(320.2, 98.2, 562.5, 255.0)],
    "_OUTPUT_/plain0_problem_10_figure.png"
)

print("\n모든 이미지 추출 완료!")
