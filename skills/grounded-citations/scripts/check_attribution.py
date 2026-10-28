#!/usr/bin/env python3
"""Check that a quoted fragment belongs to the source its citation names.

    python check_attribution.py draft.md --map ids.json
    python check_attribution.py src/chapters/*.md --map ids.json --fix

``verify`` proves a citation id resolves and that the Sources block matches
the ledger. It cannot prove the quoted sentence came from the page the id
points at — a quote attributed to [7] may actually be in [12]. This script
makes that check: it extracts quoted fragments, finds the nearest citation,
and looks the fragment up in that source's text.

The map file is JSON: {"<id>": "<path to the fetched page text>"}. Source
ids that are absent from the map are skipped, so a partial map still works.

Exit code 0 when every fragment matches, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# A quoted fragment inside «...» or "...".
QUOTE_RE = re.compile(r"[«“\"]([^«»“”\"]{15,600})[»”\"]")

# A citation marker.
CITE_RE = re.compile(r"\[(\d+)\]")

# Scripts that indicate a fragment is a real quotation rather than a
# highlighted phrase: an English phrase quoted inside a Russian sentence
# contains Latin letters, a Russian highlight does not.
LATIN_RE = re.compile(r"[A-Za-z]")
CYRILLIC_RE = re.compile(r"[Ѐ-ӿ]")


def normalize(text: str) -> str:
    """Fold typography differences that do not change the words.

    Curly quotes become straight ones, dashes normalize, whitespace
    collapses, and a trailing ellipsis is dropped — a quotation ending in
    "..." cites a fragment, not the whole sentence.
    """
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-")
    text = " ".join(text.split())
    if text.endswith("..."):
        text = text[:-3].rstrip()
    elif text.endswith("…"):
        text = text[:-1].rstrip()
    return text.rstrip(",;:.!?")


def is_quotation(text: str, require_latin: bool) -> bool:
    """True when the fragment looks like a quotation from a source.

    In a non-Latin manuscript, «...» is used both for quotations and for
    highlighted words. A fragment with Latin letters is a quotation of
    foreign text; a fragment without is prose emphasis.
    """
    latin = len(LATIN_RE.findall(text))
    if latin < 8:
        return False
    if require_latin:
        cyrillic = len(CYRILLIC_RE.findall(text))
        return cyrillic / max(latin + cyrillic, 1) < 0.35
    return True


def nearest_citation(text: str, start: int, end: int) -> int | None:
    """The citation id that governs the fragment at [start, end).

    Looks forward first (the usual convention: the citation follows the
    fragment), then backward.
    """
    forward = CITE_RE.search(text, end, end + 200)
    if forward:
        return int(forward.group(1))
    backward = None
    for match in CITE_RE.finditer(text, max(0, start - 200), start):
        backward = match
    if backward:
        return int(backward.group(1))
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("drafts", nargs="+", type=Path)
    parser.add_argument("--map", required=True, type=Path,
                        help='JSON: {"<id>": "<path to page text>"}')
    parser.add_argument("--fix", action="store_true",
                        help="rewrite a citation to the source that contains "
                             "the fragment")
    parser.add_argument("--any-script", action="store_true",
                        help="treat fragments in any script as quotations "
                             "(use for a Latin-script manuscript)")
    args = parser.parse_args()

    mapping = json.loads(args.map.read_text(encoding="utf-8"))
    evidence = {}
    for source_id, location in mapping.items():
        source_path = Path(location)
        if source_path.exists():
            evidence[source_id] = source_path.read_text(encoding="utf-8")

    if not evidence:
        print("The map points at no readable source files.")
        return 1

    normalized_evidence = {
        source_id: normalize(text) for source_id, text in evidence.items()
    }

    problems: list[str] = []
    fixed = 0

    for draft in args.drafts:
        if not draft.exists():
            print(f"Not found: {draft}")
            continue
        text = draft.read_text(encoding="utf-8")

        for match in QUOTE_RE.finditer(text):
            fragment = match.group(1)
            if not is_quotation(fragment, require_latin=not args.any_script):
                continue
            cited = nearest_citation(text, match.start(), match.end())
            if cited is None:
                continue
            if cited not in normalized_evidence:
                continue

            if normalize(fragment) in normalized_evidence[cited]:
                continue

            found_in = [
                source_id for source_id, source in normalized_evidence.items()
                if normalize(fragment) in source
            ]

            if len(found_in) == 1 and found_in[0] != cited:
                problems.append(
                    f"{draft.name}: attributed to [{cited}], found in "
                    f"[{found_in[0]}] — «{fragment[:70]}»"
                )
                if args.fix:
                    window = text[match.end():match.end() + 400]
                    reference = CITE_RE.search(window)
                    if reference:
                        position = match.end() + reference.start()
                        text = (
                            text[:position]
                            + f"[{found_in[0]}]"
                            + text[position + len(reference.group(0)):]
                        )
                        fixed += 1
            elif not found_in:
                problems.append(
                    f"{draft.name}: not found in any mapped source — "
                    f"«{fragment[:70]}» (cited [{cited}])"
                )
            else:
                problems.append(
                    f"{draft.name}: found in several sources {found_in}, cited "
                    f"[{cited}] — «{fragment[:70]}»"
                )

        if args.fix and text != draft.read_text(encoding="utf-8"):
            draft.write_text(text, encoding="utf-8")

    if problems:
        print(f"Findings: {len(problems)}")
        for problem in problems:
            print(f"  ! {problem}")
        if fixed:
            print(f"\nRe-attributed: {fixed}")
        return 1

    print("Every quoted fragment belongs to the source it cites.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
