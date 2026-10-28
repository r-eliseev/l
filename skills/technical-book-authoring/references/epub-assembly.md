# Assembling an EPUB by hand

EPUB 3 is a ZIP with a required layout. You can build it with `zipfile` and
`markdown` — no converter (pandoc, calibre) required. This file lists the
layout and the traps that silently break a hand-built file.

## Directory layout

```
mimetype                          (no compression, first entry)
META-INF/container.xml
OEBPS/
  content.opf                     package document
  toc.ncx                         navigation for EPUB 2 readers
  nav.xhtml                       navigation document (required by EPUB 3)
  styles/book.css
  images/cover.jpg
  text/front.xhtml
  text/part-1.xhtml               generated part divider pages
  text/01-chapter.xhtml
  text/app-a-glossary.xhtml
```

## Traps

**The `mimetype` entry must be stored uncompressed and first.** Readers that
see a compressed `mimetype` reject the file outright. In `zipfile`:

```python
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(mimetype_path, "mimetype", compress_type=zipfile.ZIP_STORED)
    for path in sorted(build.rglob("*")):
        if path.is_file() and path.name != "mimetype":
            z.write(path, path.relative_to(build).as_posix())
```

**XHTML requires self-closing void tags.** Markdown emits `<hr>`, which is
invalid XML and breaks the parse of the whole page. Close them:

```python
for tag in ("hr", "br", "img", "meta", "link", "input", "col"):
    body = re.sub(rf"<{tag}\b([^>]*?)(?<!/)>", rf"<{tag}\1/>", body)
```

**`nav.xhtml` and `toc.ncx` live in different places and use different
relative paths.** `nav.xhtml` sits in `OEBPS/text/`, so its links to sibling
chapters are `01-chapter.xhtml`; `toc.ncx` sits in `OEBPS/`, so its links are
`text/01-chapter.xhtml`. Mixing them up yields a book whose contents page is
entirely broken links.

**Every chapter appears exactly once in the navigation.** Enumerating both
the parts and their chapters adds each chapter twice. Build the TOC from the
structure file, with chapters nested under their part and parts contributing
no separate chapter entries.

**The NCX `<head>` must be closed.** A missing `</head>` shows up as a
mismatched-tag error at the very end of the file, far from the cause.

**`<details>` works but only in EPUB 3.** It gives hidden answers without any
JavaScript. The `nav` document and `properties="nav"` on its manifest item
are what make the file EPUB 3 rather than a malformed EPUB 2.

## Rendering Markdown

```python
MD_EXTENSIONS = [
    "markdown.extensions.fenced_code",
    "markdown.extensions.tables",
    "markdown.extensions.attr_list",
    "markdown.extensions.def_list",
    "markdown.extensions.md_in_html",
    "markdown.extensions.sane_lists",
]
```

`md_in_html` is what makes `markdown="1"` work inside `<details>`.

Code highlighting via pygments, inlined into the page so the file needs no
extra stylesheet:

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
highlighted = highlight(code, lexer, HtmlFormatter(nowrap=False))
```

The pygments wrapper emits `<div class="highlight"><pre>`; strip the wrapper
and keep the `<pre>` so the book's own CSS controls the panel.

## Cover

Generate with Pillow. Two details that matter visually:

- draw the accent rule **above** the title, never across it — a rule that
  strikes through the title reads as a mistake;
- render the gradient in a loop of 1-pixel lines; the gradient banding is
  visible on a flat fill.

## After building

Validate, then look at it:

```python
import zipfile, xml.etree.ElementTree as ET
with zipfile.ZipFile(path) as z:
    for name in z.namelist():
        if name.endswith((".xhtml", ".opf", ".ncx", ".xml")):
            ET.fromstring(z.read(name))   # raises on malformed XML
```

Then extract the pages and open them in a browser to inspect the rendering —
the TOC, a chapter with code, and the cover. Structural checks do not catch
visual problems.

## Rebuilding

Always build to a temporary name and move it into place at the end. On
Windows, replacing a file that another process has open fails, and a reader
application is exactly that kind of process.

```python
tmp = out.with_suffix(out.suffix + ".tmp")
# ... write the zip to tmp ...
tmp.replace(out)
```
