"""Линтер глав: проверяет структуру, ссылки на источники и качество кода.

Контракт главы приходит из `books/<slug>/book.json`, поэтому линтер один на
все книги репозитория.

Запуск:
    python tools/lint_book.py --book ddd-praktika
    python tools/lint_book.py --book ddd-praktika --json
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bookmeta import Book, load_book  # noqa: E402

CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.S)
FILE_REF = re.compile(r"`([A-Za-z0-9_]+/[A-Za-z0-9_/\.]+\.py)`")
CITE = re.compile(r"\[(\d+)\]")

problems: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)


def check_chars(text: str, path: Path) -> None:
    """Ищет символы из других письменностей — признак замены слов при вводе."""
    for i, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(
            r"[^\x00-\x7FЀ-ӿ‐-―‘’“”–—…«»°·•≈×≤≥→←⇒∈≠−]", line
        ):
            bad = m.group(0)
            fail(
                f"{path.name}:{i}: посторонний символ {bad!r} (U+{ord(bad):04X}) — "
                f"«{line[max(0, m.start() - 30):m.start() + 30].strip()}»"
            )
            break


def check_sections(text: str, path: Path, contract: dict) -> None:
    required = contract.get("sections", [])
    prefix = contract.get("section_prefix_match", False)
    headings = re.findall(r"(?m)^(#{2,3})\s+(.+)$", text)
    for section in required:
        wanted = section.lstrip("#").strip()
        found = any(
            h.strip() == wanted or (prefix and h.strip().startswith(wanted))
            for _, h in headings
        )
        if not found:
            fail(f"{path.name}: нет секции «{section}»")


DETAILS_OPEN = re.compile(r"<details\b[^>]*>", re.I)
DETAILS_CLOSE = re.compile(r"</details>", re.I)


def check_details(text: str, path: Path, contract: dict) -> None:
    if not contract.get("details_required", True):
        return
    opens = DETAILS_OPEN.findall(text)
    closes = DETAILS_CLOSE.findall(text)
    if not opens:
        fail(f"{path.name}: нет скрытых ответов (<details>)")
    if len(opens) != len(closes):
        fail(f"{path.name}: непарные <details> — открыто {len(opens)}, закрыто {len(closes)}")
    for tag in opens:
        if re.search(r"\bopen\b", tag, re.I):
            fail(f"{path.name}: <details> с атрибутом open — ответы должны быть скрыты")
        if "markdown=" not in tag:
            fail(f"{path.name}: нет markdown=\"1\" внутри <details>")
    for block in re.findall(r"<details\b.*?</details>", text, re.S | re.I):
        if not re.search(r"<summary>.*?</summary>", block, re.S | re.I):
            fail(f"{path.name}: блок <details> без закрытого <summary>")


def check_citations(
    text: str, path: Path, valid_ids: set[str], max_per_line: int = 3
) -> None:
    ids = set(CITE.findall(text))
    unknown = sorted(i for i in ids if i not in valid_ids)
    if unknown:
        fail(f"{path.name}: ссылки на несуществующие источники: {unknown}")

    # Ограничение «не больше трёх ссылок» относится к прозе: перечни
    # источников в конце главы это не касается, там номера идут списком.
    prose = text
    sources_section = "## Источники главы"
    if sources_section in text:
        prose = text.split(sources_section, 1)[0]
    for line in prose.split("\n"):
        found = CITE.findall(line)
        if len(found) > max_per_line:
            fail(f"{path.name}: больше {max_per_line} ссылок в строке: {line[:70]}")


def _parses(code: str) -> bool:
    """Проверяет, что блок кода разбирается Python'ом.

    Фрагменты методов часто приводят с отступом класса — такой блок не
    разбирается как модуль, но разбирается после снятия общего отступа.
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        pass
    lines = [line for line in code.split("\n") if line.strip()]
    if not lines:
        return True
    indent = min(len(line) - len(line.lstrip()) for line in lines)
    if indent == 0:
        return False
    dedented = "\n".join(line[indent:] for line in lines)
    try:
        ast.parse(dedented)
        return True
    except SyntaxError:
        return False


def check_code(text: str, path: Path, package_files: set[str]) -> None:
    for i, block in enumerate(CODE_BLOCK.findall(text), 1):
        if not _parses(block):
            fail(f"{path.name}: кодовый блок {i} не парсится как Python")
        if "TODO" in block or "FIXME" in block:
            fail(f"{path.name}: в коде остались TODO/FIXME")
    for ref in FILE_REF.findall(text):
        if ref not in package_files:
            fail(f"{path.name}: ссылка на несуществующий файл пакета: {ref}")


