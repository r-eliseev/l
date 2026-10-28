"""Сборка EPUB из Markdown-глав.

Собирает любую книгу репозитория: структура берётся из
`books/<slug>/src/structure.json`, метаданные и обложка — из
`books/<slug>/book.json`.

Использование:
    python tools/build_epub.py --book ddd-praktika

Требуется: markdown (с расширениями tables, fenced_code, attr_list,
md_in_html, def_list, toc), Pillow (обложка), pygments (подсветка кода).
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

import markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bookmeta import Book, load_book  # noqa: E402

MD_EXTENSIONS = [
    "markdown.extensions.fenced_code",
    "markdown.extensions.tables",
    "markdown.extensions.attr_list",
    "markdown.extensions.def_list",
    "markdown.extensions.md_in_html",
    "markdown.extensions.sane_lists",
]

HIGHLIGHT = {
    "python": "python",
    "json": "json",
    "text": "text",
    "bash": "bash",
    "yaml": "yaml",
    "yml": "yaml",
    "cml": "text",
    "shell": "bash",
    "sh": "bash",
    "console": "bash",
}

missing: list[str] = []

# ---------------------------------------------------------------------------
# Markdown -> XHTML
# ---------------------------------------------------------------------------


def md_to_html(text: str) -> str:
    """Конвертирует Markdown в HTML.

    ``md_in_html`` нужен, чтобы разметка внутри ``<details markdown="1">``
    обрабатывалась как Markdown, а не как сырой текст.
    """
    text = _prepare_details(text)
    return markdown.markdown(text, extensions=MD_EXTENSIONS, output_format="html5")


def _prepare_details(text: str) -> str:
    """Добавляет ``markdown="1"`` внутрь ``<details>``, чтобы внутренний
    текст превращался в HTML, а не оставался строкой."""
    text = re.sub(
        r"<details>\s*\n<summary>",
        '<details markdown="1">\n<summary>',
        text,
    )
    return text


def highlight_code(html_text: str) -> str:
    """Подсвечивает блоки ``<pre><code class="language-python">``."""
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name, TextLexer

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
            lexer = get_lexer_by_name(HIGHLIGHT.get(lang, lang), stripall=False)
        except Exception:
            lexer = TextLexer()
        try:
            highlighted = highlight(code, lexer, formatter)
        except Exception:
            return block
        return highlighted.replace(
            '<div class="highlight"><pre>', '<pre class="highlight">'
        ).replace("</pre></div>", "</pre>")

    return re.sub(r"<pre><code[^>]*>.*?</code></pre>", repl, html_text, flags=re.S)


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
.chapter-subtitle { text-align: center; font-style: italic; color: #666; margin-bottom: 1.4em; }
.reading-time { text-align: center; font-size: 0.88em; color: #666; margin-bottom: 1.6em; }
nav ol { list-style-type: none; margin-left: 0; }
nav ol ol { margin-left: 1.1em; }
.nav-part { font-family: "Segoe UI", Helvetica, sans-serif; font-weight: 700; margin-top: 1.3em; }
hr.sep { page-break-after: always; break-after: page; margin: 0; border: 0; }
.cover-page { text-align: center; margin-top: 22%; }
.cover-page h1 { font-size: 2.1em; text-align: center; border: 0; }
.cover-page .subtitle { font-size: 1.15em; font-style: italic; color: #555; margin: 0.8em 0 3em; }
.cover-page .author { font-size: 1.05em; }
.toc-hint { font-size: 0.9em; color: #666; text-align: center; margin-top: 1.4em; }
"""

VOID_TAGS = ("hr", "br", "img", "meta", "link", "input", "col")


def xhtml_fix(body: str) -> str:
    """Закрывает одиночные HTML-теги по правилам XHTML.

    Markdown отдаёт ``<hr>``, а XHTML требует ``<hr/>``.
    """
    for tag in VOID_TAGS:
        body = re.sub(rf"<{tag}\b([^>]*?)(?<!/)>", rf"<{tag}\1/>", body)
    return body


def page_xhtml(title: str, body: str, language: str = "ru", extra_head: str = "") -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{language}" xml:lang="{language}">
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


# ---------------------------------------------------------------------------
# Обложка
# ---------------------------------------------------------------------------


