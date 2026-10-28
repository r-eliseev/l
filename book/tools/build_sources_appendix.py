"""Генерирует приложение «Источники» из ledger цитат.

Страница собирается механически: id → URL берётся из ledger, а не
переписывается руками, поэтому нумерация в книге и в ledger не разойдутся.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent


def hermes_home() -> Path:
    """Каталог Hermes: одинаково на Windows и Linux."""
    val = os.environ.get("HERMES_HOME", "").strip()
    if val:
        return Path(val)
    if os.name == "nt":
        return Path.home() / "AppData/Local/hermes"
    return Path.home() / ".hermes"


SP = (
    hermes_home()
    / "skills/research/grounded-citations/scripts/sources.py"
)

OUT = BOOK / "src" / "chapters" / "app-d-sources.md"

INTRO = """# Приложение Г. Источники

*Все утверждения о первоисточниках в книге снабжены номером в квадратных
скобках. Ниже — полный перечень источников с адресами и ключевыми
дословными цитатами, на которые опирается текст.*

*Цитаты приведены в том виде, в каком они звучат в оригинале, — чтобы можно
было проверить формулировку, не доверяя пересказу.*

"""


def load_ledger() -> dict | None:
    """Читает ledger цитат. None — если ledger недоступен (например, в CI)."""
    if not SP.exists():
        return None
    spec = importlib.util.spec_from_file_location("sources", SP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    path = mod.resolve_ledger_path(None)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ledger = load_ledger()
    if ledger is None:
        print(
            "Приложение «Источники» не пересобрано: ledger недоступен "
            f"({SP}). Ledger лежит вне репозитория, поэтому приложение "
            "обновляется только на машине автора. Существующий файл сохранён."
        )
        return
    sources = sorted(ledger["sources"], key=lambda s: s["id"])

    used = collect_used_ids()
    lines = [INTRO]

    lines.append("## Как читать ссылки\n")
    lines.append(
        "Номер в квадратных скобках после утверждения означает: это утверждение "
        "опирается на источник под этим номером в перечне ниже. Источники "
        "сгруппированы по типу — сначала первоисточники DDD, затем "
        "архитектурные материалы и практические ресурсы.\n"
    )

    groups = [
        ("Первоисточники DDD", lambda s: s["id"] in {1, 2, 16, 21, 22}),
        ("Классические эссе и паттерны", lambda s: s["id"] in {3, 4, 5, 27, 28, 29, 30}),
        ("Архитектурные руководства", lambda s: s["id"] in {7, 8, 9, 10, 23, 31, 32}),
        ("Практика и сообщество", lambda s: s["id"] in {6, 11, 12, 13, 14, 15, 18, 19, 20, 24, 25, 26}),
    ]

    assigned: set[int] = set()
    for title, predicate in groups:
        group = [s for s in sources if predicate(s) and s["id"] not in assigned]
        if not group:
            continue
        assigned.update(s["id"] for s in group)
        lines.append(f"## {title}\n")
        for s in group:
            lines.append(f"### [{s['id']}] {s.get('title') or s['url']}\n")
            lines.append(f"{s['url']}\n")
            quotes = s.get("quotes", [])
            if quotes:
                lines.append("Ключевые формулировки:\n")
                for q in quotes:
                    text = q["text"].replace("\n", " ").strip()
                    lines.append(f"> «{text}»\n")
            else:
                lines.append("Источник используется для общих сведений без прямого цитирования.\n")
            lines.append("")

    rest = [s for s in sources if s["id"] not in assigned]
    if rest:
        lines.append("## Прочие материалы\n")
        for s in rest:
            lines.append(f"- **[{s['id']}]** {s.get('title') or ''} — {s['url']}")
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

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Записано: {OUT} ({len(sources)} источников)")


def collect_used_ids() -> set[int]:
    """Собирает номера источников, реально встречающихся в главах."""
    used: set[int] = set()
    for path in (BOOK / "src" / "chapters").glob("*.md"):
        if path.name == "app-d-sources.md":
            continue
        text = path.read_text(encoding="utf-8")
        used.update(int(x) for x in re.findall(r"\[(\d+)\]", text))
    return used


if __name__ == "__main__":
    main()
