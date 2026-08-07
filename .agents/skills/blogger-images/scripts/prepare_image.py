#!/usr/bin/env python3
"""Create an SEO-ready WebP image and emit Markdown/front-matter metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from PIL import Image, ImageOps

MAX_OUTPUT_BYTES = 5_000_000


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser()
    command.add_argument("source", type=Path)
    command.add_argument("--output-dir", type=Path, required=True)
    command.add_argument("--name", required=True, help="Lowercase ASCII filename without extension")
    command.add_argument("--alt", required=True)
    command.add_argument("--base-url")
    command.add_argument("--max-width", type=int, default=2560)
    command.add_argument("--quality", type=int, default=92)
    command.add_argument("--force", action="store_true")
    return command


def main() -> int:
    args = parser().parse_args()
    if not args.source.is_file():
        raise SystemExit(f"Source image not found: {args.source}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.name):
        raise SystemExit("--name must use lowercase ASCII words separated by hyphens")
    if not args.alt.strip():
        raise SystemExit("--alt must not be empty")
    if args.max_width < 320:
        raise SystemExit("--max-width must be at least 320")
    if not 40 <= args.quality <= 95:
        raise SystemExit("--quality must be between 40 and 95")

    destination = args.output_dir / f"{args.name}.webp"
    if destination.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing image: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    source_bytes = args.source.stat().st_size
    with Image.open(args.source) as opened:
        image = ImageOps.exif_transpose(opened)
        if image.width > args.max_width:
            height = round(image.height * args.max_width / image.width)
            image = image.resize((args.max_width, height), Image.Resampling.LANCZOS)
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.save(destination, "WEBP", quality=args.quality, method=6, exif=b"")
        width, height = image.size

    output_bytes = destination.stat().st_size
    if output_bytes > MAX_OUTPUT_BYTES:
        destination.unlink()
        raise SystemExit("Optimized image exceeds 5 MB; lower --max-width or --quality")

    url = f"{args.base_url.rstrip('/')}/{destination.name}" if args.base_url else destination.as_posix()
    result = {
        "source": str(args.source),
        "output": str(destination),
        "source_bytes": source_bytes,
        "output_bytes": output_bytes,
        "reduction_percent": round((1 - output_bytes / source_bytes) * 100, 1) if source_bytes else 0,
        "width": width,
        "height": height,
        "markdown": f"![{args.alt.strip()}]({url})",
        "image_dimensions": {args.alt.strip(): [width, height]},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
