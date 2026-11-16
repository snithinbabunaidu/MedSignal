# Contributing

Two engineers work in this repository. These rules keep the work reviewable and the main branch runnable.

## Branches and pull requests

The full rules, including which files each task owns, are in [docs/branching.md](docs/branching.md). In short:

- `main` is protected. Changes arrive by pull request with green CI and one approval from the other engineer.
- One backlog task, one branch, one pull request. The branch name is given in the backlog: `feat/S2-drug-xref`, `chore/F1-sbt-build`.
- A branch changes only the files its task owns, so branches merge without conflicts.
- The pull request description states the task ID and shows its "done when" condition being met (a test name, a count, a screenshot).
- Squash-merge, then delete the branch.

## Commit messages

One line: a type in square brackets, then four or five words.

```
[Feat]: Add drug identity resolver
[Enhc]: Rank signals by shrinkage
[Chore]: Add sbt build skeleton
[Fix]: Count each case once
```

`[Feat]` is a new capability, `[Enhc]` an improvement to something that works, `[Chore]` build, CI, docs and housekeeping, `[Fix]` a bug fix. Pull request titles use the same format. No tool or assistant attribution lines.

## Code

- Scala style: immutable values, no `var`, no `null`; `Option`, `Try` and `Either` for absence and failure.
- Typed `Dataset[T]` with case classes at stage boundaries. Untyped DataFrame operations are fine inside a stage.
- Pure functions for anything that can be pure (statistics, normalization, negation). They are tested without Spark.
- No row is dropped silently. A row that cannot be used goes to `rejects` with a reason.
- Format with scalafmt before committing.

## Tests

- Every statistic and every pipeline stage has a ScalaTest spec.
- Spark tests use a local session and small hand-made inputs checked into `src/test/resources`.
- A bug fix comes with a test that fails without it.

## Data

- Never commit downloaded data. `data/raw` and the Delta directories are git-ignored.
- Reference files under `data/reference` are small, hand-curated and committed.
- Public sources only. No patient-identifying or proprietary data.

## Decisions and surprises

- A decision that is hard to reverse gets a short record in `docs/decisions/<task id>-title.md`: context, options, choice, why.
- A surprise in the data goes in the task's `docs/results/<task id>.md` with its measured size and what was done; S6 collects these into `docs/data-issues.md`.

## Backlog

`docs/backlog/backlog.json` is the source for the task list. After editing it, run:

```bash
python docs/backlog/render.py
```

and commit the regenerated `backlog.md` and `backlog.csv`.
