#!/usr/bin/env python3
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path

def analyze_images(pdf_path, page_num):
    """PDF 페이지의 이미지 위치 분석"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    page_dict = page.get_text("dict")

    print(f"\n페이지 {page_num + 1}의 이미지:")
    images = []
    for block_idx, block in enumerate(page_dict["blocks"]):
        if block["type"] == 1:  # 이미지 블록
            bbox = block["bbox"]
            print(f"  이미지 {block_idx}: bbox = ({bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f})")
            images.append(bbox)

    doc.close()
    return images

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

# 먼저 이미지 위치 분석
print("=== area.pdf 분석 ===")
area_images_p1 = analyze_images("_INPUT_/area.pdf", 0)

print("\n=== plain0.pdf 분석 ===")
plain0_images_p1 = analyze_images("_INPUT_/plain0.pdf", 0)
plain0_images_p2 = analyze_images("_INPUT_/plain0.pdf", 1)
plain0_images_p3 = analyze_images("_INPUT_/plain0.pdf", 2)
