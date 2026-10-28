# The chapter contract

What a chapter file must contain, and what each machine check enforces.
Edit the section list constant in `scripts/lint_chapters.py` to match the
book's language before linting a non-Russian manuscript.

## File layout

```
src/
  STYLE.md            the contract, read by authors and subagents
  structure.json      parts, chapters, appendices — the single source of order
  quotes.json         source bank: {"<id>": {"url": ..., "title": ..., "quotes": [...]}}
  chapters/
    00-front.md       front matter (skipped by the linter's chapter checks)
    01-<slug>.md      one chapter
    app-<slug>.md     appendix (checked by a reduced rule set)
code/
  ddd_examples/       the real package the chapters quote
```

`structure.json` drives both the build order and the table of contents. Never
enumerate chapter files a second time to build the TOC — that is how a book
ends up listing every chapter twice.

## Chapter template

````markdown
# NN. Chapter title

*Лист чтения:* 20 минут · **Код:** `ddd_examples/path/to/file.py`

> **Краткое содержание.** One sentence: what the reader can do after this.

## Введение
2–4 paragraphs: why this chapter, which problem it solves.

## Основной материал
Subheadings ## / ###. Definitions, examples, tables where they help.

## Пример в коде
A real fragment of the package, ≤ 35 lines.

## Разбор примера
Line-by-line: what each part does and why it is that way.

## Ловушки
2–4 typical mistakes in this topic.

## Проверь себя
5–8 short questions, each ending in "?", no answers.

## Размышления
2–4 trade-off questions + 2–4 hidden answers.

## Что дальше
The bridge to the next chapter.

## Источники главы
The ids used in this chapter, each with what it supports.
````

## The hidden-answer block

Answers must be genuinely hidden until the reader clicks. In Markdown:

```markdown
<details markdown="1">
<summary><strong>Ответ.</strong> Нажмите, чтобы раскрыть</summary>

The answer text. May contain paragraphs, lists, code.

</details>
```

`markdown="1"` is required: without it the Markdown extension does not process
the body and the answer renders as raw source text.

Rules the linter enforces:

- every `<details>` has a closed `<summary>`;
- no `<details>` carries the `open` attribute (an open answer is a spoiler);
- every `<details>` block is balanced;
- the chapter has 2–4 of them in the reflection section.

## Code blocks

```python
from ddd_examples.shared import Money

money = Money.of(490, "RUB")
```

- Always tag the fence `python`.
- Every block must be a **real fragment of the package**. The linter proves
  this by matching the block's lines against the package sources as a
  subsequence — so a shortened excerpt (dropped docstrings, elided method
  bodies) passes, but an invented API does not.
- Keep blocks under ~35 lines; a longer one belongs in an appendix.
- If the excerpt needs a helper that does not exist yet, add the helper to
  the package rather than paraphrasing it into the chapter.
- Comments inside the code are part of the lesson and stay in the user's
  language.

## Citations

- Inline `[n]`, no space before the bracket, max 3 per sentence.
- Only ids present in `quotes.json`.
- A direct quotation goes in «quotes» with its id immediately after.
- The chapter's source list enumerates the ids used, with a note on what each
  supports.

Ids that resolve are not the same as ids that are correct — see the
`grounded-citations` skill for attribution checking.

## What the linter checks

| Check | Failure means |
|---|---|
| Required sections present, in order | The chapter drifted from the contract |
| 5–8 questions in the self-check section | Under- or over-tested |
| No answers in the self-check section | The reader is handed the answer |
| 2–4 hidden answers, all closed | Reflection block malformed or spoiling |
| Code blocks parse as Python | Typo, or a fragment spliced mid-expression |
| Code blocks exist in the package | The illustration is fiction |
| Package file references resolve | A `ddd_examples/...` path is wrong |
| Citation ids exist in the source bank | A dangling reference |
| ≤ 3 citations per prose line | Over-citation |
| No foreign-script characters | A word was substituted during writing |

The last check matters more than it looks: a Russian manuscript can acquire a
Chinese or Korean character inside a word, and proofreading misses it because
the eye skips characters it does not expect. The linter flags any character
outside the intended script.

## Front matter and appendices

`00-front.md` and `app-*.md` are checked by a reduced rule set: no required
sections, no question counts, but still citation ids, code parsing, and the
foreign-script check. Front matter is where you state what the reader is
expected to do — in particular, whether answers to the self-check questions
exist somewhere. If they do not, say so plainly; a promise of answers that
never arrive is the most common flaw in this format.
