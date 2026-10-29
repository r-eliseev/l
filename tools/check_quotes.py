"""Проверяет, что цитаты в главах дословны и привязаны к верному источнику.

Книга обещает: всё, что стоит в кавычках и приписано источнику, взято из
него дословно. Этот скрипт проверяет обещание по факту.

Тексты источников лежат в репозитории: `books/<slug>/src/evidence/`.
Карта «id → файл» — `books/<slug>/src/evidence-map.json`. Поэтому проверка
работает одинаково на любой машине и в CI.

Запуск:
    python tools/check_quotes.py --book ddd-praktika
    python tools/check_quotes.py --book ddd-praktika --fix
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bookmeta import load_book  # noqa: E402

# Матчер дословности лежит в навыке grounded-citations, копия которого есть
# в этом репозитории: skills/grounded-citations/scripts/sources.py.
# Он понимает разметку страницы: markdown-ссылки схлопываются в подписи,
# переносы строк и регистр не важны.
MATCHER_PATH = (
    Path(__file__).resolve().parent.parent
    / "skills/grounded-citations/scripts/sources.py"
)

QUOTE_RE = re.compile(r"«([^»]{20,600})»")
CYRILLIC = re.compile(r"[Ѐ-ӿ]")
LATIN = re.compile(r"[A-Za-z]")


def load_matcher():
    """Загружает модуль сопоставления цитат."""
    if not MATCHER_PATH.exists():
        raise FileNotFoundError(f"Не найден матчер цитат: {MATCHER_PATH}")
    spec = importlib.util.spec_from_file_location("sources", MATCHER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_quotation(text: str) -> bool:
    """Отделяет цитату от обычного выделения.

    Цитата — преимущественно латинский текст. Русские фразы в кавычках — это
    выделения терминов, а не цитаты из источников.
    """
    cyr = len(CYRILLIC.findall(text))
    lat = len(LATIN.findall(text))
    if lat < 12:
        return False
    return cyr / max(cyr + lat, 1) < 0.35


def _matches(quote: str, source: str, mod) -> bool:
    """Проверяет, что цитата дословно есть в источнике.

    Допускается многоточие в конце — стандартный приём цитирования.
    """
    if mod.quote_in_evidence(quote, source):
        return True
    # Многоточие в конце цитаты означает пропуск: проверяем без него.
    trimmed = quote.rstrip(".…").rstrip()
    if trimmed != quote and mod.quote_in_evidence(trimmed, source):
        return True
    return False


def load_evidence(book) -> dict[int, str]:
    """Читает тексты источников из репозитория."""
    map_path = book.src / "evidence-map.json"
    if not map_path.exists():
        return {}
    filemap: dict[str, str] = json.loads(map_path.read_text(encoding="utf-8"))
    evidence: dict[int, str] = {}
    for sid, relative in filemap.items():
        path = book.src / relative
        if path.exists():
            evidence[int(sid)] = path.read_text(encoding="utf-8", errors="replace")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверка дословности цитат")
    parser.add_argument("--book", required=True, help="slug или путь к книге")
    parser.add_argument("--fix", action="store_true", help="исправить привязки")
    args = parser.parse_args()

    book = load_book(args.book)
    if not book.contract.get("citations"):
        print(f"Книга «{book.title}»: цитаты не проверяются (контракт без цитат).")
        return 0

    mod = load_matcher()
    evidence = load_evidence(book)
    if not evidence:
        print(
            f"Проверка цитат пропущена: нет текстов источников в "
            f"{book.src / 'evidence'}. Карта: {book.src / 'evidence-map.json'}."
        )
        return 0

    problems: list[str] = []
    fixed = 0

    for path in book.all_content_files():
        if not path.exists():
            continue
        if path.name.startswith("app-d-sources") or path.name.startswith("app-c-sources"):
            continue
        text = path.read_text(encoding="utf-8")
        original = text

        for match in QUOTE_RE.finditer(text):
            quote = match.group(1)
            if not is_quotation(quote):
                continue
            tail = text[match.end():match.end() + 120]
            head = text[max(0, match.start() - 160):match.start()]
            ids = re.findall(r"\[(\d+)\]", tail) or re.findall(r"\[(\d+)\]", head)
            if not ids:
                continue
            sid = int(ids[0])
            if sid not in evidence:
                continue
            if _matches(quote, evidence[sid], mod):
                continue

            # ищем, где цитата есть на самом деле
            found_in = [
                other for other, source in evidence.items()
                if _matches(quote, source, mod)
            ]

            if len(found_in) == 1 and found_in[0] != sid:
                problems.append(
                    f"{path.name}: цитата приписана [{sid}], а найдена в "
                    f"[{found_in[0]}] — «{quote[:70]}»"
                )
                if args.fix:
                    # Заменяем ближайшую ссылку, стоящую после цитаты.
                    # Окно поиска широкое: цитата может быть разбита
                    # переносами строк, и её хвост длиннее, чем кажется.
                    window = text[match.end():match.end() + 400]
                    reference = re.search(r"\[(\d+)\]", window)
                    if reference:
                        position = match.end() + reference.start()
                        new_ref = f"[{found_in[0]}]"
                        text = text[:position] + new_ref + text[position + len(reference.group(0)):]
                        fixed += 1
                        print(
                            f"  исправлено: {path.name} "
                            f"[{sid}] → [{found_in[0]}] — «{quote[:50]}»"
                        )
            elif not found_in:
                problems.append(
                    f"{path.name}: цитата не найдена ни в одном источнике — "
                    f"«{quote[:70]}» (приписана [{sid}])"
                )
            else:
                problems.append(
                    f"{path.name}: цитата встречается в нескольких источниках "
                    f"{found_in}, приписана [{sid}] — «{quote[:70]}»"
                )

        if args.fix and text != original:
            path.write_text(text, encoding="utf-8")

    if problems:
        print(f"Замечаний: {len(problems)}")
        for p in problems:
            print(f"  ! {p}")
        if fixed:
            print(f"\nИсправлено привязок: {fixed}")
        return 1

    print("Все цитаты дословны и привязаны верно.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
