"""
DRIPPINSTANK × YouTube Niche Intelligence Report
Branded multi-page PDF — AI Automation Space

Design philosophy: Asphalt Dispatch
Dark performance-culture intelligence brief: black field, aged-gold accents,
OCR-A monospaced data labels, architectural dividers. Meticulous craft throughout.

Uses PIL for full-page composition and matplotlib Agg for chart buffers.

  python tools/render_canvas_yt_report.py
  python tools/render_canvas_yt_report.py --csv .tmp/pipeline_*/ingest_*_metrics.csv --out .tmp/yt_niche_report.pdf
"""
from __future__ import annotations

import argparse
import csv
import glob as _glob
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from yt_common import ROOT

# ── Paths ──────────────────────────────────────────────────────────────────────
BRAND_IMG_PATH  = ROOT / ".tmp" / "reference.png"
DEFAULT_CSV_GLOB = str(ROOT / ".tmp" / "pipeline_*" / "*_metrics.csv")
DEFAULT_OUT      = ROOT / ".tmp" / "yt_niche_report.pdf"
WIN_FONTS        = Path("C:/Windows/Fonts")

# ── Page dimensions: 8.5 × 11 in @ 150 dpi ───────────────────────────────────
DPI = 150
PW  = int(8.5  * DPI)   # 1275
PH  = int(11.0 * DPI)   # 1650
M   = int(0.55 * DPI)   # outer margin ~82 px

# ── Brand palette (RGB) ───────────────────────────────────────────────────────
BG     = (10,  10,  10)
GOLD   = (212, 194, 159)
GOLD2  = (200, 169, 110)
SILVER = (120, 120, 120)
DIM    = (42,  42,  42)
CARD   = (18,  18,  18)
WHITE  = (240, 236, 228)
MUTED  = (80,  80,  80)

# ── Fonts (system, verified loadable by PIL) ──────────────────────────────────
def _fnt(path_str: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path(path_str)), size)

FONT_DISPLAY = str(WIN_FONTS / "impact.ttf")        # massive display headers
FONT_BOLD    = str(WIN_FONTS / "segoeuib.ttf")      # bold section text
FONT_BODY    = str(WIN_FONTS / "segoeui.ttf")       # body / labels
FONT_MONO    = str(WIN_FONTS / "OCRAEXT.TTF")       # data / metrics (OCR-A)
FONT_CONSOLE = str(WIN_FONTS / "consola.ttf")       # monospace labels

# ── Data ──────────────────────────────────────────────────────────────────────
def load_data(csv_path: str) -> list[dict]:
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["view_count"]              = int(row["view_count"])
            row["like_count"]              = int(row["like_count"])
            row["comment_count"]           = int(row["comment_count"])
            row["engagement_per_1k_views"] = float(row["engagement_per_1k_views"])
            rows.append(row)
    return rows


def _trunc(s: str, n: int = 48) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


# ── Drawing helpers ───────────────────────────────────────────────────────────
def _new_page() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (PW, PH), BG)
    return img, ImageDraw.Draw(img)


