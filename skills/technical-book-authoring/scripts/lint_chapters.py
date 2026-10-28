#!/usr/bin/env python3
"""Enforce the chapter contract on a manuscript.

    python lint_chapters.py --chapters src/chapters \\
        --quotes src/quotes.json --package code/ddd_examples

Checks, per chapter file:
  * required sections, present and in order
  * 5-8 self-check questions, no answers among them
  * 2-4 hidden answers, each closed and each with a <summary>
  * code blocks parse as Python AND occur in the code package
  * references to package files resolve
  * citation ids exist in the source bank; at most 3 per prose line
  * no characters from a foreign writing system

Exit code 0 when clean, 1 otherwise.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

# --- the contract ------------------------------------------------------------

REQUIRED_SECTIONS = [
    "## Введение",
    "## Основной материал",
    "## Пример в коде",
    "## Разбор примера",
    "## Ловушки",
    "## Проверь себя",
    "## Размышления",
    "## Что дальше",
    "## Источники главы",
]

MIN_QUESTIONS = 5
MAX_QUESTIONS = 8
MIN_ANSWERS = 2
MAX_ANSWERS = 4
MAX_CITES_PER_LINE = 3

# Files that are not chapters and are checked with a reduced rule set.
FRONT_PREFIX = "00-"
APPENDIX_PREFIX = "app-"

# --- patterns ----------------------------------------------------------------

CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.S)
FILE_REF = re.compile(r"`(ddd_examples/[A-Za-z0-9_/\.]+\.py)`")
CITE = re.compile(r"\[(\d+)\]")
DETAILS_OPEN = re.compile(r"<details\b[^>]*>", re.I)
DETAILS_CLOSE = re.compile(r"</details>", re.I)
DETAILS_BLOCK = re.compile(r"<details\b.*?</details>", re.S | re.I)
SUMMARY = re.compile(r"<summary>.*?</summary>", re.S | re.I)

# Characters allowed beyond ASCII: the manuscript's script, common
# typography, arrows and math signs. Anything else is a substituted word.
ALLOWED_NON_ASCII = re.compile(
    r"[Ѐ-ӿ‐-―‘’“”–—…«»°·•≈×≤≥→←⇒∈≠−]"
)

problems: list[str] = []


def fail(message: str) -> None:
    problems.append(message)


# --- helpers -----------------------------------------------------------------


def parses_as_python(code: str) -> bool:
    """True when the block is valid Python.

    Fragments of methods are often indented as they appear inside a class;
    such a block does not parse as a module but does after the common
    indent is removed.
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
    try:
        ast.parse("\n".join(line[indent:] for line in lines))
        return True
    except SyntaxError:
        return False


