"""Render captured outputs of the final demonstration (docs/final/demo/outputs) to PNG "terminal screenshots".

Reuses the renderer of the lecturer demo (docs/demo/screenshots/render_screenshots.py). These images are NOT live
screen captures. Each is drawn from a text file captured during the recorded run (docs/final/demo/RUN_LOG.md). The
text is unchanged; only a header naming the command and a footer naming the source file are added.

    .venv/Scripts/python docs/final/demo/screenshots/render_screenshots.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parent / "outputs"
_spec = importlib.util.spec_from_file_location(
    "demo_render", HERE.parents[2] / "demo" / "screenshots" / "render_screenshots.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


SHOTS = [
    ("01_real_cryptography_summary.png", "real/cryptography-47.0.0_summary.txt",
     "pqscan scan cryptography-47.0.0   (installed pyca cryptography 47.0.0, .py files)", None),
    ("02_real_pycryptodome_summary_head.png", "real/pycryptodome-4.4.0_summary.txt",
     "pqscan scan pycryptodome-4.4.0   (installed PyCryptodome 4.4.0, .py files; first 40 lines)", (1, 40)),
    ("03_output_validation.png", "validation.txt",
     "python docs/final/demo/validate_outputs.py   (independent CycloneDX 1.6 / SARIF 2.1.0 validation)", None),
]

def render(png: str, src: str, command: str, rng: tuple[int, int] | None) -> None:
    """Same drawing as the lecturer-demo renderer; the footer names docs/final/demo/outputs/<src>."""
    text = (OUTPUTS / src).read_text(encoding="utf-8").splitlines()
    if rng:
        text = text[rng[0] - 1:rng[1]]
    wrapped = any(len(s) > R.WRAP for s in text)
    text = [part for s in text for part in ([s[i:i + R.WRAP] for i in range(0, len(s), R.WRAP)] or [""])]
    header = [f"# command: {command}", ""]
    footer = ["", f"[rendered from captured output: docs/final/demo/outputs/{src}"
                  + (f", lines {rng[0]}-{rng[1]}" if rng else "") + "; not a live screen capture"
                  + (f"; lines longer than {R.WRAP} characters are wrapped" if wrapped else "") + "]"]
    lines = header + text + footer
    font = R._font(18)
    cw, lh = font.getbbox("M")[2], 24
    img = R.Image.new("RGB", (max(len(s) for s in lines) * cw + 48, len(lines) * lh + 48), R.BG)
    d = R.ImageDraw.Draw(img)
    for i, s in enumerate(lines):
        col = R.HEAD if i < len(header) else R.DIM if i >= len(lines) - len(footer) else R._color(s)
        d.text((24, 24 + i * lh), s, font=font, fill=col)
    img.save(HERE / png)
    print(f"wrote {png} ({img.width}x{img.height}) from outputs/{src}")


if __name__ == "__main__":
    for shot in SHOTS:
        render(*shot)
