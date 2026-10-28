---
name: technical-book-authoring
description: "Build a technical book: chapters, exercises, code, EPUB."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Writing, Books, EPUB, Documentation, Teaching, Publishing]
    category: productivity
    related_skills: [grounded-citations, pdf, docx, powerpoint, humanizer]
---

# Technical Book Authoring

Turn research or an existing draft into a book-length technical title whose
chapters follow a fixed contract, whose code illustrations are real and
runnable, and whose citations point at sources that actually contain the
quoted words.

The output is a validated EPUB plus the sources and the code package.

## When to Use

- The user asks for a book, a long course, or "make this more complete" out of
  notes or research.
- The user asks for chapters with exercises, self-check questions, answers,
  hidden answers, or worked examples.
- The user asks for an EPUB, or for a technical title to be assembled from
  Markdown sources.

For a one-page brief, a report, or a slide deck, use `grounded-citations` /
`powerpoint` directly — this skill is for book-length work where a contract
and a linter pay for themselves.

## The Shape of the Job

Three things must be true before the book is worth building:

1. **The code examples are real.** A reader must be able to run them.
2. **The citations are honest.** Every quoted fragment belongs to the source
   the number points at.
3. **The chapters share a contract.** Nine fixed sections, a fixed number of
   questions, a fixed format for hidden answers.

Each of these is enforced by a machine check, not by rereading. That is the
whole point: a book has too many pages to proofread, so the pages are
constrained by a linter instead.

## Procedure

### ① Plan the structure before writing prose

Write `src/structure.json` first — parts, chapters, appendices, and a reading
time per chapter:

```json
{ "parts": [ { "n": 1, "title": "Part I. Foundations",
  "chapters": [ { "file": "01-what-is-ddd", "title": "What is DDD",
                  "minutes": 18 } ] } ],
  "appendices": [ { "file": "app-a-glossary", "title": "Appendix A. Glossary" } ] }
```

Numbering lives in this file and nowhere else. Chapter files are
`src/chapters/<file>.md`; part pages are generated, never written by hand.

Decision point: **how many chapters** — one chapter per concept the reader
must be able to *use*, not per subtopic. A chapter that cannot carry its own
exercises is too small; a chapter with two unrelated ideas is too big.

### ② Write the chapter contract

Write `src/STYLE.md` before any chapter exists. It fixes: the required
sections and their order, the question counts, the hidden-answer block format,
the code-block rules, the citation format, and the running example domain.

Copy the section list into the contract verbatim — the linter checks those
exact strings.

Required sections, in order:

```
## Введение        ## Основной материал   ## Пример в коде
## Разбор примера   ## Ловушки              ## Проверь себя
## Размышления      ## Что дальше           ## Источники главы
```

(For a non-Russian book, translate these; the linter reads them from a
constant you edit.)

### ③ Build the code package before the chapters

Every code block in the book must be a fragment of a real, running package.
Build the package first, with tests, then write chapters against it.

Order matters: if you write chapters first, you will invent APIs that do not
exist, and the illustrations become lies. The package is the ground truth the
chapters quote.

```bash
cd code && python -m unittest discover -s tests
```

### ④ Author the chapters against the contract

Write chapters yourself, or delegate them to parallel subagents — but a
delegated chapter must be checked by the linter before it counts.

**Delegation contract:** give the subagent the contract path, the source bank
path, the code package path, the exact file names, and the exact required
sections, and tell it to run the linter itself. Then re-run the linter
yourself over everything.

Pitfall: **a contract described in prose drifts.** Parallel authors each
interpret "5–8 questions" differently, or drop the `## Источники главы`
section. The linter is the contract's teeth — if the linter is not run after
every delegation round, the drift reaches the reader.

### ⑤ Lint the chapters

```bash
python tools/lint_chapters.py --chapters src/chapters \
    --quotes src/quotes.json --package code/ddd_examples
```

The linter checks the section contract, question counts, the hidden-answer
blocks, that citation ids exist in the source bank, that code blocks parse,
that every code block is a real fragment of the package, and that the
manuscript contains no characters from a foreign script.

Fix and re-run until clean. See `references/chapter-contract.md` for what each
check means and how to satisfy it.

### ⑥ Verify the citations

