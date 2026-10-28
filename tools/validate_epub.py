"""Валидатор EPUB: структура пакета, XML, ссылки, метаданные.

Запуск:
    python tools/validate_epub.py --book ddd-praktika
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bookmeta import load_book  # noqa: E402

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
    parser = argparse.ArgumentParser(description="Валидация EPUB книги")
    parser.add_argument("--book", required=True, help="slug или путь к книге")
    args = parser.parse_args()

    book = load_book(args.book)
    epub = book.epub_path
    language = book.language

    if not epub.exists():
        print(f"Файл не найден: {epub}")
        return 1

    with zipfile.ZipFile(epub) as z:
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
        if not any((e.text or "").strip() == language for e in langs):
            err(f"в OPF нет dc:language={language}")
        if opf.find(f".//{{{OPF_NS}}}manifest") is None:
            err("в OPF нет manifest")
        if opf.find(f".//{{{OPF_NS}}}spine") is None:
            err("в OPF нет spine")

        manifest = opf.find(f".//{{{OPF_NS}}}manifest")
        if manifest is not None:
            declared = {item.get("href") for item in manifest.findall(f"{{{OPF_NS}}}item")}
            for href in sorted(declared):
                # href в манифесте задан относительно OEBPS — корня пакета.
                if href and f"OEBPS/{href}" not in names:
                    err(f"в манифесте, но нет в архиве: {href}")

            spine = opf.find(f".//{{{OPF_NS}}}spine")
            if spine is not None:
                idrefs = [r.get("idref") for r in spine.findall(f"{{{OPF_NS}}}itemref")]
                ids = {item.get("id") for item in manifest.findall(f"{{{OPF_NS}}}item")}
                for idref in idrefs:
                    if idref not in ids:
                        err(f"spine ссылается на неизвестный id: {idref}")

        # --- навигация ---
        if "OEBPS/text/nav.xhtml" not in names:
            err("нет навигационного документа nav.xhtml")
        else:
            nav = z.read("OEBPS/text/nav.xhtml").decode("utf-8")
            chapter_files = [p.stem for p in book.chapter_files()]
            for chapter in chapter_files:
                if chapter not in nav:
                    err(f"главы {chapter} нет в оглавлении")

        if "OEBPS/toc.ncx" not in names:
            warn("нет toc.ncx — старые ридеры не покажут оглавление")

        # --- внутренние ссылки ---
        for name in sorted(names):
            if not name.endswith(".xhtml"):
                continue
            body = z.read(name).decode("utf-8", errors="replace")
            base = posixpath.dirname(name)
            for href in re.findall(r'href="([^"]+)"', body):
                if href.startswith(("http", "mailto:", "#")):
                    continue
                target = posixpath.normpath(posixpath.join(base, href.split("#")[0]))
                if target not in names:
                    err(f"{name}: битая ссылка {href}")

        # --- скрытые ответы закрыты ---
        for name in sorted(names):
            if not name.endswith(".xhtml"):
                continue
            body = z.read(name).decode("utf-8", errors="replace")
            for tag in re.findall(r"<details\b[^>]*>", body, re.I):
                if re.search(r"\bopen\b", tag, re.I):
                    err(f"{name}: <details> раскрыт по умолчанию")

    if errors:
        print(f"Ошибок: {len(errors)}")
        for e in errors:
            print(f"  ✗ {e}")
        if warnings:
            print(f"\nПредупреждений: {len(warnings)}")
            for w in warnings:
                print(f"  ! {w}")
        return 1

    print(f"EPUB валиден: {epub}")
    if warnings:
        print(f"Предупреждений: {len(warnings)}")
        for w in warnings:
            print(f"  ! {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
