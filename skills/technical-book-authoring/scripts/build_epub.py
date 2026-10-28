#!/usr/bin/env python3
"""Assemble an EPUB 3 book from Markdown chapters and a code package.

    python build_epub.py --root . --out dist/book.epub

Reads from the project root:
    src/structure.json     parts, chapters, appendices — drives order and TOC
    src/chapters/*.md      the manuscript
    src/quotes.json        optional source bank (for a generated sources page)

Requires: markdown (fenced_code, tables, attr_list, def_list, md_in_html,
sane_lists), pygments, pillow.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

try:
    import markdown
except ImportError:
    sys.exit("Need: pip install markdown")

MD_EXTENSIONS = [
    "markdown.extensions.fenced_code",
    "markdown.extensions.tables",
    "markdown.extensions.attr_list",
    "markdown.extensions.def_list",
    "markdown.extensions.md_in_html",
    "markdown.extensions.sane_lists",
]

VOID_TAGS = ("hr", "br", "img", "meta", "link", "input", "col")

BOOK_TITLE = "Technical Book"
BOOK_SUBTITLE = ""
BOOK_AUTHOR = ""

CSS = """
:root { color-scheme: light dark; }
body {
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.55;
  margin: 0 5%;
  text-align: justify;
  hyphens: auto;
}
h1, h2, h3, h4 {
  font-family: "Segoe UI", Helvetica, Arial, sans-serif;
  text-align: left;
  line-height: 1.25;
  page-break-after: avoid;
  break-after: avoid;
}
h1 { font-size: 1.55em; margin: 1.2em 0 0.6em; }
h2 { font-size: 1.22em; margin: 1.5em 0 0.5em; border-bottom: 1px solid #bbb; padding-bottom: 0.15em; }
h3 { font-size: 1.06em; margin: 1.2em 0 0.4em; }
p { margin: 0.55em 0; orphans: 3; widows: 3; }
ul, ol { margin: 0.5em 0 0.7em 1.4em; padding: 0; }
li { margin: 0.28em 0; }
blockquote {
  margin: 1em 0.9em;
  padding: 0.5em 0.9em;
  border-left: 3px solid #b8894a;
  background: rgba(184,137,74,0.09);
  font-style: italic;
}
blockquote p { margin: 0.3em 0; }
code {
  font-family: "Cascadia Mono", Consolas, "DejaVu Sans Mono", monospace;
  font-size: 0.88em;
}
p > code, li > code, td > code, th > code {
  background: rgba(128,128,128,0.16);
  padding: 0.08em 0.32em;
  border-radius: 3px;
}
pre {
  background: rgba(128,128,128,0.12);
  border-left: 3px solid #b8894a;
  padding: 0.7em 0.9em;
  overflow-x: auto;
  font-size: 0.78em;
  line-height: 1.42;
  page-break-inside: avoid;
  break-inside: avoid;
}
pre code { background: none; padding: 0; font-size: 1em; }
table {
  border-collapse: collapse;
  margin: 1em 0;
  width: 100%;
  font-size: 0.9em;
  page-break-inside: avoid;
  break-inside: avoid;
}
th, td { border: 1px solid #999; padding: 0.38em 0.55em; text-align: left; vertical-align: top; }
th { background: rgba(128,128,128,0.14); font-family: "Segoe UI", Helvetica, sans-serif; }
details {
  margin: 0.9em 0;
  padding: 0.55em 0.8em;
  border: 1px solid #aaa;
  border-radius: 4px;
  background: rgba(128,128,128,0.07);
  page-break-inside: avoid;
  break-inside: avoid;
}
details > summary {
  cursor: pointer;
  font-family: "Segoe UI", Helvetica, sans-serif;
  font-size: 0.95em;
  margin: 0.2em 0;
}
details[open] > summary { margin-bottom: 0.45em; }
hr { border: 0; border-top: 1px solid #bbb; margin: 1.6em 0; }
.chapter-title { text-align: center; margin: 2em 0 0.5em; }
.nav-part { font-family: "Segoe UI", Helvetica, sans-serif; font-weight: 700; margin-top: 1.3em; }
.reading-time { color: #666; font-size: 0.9em; }
"""


def md_to_html(text: str) -> str:
    """Markdown to HTML.

    ``md_in_html`` is what makes ``markdown="1"`` inside ``<details>`` work.
    """
    text = re.sub(r"<details>\s*\n<summary>", '<details markdown="1">\n<summary>', text)
    return markdown.markdown(text, extensions=MD_EXTENSIONS, output_format="html5")


def highlight_code(html_text: str) -> str:
    """Inline syntax highlighting into the page."""
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import get_lexer_by_name, TextLexer
    except ImportError:
        return html_text

    formatter = HtmlFormatter(nowrap=False, cssclass="highlight")

    def repl(match: re.Match[str]) -> str:
        block = match.group(0)
        lang_match = re.search(r'class="language-([a-z0-9]+)"', block)
        lang = lang_match.group(1) if lang_match else "text"
        code_match = re.search(r"<code[^>]*>(.*?)</code>", block, re.S)
        if not code_match:
            return block
        code = html.unescape(code_match.group(1))
        try:
            lexer = get_lexer_by_name(lang, stripall=False)
        except Exception:
            lexer = TextLexer()
        try:
            out = highlight(code, lexer, formatter)
        except Exception:
            return block
        return out.replace(
            '<div class="highlight"><pre>', '<pre class="highlight">'
        ).replace("</pre></div>", "</pre>")

    return re.sub(r"<pre><code[^>]*>.*?</code></pre>", repl, html_text, flags=re.S)


def xhtml_fix(body: str) -> str:
    """Self-close void tags — XHTML is XML and rejects ``<hr>``."""
    for tag in VOID_TAGS:
        body = re.sub(rf"<{tag}\b([^>]*?)(?<!/)>", rf"<{tag}\1/>", body)
    return body


def page_xhtml(title: str, body: str, extra_head: str = "") -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ru" xml:lang="ru">
<head>
<meta charset="utf-8" />
<title>{escape(title)}</title>
<link rel="stylesheet" type="text/css" href="../styles/book.css" />
{extra_head}
</head>
<body>
{body}
</body>
</html>
"""


def make_cover(path: Path, title: str, subtitle: str, author: str) -> None:
    """Generate a cover. Draw the accent rule ABOVE the title, never across it."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return

    width, height = 1600, 2400
    image = Image.new("RGB", (width, height), (26, 27, 34))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / height
        draw.line(
            [(0, y), (width, y)],
            fill=(int(26 + 22 * t), int(27 + 16 * t), int(34 + 26 * t)),
        )

    accent = (184, 137, 74)
    draw.rectangle([0, int(height * 0.215), width, int(height * 0.215) + 14], fill=accent)
    draw.rectangle([0, int(height * 0.79), width, int(height * 0.79) + 6], fill=accent)

    def load(size: int):
        for candidate in (
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/times.ttf",
        ):
            if Path(candidate).exists():
                return ImageFont.truetype(candidate, size)
        return ImageFont.load_default(size)

    def centered(text: str, y: int, font, fill) -> None:
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text(((width - (bbox[2] - bbox[0])) / 2, y), text, font=font, fill=fill)

    big, medium, small = load(150), load(78), load(56)
    centered(title, 600, big, (245, 243, 238))
    if subtitle:
        centered(subtitle, 1000, medium, accent)
    if author:
        centered(author, 2020, small, (150, 148, 145))

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "JPEG", quality=88)


def collect_pages(root: Path, structure: dict) -> list[dict]:
    chapters_dir = root / "src" / "chapters"
    pages: list[dict] = []

    front = chapters_dir / "00-front.md"
    if front.exists():
        pages.append({
            "id": "front", "href": "text/front.xhtml",
            "title": "Introduction", "file": front, "kind": "front",
        })

    for part in structure["parts"]:
        pages.append({
            "id": f"part-{part['n']}", "href": f"text/part-{part['n']}.xhtml",
            "title": part["title"], "kind": "part", "part": part,
        })
        for chapter in part["chapters"]:
            pages.append({
                "id": chapter["file"], "href": f"text/{chapter['file']}.xhtml",
                "title": chapter["title"],
                "file": chapters_dir / f"{chapter['file']}.md",
                "kind": "chapter", "meta": chapter,
            })

    for appendix in structure["appendices"]:
        pages.append({
            "id": appendix["file"], "href": f"text/{appendix['file']}.xhtml",
            "title": appendix["title"],
            "file": chapters_dir / f"{appendix['file']}.md",
            "kind": "appendix",
        })

    return pages


def write_page(page: dict, oebps: Path, built_files: set[str]) -> str | None:
    """Write one XHTML page. Returns its href, or None when the source is absent."""
    if page["kind"] == "part":
        part = page["part"]
        items = "\n".join(
            f'<li><a href="{chapter["file"]}.xhtml">{escape(chapter["title"])}</a></li>'
            for chapter in part["chapters"]
            if chapter["file"] in built_files
        )
        body = (
            f'<div class="chapter-title"><h1>{escape(part["title"])}</h1></div>'
            f'<div class="nav-part">In this part</div><ol>{items}</ol>'
        )
    else:
        source = page.get("file")
        if source is None or not source.exists():
            print(f"  ! missing chapter source: {page['href']}")
            return None
        body = highlight_code(md_to_html(source.read_text(encoding="utf-8")))

    target = oebps / page["href"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        page_xhtml(page["title"], xhtml_fix(body)), encoding="utf-8"
    )
    return page["href"]


def write_nav(pages: list[dict], oebps: Path, structure: dict,
              built: set[str]) -> None:
    """EPUB 3 navigation document.

    Built from structure.json alone: enumerating both parts and their
    chapters adds every chapter twice.
    """
    items: list[str] = []

    front = next((p for p in pages if p["kind"] == "front"), None)
    if front and front["href"] in built:
        items.append(f'<li><a href="front.xhtml">{escape(front["title"])}</a></li>')

    for part in structure["parts"]:
        chapters = [
            c for c in part["chapters"] if f"text/{c['file']}.xhtml" in built
        ]
        if not chapters:
            continue
        chapter_items = "\n".join(
            f'<li><a href="{c["file"]}.xhtml">{escape(c["title"])}</a>'
            f'<span class="reading-time"> · {c.get("minutes", 15)} min</span></li>'
            for c in chapters
        )
        items.append(
            f'<li><span class="nav-part">{escape(part["title"])}</span>'
            f"<ol>{chapter_items}</ol></li>"
        )

    appendices = [a for a in structure["appendices"]
                  if f"text/{a['file']}.xhtml" in built]
    if appendices:
        items.append(
            '<li><span class="nav-part">Appendices</span><ol>'
            + "\n".join(
                f'<li><a href="{a["file"]}.xhtml">{escape(a["title"])}</a></li>'
                for a in appendices
            )
            + "</ol></li>"
        )

    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ru" xml:lang="ru">
<head>
<meta charset="utf-8" />
<title>Contents</title>
<link rel="stylesheet" type="text/css" href="../styles/book.css" />
</head>
<body>
<nav epub:type="toc" id="toc">
<h1>Contents</h1>
<ol>
{chr(10).join(items)}
</ol>
</nav>
</body>
</html>
"""
    (oebps / "text" / "nav.xhtml").write_text(nav, encoding="utf-8")


def write_ncx(pages: list[dict], oebps: Path, structure: dict,
              built: set[str]) -> None:
    """NCX for EPUB 2 readers. Each chapter appears exactly once."""
    counter = 1

    def nav_point(title: str, href: str, children: str = "") -> str:
        nonlocal counter
        pid = f"np{counter}"
        counter += 1
        return (
            f'<navPoint id="{pid}" playOrder="{counter}">'
            f"<navLabel><text>{escape(title)}</text></navLabel>"
            f'<content src="{href}"/>{children}</navPoint>'
        )

    entries: list[str] = []

    front = next((p for p in pages if p["kind"] == "front"), None)
    if front and front["href"] in built:
        entries.append(nav_point(front["title"], "text/front.xhtml"))

    for part in structure["parts"]:
        chapters = [
            c for c in part["chapters"] if f"text/{c['file']}.xhtml" in built
        ]
        if not chapters:
            continue
        children = "".join(
            nav_point(c["title"], f"text/{c['file']}.xhtml") for c in chapters
        )
        entries.append(
            nav_point(part["title"], f"text/part-{part['n']}.xhtml", children)
        )

    # Appendices have no divider page, so a container would duplicate the
    # first one. List them flat.
    for appendix in structure["appendices"]:
        href = f"text/{appendix['file']}.xhtml"
        if href in built:
            entries.append(nav_point(appendix["title"], href))

    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head>
<meta name="dtb:uid" content="urn:uuid:technical-book"/>
<meta name="dtb:depth" content="2"/>
<meta name="dtb:totalPageCount" content="0"/>
<meta name="dtb:maxPageNumber" content="0"/>
<docTitle><text>{escape(BOOK_TITLE)}</text></docTitle>
</head>
<navMap>
{chr(10).join(entries)}
</navMap>
</ncx>
"""
    (oebps / "toc.ncx").write_text(ncx, encoding="utf-8")


def write_opf(pages: list[dict], oebps: Path, built: set[str]) -> None:
    manifest = [
        '<item id="nav" href="text/nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '<item id="css" href="styles/book.css" media-type="text/css"/>',
        '<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
    ]
    spine = []
    for page in pages:
        if page["href"] not in built:
            continue
        pid = re.sub(r"[^A-Za-z0-9_-]", "-", page["id"])
        manifest.append(
            f'<item id="{pid}" href="{page["href"]}" media-type="application/xhtml+xml"/>'
        )
        spine.append(f'<itemref idref="{pid}"/>')

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="ru">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">urn:uuid:technical-book</dc:identifier>
<dc:title>{escape(BOOK_TITLE)}</dc:title>
<dc:language xml:lang="ru">ru</dc:language>
<dc:creator id="creator">{escape(BOOK_AUTHOR)}</dc:creator>
<meta refines="#creator" property="role" scheme="marc:relators">aut</meta>
<meta property="dcterms:modified">{now}</meta>
<meta name="cover" content="cover-image"/>
</metadata>
<manifest>
{chr(10).join(manifest)}
</manifest>
<spine toc="ncx">
{chr(10).join(spine)}
</spine>
</package>
"""
    (oebps / "content.opf").write_text(opf, encoding="utf-8")


CONTAINER = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles>
</container>
"""


def build(root: Path, out: Path) -> Path:
    structure = json.loads(
        (root / "src" / "structure.json").read_text(encoding="utf-8")
    )

    build_dir = root / ".build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    oebps = build_dir / "OEBPS"
    (oebps / "text").mkdir(parents=True)
    (oebps / "styles").mkdir(parents=True)
    (oebps / "images").mkdir(parents=True)
    (build_dir / "META-INF").mkdir(parents=True)

    pages = collect_pages(root, structure)
    print(f"Pages: {len(pages)}")

    built_files = {
        p["file"].stem for p in pages if p.get("file") and p["file"].exists()
    }
    built: set[str] = set()
    for page in pages:
        href = write_page(page, oebps, built_files)
        if href:
            built.add(href)
            print(f"  + {href}")

    (oebps / "styles" / "book.css").write_text(CSS, encoding="utf-8")
    make_cover(oebps / "images" / "cover.jpg", BOOK_TITLE, BOOK_SUBTITLE, BOOK_AUTHOR)
    write_nav(pages, oebps, structure, built)
    write_ncx(pages, oebps, structure, built)
    write_opf(pages, oebps, built)
    (build_dir / "META-INF" / "container.xml").write_text(CONTAINER, encoding="utf-8")
    (build_dir / "mimetype").write_text("application/epub+zip", encoding="ascii")

    out.parent.mkdir(parents=True, exist_ok=True)
    # Build to a temp name: replacing a file another process holds open
    # fails on Windows, and a reader application is exactly such a process.
    tmp = out.with_suffix(out.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()

    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(build_dir / "mimetype", "mimetype",
                      compress_type=zipfile.ZIP_STORED)
        for path in sorted(build_dir.rglob("*")):
            if path.is_file() and path.name != "mimetype":
                archive.write(path, path.relative_to(build_dir).as_posix())

    if out.exists():
        try:
            out.unlink()
        except PermissionError:
            pass
    tmp.replace(out)

    print(f"\nBuilt: {out}  ({out.stat().st_size / 1024:.0f} KB)")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--title", default=BOOK_TITLE)
    parser.add_argument("--subtitle", default=BOOK_SUBTITLE)
    parser.add_argument("--author", default=BOOK_AUTHOR)
    args = parser.parse_args()

    global BOOK_TITLE, BOOK_SUBTITLE, BOOK_AUTHOR
    BOOK_TITLE = args.title
    BOOK_SUBTITLE = args.subtitle
    BOOK_AUTHOR = args.author

    out = args.out or (args.root / "dist" / "book.epub")
    build(args.root.resolve(), out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
