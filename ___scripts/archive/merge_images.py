#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두 이미지를 수직으로 결합
"""

from PIL import Image
from pathlib import Path

def merge_images_vertically(top_path, bottom_path, output_path):
    """
    두 이미지를 수직으로 결합

    Args:
        top_path: 상단 이미지 경로
        bottom_path: 하단 이미지 경로
        output_path: 출력 파일 경로
    """
    # 이미지 로드
    top_img = Image.open(top_path)
    bottom_img = Image.open(bottom_path)

    # 크기 확인
    top_width, top_height = top_img.size
    bottom_width, bottom_height = bottom_img.size

    print(f"상단 이미지: {top_width} x {top_height}")
    print(f"하단 이미지: {bottom_width} x {bottom_height}")

    # 새 이미지 생성 (너비는 큰 쪽 기준, 높이는 합)
    new_width = max(top_width, bottom_width)
    new_height = top_height + bottom_height

    # 흰색 배경의 새 이미지 생성
    merged_img = Image.new('RGB', (new_width, new_height), 'white')

    # 상단 이미지 붙이기 (중앙 정렬)
    top_x = (new_width - top_width) // 2
    merged_img.paste(top_img, (top_x, 0))

    # 하단 이미지 붙이기 (중앙 정렬)
    bottom_x = (new_width - bottom_width) // 2
    merged_img.paste(bottom_img, (bottom_x, top_height))

    # 저장
    merged_img.save(output_path)
    print(f"\n✅ 결합 완료: {output_path}")
    print(f"   최종 크기: {new_width} x {new_height}")
    print(f"   파일 크기: {output_path.stat().st_size / 1024:.1f} KB")

    return output_path


if __name__ == '__main__':
    figures_dir = Path("/Users/_Math_(수업)/중등_경시수업/__Geometry/___scripts/extracted_figures")

    # 미적분 26번 그림 결합
    top_image = figures_dir / "page14_image2.png"
    bottom_image = figures_dir / "page14_image3.png"
    output_image = figures_dir / "suneung_2026_calculus_26_merged.png"

    merge_images_vertically(top_image, bottom_image, output_image)
