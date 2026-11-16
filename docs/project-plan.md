# Project plan

## Goal

Deliver everything the Soragence brief asks for, on Scala and Spark, and do it completely: every stage tested, every acceptance criterion measured. Two things are left out by decision: the Palantir Foundry platform and the LLM step.

The plan is ordered by dependency, not by date. A phase starts when the phase before it meets its exit condition.

## Scope

### In scope

| From | Item |
|---|---|
| Brief A | Five sources, one unstructured; raw to clean to ontology; incremental pipelines |
| Brief B | Labeled reactions extracted from label text (rule-based), compared with FAERS to flag frequent but unlabeled reactions |
| Brief C | Application: change view, ranked signal list, drill-down with the label passage beside the extraction, recall alerts, triage that writes back |
| Brief D | Pipeline health checks; extraction health on a gold set; drift report |
| Brief hand-ins | One-page architecture note, optimization log, demo |
| Brief extras | FDA Drug Safety Communications as an answer key; ClinicalTrials.gov as a second opinion; Medicare Part D for exposure |
| Course | Backtest against FDA history, class-effect signals, drug-pair interaction signals (GraphFrames), Spark MLlib ranking model |
| Course | Professor Hillyard's TableParser and XmlDoc libraries for parsing |

### Out of scope

- Palantir Foundry and AIP.
- Any LLM or other AI integration.
- Streaming. The fastest source updates daily, so batch runs are enough.
- User accounts and access control in the app.
- PubMed case reports.

## Phases

| Phase | Epic | Exit condition |
|---|---|---|
| 0 | E0 Foundation | Build and CI green; both library spikes have a written decision |
| 1 | E1 Ingestion | All sources in bronze; every input line loaded or rejected and counted |
| 2 | E2 Cleaning and identity | One row per case; at least 95% of formulary-drug mentions resolved |
| 3 | E3 Signals, E4 Label extraction (in parallel) | Signals ranked for the formulary; extraction scored on the gold set |
| 4 | E5 Incremental, changes, monitoring | Incremental result equals full rebuild; change events correct on a replayed day |
| 5 | E6 Serving and application | Five pages working; triage survives a rebuild |
| 6 | E7 Evaluation and advanced analysis | Backtest scored; class, interaction and model results reported |
| 7 | E8 Delivery | Architecture note, optimization log, acceptance report, rehearsed demo |

Phase 3 is where the two engineers work fully in parallel: signals (A) and label extraction (B) meet at the `Signal.labeledStatus` join.

## Who does what

| Area | Owner |
|---|---|
| FAERS ingestion, deduplication, drug identity | Engineer A |
| Signal statistics, backtest, class and interaction signals, ranking model | Engineer A |
| Run orchestrator, quality checks, optimization log, publish job, deployment | Engineer A |
| Label ingestion (XmlDoc), label extraction, evaluator and drift report | Engineer B |
| Recalls, change feed | Engineer B |
| API, web pages, CI, setup guide | Engineer B |
| Formulary, FDA warning answer key, gold set, data issues log, delivery | Both |

Each engineer reviews the other's pull requests, so both can explain every part in the demo.

The full task list, with dependencies and exit conditions, is in [backlog/backlog.md](backlog/backlog.md).

## Working agreements

- A task is done only when its "done when" condition is met and shown in the pull request.
- Numbers are measured, never estimated. Estimates in early documents are replaced as soon as the data is loaded.
- When the data surprises us, the surprise goes in [data-issues.md](data-issues.md) with its size and what we did.
- Decisions that are hard to reverse get a short record in `docs/decisions/`.

## Risks

| Risk | Response |
|---|---|
| TableParser's row parser does not serialize into Spark executors, or is too slow for all of FAERS | Spike F4 decides. Fallback: Spark's CSV reader for bulk FAERS, TableParser for the smaller files |
| XmlDoc struggles with label XML (namespaces, mixed content) | Spike F5 decides. Fallback: XmlDoc's generic element tree for section bodies |
| Two Scala versions in one build | Modules share files only; the generated schema string is the contract |
| Label matcher misses paraphrased reactions | Synonym file; recall measured on the gold set; "not found in sections searched" shown to the user |
| Drug names do not resolve | Layered resolver, override file, unmatched list ranked by frequency |
| Spark on Windows | Develop under WSL2 or Docker; documented in the setup guide |
| Few known FDA warnings to train a model on | Report the model as a comparison with the transparent score, with honest intervals |
| Reports are not proof of cause | Stated in the app on every signal; signals are prompts for review |
