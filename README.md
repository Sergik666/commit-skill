# commit-flow — a Claude Code skill

Replaces the copy-pasted `commit.md` instruction. Ask for a branch name, a
commit message, a Redmine task and a GitHub PR — all of them or just the items
you need.

```
/commit-flow          -> items 1, 2, 3, 4
/commit-flow 1 2      -> branch + commit message
/commit-flow 1,4      -> branch + pull request
/commit-flow 3.2      -> only the Textile description
```

## Layout

```
skills/commit-flow/SKILL.md                  the skill itself
skills/commit-flow/scripts/validate_output.py  output self-check + CLI
tests/                                       unittest suite (stdlib only)
```

## Tests

```bash
cd /workspace/project1/commit-skill
python3 -m unittest discover -s tests
```

`test_skill_md.py` checks the parts Claude Code depends on (frontmatter shape,
name matching the directory, trigger words in the description, every item and
formatting rule documented). `test_validate_output.py` checks the validator
against valid and deliberately broken answers.

## Install

Personal (all projects):

```bash
cp -r skills/commit-flow ~/.claude/skills/
```

Project-local (committed with the repo):

```bash
cp -r skills/commit-flow <project>/.claude/skills/
```

Restart the session, then run `/commit-flow`.

## Validator

Usable on its own:

```bash
python3 skills/commit-flow/scripts/validate_output.py --items 1,4 draft.md
```

Prints one line per broken rule, exits 1 if anything is wrong.
