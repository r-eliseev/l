# Domain-Driven Design на практике

Исходники книги и её сборка. Книга читается как EPUB; всё, что в ней показано
в коде, лежит рядом и запускается.

```
books/ddd-praktika/
  src/            исходники глав
    STYLE.md      контракт: формат главы, стиль, правила цитирования
    structure.json  оглавление: части, главы, приложения
    quotes.json   банк источников (id → url, title, цитаты)
    chapters/     Markdown-главы
  code/           пакет с примерами и тестами
    ddd_examples/ домен: shared, subscriptions, billing, strategic, anemic
    tests/        unittest-тесты
  dist/           готовый EPUB и превью
```

## Сборка

```bash
BOOK=ddd-praktika

# 1. код должен работать
cd books/$BOOK/code && python -m unittest discover -s tests -v && cd -

# 2. главы должны соответствовать контракту
python tools/lint_book.py --book $BOOK

# 3. цитаты дословны и привязаны верно
python tools/check_quotes.py --book $BOOK

# 4. текст без машинных следов
python tools/check_ai_tells.py --book $BOOK

# 5. пересобрать приложение с источниками из ledger цитат
python tools/build_sources_appendix.py --book $BOOK

# 6. собрать EPUB
python tools/build_epub.py --book $BOOK

# 7. проверить пакет
python tools/validate_epub.py --book $BOOK
```

Результат: `books/ddd-praktika/dist/ddd-praktika.epub`.

## Как устроены проверки

**`tools/lint_book.py`** — проверяет каждую главу:

- наличие всех обязательных секций в правильном порядке;
- скрытые ответы: `<details markdown="1">` с закрытым `<summary>`, без `open`;
- 5–8 вопросов в «Проверь себя» без ответов, 2–4 скрытых ответа в «Размышления»;
- номера ссылок существуют в `quotes.json`, не больше трёх на строку прозы;
- кодовые блоки парсятся как Python **и встречаются в пакете** — выдуманных
  фрагментов быть не может;
- ссылки на файлы пакета (`ddd_examples/...`) указывают на существующие файлы;
- нет посторонних символов из других письменностей — признака подменённых слов.

**`tools/validate_epub.py`** — проверяет готовый пакет:

- `mimetype` первый в архиве и без сжатия;
- все XHTML/OPF/NCX — валидный XML;
- манифест, spine, `nav` и NCX согласованы, все файлы на месте;
- внутренние ссылки разрешаются;
- ни один `<details>` не раскрыт по умолчанию.

**`tools/build_sources_appendix.py`** — генерирует приложение «Источники» из
ledger цитат (`~/.hermes/cache/citations/ledger.json` или
`%LOCALAPPDATA%/hermes/cache/citations/ledger.json`). URL'ы и цитаты берутся
из ledger, а не переписываются руками, поэтому нумерация в книге и в ledger
не разойдутся.

## Формат главы

Полный контракт — в `src/STYLE.md`. Обязательные секции:

```
## Введение
## Основной материал
## Пример в коде
## Разбор примера
## Ловушки
## Проверь себя
## Размышления
## Что дальше
## Источники главы
```

Скрытый ответ:

```markdown
<details markdown="1">
<summary><strong>Ответ.</strong> Нажмите, чтобы раскрыть</summary>

Текст ответа.

</details>
```

## Скрытые ответы в EPUB

Ответы спрятаны в HTML-элементе `<details>`. Он поддерживается всеми
современными читалками EPUB 3: ответ закрыт, пока читатель не нажмёт на
заголовок. В EPUB 2 элемент не поддерживался, поэтому книга собрана как
EPUB 3.0 с `nav`-документом и NCX для совместимости со старыми устройствами.

## Требования

- Python 3.11+
- `markdown` (расширения `fenced_code`, `tables`, `attr_list`, `def_list`,
  `md_in_html`, `sane_lists`)
- `pygments` — подсветка кода
- `pillow` — обложка

Внешние зависимости нужны только для сборки; сам пример кода работает на
чистом стандартной библиотеке.
