#!/usr/bin/env python3
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np


def dir_size_bytes(path: Path) -> int:
    return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())


def half_swap(img):
    h, w = img.shape[:2]
    return np.concatenate([img[:, w // 2 :], img[:, : w // 2]], axis=1)


def generate_variants(img):
    variants = []

    def rotate(img):
        return [
            img,
            cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
            cv2.rotate(img, cv2.ROTATE_180),
            cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE),
        ]

    def flips(img):
        return [
            img,
            cv2.flip(img, 1),  # poziome
            cv2.flip(img, 0),  # pionowe
        ]

    h, w = img.shape[:2]

    # 1) Podstawowy zestaw (oryginał + rotacje + odbicia)
    for r in rotate(img):
        variants.extend(flips(r))

    # 2) Half-swap poziomy (prawa↔lewa)
    half_lr = np.concatenate([img[:, w // 2 :], img[:, : w // 2]], axis=1)
    for r in rotate(half_lr):
        variants.extend(flips(r))

    # 3) Half-swap pionowy (góra↔dół)
    half_ud = np.concatenate([img[h // 2 :], img[: h // 2]], axis=0)
    for r in rotate(half_ud):
        variants.extend(flips(r))

    # 4) Cyclic shift poziomy (przesunięcie)
    shift_x = np.roll(img, w // 4, axis=1)
    for r in rotate(shift_x):
        variants.extend(flips(r))

    # 5) Cyclic shift pionowy (przesunięcie)
    shift_y = np.roll(img, h // 4, axis=0)
    for r in rotate(shift_y):
        variants.extend(flips(r))

    return variants


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input source image")
    parser.add_argument("--out", default="web/images", help="Output directory")
    parser.add_argument(
        "--target-gb",
        type=float,
        required=True,
        help="Stop when output directory reaches this size (GB)",
    )
    parser.add_argument("--format", choices=["jpg", "png"], default="jpg")
    parser.add_argument("--quality", type=int, default=85)
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(args.input)
    assert img is not None, f"Cannot load image: {args.input}"

    save_params = []
    if args.format == "jpg":
        save_params = [cv2.IMWRITE_JPEG_QUALITY, args.quality]

    file_index = 0
    target_bytes = args.target_gb * (1024**3)

    executor = ThreadPoolExecutor(max_workers=8)

    while dir_size_bytes(out_dir) < target_bytes:
        variants = generate_variants(img)

        future_tasks = []
        for variant in variants:
            filename = f"gen_{file_index:07d}.{args.format}"
            filepath = out_dir / filename

            future_tasks.append(
                executor.submit(cv2.imwrite, str(filepath), variant, save_params)
            )

            file_index += 1

        for f in future_tasks:
            f.result()

        size_gb = dir_size_bytes(out_dir) / (1024**3)
        print(f"Progress: {size_gb:.2f} / {args.target_gb:.2f} GB")


if __name__ == "__main__":
    main()