The linter proves ids *resolve*. It cannot prove a quote belongs to the source
its number points at — only comparing the fragment against the source text
does that.

```bash
python ~/.hermes/skills/research/grounded-citations/scripts/check_attribution.py \
    src/chapters/*.md --map src/attribution-map.json
```

Build the map as `{"<id>": "<path to fetched page text>"}`. Mismatches are
auto-fixable with `--fix`. See the `grounded-citations` skill for the full
protocol.

### ⑦ Assemble the EPUB

```bash
python tools/build_epub.py --root . --out dist/book.epub
```

This builds EPUB 3 directly — no external converter required. It needs
`markdown` (extensions `fenced_code`, `tables`, `attr_list`, `def_list`,
`md_in_html`, `sane_lists`), `pygments` for code highlighting, and `pillow`
for the cover.

`references/epub-assembly.md` has the packaging recipe and the gotchas that
break a hand-built file: the uncompressed `mimetype` entry, XHTML void tags,
and the two different relative-path conventions between `nav.xhtml` and
`toc.ncx`.

### ⑧ Validate the package, then read it

```bash
python tools/validate_epub.py dist/book.epub
```

Validation covers XML well-formedness of every page, the manifest/spine
agreement, that internal links resolve, that no hidden answer is accidentally
open, and that no chapter is missing from the table of contents.

Then **open the file and look at it**: render a chapter and the TOC in a
browser and inspect the screenshots. Structural validators do not catch a
heading that collides with the code panel, a cover whose rule strikes through
the title, or a table of contents that lists every chapter twice. Fix the
template and rebuild — do not patch the artifact.

### ⑨ Deliver

Ship the EPUB plus, when the user will want to run the examples, the code
package as a zip. State what was verified (tests green, linter clean,
citations attributed) rather than what was attempted.

## Writing Style for the Manuscript

- The reader is competent but new to *this* topic. Explain the reasoning, not
  the vocabulary.
- Prefer a worked example over a description of one. Every chapter's code must
  do something the previous chapter's could not.
- Name a pitfall in every chapter. A chapter without a trap in it is a
  textbook, not a book.
- Self-check questions test recall; "reflect" questions trade off
  considerations. Never put the answer to a self-check question in the
  chapter.
- Hidden answers are the author's reasoning, not "the right answer" — say so
  in the answer itself.
- Write in the user's language. Keep technical terms in the original language
  with a translation at first mention.

## Pitfalls

- **Writing chapters before the code package.** Illustrations become invented
  APIs that do not compile and mislead the reader. Package first.
- **Trusting a prose contract instead of a linter.** Parallel authors drift
  from prose descriptions of the format; they do not drift from an executable
  check. The linter is the contract.
- **Letting the number after a quote stand for "verified".** A resolvable id
  can still point at the wrong source. Compare the fragment against the
  source text — that check is separate and easy to skip.
- **Building the EPUB before the chapters are final.** The TOC, the NCX, and
  the spine all change with the chapter list; rebuilding is cheap, but
  hand-patching generated files is not.
- **Hand-editing generated XHTML.** The builder is the source of truth; fix
  the template or the Markdown, then rebuild.
- **Adding a link target that the TOC does not know about.** Every chapter
  must appear exactly once in the navigation document, or readers see the
  book twice. Build the TOC from `structure.json`, not from a second
  enumeration of the chapter files.
- **Letting non-Latin manuscripts accumulate foreign-script characters.**
  Substituted words from another writing system survive proofreading because
  the eye skips them; detect them mechanically.
- **Omitting the running example.** Chapters that each invent their own
  toy domain read as unrelated articles. One domain, carried across the whole
  book, is what makes the patterns comparable.

## Support Files

- `references/chapter-contract.md` — the per-chapter template, the exact
  section list, the hidden-answer format, the code-block rules, and what each
  linter check enforces.
- `references/epub-assembly.md` — EPUB 3 packaging recipe, the directory
  layout, and the specific traps that silently break a hand-built file.
- `scripts/build_epub.py` — assembles the EPUB from `src/` + `code/`.
- `scripts/lint_chapters.py` — enforces the chapter contract.
- `scripts/validate_epub.py` — validates the built package.

The `grounded-citations` skill owns the citation protocol and the
attribution checker (`check_attribution.py`); this skill owns the chapter
contract, the code package, and the EPUB.
