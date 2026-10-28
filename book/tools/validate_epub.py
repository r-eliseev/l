"""Валидатор EPUB: структура пакета, XML, ссылки, метаданные.

Запуск:
    python tools/validate_epub.py
"""

from __future__ import annotations

import posixpath
import re
import sys
import zipfile
from collections import Counter
import xml.etree.ElementTree as ET
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent
EPUB = BOOK / "dist" / "ddd-praktika.epub"

OPF_NS = "http://www.idpf.org/2007/opf"
DC_NS = "http://purl.org/dc/elements/1.1/"
NCX_NS = "http://www.daisy.org/z3986/2005/ncx/"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def main() -> int:
    if not EPUB.exists():
        print(f"Файл не найден: {EPUB}")
        return 1

    with zipfile.ZipFile(EPUB) as z:
        names = set(z.namelist())

        # --- структура пакета ---
        if "mimetype" not in names:
            err("нет файла mimetype")
        else:
            if z.read("mimetype").decode().strip() != "application/epub+zip":
                err("неверное содержимое mimetype")
            info = z.getinfo("mimetype")
            if info.compress_type != zipfile.ZIP_STORED:
                err("mimetype должен храниться без сжатия")
            if z.namelist()[0] != "mimetype":
                err("mimetype должен быть первым элементом архива")

        if "META-INF/container.xml" not in names:
            err("нет META-INF/container.xml")
        if "OEBPS/content.opf" not in names:
            err("нет OEBPS/content.opf")

        # --- XML валиден ---
        for name in sorted(names):
            if name.endswith((".xhtml", ".opf", ".ncx", ".xml")):
                try:
                    ET.fromstring(z.read(name))
                except ET.ParseError as exc:
                    err(f"{name}: XML невалиден — {exc}")

        # --- метаданные ---
        opf = ET.fromstring(z.read("OEBPS/content.opf"))
        titles = [
            e for e in opf.iter()
            if e.tag.endswith("}title") or e.tag == "title"
        ]
        if not any((e.text or "").strip() for e in titles):
            err("в OPF нет dc:title")
        langs = [
            e for e in opf.iter()
            if e.tag.endswith("}language") or e.tag == "language"
        ]
        if not any((e.text or "").strip() == "ru" for e in langs):
            err("в OPF нет dc:language=ru")
        if opf.find(f".//{{{OPF_NS}}}manifest") is None:
            err("в OPF нет manifest")
        if opf.find(f".//{{{OPF_NS}}}spine") is None:
            err("в OPF нет spine")

        manifest = {
            item.get("id"): item.get("href")
            for item in opf.findall(f".//{{{OPF_NS}}}manifest/{{{OPF_NS}}}item")
        }
        spine = [
            ref.get("idref")
            for ref in opf.findall(f".//{{{OPF_NS}}}spine/{{{OPF_NS}}}itemref")
        ]
        if not spine:
            err("spine пуст")
        for idref in spine:
            if idref not in manifest:
                err(f"spine ссылается на неизвестный id: {idref}")
        for item_id, href in manifest.items():
            target = posixpath.normpath(posixpath.join("OEBPS", href))
            if target not in names:
                err(f"manifest: файла нет — {target}")

        # nav обязателен в EPUB 3
        nav_items = [
            item for item in opf.findall(f".//{{{OPF_NS}}}manifest/{{{OPF_NS}}}item")
            if "nav" in (item.get("properties") or "")
        ]
        if not nav_items:
            err("в manifest нет документа навигации (properties=nav)")

        # --- NCX ---
        if "OEBPS/toc.ncx" in names:
            ncx = ET.fromstring(z.read("OEBPS/toc.ncx"))
            points = ncx.findall(f".//{{{NCX_NS}}}navPoint")
            if not points:
                err("NCX пуст")
            ncx_sources: list[str] = []
            for point in points:
                content = point.find(f"{{{NCX_NS}}}content")
                if content is None:
                    err("navPoint без content")
                    continue
                src = content.get("src", "")
                ncx_sources.append(src)
                target = posixpath.normpath(posixpath.join("OEBPS", src))
                if target not in names:
                    err(f"NCX ссылается на несуществующий файл: {src}")
            # каждая глава должна попасть в оглавление ровно один раз
            duplicates = {
                src: count
                for src, count in Counter(ncx_sources).items()
                if count > 1
            }
            if duplicates:
                err(f"NCX: страницы в оглавлении продублированы — {duplicates}")

        if "OEBPS/text/nav.xhtml" in names:
            nav_html = z.read("OEBPS/text/nav.xhtml").decode("utf-8")
            nav_links = re.findall(r'href="([^"]+\.xhtml)"', nav_html)
            nav_duplicates = {
                href: count
                for href, count in Counter(nav_links).items()
                if count > 1
            }
            if nav_duplicates:
                err(f"nav.xhtml: страницы в оглавлении продублированы — {nav_duplicates}")
            chapters = [
                name for name in names
                if name.startswith("OEBPS/text/") and re.match(r"^\d\d-", name)
            ]
            missing_in_nav = [
                name for name in chapters
                if not any(
                    Path(name).name in href for href in nav_links
                )
            ]
            if missing_in_nav:
                err(f"nav.xhtml: главы отсутствуют в оглавлении — {missing_in_nav}")

        # --- внутренние ссылки в XHTML ---
        for name in sorted(names):
            if not name.endswith(".xhtml"):
                continue
            content = z.read(name).decode("utf-8")
            base = posixpath.dirname(name)
            for href in re.findall(r'href="([^"]+)"', content):
                if href.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if href.endswith(".css") or href.endswith(".jpg"):
                    target = posixpath.normpath(posixpath.join(base, href))
                    if target not in names:
                        err(f"{name}: битая ссылка на ресурс — {href}")
                    continue
                if href.endswith(".xhtml"):
                    target = posixpath.normpath(posixpath.join(base, href))
                    if target not in names:
                        err(f"{name}: битая ссылка — {href}")

        # --- скрытые ответы ---
        total_details = 0
        for name in sorted(names):
            if name.endswith(".xhtml") and name.startswith("OEBPS/text/"):
                content = z.read(name).decode("utf-8")
                total_details += len(re.findall(r"<details\b", content))
                if re.search(r"<details[^>]*\sopen\b", content):
                    err(f"{name}: есть раскрытый <details open>")
        if total_details == 0:
            warn("в книге нет ни одного скрытого ответа (<details>)")

        # --- код в книге ---
        total_code = 0
        for name in sorted(names):
            if name.endswith(".xhtml"):
                total_code += len(re.findall(r"<pre\b", z.read(name).decode("utf-8")))
        if total_code == 0:
            warn("в книге нет блоков кода")

        print(f"Проверено: {EPUB.name}")
        print(f"  файлов в архиве: {len(names)}")
        print(f"  страниц в spine:  {len(spine)}")
        print(f"  блоков кода:      {total_code}")
        print(f"  скрытых ответов:  {total_details}")
        print(f"  размер:           {EPUB.stat().st_size / 1024:.0f} КБ")

    if warnings:
        print("\nПредупреждения:")
        for w in warnings:
            print(f"  ! {w}")

    if errors:
        print(f"\nОшибок: {len(errors)}")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print("\nEPUB валиден.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
