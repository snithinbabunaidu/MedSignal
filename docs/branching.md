# Branches, pull requests and commits

The goal is that two engineers can work at the same time and merge without resolving conflicts, with a small number of branches: eight for the whole project.

## Eight branches, eight pull requests

Each branch carries a group of backlog tasks that belong together. A task is one commit on its branch (a few if it needs them), not a branch of its own.

| # | Branch | Who | Tasks | Start when | Waits for |
|---|---|---|---|---|---|
| 1 | `feat/foundation` | Nithin and Zenish | F1, F2, F3, F4, F5, F6, F7 | Now | - |
| 2 | `feat/faers-pipeline` | Nithin | I1, I2, I3, I10, S1, S2, S3 | `feat/foundation` is merged | - |
| 3 | `feat/label-recall-ingestion` | Zenish | I4, I5, I6, I7, I8, I9 | `feat/foundation` is merged | - |
| 4 | `feat/signals` | Nithin | G1, G2, G3, G4 | `feat/faers-pipeline` is merged (G2 can start earlier) | - |
| 5 | `feat/label-extraction` | Zenish | S4, S5, L1, L2, L3, L4, L5, L6, L7 | `feat/faers-pipeline` and `feat/label-recall-ingestion` are merged | L5 needs `feat/signals` (G3) |
| 6 | `feat/runs-and-app` | Nithin and Zenish | C1, C2, C3, C4, C5, C6, A1, A2, A3, A4, A5, A6 | `feat/signals` is merged (C1 and C5 first) | C3, C4 and A1 onward need `feat/label-extraction` |
| 7 | `feat/evaluation` | Nithin and Zenish | V1, V2, V3, V4, V5, V6, V7, V8 | `feat/signals` is merged (V4 first) | V1, V2, V3, V5 need `feat/label-extraction`; V7 needs `feat/runs-and-app` (A2) |
| 8 | `chore/delivery` | Nithin and Zenish | S6, D1, D2, D3, D4 | `feat/label-extraction` is merged (S6 first) | D1, D4 need `feat/runs-and-app`; D2 needs `feat/evaluation` |

- Create each branch from the latest `main`. At most three are open at any time: after the foundation, Nithin and Zenish each have one branch of their own (2 and 3, then 4 and 5), then share 6, 7 and 8.
- "Waits for" lists tasks inside a branch that need another branch merged first. Do the other tasks, and when that branch lands, bring it in with `git merge origin/main`. Never merge one feature branch into another.
- Open the pull request early as a draft so CI runs on every push. Mark it ready when every task in the branch meets its "done when" condition.
- Merge with a merge commit, not a squash, so each task's commit and its author stay in the history. Then delete the branch.
- On a shared branch (1, 6, 7, 8), run `git pull --rebase` before every push. Because each task owns its own files, the rebase never conflicts.
- A fix found after a branch is merged is a small `fix/<short-name>` branch with its own pull request. These are short and do not count toward the eight.

## Each task owns its files

Conflicts happen when two people edit the same file. So every task has an "Owns" entry in the backlog: the only paths its commits may create or change. This is what lets two people share one branch.

- A task's code lives in its own package folder, with its tests in the matching test folder.
- If a task needs something from another task's folder, it calls it; it does not edit it. If the other folder needs a change, its owner makes it in a separate commit.

## Shared files and how we avoid touching them

| Shared file | Rule |
|---|---|
| `build.sbt` | Written once by F1 with every dependency the plan needs. A later dependency is its own `[Chore]` commit by whoever needs it, announced to the other engineer first |
| Run orchestrator | Stages register by adding one file under `pipeline/src/main/resources/stages/`, one file per stage. Nobody edits a central list |
| Publish job | One file per published table under `publish/`. Nobody edits a central list |
| API routes | One file per route group under `api/`. The route list is owned by A2; a later route (V7) adds one line |
| `docs/data-issues.md`, `docs/acceptance-criteria.md` | Not edited by feature tasks. Each task writes its measured numbers to `docs/results/<task id>.md`; S6 and D2 collect them |
| Decision records | Named by task, not numbered: `docs/decisions/F4-tableparser-in-spark.md` |
| `README.md` | Owned by D4. Other tasks do not edit it |
| Reference data | One file per task (`formulary.csv`, `fda_warnings.csv`), or one file per item (`gold_labels/<label>.json`) where both engineers contribute |
| `docs/backlog/` | Changed only in its own `[Chore]` commit |

## Commit messages

One line, a type in square brackets, then four or five words:

```
[Feat]: Add drug identity resolver
[Enhc]: Rank signals by shrinkage
[Chore]: Add sbt build skeleton
[Fix]: Count each case once
```

| Type | Use for |
|---|---|
| `[Feat]` | A new capability |
| `[Enhc]` | An improvement to something that already works |
| `[Chore]` | Build, CI, docs, data files, housekeeping |
| `[Fix]` | A bug fix |

- Start the message with a capital letter and a verb. No full stop.
- No tool or assistant attribution lines in commits or pull requests.
- One commit per task where possible, with the task ID in the commit body, for example `Task: S2`.
- The pull request title uses the same format; each branch's title is given in the backlog.

## Pull request checklist

- Title in the commit format; the description lists the task IDs in the branch.
- Each commit changes only files its task owns.
- Every task's "done when" condition is shown (test name, count, or screenshot).
- CI is green and the other engineer has approved.