def _tw(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bb = d.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


def _th(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bb = d.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def _centered(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
               y: int, color: tuple) -> None:
    x = (PW - _tw(d, text, font)) // 2
    d.text((x, y), text, font=font, fill=color)


def _page_header(img: Image.Image, d: ImageDraw.ImageDraw, section: str) -> int:
    """Gold rule + brand label + section label. Returns Y below header zone."""
    top = int(0.052 * PH)
    d.line([(0, top), (PW, top)], fill=GOLD2, width=3)

    f_brand = _fnt(FONT_BOLD, 18)
    d.text((M, top + 12), "DRIPPINSTANK", font=f_brand, fill=GOLD2)

    f_sec = _fnt(FONT_MONO, 15)
    d.text((M, top + 38), section, font=f_sec, fill=SILVER)

    rule_y = top + 72
    d.line([(M, rule_y), (PW - M, rule_y)], fill=DIM, width=1)
    return rule_y + 16


def _page_footer(img: Image.Image, d: ImageDraw.ImageDraw) -> None:
    bot = int(0.942 * PH)
    d.line([(M, bot), (PW - M, bot)], fill=DIM, width=1)
    f = _fnt(FONT_MONO, 12)
    label = "DRIPPINSTANK  .  NICHE INTELLIGENCE  .  MARCH 2026"
    d.text(((PW - _tw(d, label, f)) // 2, bot + 8), label, font=f, fill=MUTED)


# ── Matplotlib chart → PIL ────────────────────────────────────────────────────
def _bar_chart(values: list[float], bar_colors: list[tuple],
               fmt: str = "{:,.0f}",
               w_in: float = 7.8, h_in: float = 7.4) -> Image.Image:
    """Horizontal bar chart on dark background via matplotlib Agg → PIL."""
    fig, ax = plt.subplots(figsize=(w_in, h_in))
    fig.patch.set_facecolor("#0D0D0D")
    ax.set_facecolor("#0D0D0D")

    n   = len(values)
    hex_col = ["#{:02X}{:02X}{:02X}".format(*c) for c in bar_colors]
    y_pos   = list(range(n))
    bars    = ax.barh(y_pos[::-1], values, color=hex_col, height=0.62, edgecolor="none")

    max_v = max(values) if values else 1
    for i, (val, bar) in enumerate(zip(values, bars)):
        label = fmt.format(val)
        inset = val - max_v * 0.01
        if val < max_v * 0.18:
            ax.text(val + max_v * 0.01, n - 1 - i, label,
                    va="center", ha="left", fontsize=9.5,
                    color="#C8A96E", fontfamily="monospace")
        else:
            ax.text(inset, n - 1 - i, label,
                    va="center", ha="right", fontsize=9.5,
                    color="#0A0A0A", fontfamily="monospace")

    for y in y_pos:
        ax.axhline(y=y, color="#1A1A1A", linewidth=0.5, zorder=0)

    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.set_xlim(0, max_v * 1.01)
    ax.set_ylim(-0.5, n - 0.5)
    plt.tight_layout(pad=0.2)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor="#0D0D0D", dpi=DPI)
    buf.seek(0)
    out = Image.open(buf).copy()
    plt.close(fig)
    return out


# ── PAGE 1: Cover ─────────────────────────────────────────────────────────────
def render_cover() -> Image.Image:
    img, d = _new_page()

    # Brand hero image — upper 52 % with vertical fade
    if BRAND_IMG_PATH.exists():
        brand = Image.open(BRAND_IMG_PATH).convert("RGBA")
        target_h = int(PH * 0.52)
        brand_rs  = brand.resize((PW, target_h), Image.LANCZOS)
        arr = np.asarray(brand_rs, dtype=np.float32)
        h, w = arr.shape[:2]
        arr[:, :, :3] *= 0.78          # darken to blend with bg
        fade_s = int(h * 0.38)
        fade_e = int(h * 0.85)
        for row in range(fade_s, h):
            if row < fade_e:
                t = (row - fade_s) / (fade_e - fade_s)
                arr[row, :, 3] *= max(0.0, 1.0 - t)
            else:
                arr[row, :, 3] = 0
        faded = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
        base  = Image.new("RGBA", faded.size, (*BG, 255))
        composed = Image.alpha_composite(base, faded).convert("RGB")
        img.paste(composed, (0, 0))

    # Gold separator
    sep_y = int(PH * 0.530)
    d.line([(M, sep_y), (PW - M, sep_y)], fill=GOLD2, width=2)

    # Report label
    f_label = _fnt(FONT_MONO, 16)
    label = "NICHE  INTELLIGENCE  REPORT"
    _centered(d, label, f_label, sep_y + 20, SILVER)

    # Main title
    f_disp = _fnt(FONT_DISPLAY, 90)
    t1, t2 = "AI AUTOMATION", "SPACE"
    _centered(d, t1, f_disp, sep_y + 64,  WHITE)
    _centered(d, t2, f_disp, sep_y + 164, GOLD)

    # Channel sub-label
    f_ch = _fnt(FONT_BODY, 20)
    ch_str = "Nate Herk  ·  Lucas Walter  ·  AI Andy Automation"
    _centered(d, ch_str, f_ch, sep_y + 270, MUTED)

    # Date
    f_date = _fnt(FONT_MONO, 16)
    _centered(d, "MARCH  2026", f_date, sep_y + 306, MUTED)

    # Bottom brand mark
    bot_line = int(PH * 0.920)
    d.line([(M, bot_line), (PW - M, bot_line)], fill=DIM, width=1)
    f_brand = _fnt(FONT_BOLD, 22)
    _centered(d, "DRIPPINSTANK", f_brand, bot_line + 12, GOLD2)

    print("  OK: Cover")
    return img


# ── PAGE 2: Signal Overview ───────────────────────────────────────────────────
def render_overview(data: list[dict]) -> Image.Image:
    img, d = _new_page()
    content_top = _page_header(img, d, "SIGNAL  OVERVIEW")

    total_views  = sum(r["view_count"] for r in data)
    total_videos = len(data)
    channels     = list({r["channel_title"] for r in data})
    valid        = [r for r in data if r["view_count"] > 200]
    avg_eng      = float(np.mean([r["engagement_per_1k_views"] for r in valid])) if valid else 0.0
    top_video    = max(data, key=lambda r: r["view_count"])
    top_eng      = max(valid, key=lambda r: r["engagement_per_1k_views"]) if valid else None

    # ── Stat cards (2×2, tall) ─────────────────────────────────────────────────
    cards = [
        ("VIDEOS ANALYZED", f"{total_videos}",  ""),
        ("CHANNELS TRACKED", f"{len(channels)}", ""),
        ("TOTAL VIEWS",      f"{total_views:,}", ""),
        ("AVG ENGAGEMENT",   f"{avg_eng:.1f}",   "PER 1K VIEWS"),
    ]
    card_w  = (PW - 2 * M - 26) // 2
    card_h  = 235
    gap     = 26
    cx_L    = M
    cx_R    = M + card_w + gap
    row1_y  = content_top + 16
    row2_y  = row1_y + card_h + gap

    f_lbl   = _fnt(FONT_MONO,    15)
    f_val   = _fnt(FONT_DISPLAY, 70)
    f_unit  = _fnt(FONT_MONO,    13)

    for (cx, cy), (lbl, val, unit) in zip(
        [(cx_L, row1_y), (cx_R, row1_y), (cx_L, row2_y), (cx_R, row2_y)],
        cards,
    ):
        d.rounded_rectangle([cx, cy, cx + card_w, cy + card_h],
                             radius=6, fill=CARD, outline=DIM, width=1)
        lw = _tw(d, lbl, f_lbl)
        d.text((cx + (card_w - lw) // 2, cy + 18), lbl, font=f_lbl, fill=SILVER)
        vw = _tw(d, val, f_val)
        d.text((cx + (card_w - vw) // 2, cy + 58), val, font=f_val, fill=GOLD)
        if unit:
            uw = _tw(d, unit, f_unit)
            d.text((cx + (card_w - uw) // 2, cy + card_h - 28),
                   unit, font=f_unit, fill=MUTED)

    # ── Channel breakdown ──────────────────────────────────────────────────────
    div_y = row2_y + card_h + 34
    d.line([(M, div_y), (PW - M, div_y)], fill=DIM, width=1)
    d.text((M, div_y + 10), "CHANNEL  BREAKDOWN",
           font=_fnt(FONT_MONO, 14), fill=SILVER)

    ch_stats: dict[str, dict] = {}
    for r in data:
        ch = r["channel_title"]
        if ch not in ch_stats:
            ch_stats[ch] = {"videos": 0, "views": 0, "peak_eng": 0.0}
        ch_stats[ch]["videos"] += 1
        ch_stats[ch]["views"]  += r["view_count"]
        ch_stats[ch]["peak_eng"] = max(ch_stats[ch]["peak_eng"],
                                       r["engagement_per_1k_views"])

    sorted_ch = sorted(ch_stats.items(), key=lambda x: x[1]["views"], reverse=True)
    col_x = [M + 18, PW - M - 380, PW - M - 195, PW - M - 50]
    hdr_y = div_y + 40

    f_hdr = _fnt(FONT_MONO,    13)
    f_row = _fnt(FONT_BODY,    21)
    f_num = _fnt(FONT_CONSOLE, 19)

    for i, hdr in enumerate(["CHANNEL", "VIDEOS", "TOTAL VIEWS", "PEAK ENG/1K"]):
        hw = _tw(d, hdr, f_hdr)
        d.text((col_x[i] if i == 0 else col_x[i] - hw, hdr_y),
               hdr, font=f_hdr, fill=SILVER)
    d.line([(M, hdr_y + 24), (PW - M, hdr_y + 24)], fill=DIM, width=1)

    row_h = 68
    for j, (ch, s) in enumerate(sorted_ch):
        ry = hdr_y + 30 + j * row_h
        d.ellipse([(M - 14, ry + 10), (M - 6, ry + 18)], fill=GOLD2)
        ch_label = ch.replace(" | AI Automation", "").strip()
        d.text((col_x[0], ry + 2), ch_label, font=f_row, fill=WHITE)
        for i_col, (txt, color) in enumerate([
            (str(s["videos"]),       GOLD),
            (f"{s['views']:,}",      GOLD),
            (f"{s['peak_eng']:.1f}", GOLD2),
        ]):
            tw = _tw(d, txt, f_num)
            d.text((col_x[i_col + 1] - tw, ry + 4), txt, font=f_num, fill=color)
        # Mini share bar
        share = s["views"] / max(v["views"] for _, v in sorted_ch)
        bar_w = int((PW - 2 * M) * share * 0.28)
        d.rectangle([M, ry + row_h - 10, M + bar_w, ry + row_h - 4],
                     fill=(*GOLD2, ) if True else MUTED)
        d.line([(M, ry + row_h - 2), (PW - M, ry + row_h - 2)],
               fill=(24, 24, 24), width=1)

    # ── Trend intelligence ─────────────────────────────────────────────────────
    trend_y = hdr_y + 30 + len(ch_stats) * row_h + 28
    d.line([(M, trend_y), (PW - M, trend_y)], fill=DIM, width=1)
    d.text((M, trend_y + 10), "TREND  INTELLIGENCE",
           font=_fnt(FONT_MONO, 14), fill=SILVER)

    top_title  = _trunc(top_video["title"], 52)
    top_eng_t  = _trunc(top_eng["title"], 52) if top_eng else "—"
    insights = [
        f"Peak reach: {top_title} ({top_video['view_count']:,} views)",
        f"Peak engagement: {top_eng_t} ({top_eng['engagement_per_1k_views']:.1f}/1k)" if top_eng else "",
        "Short-form clips drive disproportionate engagement relative to views",
        "Claude Code tutorial formula: upgrade/feature reveal + live demo = 100K+ reach",
    ]

    f_ins = _fnt(FONT_BODY, 16)
    f_dot = _fnt(FONT_MONO, 20)
    for k, line in enumerate(insights):
        if not line:
            continue
        iy = trend_y + 48 + k * 52
        d.text((M, iy - 4), "-", font=f_dot, fill=GOLD2)
        d.text((M + 22, iy), line, font=f_ins, fill=WHITE)

    # ── Key signal box ─────────────────────────────────────────────────────────
    ins_y = trend_y + 48 + len(insights) * 52 + 10
    box_h = 100
    d.rounded_rectangle([M, ins_y, PW - M, ins_y + box_h],
                         radius=6, fill=(12, 12, 12), outline=GOLD2, width=2)
    _centered(d, "KEY  SIGNAL", _fnt(FONT_MONO, 13), ins_y + 14, GOLD2)
    _centered(d,
              "Claude Code content captures 85%+ of total reach — the niche is dominated by tutorial content",
              _fnt(FONT_BODY, 15), ins_y + 52, WHITE)

    _page_footer(img, d)
    print("  OK: Overview")
    return img


# ── Shared chart page ─────────────────────────────────────────────────────────
def _render_chart_page(data: list[dict], section: str,
                        sort_key: str, top_n: int,
                        bar_colors_fn,
                        fmt: str,
                        filter_fn=None) -> Image.Image:
    img, d = _new_page()
    content_top = _page_header(img, d, section)

    rows = data if filter_fn is None else [r for r in data if filter_fn(r)]
    top  = sorted(rows, key=lambda r: r[sort_key], reverse=True)[:top_n]

    if not top:
        return img

    n      = len(top)
    values = [r[sort_key] for r in top]
    colors = [bar_colors_fn(i) for i in range(n)]

    # ── Two-column layout: left = rank+title, right = bars ─────────────────────
    title_col_w = int(PW * 0.44)   # ~560 px for titles
    bar_col_x   = M + title_col_w  # bars start here
    bar_col_w   = PW - bar_col_x - M
    avail_h     = int(PH * 0.875) - content_top - 10
    row_h       = avail_h // n

    f_rank  = _fnt(FONT_MONO,    17)
    f_title = _fnt(FONT_BODY,    19)
    f_ch    = _fnt(FONT_MONO,    13)
    f_val   = _fnt(FONT_CONSOLE, 17)

    max_v      = max(values) if values else 1
    bar_area_w = bar_col_w - 14

    for i, (r, val, color) in enumerate(zip(top, values, colors)):
        row_top = content_top + 10 + i * row_h
        row_mid = row_top + row_h // 2

        # Subtle row separator
        if i > 0:
            d.line([(M, row_top), (PW - M, row_top)], fill=(22, 22, 22), width=1)

        # Rank number
        rank_c = GOLD if i < 3 else SILVER
        rh = _th(d, f"{i+1:02d}", f_rank)
        d.text((M, row_mid - rh // 2), f"{i+1:02d}", font=f_rank, fill=rank_c)

        # Channel label (small, muted, above title)
        ch_label = r["channel_title"].replace(" | AI Automation", "").strip()
        d.text((M + 42, row_mid - 22), ch_label, font=f_ch, fill=MUTED)

        # Video title
        max_title_w = title_col_w - 52
        title_str = r["title"]
        while _tw(d, title_str, f_title) > max_title_w and len(title_str) > 20:
            title_str = title_str[:-2] + "…"
        d.text((M + 42, row_mid - 2), title_str, font=f_title, fill=WHITE)

        # Bar (vertical center of the row)
        bar_len = int((val / max_v) * bar_area_w)
        bar_top = row_top + int(row_h * 0.25)
        bar_bot = row_top + int(row_h * 0.75)
        if bar_len > 2:
            d.rectangle([bar_col_x, bar_top,
                          bar_col_x + bar_len, bar_bot],
                         fill=color)

        # Value label
        val_str = fmt.format(val)
        vw = _tw(d, val_str, f_val)
        vh = _th(d, val_str, f_val)
        if bar_len > vw + 18:
            d.text((bar_col_x + bar_len - vw - 8, row_mid - vh // 2),
                   val_str, font=f_val, fill=(10, 10, 10))
        else:
            d.text((bar_col_x + bar_len + 6, row_mid - vh // 2),
                   val_str, font=f_val, fill=GOLD2)

    # Vertical divider between title and bar columns
    d.line([(bar_col_x - 8, content_top + 10),
             (bar_col_x - 8, content_top + 10 + n * row_h)],
            fill=DIM, width=1)

    _page_footer(img, d)
    return img


def render_views(data: list[dict]) -> Image.Image:
    img = _render_chart_page(
        data,
        section    = "TOP  PERFORMERS  .  BY  REACH",
        sort_key   = "view_count",
        top_n      = 10,
        bar_colors_fn = lambda i: GOLD if i < 3 else GOLD2 if i < 6 else (122, 106, 80),
        fmt        = "{:,.0f}",
    )
    print("  OK: Views chart")
    return img


def render_engagement(data: list[dict]) -> Image.Image:
    img = _render_chart_page(
        data,
        section    = "ENGAGEMENT  SIGNALS  .  LIKES + COMMENTS  /  1K  VIEWS",
        sort_key   = "engagement_per_1k_views",
        top_n      = 10,
        bar_colors_fn = lambda i: (200, 169, 110) if i < 3 else (154, 122, 80) if i < 6 else (90, 74, 56),
        fmt        = "{:.1f}",
        filter_fn  = lambda r: r["view_count"] > 200 and r["engagement_per_1k_views"] > 0,
    )
    print("  OK: Engagement chart")
    return img


# ── Entry point ───────────────────────────────────────────────────────────────
def main() -> int:
    p = argparse.ArgumentParser(
        description="Render branded DRIPPINSTANK YouTube intelligence PDF"
    )
    p.add_argument("--csv", default=DEFAULT_CSV_GLOB,
                   help="Glob to *_metrics.csv (default: latest pipeline run)")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()

    csv_files = sorted(_glob.glob(str(args.csv)))
    if not csv_files:
        print(f"ERROR: No CSV found matching: {args.csv}")
        return 1
    csv_path = csv_files[-1]
    print(f"Data: {csv_path}")
    data = load_data(csv_path)
    print(f"  {len(data)} videos loaded\n")

    args.out.parent.mkdir(parents=True, exist_ok=True)

    pages = [
        render_cover(),
        render_overview(data),
        render_views(data),
        render_engagement(data),
    ]

    pages[0].save(
        str(args.out), format="PDF",
        save_all=True, append_images=pages[1:],
        resolution=DPI,
    )

    size_kb = args.out.stat().st_size // 1024
    print(f"\nWrote: {args.out}  ({size_kb} KB, {len(pages)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