def _count_questions(section: str) -> int:
    """Считает вопросы в секции.

    Элементы нумерованного или маркированного списка могут быть перенесены
    на несколько строк, поэтому сначала склеиваем весь текст в одну строку,
    а затем делим его по маркерам элементов списка.
    """
    flat = " ".join(line.strip() for line in section.split("\n"))
    flat = re.sub(r"\s+", " ", flat)
    items = re.split(r"(?=(?:\d+[.)]|[-*])\s+)", flat)
    count = 0
    for item in items:
        item = item.strip()
        if re.match(r"^(?:\d+[.)]|[-*])\s+\S", item) and item.endswith("?"):
            count += 1
    return count


def _strip_docstrings(code: str) -> str:
    """Убирает содержимое docstring'ов, оставляя сами строки-разделители.

    В книге примеры сокращаются: длинные докстринги убираются, чтобы
    код помещался на страницу. Это допустимо, поэтому сравнение идёт по
    остальным строкам.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    lines = code.split("\n")
    drop: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr):
                value = body[0].value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    start = value.lineno - 1
                    end = value.end_lineno or value.lineno
                    drop.update(range(start, end))
    return "\n".join(
        line for index, line in enumerate(lines) if index not in drop
    )


def _is_subsequence(block_lines: list[str], source_lines: list[str]) -> bool:
    """Проверяет, что строки блока идут в исходнике подряд, в том же порядке.

    Между строками блока в исходнике могут быть пропущены строки (например,
    тело метода опущено) — это допустимо для сокращённых фрагментов.
    """
    position = 0
    for line in block_lines:
        while position < len(source_lines) and source_lines[position] != line:
            position += 1
        if position >= len(source_lines):
            return False
        position += 1
    return True


def check_code_matches_package(
    text: str, path: Path, package_sources: dict[str, str]
) -> None:
    """Проверяет, что каждый блок кода встречается в пакете.

    Книга обещает, что примеры — реальные фрагменты. Блок считается
    настоящим, если все его строки идут подряд в каком-то файле пакета
    (с учётом того, что сокращённые примеры могут опускать тела методов
    и опустошать докстринги).
    """
    stripped_sources = {
        name: _strip_docstrings(source) for name, source in package_sources.items()
    }
    source_line_sets = {
        name: [line.strip() for line in source.split("\n") if line.strip()]
        for name, source in stripped_sources.items()
    }

    for i, block in enumerate(CODE_BLOCK.findall(text), 1):
        stripped = _strip_docstrings(block)
        block_lines = [line.strip() for line in stripped.split("\n") if line.strip()]
        if not block_lines:
            continue

        found = False
        for name, source_lines in source_line_sets.items():
            if _is_subsequence(block_lines, source_lines):
                found = True
                break

        if not found:
            # Блок может собирать строки из разных файлов пакета (например,
            # импорт из __init__ и вызов из demo.py). Тогда требуем, чтобы
            # каждая строка блока встречалась где-то в пакете: это гарантирует,
            # что API не выдуман.
            all_lines: set[str] = set()
            for source_lines in source_line_sets.values():
                all_lines.update(source_lines)
            if all(block_lines) and all(line in all_lines for line in block_lines):
                found = True

        if not found:
            fail(
                f"{path.name}: кодовый блок {i} не найден в пакете — "
                f"это не реальный фрагмент "
                f"(начало: {block_lines[0][:60]!r})"
            )


def check_appendix(path: Path, text: str, valid_ids: set[str]) -> None:
    """Приложения: нет обязательных секций, но есть свои правила."""
    check_chars(text, path)
    check_citations(text, path, valid_ids, max_per_line=99)

    for i, block in enumerate(CODE_BLOCK.findall(text), 1):
        try:
            ast.parse(block)
        except SyntaxError as exc:
            fail(f"{path.name}: кодовый блок {i} не парсится — {exc}")

    if path.name.startswith("app-d-sources"):
        for sid in re.findall(r"^### \[(\d+)\]", text, re.M):
            if sid not in valid_ids:
                fail(f"{path.name}: в перечне есть неизвестный источник [{sid}]")


def check_questions(text: str, path: Path, contract: dict) -> None:
    """В «Проверь себя» должно быть заданное число вопросов."""
    rules = contract.get("questions") or {}
    if not rules:
        return
    header = "## Проверь себя"
    if header not in text:
        fail(f"{path.name}: нет секции «{header}»")
        return
    section = text.split(header, 1)[1]
    for stop in ("## Размышления", "## Частые ошибки", "## Что дальше"):
        if stop in section:
            section = section.split(stop, 1)[0]
            break
    questions = _count_questions(section)
    low = rules.get("min", 0)
    high = rules.get("max", 99)
    if questions < low:
        fail(f"{path.name}: в «Проверь себя» всего {questions} вопросов (нужно {low}–{high})")
    if questions > high:
        fail(f"{path.name}: в «Проверь себя» {questions} вопросов (максимум {high})")
    if not contract.get("answers_inline", False) and re.search(r"Ответ\s*[:.]", section):
        fail(f"{path.name}: в «Проверь себя» есть ответы — их быть не должно")


def check_thoughts(text: str, path: Path, contract: dict) -> None:
    rules = contract.get("thoughts") or {}
    if not rules:
        return
    if "## Размышления" not in text:
        fail(f"{path.name}: нет секции «## Размышления»")
        return
    section = text.split("## Размышления", 1)[1]
    for stop in ("## Что дальше", "## Частые ошибки"):
        if stop in section:
            section = section.split(stop, 1)[0]
            break
    details = re.findall(r"<details.*?</details>", section, re.S)
    low = rules.get("min", 0)
    high = rules.get("max", 99)
    if len(details) < low:
        fail(f"{path.name}: в «Размышления» {len(details)} скрытых ответов (нужно {low}–{high})")
    if len(details) > high:
        fail(f"{path.name}: в «Размышления» {len(details)} скрытых ответов (максимум {high})")
    questions = [
        line for line in section.split("\n")
        if line.strip().endswith("?") and not line.strip().startswith("<")
    ]
    if len(questions) < low:
        fail(f"{path.name}: в «Размышления» мало вопросов")


def main() -> int:
    parser = argparse.ArgumentParser(description="Линтер глав книги")
    parser.add_argument("--book", required=True, help="slug или путь к книге")
    parser.add_argument("--json", action="store_true", help="вывод в JSON")
    args = parser.parse_args()

    book: Book = load_book(args.book)
    contract = book.contract

    quotes_path = book.src / "quotes.json"
    valid_ids: set[str] = set()
    if quotes_path.exists():
        valid_ids = set(json.loads(quotes_path.read_text(encoding="utf-8")).keys())
    elif contract.get("citations"):
        print(f"ОШИБКА: нет банка источников {quotes_path}")
        return 1

    code_dir = book.code_dir()
    package_name = contract.get("code", {}).get("package", "")
    package_files: set[str] = set()
    package_sources: dict[str, str] = {}
    if code_dir and package_name:
        package_root = code_dir / package_name
        if package_root.exists():
            package_files = {
                p.relative_to(code_dir).as_posix() for p in package_root.rglob("*.py")
            }
            package_sources = {
                p.relative_to(code_dir).as_posix(): p.read_text(encoding="utf-8")
                for p in package_root.rglob("*.py")
            }
        else:
            print(f"ОШИБКА: нет пакета {package_root}")
            return 1

    chapters = book.chapter_files()
    appendices = book.appendix_files()
    if not chapters:
        print("Нет ни одной главы.")
        return 1

    print(f"Проверяю {len(chapters)} глав(ы) книги «{book.title}» в {book.chapters}\n")

    for path in chapters:
        if not path.exists():
            fail(f"{path.name}: файл главы не найден (проверь оглавление)")
            continue
        text = path.read_text(encoding="utf-8")
        check_chars(text, path)
        check_sections(text, path, contract)
        check_details(text, path, contract)
        if contract.get("citations"):
            check_citations(text, path, valid_ids)
        if package_files:
            check_code(text, path, package_files)
            if contract.get("code", {}).get("must_match_package", True):
                check_code_matches_package(text, path, package_sources)
        check_questions(text, path, contract)
        check_thoughts(text, path, contract)

    for path in appendices:
        if not path.exists():
            fail(f"{path.name}: файл приложения не найден (проверь оглавление)")
            continue
        check_appendix(path, path.read_text(encoding="utf-8"), valid_ids)

    if args.json:
        print(json.dumps({"book": book.slug, "problems": problems}, ensure_ascii=False, indent=2))
    elif problems:
        print(f"Проблем: {len(problems)}\n")
        for p in problems:
            print(f"  ✗ {p}")
    else:
        print("Все проверки пройдены.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
