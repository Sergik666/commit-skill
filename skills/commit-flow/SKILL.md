---
name: commit-flow
description: Produce branch name, commit message, Redmine task (Textile) and GitHub PR (Markdown) for the current code changes. Use when the user asks to prepare a commit, a branch name, a Redmine task or a pull request description for what was just changed, or types /commit-flow with item numbers like "1 2", "1,4", "all". Do NOT use for actually running git commit/push or opening a PR.
---

# commit-flow

Generate the release paperwork for the changes made in the current module:
branch name, commit message, Redmine task, GitHub pull request.

## 1. Decide which items are requested

`args` may name items by number, in any form: `1 2 3`, `1,4`, `3.2`, `all`,
`все`, or nothing at all — or it may describe them in plain language, in
Russian or English, e.g. "commit message and branch name", "текст коммита и
имя ветки", "just the PR", "только редмайн задачу". Map the wording to items
yourself before doing anything else:

| item | matches wording like |
|---|---|
| 1 | branch, branch name, ветка, имя ветки |
| 2 | commit, commit message, текст коммита, комит |
| 3.1 | redmine title, название задачи |
| 3.2 | redmine description, описание задачи |
| 3 (both) | redmine, redmine task, редмайн, задача |
| 4.1 | pr title, заголовок PR |
| 4.2 | pr description, описание PR |
| 4 (both) | pr, pull request, пиар, пулреквест |

- No args, `all`, `все`, `*`, or a request for "everything" → produce items 1, 2, 3, 4.
- Otherwise produce only the requested items, in ascending order.
- A bare `3` or "redmine" means both `3.1` and `3.2`; a bare `4` or "PR" means
  both `4.1` and `4.2`. Asking for just the title or just the description
  narrows it to the one sub-item.
- Once decided, translate the request to the numeric form (e.g. `1,2`) before
  passing it to `--items` in step 5 — the validator only understands numbers.

## 2. Collect the diff

Look **only** at the module the user has been changing in this session.
Do not dig into git history, do not summarize unrelated commits.

```bash
git status --short
git diff
git diff --cached
```

If nothing is staged or modified, say so and stop — there is nothing to describe.

Keep the analysis fast and shallow: describe what was done, not why the
codebase looks the way it does.

## 3. Write the answer in English

The whole answer is in English, regardless of the language of the request.

**Hard formatting rule:** items 1, 2, 3.1 and 4.1 are each one continuous
line — no line breaks (`\n`) inside them, no matter how long they get. There
is no upper limit on the number of sentences within a line.

Items 3.2 and 4.2 are proper Textile/Markdown documents, so line breaks
*inside* them are expected wherever the format needs them: a heading sits on
its own line, paragraphs are separated by a blank line. What is *not*
allowed is breaking a single paragraph mid-sentence just to keep lines
short — one paragraph stays one continuous line of text, however long.

Item rules:

- **1. Branch** — short, lowercase, `kebab-case`, optional `feat/`-style prefix,
  max 50 characters, no spaces.
- **2. Commit** — 3 to 15 words, imperative mood.
- **3.1. Redmine title** — one line.
- **3.2. Redmine description** — Textile, wrapped in a ```` ```textile ```` code block. Use `h3.`-style headings and blank-line-separated paragraphs as needed; each paragraph is one continuous line.
- **4.1. PR title** — one line.
- **4.2. PR description** — Markdown, wrapped in a ```` ```md ```` code block. Use `##`-style headings and blank-line-separated paragraphs as needed; each paragraph is one continuous line.

## 4. Output template

Emit exactly this shape, skipping the items that were not requested:

    1. Branch: feat/price-request-form
    2. Commit: add call for price request form to product page
    3.1. Redmine title: Call for price request form
    3.2.
    ```textile
    h3. Summary

    ... one continuous line of Textile per paragraph ...
    ```
    4.1. PR title: Add call for price request form
    4.2.
    ```md
    ## Summary

    ... one continuous line of Markdown per paragraph ...
    ```

No preamble, no closing remarks — just the items.

## 5. Self-check

Before sending, validate the draft:

```bash
python3 scripts/validate_output.py --items <requested items> <<'EOF'
<your draft>
EOF
```

The script exits non-zero and prints the broken rules. Fix them and re-check.
If Python is unavailable, verify the same rules by eye.
