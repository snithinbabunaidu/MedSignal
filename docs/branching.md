# Branches, pull requests and commits

The goal is that two engineers can work on many branches at once and merge them in any order their dependencies allow, without resolving conflicts.

## One task, one branch, one pull request

- Every backlog task has its own branch, named in [backlog/backlog.md](backlog/backlog.md): `<type>/<task id>-<short name>`, for example `feat/S2-drug-xref`.
- Branch from the latest `main`. Open one pull request per branch. Squash-merge it, then delete the branch.
- Start a task only when the tasks it depends on are merged, so a branch never builds on another open branch.
- Keep branches short-lived. Rebase on `main` before asking for review.

## Each task owns its files

Conflicts happen when two branches edit the same file. So every task has an "Owns" entry in the backlog: the only paths its branch may create or change.

- A task's code lives in its own package folder, with its tests in the matching test folder.
- If a task needs something from another task's folder, it calls it; it does not edit it. If the other folder needs a change, that is a separate small pull request, merged first.

## Shared files and how we avoid touching them

| Shared file | Rule |
|---|---|
| `build.sbt` | Written once by F1 with every dependency the plan needs. A later dependency is its own `[Chore]` pull request, merged before the task that needs it |
| Run orchestrator | Stages register by adding one file under `pipeline/src/main/resources/stages/`, one file per stage. Nobody edits a central list |
| Publish job | One file per published table under `publish/`. Nobody edits a central list |
| API routes | One file per route group under `api/`. The route list is owned by A2; a later route (V7) adds one line |
| `docs/data-issues.md`, `docs/acceptance-criteria.md` | Not edited by feature branches. Each task writes its measured numbers to `docs/results/<task id>.md`; S6 and D2 collect them |
| Decision records | Named by task, not numbered: `docs/decisions/F4-tableparser-in-spark.md` |
| `README.md` | Owned by D4. Other tasks do not edit it |
| Reference data | One file per task (`formulary.csv`, `fda_warnings.csv`), or one file per item (`gold_labels/<label>.json`) where both engineers contribute |
| `docs/backlog/` | Changed only in its own `[Chore]` pull request |

## Work that can run in parallel

After F1 merges, these groups have no shared files and no dependency on each other:

| Stage | Nithin | Zenish |
|---|---|---|
| Foundation | F4, F7, G2 | F2, F3, F5 |
| Ingestion | I1, I2, I3, I10 | I4, I5, I6, I7, I9 |
| Silver | S1, S2, S3 | S4, S5 |
| Core analysis | G1, G3, G4 | L1, L2, L3, L4, L5, L7 |
| Runs and checks | C1, C2, C5, C6 | C3, C4 |
| Application | A1, A4, A6 | A2, A3, A5 |
| Evaluation | V1, V2, V3, V4, V6, V8 | V5, V7 |

Shared tasks (F6, I8, L6, S6, D1, D2, D3) are split by file or by row so both can contribute without overlap.

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
- The pull request title uses the same format, because the squash-merge commit takes it.
- The branch type matches the commit type: `feat/`, `enhc/`, `chore/`, `fix/`.

## Pull request checklist

- Title in the commit format, with the task ID in the description.
- Only files the task owns are changed.
- The task's "done when" condition is shown (test name, count, or screenshot).
- CI is green and the other engineer has approved.
