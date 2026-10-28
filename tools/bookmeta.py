"""Доступ к манифесту книги и её структуре.

Каждая книга лежит в `books/<slug>/` и описывается двумя файлами:

- `book.json` — паспорт: заголовок, автор, обложка и контракт главы
  (какие секции обязательны, сколько вопросов, проверяется ли код);
- `src/structure.json` — оглавление: части, главы, приложения.

Инструменты в `tools/` не знают ни про одну конкретную книгу: они берут
манифест и оглавление отсюда. Поэтому книгу можно добавить, не трогая
инструменты.

Использование:

    from bookmeta import load_book

    book = load_book("ddd-praktika")
    print(book.dir, book.manifest["title"])
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BOOKS_DIR = REPO / "books"


@dataclass
class Book:
    """Книга: каталог, манифест и оглавление."""

    dir: Path
    manifest: dict
    structure: dict

    @property
    def slug(self) -> str:
        return self.manifest.get("slug", self.dir.name)

    @property
    def src(self) -> Path:
        return self.dir / "src"

    @property
    def chapters(self) -> Path:
        return self.src / "chapters"

    @property
    def dist(self) -> Path:
        return self.dir / "dist"

    @property
    def contract(self) -> dict:
        return self.manifest.get("contract", {})

    @property
    def language(self) -> str:
        return self.manifest.get("language", "ru")

    @property
    def title(self) -> str:
        return self.manifest.get("title", self.slug)

    @property
    def subtitle(self) -> str:
        return self.manifest.get("subtitle", "")

    @property
    def author(self) -> str:
        return self.manifest.get("author", "")

    @property
    def epub_path(self) -> Path:
        return self.dist / self.manifest.get("epub_filename", f"{self.slug}.epub")

    def code_dir(self) -> Path | None:
        """Каталог пакета с примерами — если контракт его требует."""
        rel = self.contract.get("code", {}).get("path")
        return (self.dir / rel) if rel else None

    def chapter_files(self) -> list[Path]:
        """Файлы глав по оглавлению, в порядке чтения."""
        out: list[Path] = []
        for part in self.structure.get("parts", []):
            for chapter in part.get("chapters", []):
                out.append(self.chapters / f"{chapter['file']}.md")
        for chapter in self.structure.get("chapters", []):
            out.append(self.chapters / f"{chapter['file']}.md")
        return out

    def appendix_files(self) -> list[Path]:
        return [
            self.chapters / f"{appendix['file']}.md"
            for appendix in self.structure.get("appendices", [])
        ]

    def front_file(self) -> Path | None:
        front = self.structure.get("front")
        if not front:
            return None
        return self.chapters / f"{front['file']}.md"

    def all_content_files(self) -> list[Path]:
        files = []
        front = self.front_file()
        if front:
            files.append(front)
        files.extend(self.chapter_files())
        files.extend(self.appendix_files())
        return files


def load_book(slug_or_path: str) -> Book:
    """Загружает книгу по slug'у или по пути к каталогу."""
    candidate = Path(slug_or_path)
    if not candidate.is_absolute() and not candidate.exists():
        candidate = BOOKS_DIR / slug_or_path
    candidate = candidate.resolve()
    manifest_path = candidate / "book.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Нет манифеста книги: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    structure_path = candidate / manifest.get("structure", "src/structure.json")
    if not structure_path.exists():
        raise FileNotFoundError(f"Нет оглавления книги: {structure_path}")
    structure = json.loads(structure_path.read_text(encoding="utf-8"))
    return Book(dir=candidate, manifest=manifest, structure=structure)


def list_books() -> list[Path]:
    """Каталоги всех книг репозитория."""
    if not BOOKS_DIR.exists():
        return []
    return sorted(p for p in BOOKS_DIR.iterdir() if (p / "book.json").exists())


def resolve_argument(value: str | None) -> Book:
    """Разбирает аргумент `--book`: slug или путь."""
    if not value:
        raise SystemExit("Нужно указать книгу: --book <slug>")
    return load_book(value)
