#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PNG 이미지를 SVG로 변환
"""

from PIL import Image
import subprocess
from pathlib import Path

def png_to_svg_simple(png_path, svg_path, threshold=128):
    """
    PNG를 SVG로 변환 (potrace 사용)

    Args:
        png_path: PNG 파일 경로
        svg_path: 출력 SVG 파일 경로
        threshold: 이진화 임계값 (0-255)
    """
    png_path = Path(png_path)
    svg_path = Path(svg_path)

    # PNG를 PBM으로 변환
    img = Image.open(png_path)

    # 그레이스케일로 변환
    img_gray = img.convert('L')

    # 이진화 (흑백으로 변환)
    img_bw = img_gray.point(lambda x: 0 if x < threshold else 255, '1')

    # PBM 형식으로 저장
    pbm_path = png_path.with_suffix('.pbm')
    img_bw.save(pbm_path)

    print(f"PBM 변환 완료: {pbm_path}")

    # potrace로 SVG 변환
    result = subprocess.run(
        ['potrace', '-s', '-o', str(svg_path), str(pbm_path)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"✅ SVG 변환 완료: {svg_path}")
        print(f"   크기: {svg_path.stat().st_size / 1024:.1f} KB")

        # PBM 파일 유지 (필요시 삭제)
        # pbm_path.unlink()

        return svg_path
    else:
        print(f"❌ SVG 변환 실패: {result.stderr}")
        return None


if __name__ == '__main__':
    figures_dir = Path("/Users/_Math_(수업)/중등_경시수업/__Geometry/___scripts/extracted_figures")

    # 각 이미지를 SVG로 변환
    png_files = list(figures_dir.glob("*.png"))

    for png_file in png_files:
        svg_file = png_file.with_suffix('.svg')
        print(f"\n변환 중: {png_file.name}")
        png_to_svg_simple(png_file, svg_file, threshold=200)
