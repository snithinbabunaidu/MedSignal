# Acceptance criteria

Each criterion is a number we measure and report, whether or not we reach it. The "Measured" column is filled in for the acceptance report (task D2).

| # | Criterion | Target | Task | Measured |
|---|---|---|---|---|
| 1 | Data accounted | 100% of lines in the FAERS files are loaded or rejected with a reason | I2 | |
| 2 | Drug identity | At least 95% of FAERS mentions of formulary drugs resolve to an `rxcui`; overall unmatched rate reported | S2 | |
| 3 | Batch speed | Full rebuild under 45 minutes on an 8-core laptop; one new quarter under 5 minutes; daily label and recall run under 2 minutes | C2, C3 | |
| 4 | Incremental correctness | Gold tables after loading quarters one by one equal gold tables after a full rebuild, row for row | C2 | |
| 5 | Label extraction | Precision at least 90% and recall at least 75% on a 50-label gold set; at least 90% of negated mentions handled correctly | L7 | |
| 6 | Traceability | 100% of signals link to counts and to a label passage or the list of sections searched | L5 | |
| 7 | Change detection | A replayed day with a known new recall and a known label update produces exactly those change events | C4 | |
| 8 | App speed | 95% of page requests under 1 second | A5 | |
| 9 | Tests | Every statistic and pipeline stage has a ScalaTest spec; CI green; at least 75% statement coverage in `pipeline` | F2 | |
| 10 | Early warning | At least 60% of about 20 known FDA warnings flagged before the FDA; median lead time at least 2 quarters | V2 | |
| 11 | Class effects | At least 3 known class-wide FDA warnings flagged before the FDA | V3 | |
| 12 | Interactions | Top 50 interaction pairs confirmed by the drug interactions section at least 3 times as often as random pairs | V5 | |
| 13 | Model ranking | PR-AUC at least 1.5 times that of the transparent score on the held-out years | V6 | |
| 14 | Optimization | At least one pipeline measured before and after, with what did not help | C6 | |

## Hand-ins from the brief

| Hand-in | Where |
|---|---|
| Working build | This repository; `docker compose up` (task A6) |
| One-page architecture note | `docs/architecture-note.md` (task D1) |
| Optimization log | `docs/optimization-log.md` (task C6) |
| Demo | `docs/demo-script.md` (task D3) |
