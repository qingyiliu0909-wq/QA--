# -*- coding: utf-8 -*-
"""交互稿/PDF -> 可视觉读取的图片
将 PDF 每页渲染为 PNG;超长单页(长截图式交互稿)自动按高度切成纵向条带,
便于视觉模型逐条阅读(markitdown 只抽文字会丢失状态图/角标/布局信息)。

依赖: PyMuPDF(fitz) + Pillow,均已装在 Tools/markitdown 的 venv。
建议用该 venv 的 python 运行:
  Tools/markitdown/Scripts/python.exe Tools/doc_crosscheck/pdf_to_strips.py <pdf> <out_dir>

可选参数:
  --scale N     渲染倍率(默认 2)
  --strip N     条带高度像素(默认 2000),0 表示不切条
  --overlap N   条带重叠像素(默认 150)
  --width N     条带统一缩放宽度(默认 1600)
"""
import sys, os, argparse
import fitz
from PIL import Image
Image.MAX_IMAGE_PIXELS = None


def render_pages(pdf, out, scale):
    doc = fitz.open(pdf)
    mat = fitz.Matrix(scale, scale)
    paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat)
        p = os.path.join(out, f"page_{i+1:02d}.png")
        pix.save(p)
        paths.append(p)
        print(f"[page] {i+1}: {pix.width}x{pix.height} -> {p}")
    return paths


def slice_tall(png, out, strip, overlap, width):
    im = Image.open(png)
    W, H = im.size
    base = os.path.splitext(os.path.basename(png))[0]
    if strip <= 0 or H <= strip:
        return [png]
    paths, i, y = [], 0, 0
    while y < H:
        y2 = min(y + strip, H)
        crop = im.crop((0, y, W, y2))
        scale = width / W
        crop = crop.resize((width, int((y2 - y) * scale)))
        p = os.path.join(out, f"{base}_strip_{i:02d}.png")
        crop.save(p)
        paths.append(p)
        print(f"[strip] {p} {crop.size}")
        i += 1
        y += strip - overlap
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out_dir")
    ap.add_argument("--scale", type=float, default=2)
    ap.add_argument("--strip", type=int, default=2000)
    ap.add_argument("--overlap", type=int, default=150)
    ap.add_argument("--width", type=int, default=1600)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    for pg in render_pages(a.pdf, a.out_dir, a.scale):
        slice_tall(pg, a.out_dir, a.strip, a.overlap, a.width)
    print("done ->", a.out_dir)


if __name__ == "__main__":
    main()