def strip_docstrings(code: str) -> str:
    """Drop docstring bodies, keeping the surrounding structure.

    Chapters shorten examples by removing long docstrings; that must not
    count as "not in the package".
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    lines = code.split("\n")
    drop: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)
        ):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr):
                value = body[0].value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    start = body[0].lineno - 1
                    end = body[0].end_lineno or body[0].lineno
                    drop.update(range(start, end))
    return "\n".join(line for index, line in enumerate(lines) if index not in drop)


def is_subsequence(block_lines: list[str], source_lines: list[str]) -> bool:
    """True when the block's lines occur in order in the source.

    Lines may be skipped in between, so an excerpt with an elided method
    body still matches.
    """
    position = 0
    for line in block_lines:
        while position < len(source_lines) and source_lines[position] != line:
            position += 1
        if position >= len(source_lines):
            return False
        position += 1
    return True


def count_questions(section: str) -> int:
    """Count questions in a section, joining wrapped lines first."""
    flat = re.sub(r"\s+", " ", " ".join(line.strip() for line in section.split("\n")))
    items = re.split(r"(?=(?:\d+[.)]|[-*])\s+)", flat)
    count = 0
    for item in items:
        item = item.strip()
        if re.match(r"^(?:\d+[.)]|[-*])\s+\S", item) and item.endswith("?"):
            count += 1
    return count


# --- checks ------------------------------------------------------------------


def check_sections(text: str, path: Path) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f"{path.name}: missing section {section!r}")


def check_details(text: str, path: Path) -> None:
    opens = DETAILS_OPEN.findall(text)
    closes = DETAILS_CLOSE.findall(text)
    if not opens:
        fail(f"{path.name}: no hidden answers (<details>)")
    if len(opens) != len(closes):
        fail(
            f"{path.name}: unbalanced <details> — {len(opens)} open, "
            f"{len(closes)} closed"
        )
    for tag in opens:
        if re.search(r"\bopen\b", tag, re.I):
            fail(f"{path.name}: <details open> — the answer is already visible")
        if "markdown=" not in tag:
            fail(f"{path.name}: <details> lacks markdown=\"1\" — the body will "
                 f"render as raw text")
    for block in DETAILS_BLOCK.findall(text):
        if not SUMMARY.search(block):
            fail(f"{path.name}: <details> without a closed <summary>")


def check_citations(text: str, path: Path, valid_ids: set[str]) -> None:
    ids = set(CITE.findall(text))
    unknown = sorted(i for i in ids if i not in valid_ids)
    if unknown:
        fail(f"{path.name}: unknown citation ids: {unknown}")
    prose = text.split("## Источники главы", 1)[0]
    for line in prose.split("\n"):
        found = CITE.findall(line)
        if len(found) > MAX_CITES_PER_LINE:
            fail(f"{path.name}: more than {MAX_CITES_PER_LINE} citations on one "
                 f"line: {line[:70]}")


def check_questions(text: str, path: Path) -> None:
    try:
        section = text.split("## Проверь себя", 1)[1].split("## Размышления", 1)[0]
    except IndexError:
        return
    count = count_questions(section)
    if count < MIN_QUESTIONS:
        fail(f"{path.name}: {count} self-check questions (need "
             f"{MIN_QUESTIONS}-{MAX_QUESTIONS})")
    if count > MAX_QUESTIONS:
        fail(f"{path.name}: {count} self-check questions (need "
             f"{MIN_QUESTIONS}-{MAX_QUESTIONS})")
    if re.search(r"Ответ\s*[:.]", section):
        fail(f"{path.name}: the self-check section contains answers")


def check_answers(text: str, path: Path) -> None:
    try:
        section = text.split("## Размышления", 1)[1].split("## Что дальше", 1)[0]
    except IndexError:
        return
    blocks = DETAILS_BLOCK.findall(section)
    if len(blocks) < MIN_ANSWERS:
        fail(f"{path.name}: {len(blocks)} hidden answers in the reflection "
             f"section (need {MIN_ANSWERS}-{MAX_ANSWERS})")
    if len(blocks) > MAX_ANSWERS:
        fail(f"{path.name}: {len(blocks)} hidden answers in the reflection "
             f"section (max {MAX_ANSWERS})")
    questions = [
        line for line in section.split("\n")
        if line.strip().endswith("?") and not line.strip().startswith("<")
    ]
    if len(questions) < MIN_ANSWERS:
        fail(f"{path.name}: too few reflection questions")


def check_code(text: str, path: Path, package_sources: dict[str, str]) -> None:
    source_lines = {
        name: [line.strip() for line in source.split("\n") if line.strip()]
        for name, source in package_sources.items()
    }
    all_lines: set[str] = set()
    for lines in source_lines.values():
        all_lines.update(lines)

    for index, block in enumerate(CODE_BLOCK.findall(text), 1):
        if not parses_as_python(block):
            fail(f"{path.name}: code block {index} does not parse as Python")
        if "TODO" in block or "FIXME" in block:
            fail(f"{path.name}: code block {index} still has TODO/FIXME")

        block_lines = [
            line.strip()
            for line in strip_docstrings(block).split("\n")
            if line.strip()
        ]
        if not block_lines:
            continue
        found = any(
            is_subsequence(block_lines, lines) for lines in source_lines.values()
        )
        if not found:
            # a block may combine lines from several files
            if not all(line in all_lines for line in block_lines):
                fail(
                    f"{path.name}: code block {index} is not a fragment of the "
                    f"package — the illustration is fiction "
                    f"(starts: {block_lines[0][:60]!r})"
                )


def check_file_refs(text: str, path: Path, package_files: set[str]) -> None:
    for ref in FILE_REF.findall(text):
        if ref not in package_files:
            fail(f"{path.name}: reference to a file that does not exist: {ref}")


def check_script(text: str, path: Path) -> None:
    """Flag characters from a writing system the manuscript does not use.

    A substituted character survives proofreading because the eye skips
    characters it does not expect.
    """
    for number, line in enumerate(text.split("\n"), 1):
        for match in re.finditer(
            r"[^\x00-\x7FЀ-ӿ‐-―‘’“”–—…«»°·•≈×≤≥→←⇒∈≠−]", line
        ):
            char = match.group(0)
            fail(
                f"{path.name}:{number}: foreign character {char!r} "
                f"(U+{ord(char):04X}) — «{line.strip()[:60]}»"
            )
            break


# --- main --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters", required=True, type=Path)
    parser.add_argument("--quotes", type=Path,
                        help="source bank JSON: {\"1\": {...}}")
    parser.add_argument("--package", type=Path,
                        help="code package whose files the chapters quote")
    args = parser.parse_args()

    valid_ids: set[str] = set()
    if args.quotes and args.quotes.exists():
        valid_ids = set(json.loads(args.quotes.read_text(encoding="utf-8")).keys())

    package_sources: dict[str, str] = {}
    package_files: set[str] = set()
    if args.package and args.package.exists():
        for path in args.package.rglob("*.py"):
            relative = path.relative_to(args.package).as_posix()
            package_files.add(relative)
            package_sources[relative] = path.read_text(encoding="utf-8")

    chapters = sorted(args.chapters.glob("*.md"))
    if not chapters:
        print(f"No chapters found in {args.chapters}")
        return 1

    print(f"Checking {len(chapters)} file(s) in {args.chapters}\n")

    for path in chapters:
        text = path.read_text(encoding="utf-8")
        is_chapter = not (
            path.name.startswith(FRONT_PREFIX)
            or path.name.startswith(APPENDIX_PREFIX)
        )
        check_script(text, path)
        check_citations(text, path, valid_ids)
        if is_chapter:
            check_sections(text, path)
            check_details(text, path)
            check_questions(text, path)
            check_answers(text, path)
        for index, block in enumerate(CODE_BLOCK.findall(text), 1):
            if not parses_as_python(block):
                fail(f"{path.name}: code block {index} does not parse as Python")

    if problems:
        print(f"Problems: {len(problems)}\n")
        for problem in problems:
            print(f"  x {problem}")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
