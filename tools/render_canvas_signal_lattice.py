"""
Render a single PNG for the Signal Lattice canvas-design workflow.
Uses fonts from .cursor/skills/canvas-design/canvas-fonts (project-local).

  python tools/render_canvas_signal_lattice.py
  python tools/render_canvas_signal_lattice.py --out .tmp/canvas_piece_signal_lattice.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from matplotlib import font_manager as _mf
from PIL import Image, ImageDraw, ImageFont

from yt_common import ROOT

SKILL_FONTS = ROOT / ".cursor" / "skills" / "canvas-design" / "canvas-fonts"
DEFAULT_OUT = ROOT / ".tmp" / "canvas_piece_signal_lattice.png"


def _dejavu_path(weight: str = "regular") -> str:
    """Matplotlib ships DejaVu TTFs; reliable on Windows when local skill fonts fail FreeType."""
    fp = (
        _mf.FontProperties(family="DejaVu Sans", weight="normal")
        if weight == "regular"
        else _mf.FontProperties(family="DejaVu Sans", weight="bold")
    )
    return _mf.findfont(fp)

BG_TOP = (18, 24, 34)
BG_BOT = (10, 14, 20)
GRID = (28, 38, 54)
GRID_FINE = (22, 30, 44)
ACCENT = (34, 211, 238)
ACCENT_DIM = (45, 212, 191)
NODE = (148, 163, 184)
NODE_HI = (203, 213, 225)
MUTED = (100, 116, 139)


def _font(name: str, size: int, *, fallback_bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = SKILL_FONTS / name
    if path.exists():
        try:
            return ImageFont.truetype(str(path.resolve()), size)
        except OSError:
            pass
    try:
        return ImageFont.truetype(
            _dejavu_path("bold" if fallback_bold else "regular"),
            size,
        )
    except OSError:
        return ImageFont.load_default()


def render(out_path: Path, w: int = 1200, h: int = 1680) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    margin = 72
    img = Image.new("RGB", (w, h), BG_BOT)
    draw = ImageDraw.Draw(img)

    # Vertical gradient field
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Primary grid
    step = 48
    for x in range(0, w + 1, step):
        draw.line([(x, 0), (x, h)], fill=GRID)
    for y in range(0, h + 1, step):
        draw.line([(0, y), (w, y)], fill=GRID)

    band_t, band_b = margin + 120, h - margin - 280
    sub = 12
    for x in range(margin, w - margin, sub):
        draw.line([(x, band_t), (x, band_b)], fill=GRID_FINE)
    for y in range(band_t, band_b, sub):
        draw.line([(margin, y), (w - margin, y)], fill=GRID_FINE)

    cx0, cy0 = margin + 24, band_t + 24
    cell = 56
    cols = (w - 2 * margin - 48) // cell
    rows = (band_b - band_t - 48) // cell
    nodes: list[tuple[int, int]] = []
    for j in range(rows):
        for i in range(cols):
            cx = cx0 + i * cell
            cy = cy0 + j * cell
            nodes.append((cx, cy))
            r = 3 if (i + j) % 3 else 4
            fill = NODE_HI if (i * j + j) % 13 == 0 else NODE
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)

    for k in range(0, max(0, len(nodes) - cols - 1), 7):
        x1, y1 = nodes[k]
        x2, y2 = nodes[k + cols + 1]
        draw.line([(x1, y1), (x2, y2)], fill=ACCENT, width=1)
    for k in range(cols * 2, len(nodes) - 1, 11):
        x1, y1 = nodes[k]
        x2, y2 = nodes[k + 1]
        draw.line([(x1, y1), (x2, y2)], fill=ACCENT_DIM, width=1)

    font_mono = _font("JetBrainsMono-Regular.ttf", 14)
    for i, lab in enumerate(["I", "II", "III", "IV"]):
        draw.text((margin + i * 160, margin - 8), f"[{lab}]", font=font_mono, fill=MUTED)

    font_title = _font("InstrumentSans-Bold.ttf", 42, fallback_bold=True)
    font_sub = _font("InstrumentSans-Regular.ttf", 18)
    tag = _font("JetBrainsMono-Regular.ttf", 13)

    title = "SIGNAL LATTICE"
    subtitle = "observation · interval · craft"
    y_base = h - margin - 120

    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) / 2, y_base), title, font=font_title, fill=(226, 232, 240))

    bbox2 = draw.textbbox((0, 0), subtitle, font=font_sub)
    sw = bbox2[2] - bbox2[0]
    draw.text(((w - sw) / 2, y_base + 52), subtitle, font=font_sub, fill=MUTED)

    stamp = "FIELD NOTES  ·  SIGNAL LATTICE  ·  V1"
    bbox3 = draw.textbbox((0, 0), stamp, font=tag)
    stw = bbox3[2] - bbox3[0]
    draw.text(((w - stw) / 2, y_base + 92), stamp, font=tag, fill=GRID)

    img.save(out_path, format="PNG", optimize=True)
    return out_path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--width", type=int, default=1200)
    p.add_argument("--height", type=int, default=1680)
    args = p.parse_args()
    path = render(args.out, args.width, args.height)
    print(f"Wrote {path} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
