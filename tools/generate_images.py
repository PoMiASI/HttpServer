#!/usr/bin/env python3
"""
Generate large random images for browser download tests.

Examples:
  python tools/generate_images.py --out web/images --count 12 --width 4000 --height 3000 --format jpg --quality 85
  python tools/generate_images.py --out web/images --sizes 1024x1024,2000x2000 --count 5 --format png
"""
import argparse
import os
import random
import string
from pathlib import Path

from PIL import Image
import numpy as np


def parse_sizes(sizes_arg: str):
    sizes = []
    for part in sizes_arg.split(','):
        part = part.strip()
        if not part:
            continue
        w_h = part.lower().split('x')
        if len(w_h) != 2:
            raise ValueError(f"Invalid size spec: {part}")
        w, h = int(w_h[0]), int(w_h[1])
        sizes.append((w, h))
    return sizes


def random_name(prefix: str, ext: str) -> str:
    token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}-{token}.{ext}"


def create_noise_image(width: int, height: int) -> Image.Image:
    # Use uint8 noise across 3 channels (RGB)
    data = np.random.randint(0, 256, size=(height, width, 3), dtype=np.uint8)
    return Image.fromarray(data, mode='RGB')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='web/images', help='Output directory')
    parser.add_argument('--count', type=int, default=8, help='Images per size')
    parser.add_argument('--width', type=int, default=3000)
    parser.add_argument('--height', type=int, default=2000)
    parser.add_argument('--sizes', type=str, default='', help='Comma-separated list like 1024x1024,2000x1200')
    parser.add_argument('--format', choices=['jpg', 'png', 'webp'], default='jpg')
    parser.add_argument('--quality', type=int, default=85, help='Quality for lossy formats')
    parser.add_argument('--prefix', type=str, default='img')
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    sizes = parse_sizes(args.sizes) if args.sizes else [(args.width, args.height)]
    ext = args.format

    save_params = {}
    if ext in ('jpg', 'webp'):
        save_params['quality'] = args.quality

    for (w, h) in sizes:
        for _ in range(args.count):
            img = create_noise_image(w, h)
            name = random_name(f"{args.prefix}-{w}x{h}", ext)
            out_path = out_dir / name
            img.save(out_path, **save_params)
            print(out_path)


if __name__ == '__main__':
    main()


