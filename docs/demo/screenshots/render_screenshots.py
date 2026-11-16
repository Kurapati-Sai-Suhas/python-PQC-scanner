"""Render captured terminal output (docs/demo/outputs/*.txt) to PNG "terminal screenshots".

These images are NOT live screen captures. Each one is drawn from a text file that was captured verbatim
when the commands in docs/demo/commands.md were run (see docs/demo/outputs/RUN_LOG.md). The text is copied
unchanged; only a header naming the command and a footer naming the source file are added.

Requires Pillow (not a pqscan dependency; any Python with Pillow works):
    py -3.12 -m pip install pillow
    py -3.12 docs/demo/screenshots/render_screenshots.py
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parent / "outputs"

# (png name, source file, command shown in the header, optional line range of the source to show)
SHOTS = [
    ("01_versions.png", "raw_run_transcript.txt", "environment check (python / pqscan / semgrep versions)", (1, 26)),
    ("02_summary_default.png", "01_summary.txt", "pqscan scan docs/demo/demo_repo", None),
    ("03_summary_threshold_T3.png", "05_summary_threshold_T3.txt", "pqscan scan docs/demo/demo_repo --tier-threshold T3", None),
    ("04_summary_arm_method-only.png", "06_summary_arm_method-only.txt", "pqscan scan docs/demo/demo_repo --arm method-only", None),
]

WRAP = 120
BG, FG, DIM, HEAD =(12, 12, 12), (204, 204, 204), (120, 120, 120), (97, 175, 239)
ACCENT = {"ABSTAIN": (229, 192, 123), "RECOMMEND": (152, 195, 121), "FLAG_NO_TARGET": (86, 182, 194)}


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("consola.ttf", "C:/Windows/Fonts/consola.ttf", "DejaVuSansMono.ttf", "Menlo.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _color(line: str) -> tuple[int, int, int]:
    for word, col in ACCENT.items():
        if f"  {word}" in line and ":" in line.split()[0]:
            return col
    return FG


def render(png: str, src: str, command: str, rng: tuple[int, int] | None) -> None:
    text = (OUTPUTS / src).read_text(encoding="utf-8").splitlines()
    if rng:
        text = text[rng[0] - 1:rng[1]]
    wrapped = any(len(s) > WRAP for s in text)
    text = [part for s in text for part in ([s[i:i + WRAP] for i in range(0, len(s), WRAP)] or [""])]
    header = [f"# command: {command}", ""]
    footer = ["", f"[rendered from captured output: docs/demo/outputs/{src}"
                  + (f", lines {rng[0]}-{rng[1]}" if rng else "") + "; not a live screen capture"
                  + (f"; lines longer than {WRAP} characters are wrapped" if wrapped else "") + "]"]
    lines = header + text + footer
    font = _font(18)
    cw = font.getbbox("M")[2]
    lh = 24
    width = max(len(s) for s in lines) * cw + 48
    height = len(lines) * lh + 48
    img = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(img)
    for i, s in enumerate(lines):
        if i < len(header):
            col = HEAD
        elif i >= len(lines) - len(footer):
            col = DIM
        else:
            col = _color(s)
        d.text((24, 24 + i * lh), s, font=font, fill=col)
    img.save(HERE / png)
    print(f"wrote {png} ({width}x{height}) from outputs/{src}")


if __name__ == "__main__":
    for shot in SHOTS:
        render(*shot)
