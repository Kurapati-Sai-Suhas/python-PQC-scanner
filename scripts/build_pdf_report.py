"""Build a phase PDF report from a Markdown file.

Usage: python scripts/build_pdf_report.py <input.md> <output.pdf> "<Report title>"

The PDF gets a title page (project title, base-paper citation, date), an automatic
table of contents built from the Markdown headings, page numbers, and the body
rendered from Markdown (tables, fenced code, lists, images relative to the Markdown
file). Nothing is added that is not in the Markdown source. DejaVu fonts shipped
with matplotlib are embedded so arrows, Greek letters and box-drawing glyphs render.
"""
from __future__ import annotations
import datetime, sys
from pathlib import Path
import markdown
from xhtml2pdf import pisa

PROJECT = "Post-quantum crypto scanner for Python projects"
BASE_PAPER = ("Lei Zhang. Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum "
              "Cryptography Migration. ICSE-Companion '26, pp. 402-403. DOI 10.1145/3774748.3795653. arXiv:2602.05759.")


def font_css() -> str:
    import matplotlib
    fd = (Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf").resolve()

    def face(family: str, file: str, extra: str = "") -> str:
        return "@font-face { font-family: %s; src: url('%s'); %s}" % (family, (fd / file).as_posix(), extra)

    return "\n".join([face("DejaVu", "DejaVuSans.ttf"),
                      face("DejaVu", "DejaVuSans-Bold.ttf", "font-weight: bold; "),
                      face("DejaVuMono", "DejaVuSansMono.ttf")])


CSS = """
@page { size: A4; margin: 2cm 1.8cm 2.2cm 1.8cm;
        @frame footer_frame { -pdf-frame-content: footer_content; left: 1.8cm; width: 17.4cm; top: 27.6cm; height: 1cm; } }
body { font-family: DejaVu; font-size: 9.5pt; line-height: 1.32; }
h1 { font-size: 17pt; margin-top: 18pt; border-bottom: 1px solid #444; padding-bottom: 2pt; }
h2 { font-size: 13pt; margin-top: 14pt; }
h3 { font-size: 11pt; margin-top: 10pt; }
h4 { font-size: 10pt; margin-top: 8pt; }
p { margin: 4pt 0; }
code { font-family: DejaVuMono; font-size: 8.3pt; }
pre { font-family: DejaVuMono; font-size: 7.6pt; background: #f3f3f3; border: 1px solid #ccc; padding: 4pt; white-space: pre-wrap; }
table { width: 100%; margin: 6pt 0; font-size: 8pt; }
th, td { border: 1px solid #999; padding: 2pt 3pt; vertical-align: top; }
th { background: #e8e8e8; font-weight: bold; }
ul, ol { margin: 3pt 0 3pt 14pt; }
li { margin: 1.5pt 0; }
img { max-width: 100%; }
.titlepage { text-align: center; margin-top: 150pt; }
.titlepage h1 { border: none; font-size: 22pt; }
.titlepage p { font-size: 11pt; margin: 8pt 40pt; }
.toc { font-size: 9pt; }
.toc ul { list-style: none; margin-left: 10pt; }
#footer_content { text-align: center; font-size: 8pt; color: #555; }
"""


def build(md_path: Path, pdf_path: Path, title: str) -> None:
    src = md_path.read_text(encoding="utf-8")
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                           extension_configs={"toc": {"toc_depth": "1-3"}})
    body = md.convert(src)
    toc = md.toc
    today = datetime.date.today().strftime("%d %B %Y")
    html = f"""<html><head><meta charset="utf-8"><style>{font_css()}{CSS}</style></head><body>
<div id="footer_content">{PROJECT} - {title} - page <pdf:pagenumber/> of <pdf:pagecount/></div>
<div class="titlepage"><h1>{title}</h1><p><b>{PROJECT}</b></p>
<p>Mandatory base paper: {BASE_PAPER}</p><p>Generated {today} from <code>{md_path.name}</code>.</p></div>
<pdf:nextpage/>
<h1>Contents</h1><div class="toc">{toc}</div>
<pdf:nextpage/>
{body}
</body></html>"""
    with open(pdf_path, "wb") as f:
        # `path` makes relative image links (figures/x.png) resolve against the Markdown file's folder
        result = pisa.CreatePDF(html, dest=f, encoding="utf-8", path=str(md_path.resolve()))
    if result.err:
        raise SystemExit(f"PDF generation reported {result.err} error(s)")
    print(f"wrote {pdf_path} ({pdf_path.stat().st_size} bytes)")


if __name__ == "__main__":
    build(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
