# MedSignal

A medication safety signal monitor for a hospital pharmacy, built with Scala and Apache Spark.

CSYE 7200 Big-Data Systems Engineering Using Scala, Fall 2026 (Professor Robin Hillyard).

## What it does

A pharmacy safety officer watches a formulary of about 150 drugs. MedSignal gives her one page that answers three questions each morning:

1. Which drugs have adverse events being reported that the label does not mention?
2. Which drugs have an active recall?
3. What has changed since yesterday?

Every flag links to the report counts and the exact label passage behind it.

The project follows the Soragence build brief "Medication Safety Signal Monitor", with two deliberate changes: Spark and Delta Lake replace Palantir Foundry, and a rule-based label reader replaces the LLM step.

## How it works

```
sources            parse                 bronze          silver             gold (ontology)     serve
FAERS ($ text)  -> TableParser in Spark -> as received -> deduplicated   -> Drug, Label,     -> serving DB
RxNorm (| text) -> TableParser          -> by quarter     cases,            LabeledReaction,    -> http4s API
DailyMed (XML)  -> XmlDoc (Scala 3)     -> JSON lines     drug_xref         AdverseEventStat,   -> web pages
openFDA recalls -> Spark JSON           ->                (one drug ID),    Signal, Recall,
FDA warnings    -> TableParser          ->                rejects           ChangeEvent,
                                                                            TriageDecision
```

- **Storage:** Delta Lake tables in three layers (bronze, silver, gold).
- **Drug identity:** resolved once, in the silver table `drug_xref`; every source joins through it.
- **Signals:** proportional reporting ratio and chi-square screen, ranked by the lower 95% bound of the reporting odds ratio.
- **Label reading:** dictionary matcher with negation rules; every result stores its passage and offsets.
- **Incremental:** FAERS by quarter, labels by version, recalls by report date.
- **Application:** http4s API and web pages over a small serving database; triage decisions flow back into the gold layer.

## Modules

| Module | Scala | Purpose |
|---|---|---|
| `labels` | 3.9 | Reads DailyMed label XML with [XmlDoc](https://github.com/rchillyard/XmlDoc); writes JSON Lines and the Spark schema |
| `pipeline` | 2.13 | Spark 4.0 jobs, Delta Lake, [TableParser](https://github.com/rchillyard/TableParser) 1.7 for delimited files |
| `app` | 3.9 | http4s API and web pages; no Spark dependency |

Spark is published for Scala 2.13 only and XmlDoc for Scala 3.9 only, so the modules exchange files, not classes.

## Status

Planning is complete; no code yet. The first tasks are the sbt build (F1) and two library spikes (F4, F5). See the backlog.

## Documentation

| Document | Contents |
|---|---|
| [Project plan](docs/project-plan.md) | Scope, phases, who does what, risks |
| [Architecture](docs/architecture.md) | Layers, modules, the decisions that matter |
| [Ontology](docs/ontology.md) | Gold objects, keys and links |
| [Pipeline specification](docs/pipeline-spec.md) | Each stage: inputs, rules, outputs, tests |
| [Data sources](docs/data-sources.md) | Where each source comes from, format, cadence |
| [Data issues](docs/data-issues.md) | Known problems in the data and how each is handled |
| [Acceptance criteria](docs/acceptance-criteria.md) | The numbers we will measure and report |
| [Backlog](docs/backlog/backlog.md) | All tasks with owner, dependencies, branch, owned files and exit condition |
| [Branches and commits](docs/branching.md) | The eight branches, file ownership, commit message format |
| [Contributing](CONTRIBUTING.md) | Branches, pull requests, tests, definition of done |

## Team

Two engineers. Nithin Naidu owns FAERS, drug identity, signals, the backtest and the models. Zenish owns labels, recalls, the change feed, the API and the web pages. Build, the formulary, the gold set and delivery are shared.
