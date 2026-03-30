"""
Original poster PNG: Asphalt Drip mood (gold on black, drip-style display type).
Does not reproduce third-party logos or photography. Reference-only palette from user description.

  python tools/render_canvas_drip_poster.py
  python tools/render_canvas_drip_poster.py --text "YOUR WORD" --out .tmp/canvas_piece_asphalt_drip.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from matplotlib import font_manager as _mf
from PIL import Image, ImageDraw, ImageFont

from yt_common import ROOT

SKILL_FONTS = ROOT / ".cursor" / "skills" / "canvas-design" / "canvas-fonts"
DEFAULT_OUT = ROOT / ".tmp" / "canvas_piece_asphalt_drip.png"

# Palette from brief (approximate; original work)
BG = (10, 10, 10)
GOLD = (212, 194, 159)  # ~#D4C29F
SILVER = (168, 169, 173)  # ~#A8A9AD
SHADOW = (0, 0, 0)


def _font(name: str, size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    p = SKILL_FONTS / name
    if p.exists():
        try:
            return ImageFont.truetype(str(p.resolve()), size)
        except OSError:
            pass
    fp = (
        _mf.FontProperties(family="DejaVu Sans", weight="bold")
        if bold
        else _mf.FontProperties(family="DejaVu Sans", weight="normal")
    )
    return ImageFont.truetype(_mf.findfont(fp), size)


def _vignette(img: Image.Image, strength: float = 0.5) -> None:
    w, h = img.size
    arr = np.asarray(img, dtype=np.float32) / 255.0
    yy, xx = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / np.sqrt(cx**2 + cy**2)
    k = (1.0 - strength * (d**1.8))[..., None]
    arr *= k
    out = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
    img.paste(Image.fromarray(out))


def _draw_drips(
    draw: ImageDraw.ImageDraw,
    bbox: tuple[int, int, int, int],
    seed: int,
    color: tuple[int, int, int],
) -> None:
    x0, y0, x1, y1 = bbox
    rng = np.random.default_rng(seed)
    y_base = y1
    x = x0
    while x < x1:
        step = int(rng.integers(10, 29))
        cx = min(x + step // 2, x1 - 2)
        n = int(rng.integers(2, 6))
        for _ in range(n):
            dx = cx + int(rng.integers(-4, 5))
            length = int(rng.integers(18, 73))
            thick = int(rng.integers(2, 6))
            draw.rectangle(
                (dx - thick // 2, y_base, dx + thick // 2, y_base + length),
                fill=color,
            )
        x += step


def render(
    text: str,
    out_path: Path,
    w: int = 1080,
    h: int = 1920,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)

    # Subtle silver horizontal streaks (speed hint, not literal photo)
    for y in range(h // 3, h, 40):
        t = (y % 120) / 120.0
        c = tuple(int(SILVER[i] * (0.08 + 0.06 * t)) for i in range(3))
        draw.line([(0, y), (w, y)], fill=c, width=1)

    # Fit title size
    size = 92
    font = _font("EricaOne-Regular.ttf", size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    while tw > w - 120 and size > 36:
        size -= 4
        font = _font("EricaOne-Regular.ttf", size, bold=True)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    tx = (w - tw) / 2
    ty = h * 0.18

    # Shadow (outline) + gold fill
    for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)):
        draw.text((tx + ox, ty + oy), text, font=font, fill=SHADOW)
    draw.text((tx, ty), text, font=font, fill=GOLD)

    tb = draw.textbbox((tx, ty), text, font=font)
    _draw_drips(draw, tb, seed=7, color=GOLD)

    sub = "NIGHT SIGNAL · CUSTOM CRAFT · ORIGINAL ARTIFACT"
    font_sub = _font("JetBrainsMono-Regular.ttf", 14, bold=False)
    bb = draw.textbbox((0, 0), sub, font=font_sub)
    sw = bb[2] - bb[0]
    draw.text(((w - sw) / 2, h - 120), sub, font=font_sub, fill=(SILVER[0] // 2, SILVER[1] // 2, SILVER[2] // 2))

    _vignette(img, 0.45)
    img.save(out_path, format="PNG", optimize=True)
    return out_path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--text", "-t", default="DRIPPINSTANK", help="Display word (your brand)")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    args = p.parse_args()
    path = render(args.text.strip().upper(), args.out, args.width, args.height)
    print(f"Wrote {path} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