def make_cover(path: Path, book: Book) -> None:
    """Генерирует обложку: тёмный фон, крупный заголовок, акцентная полоса."""
    from PIL import Image, ImageDraw

    w, h = 1600, 2400
    img = Image.new("RGB", (w, h), (26, 27, 34))
    draw = ImageDraw.Draw(img)

    # мягкий градиент
    for y in range(h):
        t = y / h
        r = int(26 + 22 * t)
        g = int(27 + 16 * t)
        b = int(34 + 26 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    accent = (184, 137, 74)
    # Полоса-разделитель выше заголовка, чтобы не резать текст.
    draw.rectangle([0, int(h * 0.215), w, int(h * 0.215) + 14], fill=accent)
    draw.rectangle([0, int(h * 0.79), w, int(h * 0.79) + 6], fill=accent)

    cover = book.manifest.get("cover", {})
    title_lines: list[str] = cover.get("title_lines") or [book.title]
    subtitle_line: str | None = cover.get("subtitle_line")
    tagline_lines: list[str] = cover.get("tagline_lines") or []

    try:
        from PIL import ImageFont

        def load(size: int):
            for pattern in (
                "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/times.ttf",
            ):
                if Path(pattern).exists():
                    return ImageFont.truetype(pattern, size)
            return ImageFont.load_default(size)

        f_big = load(150)
        f_mid = load(78)
        f_small = load(56)

        def centered(text, y, font, fill):
            bbox = draw.textbbox((0, 0), text, font=font)
            draw.text(((w - (bbox[2] - bbox[0])) / 2, y), text, font=font, fill=fill)

        y = 600
        for line in title_lines:
            centered(line, y, f_big, (245, 243, 238))
            y += 170
        if subtitle_line:
            centered(subtitle_line, y, f_mid, accent)
            y += 120
        for line in tagline_lines:
            centered(line, 1420 + tagline_lines.index(line) * 75, f_small, (215, 213, 208))
        if book.author:
            centered(book.author, 2020, f_small, (150, 148, 145))
    except Exception as exc:  # pragma: no cover - обложка не критична
        print(f"  ! обложка без текста: {exc}")

    img.save(path, "JPEG", quality=88)


# ---------------------------------------------------------------------------
# Сборка
# ---------------------------------------------------------------------------


def collect_pages(book: Book) -> list[dict]:
    """Собирает список страниц: front matter, главы, приложения."""
    structure = book.structure
    pages: list[dict] = []

    front = book.front_file()
    if front is not None:
        pages.append(
            {
                "id": "front",
                "href": "text/front.xhtml",
                "title": structure.get("front", {}).get("title", "Введение"),
                "file": front,
                "kind": "front",
            }
        )

    for part in structure.get("parts", []):
        pages.append(
            {
                "id": f"part-{part['n']}",
                "href": f"text/part-{part['n']}.xhtml",
                "title": part["title"],
                "kind": "part",
                "part": part,
            }
        )
        for ch in part["chapters"]:
            pages.append(
                {
                    "id": ch["file"],
                    "href": f"text/{ch['file']}.xhtml",
                    "title": ch["title"],
                    "file": book.chapters / f"{ch['file']}.md",
                    "kind": "chapter",
                    "meta": ch,
                }
            )

    for ch in structure.get("chapters", []):
        pages.append(
            {
                "id": ch["file"],
                "href": f"text/{ch['file']}.xhtml",
                "title": ch["title"],
                "file": book.chapters / f"{ch['file']}.md",
                "kind": "chapter",
                "meta": ch,
            }
        )

    for app in structure.get("appendices", []):
        pages.append(
            {
                "id": app["file"],
                "href": f"text/{app['file']}.xhtml",
                "title": app["title"],
                "file": book.chapters / f"{app['file']}.md",
                "kind": "appendix",
            }
        )

    return pages


def write_page(page: dict, out_dir: Path, built_files: set[str], language: str) -> None:
    if page["kind"] == "part":
        part = page["part"]
        items = "\n".join(
            f'<li><a href="{ch["file"]}.xhtml">{escape(ch["title"])}</a></li>'
            for ch in part["chapters"]
            if ch["file"] in built_files
        )
        body_html = (
            f'<div class="chapter-title"><h1>{escape(part["title"])}</h1></div>'
            f'<div class="nav-part">В этой части</div><ol>{items}</ol>'
        )
    else:
        src = page.get("file")
        if src is None or not src.exists():
            missing.append(page["href"])
            return
        raw = src.read_text(encoding="utf-8")
        body_html = md_to_html(raw)
        body_html = highlight_code(body_html)

    extra = ""
    if page["kind"] == "front":
        extra = '<meta name="cover" content="cover-image" />'

    out = out_dir / page["href"]
    out.write_text(
        page_xhtml(page["title"], xhtml_fix(body_html), language, extra),
        encoding="utf-8",
    )


def write_nav(book: Book, pages: list[dict], out_dir: Path) -> None:
    """Документ навигации EPUB 3.

    Строится напрямую по structure.json: каждая глава попадает в оглавление
    ровно один раз — внутри своей части. Иначе главы дублируются: сначала
    вложенным списком, потом плоским.
    """
    structure = book.structure
    built = {p["href"] for p in pages} - set(missing)

    items: list[str] = []

    front = next((p for p in pages if p["kind"] == "front"), None)
    if front and front["href"] in built:
        items.append(
            f'<li><a href="front.xhtml">{escape(front["title"])}</a></li>'
        )

    for part in structure.get("parts", []):
        chapters = [
            ch for ch in part["chapters"]
            if f"text/{ch['file']}.xhtml" in built
        ]
        if not chapters:
            continue
        chapter_items = "\n".join(
            f'<li><a href="{ch["file"]}.xhtml">{escape(ch["title"])}</a>'
            f'<span class="reading-time"> · {ch.get("minutes", 15)} мин</span></li>'
            for ch in chapters
        )
        items.append(
            f'<li><span class="nav-part">{escape(part["title"])}</span>'
            f"<ol>{chapter_items}</ol></li>"
        )

    loose_chapters = [
        ch for ch in structure.get("chapters", [])
        if f"text/{ch['file']}.xhtml" in built
    ]
    if loose_chapters:
        chapter_items = "\n".join(
            f'<li><a href="{ch["file"]}.xhtml">{escape(ch["title"])}</a>'
            f'<span class="reading-time"> · {ch.get("minutes", 15)} мин</span></li>'
            for ch in loose_chapters
        )
        items.append(f"<ol>{chapter_items}</ol>")

    appendices = [
        a for a in structure.get("appendices", [])
        if f"text/{a['file']}.xhtml" in built
    ]
    if appendices:
        appendix_items = "\n".join(
            f'<li><a href="{a["file"]}.xhtml">{escape(a["title"])}</a></li>'
            for a in appendices
        )
        items.append(
            f'<li><span class="nav-part">Приложения</span>'
            f"<ol>{appendix_items}</ol></li>"
        )

    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{book.language}" xml:lang="{book.language}">
<head>
<meta charset="utf-8" />
<title>Содержание</title>
<link rel="stylesheet" type="text/css" href="../styles/book.css" />
</head>
<body>
<nav epub:type="toc" id="toc">
<h1>Содержание</h1>
<ol>
{chr(10).join(items)}
</ol>
</nav>
</body>
</html>
"""
    (out_dir / "text" / "nav.xhtml").write_text(nav, encoding="utf-8")


def write_ncx(book: Book, pages: list[dict], out_dir: Path) -> None:
    """NCX — оглавление для старых ридеров, не понимающих EPUB 3.

    Каждая глава входит ровно один раз: внутри navPoint своей части.
    """
    structure = book.structure
    built = {p["href"] for p in pages} - set(missing)

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

    for part in structure.get("parts", []):
        chapters = [
            ch for ch in part["chapters"]
            if f"text/{ch['file']}.xhtml" in built
        ]
        if not chapters:
            continue
        children = "".join(
            nav_point(ch["title"], f"text/{ch['file']}.xhtml")
            for ch in chapters
        )
        entries.append(nav_point(part["title"], f"text/part-{part['n']}.xhtml", children))

    for chapter in structure.get("chapters", []):
        href = f"text/{chapter['file']}.xhtml"
        if href in built:
            entries.append(nav_point(chapter["title"], href))

    # Приложения перечисляются плоско: отдельной страницы-разделителя у них
    # нет, а контейнер с первым приложением создавал бы дубль в оглавлении.
    for appendix in structure.get("appendices", []):
        href = f"text/{appendix['file']}.xhtml"
        if href in built:
            entries.append(nav_point(appendix["title"], href))

    uid = f"urn:uuid:{book.slug}"
    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head>
<meta name="dtb:uid" content="{uid}"/>
<meta name="dtb:depth" content="2"/>
<meta name="dtb:totalPageCount" content="0"/>
<meta name="dtb:maxPageNumber" content="0"/>
<docTitle><text>{escape(book.title)}</text></docTitle>
</head>
<navMap>
{chr(10).join(entries)}
</navMap>
</ncx>
"""
    (out_dir / "toc.ncx").write_text(ncx, encoding="utf-8")


def write_opf(book: Book, pages: list[dict], out_dir: Path) -> None:
    manifest = [
        '<item id="nav" href="text/nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '<item id="css" href="styles/book.css" media-type="text/css"/>',
        '<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
    ]
    spine = []
    built = {p["href"] for p in pages} - set(missing)
    for page in pages:
        if page["href"] not in built:
            continue
        pid = re.sub(r"[^A-Za-z0-9_-]", "-", page["id"])
        manifest.append(
            f'<item id="{pid}" href="{page["href"]}" media-type="application/xhtml+xml"/>'
        )
        spine.append(f'<itemref idref="{pid}"/>')

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    subtitle = f'<dc:title id="sub">{escape(book.subtitle)}</dc:title>' if book.subtitle else ""
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{book.language}">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">urn:uuid:{book.slug}</dc:identifier>
<dc:title>{escape(book.title)}</dc:title>
{subtitle}
<dc:language xml:lang="{book.language}">{book.language}</dc:language>
<dc:creator id="creator">{escape(book.author)}</dc:creator>
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
    (out_dir / "content.opf").write_text(opf, encoding="utf-8")


CONTAINER = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles>
</container>
"""


def build(book: Book) -> Path:
    build_dir = book.dir / ".build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    oebps = build_dir / "OEBPS"
    (oebps / "text").mkdir(parents=True)
    (oebps / "styles").mkdir(parents=True)
    (oebps / "images").mkdir(parents=True)
    (build_dir / "META-INF").mkdir(parents=True)

    pages = collect_pages(book)
    print(f"Страниц: {len(pages)}")

    built_files = {
        p["file"].stem
        for p in pages
        if p.get("file") and p["file"].exists()
    }
    for page in pages:
        write_page(page, oebps, built_files, book.language)
        if page["href"] not in set(missing):
            print(f"  + {page['href']}")

    (oebps / "styles" / "book.css").write_text(CSS, encoding="utf-8")
    make_cover(oebps / "images" / "cover.jpg", book)
    write_nav(book, pages, oebps)
    write_ncx(book, pages, oebps)
    write_opf(book, pages, oebps)
    (build_dir / "META-INF" / "container.xml").write_text(CONTAINER, encoding="utf-8")
    (build_dir / "mimetype").write_text("application/epub+zip", encoding="ascii")

    book.dist.mkdir(parents=True, exist_ok=True)
    out = book.epub_path
    # Сборка идёт во временный файл: иначе нельзя перезаписать EPUB, который
    # ещё открыт другим процессом (ридер, антивирус).
    tmp_out = out.with_suffix(out.suffix + ".tmp")
    if tmp_out.exists():
        tmp_out.unlink()

    # mimetype должен идти первым и без сжатия
    with zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(build_dir / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(build_dir.rglob("*")):
            if path.is_file() and path.name != "mimetype":
                z.write(path, path.relative_to(build_dir).as_posix())

    if out.exists():
        try:
            out.unlink()
        except PermissionError:
            pass
    tmp_out.replace(out)

    if missing:
        print(f"\n! Пропущено файлов глав: {len(missing)}")
        for href in missing:
            print(f"   - {href}")

    print(f"\nГотово: {out}  ({out.stat().st_size / 1024:.0f} КБ)")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Сборка EPUB книги")
    parser.add_argument("--book", required=True, help="slug или путь к книге")
    args = parser.parse_args()
    book = load_book(args.book)
    build(book)
    return 0


if __name__ == "__main__":
    sys.exit(main())
