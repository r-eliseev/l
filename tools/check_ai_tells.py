"""Линтер AI-признаков: ловит в тексте книги следы машинного происхождения.

Источники признаков: «Wikipedia: Signs of AI writing» (WikiProject AI
Cleanup) и навык `humanizer`. Линтер ловит то, что ловится механически:
слова-маркеры, чрезмерное форматирование, конструкции вроде «не только X,
но и Y», титульный регистр в английских заголовках.

Русский текст — основной: у признаков есть русские эквиваленты, и только
они срабатывают на русских главах. Английские маркеры проверяются там, где
есть английский текст без кириллицы.

Что линтер намеренно не ловит:

- английские слова внутри русских цитат «…» — там они законны;
- ровный ритм, наигранная уверенность, «морализирующий» тон — это ловит
  ревью глазами, навык `humanizer`.

Пороги правятся под конкретную книгу в `books/<slug>/book.json`, секция
`ai_tells`.

Запуск:
    python tools/check_ai_tells.py --book ddd-praktika
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bookmeta import load_book  # noqa: E402

# ---------------------------------------------------------------------------
# Пороги по умолчанию
# ---------------------------------------------------------------------------

DEFAULTS = {
    # Пороги — эвристика, а не результат корпусного замера: их правят под
    # конкретную книгу в book.json, секция ai_tells. Значения по умолчанию
    # отобраны так, чтобы ловить явные перекосы, а не стиль автора.
    "em_dash_per_1k_words": 45,
    "bold_per_1k_words": 25,
    "inline_header_lists": 8,
    "title_case_headings": 0,
    "emoji": 0,
    "curly_double_quotes": 0,
    # Частотные маркеры: сколько раз оборот допустимо в одном файле.
    # «freq»-маркер срабатывает, только когда счётчик превысил этот порог.
    "freq_limit": 2,
}

# ---------------------------------------------------------------------------
# Маркеры
# ---------------------------------------------------------------------------

# Каждый маркер — тройка (шаблон, подпись, режим):
#   "once" — оборот сам по себе характерен для машинного текста, срабатывает
#            при первом же появлении;
#   "freq" — оборот сам по себе допустим в русской прозе, но частым быть
#            не должен: срабатывает, только когда превышен порог частоты.
#
# Пороги частотных маркеров — в DEFAULT_FREQ_LIMITS.
RU_MARKERS: list[tuple[str, str, str]] = [
    (r"подч[её]ркивает значимость", "преувеличение значимости", "once"),
    (r"олицетворяет\b", "декоративная символика", "once"),
    (r"символизирует\b", "декоративная символика", "once"),
    (r"играет (?:ключевую|важную|центральную|значительную) роль", "преувеличение значимости", "once"),
    (r"зада[её]т тон", "штамп «задаёт тон»", "once"),
    (r"закрепляет(?:ет)? (?:тенденцию|позицию|практику)", "штамп", "once"),
    (r"переломный момент", "штамп «переломный момент»", "once"),
    (r"неотъемлем(?:ая|ой|ую) часть", "штамп «неотъемлемая часть»", "freq"),
    (r"краеугольн(?:ый|ого) камень", "штамп «краеугольный камень»", "once"),
    (r"воплоща(?:ет|я) (?:в себе|собой)", "штамп «воплощает»", "freq"),
    (r"формирует? (?:ландшафт|экосистему|контур)", "штамп", "once"),
    (r"независим(?:ое|ые) освещение", "нарочитая «известность»", "once"),
    (r"медиа(?:а)? (?:издания|ресурсы|каналы)", "нарочитая «известность»", "once"),
    (r"активн(?:ое|ая|ую) присутствие в соцсетях", "нарочитая «известность»", "once"),
    (r"\bподч[её]ркивая\b", "пустая причастная конструкция", "freq"),
    (r"\bобеспечивая\b", "пустая причастная конструкция", "freq"),
    (r"\bотражая\b", "пустая причастная конструкция", "freq"),
    (r"\bспособствуя\b", "пустая причастная конструкция", "freq"),
    (r"\bдемонстрируя\b", "пустая причастная конструкция", "freq"),
    (r"\bуглубляя\b", "пустая причастная конструкция", "freq"),
    (r"\bсодействуя\b", "пустая причастная конструкция", "freq"),
    (r"\bнаполняя\b", "пустая причастная конструкция", "freq"),
    (r"\bуникальн(?:ый|ая|ое|ые)\b", "рекламный тон (уникальный)", "freq"),
    (r"\bневероятн(?:ый|ая|ое|ые)\b", "рекламный тон", "freq"),
    (r"\bпоразительн(?:ый|ая|ое|ые)\b", "рекламный тон", "freq"),
    (r"\bбезупречн(?:ый|ая|ое|ые)\b", "рекламный тон", "once"),
    (r"\bвпечатляющ(?:ий|ая|ее)\b", "рекламный тон", "freq"),
    (r"\bв самом сердце\b", "рекламный оборот", "once"),
    (r"\bнадеж(?:ный|ая|ное) решение\b", "рекламный тон", "once"),
    (r"\bмощн(?:ый|ая|ое) инструмент\b", "рекламный тон", "once"),
    (r"эксперты счита(?:ют|ли)", "размытая атрибуция", "once"),
    (r"исследования показыва(?:ют|ли)", "размытая атрибуция", "once"),
    (r"наблюдатели отмеча(?:ют|ли)", "размытая атрибуция", "once"),
    (r"отраслев(?:ые|ых) отч[её]т(?:а|ов)?", "размытая атрибуция", "once"),
    (r"многие полага(?:ют|ли)", "размытая атрибуция", "once"),
    (r"по мнению (?:экспертов|специалистов|аналитиков)", "размытая атрибуция", "once"),
    (r"\bландшафт(?:а|е|ом|у)?\b", "словарь AI (ландшафт)", "freq"),
    (r"\bэкосистем(?:а|ы|е|у)?\b", "словарь AI (экосистема)", "freq"),
    (r"\bсинерги(?:я|и|ю)\b", "словарь AI (синергия)", "once"),
    (r"\bтрансформац(?:ия|ию|ии)\b", "словарь AI (трансформация)", "freq"),
    (r"\bимплементац(?:ия|ию|ии)\b", "словарь AI (имплементация)", "once"),
    (r"\bвизуализац(?:ия|ию|ии) данных\b", "словарь AI", "once"),
    (r"\bвстроенн(?:ый|ая|ое) (?:воркфлоу|процесс)\b", "словарь AI", "once"),
    (r"\bкомплексн(?:ый|ое|ая) решение\b", "словарь AI", "once"),
    (r"\bгибк(?:ий|ая|ое|ие) подход\b", "словарь AI", "once"),
    (r"\bвыступа(?:ет|ют) (?:как|в качестве)\b", "связка вместо глагола", "once"),
    (r"\bпредставля(?:ет|ют) собой\b", "связка вместо глагола", "once"),
    (r"\bслужит (?:как|для)\b", "связка вместо глагола", "freq"),
    (r"\bдавайте (?:разбер|рассмотр|изучи|пройд|посмотр)", "указание на переход", "once"),
    (r"\bтеперь (?:давайте|разбер|рассмотр|перейд)", "указание на переход", "freq"),
    (r"\bпереходим к\b", "указание на переход", "once"),
    (r"\bвот (?:что|как) (?:важно|нужно|стоит|получается)", "указание на переход", "once"),
    (r"надеюсь, (?:это|вам) (?:поможет|пригодится)", "обрывок переписки", "once"),
    (r"\bдайте знать\b", "обрывок переписки", "once"),
    (r"\bесли хотите, могу\b", "обрывок переписки", "once"),
    (r"^\s*(?:Конечно|Разумеется)[!.]", "обрывок переписки", "once"),
    (r"вы абсолютно правы", "обрывок переписки", "once"),
    (r"\bвсё в порядке\b", "успокоительная вставка", "freq"),
    (r"\bне переживайте\b", "успокоительная вставка", "once"),
    (r"\bэто нормально\b", "успокоительная вставка", "freq"),
    (r"\bне стесняйтесь\b", "успокоительная вставка", "once"),
    (r"\bв заключение\b", "штамп «в заключение»", "freq"),
    (r"\bподводя итог\b", "штамп «подводя итог»", "once"),
    (r"\bв будущем (?:это |этот |данный )?(?:принесёт|откроет|позволит)", "штамп «в будущем…»", "once"),
    (r"\bвот в чём дело\b", "рекламная рамка", "once"),
    (r"\bнастоящий вопрос\b", "рекламная рамка", "once"),
    (r"\bв конечном счёте важно\b", "рекламная рамка", "once"),
    (r"\bвопрос в том, что\b", "рекламная рамка", "freq"),
    (r"отражает более широк", "обобщение до «широкого контекста»", "freq"),
]

# Английский текст (когда в абзаце нет кириллицы).
EN_MARKERS: list[tuple[str, str, str]] = [
    (r"is a testament to", "преувеличение значимости (testament to)", "once"),
    (r"serves as a", "связка вместо глагола (serves as)", "once"),
    (r"stands as a", "связка вместо глагола (stands as)", "once"),
    (r"\bkey role\b", "преувеличение значимости (key role)", "once"),
    (r"\bpivotal\b", "преувеличение значимости (pivotal)", "once"),
    (r"\bcrucial\b", "преувеличение значимости (crucial)", "once"),
    (r"reflects broader", "обобщение до «широкого контекста»", "freq"),
    (r"symbolizing", "декоративная символика (symbolizing)", "once"),
    (r"evolving landscape", "штамп «evolving landscape»", "once"),
    (r"setting the stage for", "штамп (setting the stage for)", "once"),
    (r"marks a shift", "штамп (marks a shift)", "once"),
    (r"deeply rooted", "штамп (deeply rooted)", "once"),
    (r"independent coverage", "нарочитая «известность»", "once"),
    (r"media outlets", "нарочитая «известность»", "once"),
    (r"\bhighlighting\b", "пустая причастная конструкция", "freq"),
    (r"\bunderscoring\b", "пустая причастная конструкция", "freq"),
    (r"\bensuring\b", "пустая причастная конструкция", "freq"),
    (r"\breflecting\b", "пустая причастная конструкция", "freq"),
    (r"\bcontributing to\b", "пустая причастная конструкция", "freq"),
    (r"\bfostering\b", "пустая причастная конструкция", "freq"),
    (r"\bencompassing\b", "пустая причастная конструкция", "freq"),
    (r"\bshowcasing\b", "пустая причастная конструкция", "freq"),
    (r"\bvibrant\b", "рекламный тон (vibrant)", "once"),
    (r"\bboasts\b", "рекламный тон (boasts)", "once"),
    (r"\bprofound\b", "рекламный тон (profound)", "once"),
    (r"\bnestled\b", "рекламный тон (nestled)", "once"),
    (r"\bgroundbreaking\b", "рекламный тон (groundbreaking)", "once"),
    (r"industry reports", "размытая атрибуция", "once"),
    (r"experts argue", "размытая атрибуция", "once"),
    (r"some critics argue", "размытая атрибуция", "once"),
    (r"\bdelve\b", "словарь AI (delve)", "once"),
    (r"\btapestry\b", "словарь AI (tapestry)", "once"),
    (r"\binterplay\b", "словарь AI (interplay)", "once"),
    (r"\bintricate\b", "словарь AI (intricate)", "once"),
    (r"\balign with\b", "словарь AI (align with)", "once"),
    (r"\badditionally\b", "словарь AI (additionally)", "freq"),
    (r"\bin conclusion\b", "словарь AI (in conclusion)", "freq"),
    (r"\bin summary\b", "словарь AI (in summary)", "freq"),
    (r"\bat its core\b", "рекламная рамка", "once"),
    (r"\bthe real question\b", "рекламная рамка", "once"),
    (r"\bdeep dive\b", "штамп (deep dive)", "once"),
    (r"\bgame-changer\b", "штамп (game-changer)", "once"),
    (r"i hope this helps", "обрывок переписки", "once"),
    (r"\blet me know\b", "обрывок переписки", "once"),
    (r"of course!", "обрывок переписки", "once"),
    (r"would you like", "обрывок переписки", "once"),
    (r"as of my last", "оговорка о знаниях модели", "once"),
    (r"based on available information", "размытая оговорка", "once"),
    (r"and that's okay", "успокоительная вставка", "once"),
    (r"no shame in", "успокоительная вставка", "once"),
]

# Обороты-конструкции: ловятся по шаблону целиком.
PHRASE_MARKERS: list[tuple[str, str, str]] = [
    (r"не только [^.!?]{2,60}? но и", "контрастная пара «не только… но и»", "freq"),
    (r"не просто [^.!?]{2,60}? а", "контрастная пара «не просто… а»", "freq"),
    (r"не [^.!?]{2,40}? а [^.!?]{2,40}? а ", "контрастная пара «не… а… а»", "freq"),
    (r"от [^.!?]{2,40}? до [^.!?]{2,40}?, от", "ложный диапазон «от… до…, от…»", "freq"),
    (r"несмотря на (?:то что|ряд |множество )", "шаблонная секция «вызовов»", "freq"),
    (r"в мире, где ", "маркетинговый оборот", "once"),
    (r"в наши дни ", "маркетинговый оборот", "once"),
    (r"в современном мире", "маркетинговый оборот", "once"),
    (r"двигаясь вперёд", "маркетинговый оборот", "once"),
    (r"в конечном итоге всё", "штамп «в конечном итоге всё»", "once"),
    (r"стоит отметить, что", "штамп «стоит отметить»", "once"),
    (r"важно понимать, что", "штамп «важно понимать»", "once"),
    (r"имеет смысл рассмотреть", "штамп «имеет смысл рассмотреть»", "once"),
]

# ---------------------------------------------------------------------------
# Разбор текста
# ---------------------------------------------------------------------------

FENCE = re.compile(r"(?ms)^```.*?^```")
DETAILS = re.compile(r"(?ms)^<details.*?</details>")
HTML_TAG = re.compile(r"<[^>]+>")
LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
INLINE_CODE = re.compile(r"`[^`\n]+`")
RUSSIAN_QUOTE = re.compile(r"«[^»]*»")
BLOCKQUOTE = re.compile(r"(?m)^>.*$")
HEADING = re.compile(r"(?m)^#{1,6}\s+.*$")
TABLE_ROW = re.compile(r"(?m)^\s*\|.*$")
LIST_LINE = re.compile(r"(?m)^\s*(?:[-*+]|\d+[.)])\s+.*$")
BOLD = re.compile(r"\*\*[^*\n]+\*\*")
DEFINITION_BOLD = re.compile(r"(?m)^\*\*[^*\n]{1,80}\*\*\s+[—-]")
INLINE_HEADER = re.compile(r"(?m)^\s*[-*+]\s+\*\*[^*\n]{1,60}\*\*\s*:")
EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]"
)
CURLY_DOUBLE = re.compile(r"[\u201C\u201D]")
CYRILLIC = re.compile(r"[Ѐ-ӿ]")
# Титульный регистр: все слова с заглавной, включая короткие служебные
# (of, and, the, for…). Раскрытие термина вроде «IRSA (IAM Roles for
# Service Accounts)» под это не попадает: там строчные есть.
TITLE_CASE = re.compile(
    r"(?m)^#{2,4}\s+([A-Z][A-Za-z'’&-]*"
    r"(?:\s+(?:of|and|the|for|to|in|with|on|or|a|an|at|by)\s+[A-Za-z'’&-]+)"
    r"(?:\s+[A-Z][A-Za-z'’&-]*){1,})\s*$"
)


def prose(text: str) -> str:
    """Русская проза без разметки, кода, таблиц, списков и цитат."""
    text = FENCE.sub(" ", text)
    text = DETAILS.sub(" ", text)
    text = BLOCKQUOTE.sub(" ", text)
    text = TABLE_ROW.sub(" ", text)
    text = LIST_LINE.sub(" ", text)
    text = HEADING.sub(" ", text)
    text = HTML_TAG.sub(" ", text)
    text = LINK.sub(" ", text)
    text = INLINE_CODE.sub(" ", text)
    text = RUSSIAN_QUOTE.sub(" ", text)
    return text


def prose_lines(text: str) -> list[str]:
    """Строки прозы: без заголовков, списков, таблиц и цитат."""
    out = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("|", ">", "#", "-", "*", "+")):
            continue
        if re.match(r"^\d+[.)]\s", stripped):
            continue
        out.append(stripped)
    return out


def scan_file(path: Path, limits: dict) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    findings: list[str] = []

    body = prose(raw)
    words = len(body.split())
    per_k = max(words / 1000, 1)

    em_dashes = body.count("—")
    limit = limits["em_dash_per_1k_words"]
    if em_dashes / per_k > limit:
        findings.append(
            f"тире «—»: {em_dashes} на {words} слов "
            f"({em_dashes / per_k:.0f} на 1000, порог {limit})"
        )

    bolds = len(BOLD.findall(body))
    # Глоссарий печатает термин жирным — это формат словаря, а не избыточное
    # подчёркивание. Такие строки не считаем.
    bolds = max(bolds - len(DEFINITION_BOLD.findall(raw)), 0)
    limit = limits["bold_per_1k_words"]
    if bolds / per_k > limit:
        findings.append(
            f"жирный шрифт: {bolds} ({bolds / per_k:.0f} на 1000 слов, "
            f"порог {limit})"
        )

    inline_headers = INLINE_HEADER.findall(raw)
    limit = limits["inline_header_lists"]
    if len(inline_headers) > limit:
        findings.append(
            f"списки с жирными подзаголовками: {len(inline_headers)} "
            f"(порог {limit})"
        )

    title_headings = TITLE_CASE.findall(raw)
    limit = limits["title_case_headings"]
    if len(title_headings) > limit:
        findings.append(
            f"английские заголовки в титульном регистре: {len(title_headings)} "
            f"(порог {limit})"
        )

    emoji = EMOJI.findall(raw)
    limit = limits["emoji"]
    if len(emoji) > limit:
        findings.append(f"эмодзи: {len(emoji)} (порог {limit})")

    curly = CURLY_DOUBLE.findall(raw)
    limit = limits["curly_double_quotes"]
    if len(curly) > limit:
        findings.append(
            f"«умные» двойные кавычки: {len(curly)} (порог {limit}) — "
            "в русском тексте используют «ёлочки»"
        )

    # Слова-маркеры: построчно, с учётом языка абзаца.
    #
    # Маркер режима "once" — сам по себе характерен для машинного текста:
    # достаточно одного появления. Маркер режима "freq" — обычный русский
    # оборот, который просто не должен встречаться слишком часто: такие
    # считаем и показываем, только когда порог превышен.
    freq_limit = limits.get("freq_limit", 2)
    freq_counts: dict[str, int] = {}
    freq_examples: dict[str, str] = {}

    for line in prose_lines(raw):
        markers = RU_MARKERS if CYRILLIC.search(line) else EN_MARKERS
        for pattern, label, mode in markers + PHRASE_MARKERS:
            if not re.search(pattern, line, re.I):
                continue
            if mode == "once":
                findings.append(f"{label}: «{line[:90]}»")
                break
            freq_counts[label] = freq_counts.get(label, 0) + 1
            freq_examples.setdefault(label, line[:90])
            break

    for label, count in sorted(freq_counts.items(), key=lambda kv: -kv[1]):
        if count > freq_limit:
            findings.append(
                f"{label}: {count} раз (порог {freq_limit}) — "
                f"«{freq_examples[label]}»"
            )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Линтер AI-признаков")
    parser.add_argument("--book", required=True, help="slug или путь к книге")
    parser.add_argument("--json", action="store_true", help="вывод в JSON (для CI)")
    args = parser.parse_args()

    book = load_book(args.book)
    limits = dict(DEFAULTS)
    limits.update(book.manifest.get("ai_tells", {}))

    files = [p for p in book.all_content_files() if p.exists()]

    report: dict[str, list[str]] = {}
    total = 0
    for path in files:
        findings = scan_file(path, limits)
        if findings:
            report[path.name] = findings
            total += len(findings)

    if args.json:
        print(
            json.dumps(
                {"book": book.slug, "findings": report}, ensure_ascii=False, indent=2
            )
        )
    else:
        for name, findings in report.items():
            print(f"\n{name}: {len(findings)} замечаний")
            for finding in findings:
                print(f"  ! {finding}")
        print()
        if total:
            print(f"Замечаний: {total}")
            print(
                "Метка не означает, что текст написан нейросетью: это подсказка, "
                "где стоит посмотреть глазами."
            )
        else:
            print("AI-признаков не найдено.")

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
