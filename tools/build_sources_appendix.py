"""Генерирует приложение «Источники» из ledger цитат.

Страница собирается механически: id → URL берётся из ledger, а не
переписывается руками, поэтому нумерация в книге и в ledger не разойдутся.

Ledger лежит вне репозитория (`$HERMES_HOME/cache/citations/ledger.json`),
поэтому на машине без него приложение не пересобирается и остаётся прежним.

Запуск:
    python tools/build_sources_appendix.py --book ddd-praktika
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bookmeta import Book, load_book  # noqa: E402

DEFAULT_INTRO = """# Приложение. Источники

*Все утверждения о первоисточниках в книге снабжены номером в квадратных
скобках. Ниже — полный перечень источников с адресами и ключевыми
дословными цитатами, на которые опирается текст.*

*Цитаты приведены в том виде, в каком они звучат в оригинале, — чтобы можно
было проверить формулировку, не доверяя пересказу.*

"""

DEFAULT_HOWTO = (
    "Номер в квадратных скобках после утверждения означает: это утверждение "
    "опирается на источник под этим номером в перечне ниже.\n"
)


def load_sources(book: Book) -> dict:
    """Читает банк источников книги из репозитория.

    Банк лежит в `books/<slug>/src/quotes.json`, поэтому приложение
    «Источники» собирается одинаково на любой машине и в CI.
    """
    path = book.src / "quotes.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def collect_used_ids(book: Book) -> set[int]:
    """Собирает номера источников, реально встречающихся в главах."""
    used: set[int] = set()
    for path in book.all_content_files():
        if not path.exists():
            continue
        if path.name.startswith("app-d-sources"):
            continue
        text = path.read_text(encoding="utf-8")
        used.update(int(x) for x in re.findall(r"\[(\d+)\]", text))
    return used


# Ссылка в цитате может вести на соседнюю страницу документации. В книге
# такая ссылка бессмысленна: читатель не кликает по цитате. Поэтому
# markdown-ссылки превращаются в подписи, а внешние остаются как есть.
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def _clean_quote(text: str) -> str:
    """Готовит цитату к выводу: однострочная, без markdown-ссылок."""
    text = text.replace("\n", " ")
    text = _MD_LINK.sub(r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def render_source(source: dict) -> list[str]:
    lines = [f"### [{source['id']}] {source.get('title') or source['url']}\n"]
    lines.append(f"{source['url']}\n")
    quotes = source.get("quotes", [])
    if quotes:
        lines.append("Ключевые формулировки:\n")
        for quote in quotes:
            text = quote["text"] if isinstance(quote, dict) else quote
            text = _clean_quote(text)
            lines.append(f"> «{text}»\n")
    else:
        lines.append("Источник используется для общих сведений без прямого цитирования.\n")
    lines.append("")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Сборка приложения «Источники»")
    parser.add_argument("--book", required=True, help="slug или путь к книге")
    args = parser.parse_args()

    book = load_book(args.book)
    sources_cfg = book.manifest.get("sources", {})
    appendix_file = sources_cfg.get("appendix", {}).get("file")
    if not appendix_file:
        print(f"Книга «{book.title}»: приложение «Источники» не предусмотрено.")
        return 0

    out = book.chapters / f"{appendix_file}.md"
    intro = sources_cfg.get("appendix", {}).get("intro", DEFAULT_INTRO)
    howto = sources_cfg.get("appendix", {}).get("howto", DEFAULT_HOWTO)

    bank = load_sources(book)
    if not bank:
        print(
            "Приложение «Источники» не пересобрано: нет банка источников "
            f"({book.src / 'quotes.json'})."
        )
        return 0

    sources = [
        {"id": int(sid), **src} for sid, src in bank.items()
    ]
    sources.sort(key=lambda s: s["id"])
    used = collect_used_ids(book)
    lines = [intro]

    lines.append("## Как читать ссылки\n")
    lines.append(howto)

    groups = sources_cfg.get("groups") or []
    assigned: set[int] = set()

    for group in groups:
        ids = set(group.get("ids", []))
        members = [s for s in sources if s["id"] in ids and s["id"] not in assigned]
        if not members:
            continue
        assigned.update(s["id"] for s in members)
        lines.append(f"## {group['title']}\n")
        for source in members:
            lines.extend(render_source(source))

    rest = [s for s in sources if s["id"] not in assigned]
    if rest:
        lines.append("## Прочие материалы\n")
        for source in rest:
            lines.append(
                f"- **[{source['id']}]** {source.get('title') or ''} — {source['url']}"
            )
        lines.append("")

    if used:
        unused = [s["id"] for s in sources if s["id"] not in used]
        if unused:
            lines.append("## Источники, не процитированные в тексте\n")
            lines.append(
                "Эти материалы были изучены при подготовке книги, но прямой "
                "ссылки на них в главах нет: "
                + ", ".join(f"[{i}]" for i in sorted(unused))
                + "\n"
            )

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Записано: {out} ({len(sources)} источников)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
