#!/usr/bin/env python3
"""Validate a commit-flow answer against the rules in SKILL.md.

Usage:
    python3 validate_output.py [--items 1,2,3,4] [FILE]

Reads the draft from FILE or stdin, prints one line per broken rule and
exits 1 if anything is wrong.
"""

import argparse
import re
import sys

ALL_ITEMS = ("1", "2", "3.1", "3.2", "4.1", "4.2")

BRANCH_RE = re.compile(r"^[a-z0-9]+(?:[-/.][a-z0-9]+)*$")
PLAIN_RE = {
    "1": re.compile(r"^1\.\s*Branch:\s*(.+)$"),
    "2": re.compile(r"^2\.\s*Commit:\s*(.+)$"),
    "3.1": re.compile(r"^3\.1\.\s*Redmine title:\s*(.+)$"),
    "4.1": re.compile(r"^4\.1\.\s*PR title:\s*(.+)$"),
}
BLOCK_HEADER_RE = {"3.2": re.compile(r"^3\.2\.\s*$"), "4.2": re.compile(r"^4\.2\.\s*$")}
BLOCK_LANG = {"3.2": "textile", "4.2": "md"}


def expand_items(raw):
    """Turn a user request like "1,3" or "all" into a tuple of item ids."""
    if raw is None:
        return ALL_ITEMS
    tokens = [t for t in re.split(r"[\s,]+", raw.strip().lower()) if t]
    if not tokens or {"all", "все", "*"} & set(tokens):
        return ALL_ITEMS
    items = []
    for token in tokens:
        if token in ("3", "4"):
            items += [f"{token}.1", f"{token}.2"]
        elif token in ALL_ITEMS:
            items.append(token)
        else:
            raise ValueError(f"unknown item: {token}")
    return tuple(sorted(set(items)))


def parse(text):
    """Return {item: value} found in the draft. Code blocks are joined by \\n."""
    found = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        for item, pattern in PLAIN_RE.items():
            match = pattern.match(line.strip())
            if match:
                found[item] = match.group(1).strip()
                break
        else:
            for item, pattern in BLOCK_HEADER_RE.items():
                if pattern.match(line.strip()):
                    i, body, lang = _read_block(lines, i + 1)
                    found[item] = body
                    found[item + ":lang"] = lang
                    break
        i += 1
    return found


def _read_block(lines, i):
    """Read a fenced code block starting at or after index i."""
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not lines[i].strip().startswith("```"):
        return i, None, None
    lang = lines[i].strip()[3:].strip()
    body = []
    i += 1
    while i < len(lines) and not lines[i].strip().startswith("```"):
        body.append(lines[i])
        i += 1
    return i, "\n".join(body).strip(), lang


def _paragraph_errors(item, body):
    """Textile/Markdown bodies may break lines between headings and
    paragraphs, but not in the middle of a single paragraph's sentence flow.
    Blank lines separate blocks; each block must be exactly one line."""
    errors = []
    blocks = re.split(r"\n\s*\n", body.strip())
    for block in blocks:
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) > 1:
            snippet = lines[0][:40]
            errors.append(
                f"item {item}: paragraph broken across multiple lines near {snippet!r}; "
                "separate paragraphs/headings with a blank line instead"
            )
    return errors


def validate(text, items=ALL_ITEMS):
    """Return a list of human readable rule violations."""
    errors = []
    found = parse(text)

    for item in ALL_ITEMS:
        present = found.get(item) is not None
        if item in items and not present:
            errors.append(f"item {item}: missing")
        elif item not in items and present:
            errors.append(f"item {item}: not requested but present")

    branch = found.get("1")
    if "1" in items and branch:
        if not BRANCH_RE.match(branch):
            errors.append(f"item 1: bad branch name {branch!r}")
        if len(branch) > 50:
            errors.append(f"item 1: branch name longer than 50 chars ({len(branch)})")

    commit = found.get("2")
    if "2" in items and commit:
        words = len(commit.split())
        if not 3 <= words <= 15:
            errors.append(f"item 2: commit message has {words} words, expected 3-15")

    for item in ("3.2", "4.2"):
        body = found.get(item)
        if item not in items or body is None:
            continue
        lang = found.get(item + ":lang")
        if lang != BLOCK_LANG[item]:
            errors.append(f"item {item}: code block label is {lang!r}, expected {BLOCK_LANG[item]!r}")
        if not body:
            errors.append(f"item {item}: empty description")
            continue
        errors += _paragraph_errors(item, body)

    for item in ("3.1", "4.1"):
        value = found.get(item)
        if item in items and value is not None and not value:
            errors.append(f"item {item}: empty title")

    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="draft file (default: stdin)")
    parser.add_argument("--items", help='requested items, e.g. "1,3" or "all"')
    args = parser.parse_args(argv)

    text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    errors = validate(text, expand_items(args.items))
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
