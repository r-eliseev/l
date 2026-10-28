#!/usr/bin/env python3
"""Validate a built EPUB: structure, XML, links, navigation.

    python validate_epub.py dist/book.epub

Exit code 0 when the package is valid, 1 otherwise.
"""

from __future__ import annotations

import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

OPF_NS = "http://www.idpf.org/2007/opf"
DC_NS = "http://purl.org/dc/elements/1.1/"
NCX_NS = "http://www.daisy.org/z3986/2005/ncx/"

errors: list[str] = []
warnings: list[str] = []


def err(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: validate_epub.py <file.epub>")
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Not found: {path}")
        return 1

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())

        # --- package layout ---
        if "mimetype" not in names:
            err("no mimetype entry")
        else:
            if archive.read("mimetype").decode().strip() != "application/epub+zip":
                err("mimetype has the wrong content")
            if archive.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
                err("mimetype must be stored uncompressed")
            if archive.namelist()[0] != "mimetype":
                err("mimetype must be the first entry in the archive")

        for required in ("META-INF/container.xml", "OEBPS/content.opf"):
            if required not in names:
                err(f"missing {required}")

        # --- XML well-formedness ---
        for name in sorted(names):
            if name.endswith((".xhtml", ".opf", ".ncx", ".xml")):
                try:
                    ET.fromstring(archive.read(name))
                except ET.ParseError as exc:
                    err(f"{name}: invalid XML — {exc}")

        # --- metadata and manifest ---
        if "OEBPS/content.opf" in names:
            opf = ET.fromstring(archive.read("OEBPS/content.opf"))
            titles = [
                e for e in opf.iter()
                if e.tag.endswith("}title") or e.tag == "title"
            ]
            if not any((e.text or "").strip() for e in titles):
                err("no dc:title in the package document")
            languages = [
                e for e in opf.iter()
                if e.tag.endswith("}language") or e.tag == "language"
            ]
            if not any((e.text or "").strip() for e in languages):
                err("no dc:language in the package document")

            manifest = {
                item.get("id"): item.get("href")
                for item in opf.findall(
                    f".//{{{OPF_NS}}}manifest/{{{OPF_NS}}}item"
                )
            }
            spine = [
                ref.get("idref")
                for ref in opf.findall(
                    f".//{{{OPF_NS}}}spine/{{{OPF_NS}}}itemref"
                )
            ]
            if not spine:
                err("the spine is empty")
            for idref in spine:
                if idref not in manifest:
                    err(f"spine references an unknown id: {idref}")
            for item_id, href in manifest.items():
                target = posixpath.normpath(posixpath.join("OEBPS", href))
                if target not in names:
                    err(f"manifest lists a missing file: {target}")

            nav_items = [
                item for item in opf.findall(
                    f".//{{{OPF_NS}}}manifest/{{{OPF_NS}}}item"
                )
                if "nav" in (item.get("properties") or "")
            ]
            if not nav_items:
                err("no navigation document (properties=\"nav\")")

        # --- NCX ---
        if "OEBPS/toc.ncx" in names:
            ncx = ET.fromstring(archive.read("OEBPS/toc.ncx"))
            points = ncx.findall(f".//{{{NCX_NS}}}navPoint")
            if not points:
                err("the NCX is empty")
            sources: list[str] = []
            for point in points:
                content = point.find(f"{{{NCX_NS}}}content")
                if content is None:
                    err("a navPoint has no content")
                    continue
                src = content.get("src", "")
                sources.append(src)
                target = posixpath.normpath(posixpath.join("OEBPS", src))
                if target not in names:
                    err(f"the NCX links to a missing file: {src}")
            duplicates = {
                src: count for src, count in Counter(sources).items() if count > 1
            }
            if duplicates:
                err(f"the NCX lists pages more than once: {duplicates}")

        # --- navigation document ---
        if "OEBPS/text/nav.xhtml" in names:
            nav_html = archive.read("OEBPS/text/nav.xhtml").decode("utf-8")
            links = re.findall(r'href="([^"]+\.xhtml)"', nav_html)
            duplicates = {
                href: count for href, count in Counter(links).items() if count > 1
            }
            if duplicates:
                err(f"the navigation lists pages more than once: {duplicates}")
            chapters = [
                name for name in names
                if name.startswith("OEBPS/text/") and re.match(r"^\d\d-", name)
            ]
            missing = [
                name for name in chapters
                if not any(Path(name).name in href for href in links)
            ]
            if missing:
                err(f"chapters absent from the navigation: {missing}")

        # --- internal links in every page ---
        for name in sorted(names):
            if not name.endswith(".xhtml"):
                continue
            content = archive.read(name).decode("utf-8")
            base = posixpath.dirname(name)
            for href in re.findall(r'href="([^"]+)"', content):
                if href.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = posixpath.normpath(posixpath.join(base, href))
                if target not in names:
                    err(f"{name}: broken link — {href}")

        # --- hidden answers must stay hidden ---
        total_details = 0
        for name in sorted(names):
            if name.startswith("OEBPS/text/") and name.endswith(".xhtml"):
                content = archive.read(name).decode("utf-8")
                total_details += len(re.findall(r"<details\b", content))
                if re.search(r"<details[^>]*\sopen\b", content):
                    err(f"{name}: a <details> block is open by default")

        total_code = sum(
            len(re.findall(r"<pre\b", archive.read(name).decode("utf-8")))
            for name in sorted(names) if name.endswith(".xhtml")
        )
        if total_details == 0:
            warn("the book contains no hidden answers (<details>)")
        if total_code == 0:
            warn("the book contains no code blocks")

        print(f"Checked: {path.name}")
        print(f"  files in archive:  {len(names)}")
        print(f"  pages in spine:    {len(spine) if 'spine' in dir() else '?'}")
        print(f"  code blocks:       {total_code}")
        print(f"  hidden answers:    {total_details}")
        print(f"  size:              {path.stat().st_size / 1024:.0f} KB")

    if warnings:
        print("\nWarnings:")
        for message in warnings:
            print(f"  ! {message}")

    if errors:
        print(f"\nErrors: {len(errors)}")
        for message in errors:
            print(f"  x {message}")
        return 1

    print("\nThe EPUB is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
