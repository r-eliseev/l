"""Проверяет, что цитаты в главах дословны и привязаны к верному источнику.

Книга обещает: всё, что стоит в кавычках и приписано источнику, взято из
него дословно. Этот скрипт проверяет обещание по факту.

Карта «источник → файл с текстом страницы» лежит в
`books/<slug>/src/evidence-map.json`: файлы извлечений лежат вне репозитория,
в локальном кэше, поэтому на другой машине проверка пропускается.

Запуск:
    python tools/check_quotes.py --book ddd-praktika
    python tools/check_quotes.py --book ddd-praktika --fix
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bookmeta import load_book  # noqa: E402


def hermes_home() -> Path:
    """Каталог Hermes: одинаково на Windows и Linux."""
    val = os.environ.get("HERMES_HOME", "").strip()
    if val:
        return Path(val)
    if os.name == "nt":
        return Path.home() / "AppData/Local/hermes"
    return Path.home() / ".hermes"


HERMES = hermes_home()
SCRATCH = HERMES / "cache/scratch"
SP = HERMES / "skills/research/grounded-citations/scripts/sources.py"

# Копия ledger-скрипта лежит в репозитории — она приоритетнее: репозиторий
# должен работать на любой машине, где установлен Hermes, и без него.
REPO_SP = (
    Path(__file__).resolve().parent.parent
    / "skills/grounded-citations/scripts/sources.py"
)
if REPO_SP.exists():
    SP = REPO_SP

QUOTE_RE = re.compile(r"«([^»]{20,600})»")
CYRILLIC = re.compile(r"[Ѐ-ӿ]")
LATIN = re.compile(r"[A-Za-z]")


def load_matcher():
    if not SP.exists():
        raise FileNotFoundError(f"Не найден скрипт ledger: {SP}")
    spec = importlib.util.spec_from_file_location("sources", SP)
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


def _normalize(text: str) -> str:
    """Приводит текст к сравнимому виду.

    Убирает типографские различия, которые не меняют содержания:
    «ёлочки» против прямых кавычек, лишние пробелы, переносы строк.
    Многоточие в конце цитаты означает пропуск — такое допустимо.
    """
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = " ".join(text.split())
    if text.endswith("..."):
        text = text[:-3].rstrip()
    elif text.endswith("\u2026"):
        text = text[:-1].rstrip()
    return text.rstrip(",;:.")


def _matches(quote: str, source: str) -> bool:
    """Проверяет, что цитата дословно есть в источнике.

    Допускается многоточие в конце — стандартный приём цитирования.
    """
    mod = load_matcher()
    if mod.quote_in_evidence(quote, source):
        return True
    return _normalize(quote) in _normalize(source)


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверка дословности цитат")
    parser.add_argument("--book", required=True, help="slug или путь к книге")
    parser.add_argument("--fix", action="store_true", help="исправить привязки")
    args = parser.parse_args()

    book = load_book(args.book)
    if not book.contract.get("citations"):
        print(f"Книга «{book.title}»: цитаты не проверяются (контракт без цитат).")
        return 0

    if not SP.exists():
        print(
            "Проверка цитат пропущена: нет скрипта ledger "
            f"({SP}). Запускать на машине автора."
        )
        return 0

    map_path = book.src / "evidence-map.json"
    if not map_path.exists():
        print(
            f"Проверка цитат пропущена: нет карты извлечений {map_path}. "
            "Файлы страниц лежат вне репозитория, поэтому проверка "
            "выполняется только на машине автора."
        )
        return 0

    filemap: dict[str, str] = json.loads(map_path.read_text(encoding="utf-8"))

    mod = load_matcher()
    evidence = {
        int(sid): (SCRATCH / name).read_text(encoding="utf-8")
        for sid, name in filemap.items()
        if (SCRATCH / name).exists()
    }
    if not evidence:
        print(
            "Проверка цитат пропущена: нет локального кэша извлечений "
            f"({SCRATCH}). Источники страниц лежат вне репозитория, "
            "поэтому проверка выполняется только на машине автора."
        )
        return 0

    problems: list[str] = []
    fixed = 0

    for path in book.all_content_files():
        if not path.exists():
            continue
        if path.name.startswith("app-d-sources"):
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
            if _matches(quote, evidence[sid]):
                continue

            # ищем, где цитата есть на самом деле
            found_in = [
                other for other, source in evidence.items()
                if _matches(quote, source)
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
