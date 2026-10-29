# Книги

Книга — каталог `books/<slug>/`. Книги независимы: своя нумерация, свой
контракт глав, свои источники, свой EPUB. Общие только инструменты в `tools/`.

## Устройство каталога

```
books/<slug>/
  book.json              паспорт: заголовок, автор, обложка, контракт главы
  README.md              что это за книга и как её собрать
  src/
    structure.json       оглавление: части, главы, приложения
    STYLE.md             контракт главы словами
    quotes.json          банк источников: id → url, title, цитаты
    evidence-map.json    id → файл с текстом страницы
    evidence/            тексты страниц-источников
    chapters/            Markdown-главы и приложения
  code/                  пакет с примерами и тесты (не у всех книг)
  dist/                  собранный EPUB
```

## Паспорт книги

`book.json` — единственное место, где описано, чем книга отличается от
других. Инструменты читают его и ничего не знают заранее.

```json
{
  "slug": "ddd-praktika",
  "title": "Domain-Driven Design на практике",
  "subtitle": "От моделирования домена к работающему коду",
  "author": "Ира",
  "language": "ru",
  "epub_filename": "ddd-praktika.epub",
  "structure": "src/structure.json",
  "cover": {
    "title_lines": ["Domain-Driven", "Design"],
    "subtitle_line": "на практике",
    "tagline_lines": ["От моделирования домена", "к работающему коду"]
  },
  "contract": {
    "sections": ["## Введение", "## Основной материал", "..."],
    "section_prefix_match": false,
    "questions": {"min": 5, "max": 8},
    "thoughts": {"min": 2, "max": 4},
    "answers_inline": false,
    "details_required": true,
    "citations": true,
    "code": {
      "language": "python",
      "package": "ddd_examples",
      "path": "code",
      "must_match_package": true
    }
  }
}
```

Поля контракта:

| Поле | Что задаёт |
|---|---|
| `sections` | Обязательные секции главы, по порядку |
| `section_prefix_match` | Сравнивать ли по префиксу: «## В EKS» подходит к «## В EKS: два вопроса» |
| `questions` | Сколько вопросов в «Проверь себя»: `min`, `max` |
| `thoughts` | Сколько скрытых ответов в «Размышления»: `min`, `max`. Пустой объект — секция не нужна |
| `answers_inline` | Разрешены ли ответы рядом с вопросами |
| `details_required` | Нужны ли блоки `<details>` |
| `citations` | Проверяются ли ссылки на источники |
| `code.language` | Язык примеров |
| `code.package` | Имя пакета с примерами |
| `code.path` | Каталог с кодом относительно корня книги |
| `code.must_match_package` | Обязаны ли блоки кода встречаться в пакете |

Секция `ai_tells` задаёт пороги линтера машинных следов (см.
`skills/chelovecheskiy-tekst`).

## Команды

У всех инструментов есть обязательный `--book <slug>`:

```bash
python tools/lint_book.py --book <slug>
python tools/check_quotes.py --book <slug>
python tools/check_ai_tells.py --book <slug>
python tools/build_sources_appendix.py --book <slug>
python tools/build_epub.py --book <slug>
python tools/validate_epub.py --book <slug>
```

## Источники и тексты страниц

Банк источников и тексты страниц лежат в репозитории — поэтому проверка
дословности работает одинаково на любой машине и в CI.

```
src/quotes.json        "1": {"url": ..., "title": ..., "quotes": [{"text": ...}]}
src/evidence-map.json  {"1": "evidence/eks-what-is-eks.txt", ...}
src/evidence/          тексты страниц, как их отдали при извлечении
```

Цитата проверяется сравнением с текстом своей страницы: совпадение
дословное, с учётом регистра, переносов строк и markdown-разметки. Цитата,
которой нет в тексте страницы, — это не цитата.

Как добавить источник:

1. Сохранить текст страницы в `src/evidence/<имя>.txt`.
2. Добавить запись в `src/quotes.json`: id, url, title, цитаты (дословные).
3. Добавить строку в `src/evidence-map.json`: id → путь к файлу.
4. Поставить `[n]` после утверждения в главе и добавить источник в
   секцию «## Источники главы».

Проверить: `python tools/check_quotes.py --book <slug>`.

## Как добавить книгу

1. Создать каталог `books/<slug>/` с `book.json`, `src/structure.json`,
   `src/chapters/`, `src/quotes.json`.
2. Описать контракт в `book.json`.
3. Написать `src/STYLE.md` — контракт словами.
4. Добавить главы и внести их в `structure.json`.
5. Проверить: `python tools/lint_book.py --book <slug>`.
6. Собрать: `python tools/build_epub.py --book <slug>` и
   `python tools/validate_epub.py --book <slug>`.

CI возьмёт новую книгу сам: матрица строится по каталогу `books/`, где у
книги есть `book.json`. Правки в workflow не нужны.
