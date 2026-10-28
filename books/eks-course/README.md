# EKS на практике

Курс по Kubernetes на Amazon EKS: 12 модулей от подготовки до EKS Auto Mode.
Каждый модуль разделён на две части — «Общее» (проверяется на kind, локальном
кластере в Docker) и «В EKS» (что добавляет, прячет или ломает AWS).

```
books/eks-course/
  book.json              паспорт: заголовок, обложка, контракт модуля
  src/
    structure.json       оглавление: 5 частей, 12 модулей, 3 приложения
    STYLE.md             контракт модуля
    quotes.json          банк источников AWS
    evidence-map.json    id → файл с текстом страницы в локальном кэше
    chapters/            модули (m-*.md) и приложения (app-*.md)
  dist/                  собранный EPUB
```

## Сборка

```bash
python tools/lint_book.py --book eks-course
python tools/check_quotes.py --book eks-course
python tools/check_ai_tells.py --book eks-course
python tools/build_sources_appendix.py --book eks-course
python tools/build_epub.py --book eks-course
python tools/validate_epub.py --book eks-course
```

Результат: `dist/eks-course.epub`.

## Контракт модуля

Секции: `## Общее`, `## В EKS`, `## Частые ошибки`, `## Проверка себя`,
`## Источники главы`. Сравнение секций — по префиксу, поэтому «В EKS: два
разных вопроса про доступ» подходит под «В EKS».

Вопросов в «Проверка себя» — от 2 до 6. Ответы разрешены рядом с вопросами:
в курсе они нужны читателю сразу, потому что это справочник, а не учебник
с размышлениями.

## Источники

Фактические утверждения (версии, цены, поведение сервисов) ссылаются на
официальную документацию AWS. Цитаты дословные, проверяются сравнением с
текстом сохранённой страницы.
