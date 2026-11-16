# Backlog

Generated from `backlog.json` by `render.py`. Order within a phase follows the dependencies, not dates.

Owners: **A** = Engineer A (Nithin): FAERS, identity, signals, backtest, models; **B** = Engineer B: labels, recalls, changes, API and app; **Both** = Both engineers.

## E0 Foundation (phase 0)

A build both engineers can work in, with the two library risks settled.

| ID | Task | Owner | Depends on | Branch | Owns | Done when |
|---|---|---|---|---|---|---|
| F1 | **sbt multi-module build.** Three modules: labels (Scala 3.9, XmlDoc core + json), pipeline (Scala 2.13, Spark 4.0.x provided, Delta Lake, TableParser 1.7.2 core + spark), app (Scala 3.9, http4s). JDK 21. No dependsOn between modules. | A | - | `chore/F1-sbt-build` | build.sbt, project/, empty module folders | sbt test passes on a clean checkout on both engineers' machines. |
| F2 | **CI on GitHub Actions.** Compile, test, scalafmt check and scoverage for all modules on every pull request. Protect main: pull request and green CI required. | B | F1 | `chore/F2-ci` | .github/workflows/, .scalafmt.conf | A pull request shows a green check; a failing test blocks merge. |
| F3 | **Developer environment guide and config.** docs/setup.md: JDK 21, sbt, WSL2 or Docker for Spark on Windows, data directory layout (data/raw, bronze, silver, gold; git-ignored). Typed config for paths and thresholds. | B | F1 | `chore/F3-setup-guide` | docs/setup.md, pipeline/src/main/resources/application.conf | The other engineer sets up from the guide alone. |
| F4 | **Spike: TableParser inside Spark.** Parse one FAERS quarter (DRUG file) with TableParser's row parser applied in a Dataset map, as in tableparser-spark's DatasetMapper. Check serialization, header-by-name across an old and a new quarter, and throughput against Spark's CSV reader. | A | F1 | `feat/F4-tableparser-spike` | pipeline/src/**/medsignal/spike/tableparser/, docs/decisions/F4-tableparser-in-spark.md | Decision record docs/decisions/F4-tableparser-in-spark.md says which parser handles bulk FAERS and why, with timings. |
| F5 | **Spike: XmlDoc on SPL labels.** Extract sections (LOINC code, title, text) from five real labels with derived Extractors, XmlStream and GenericElement. Check hl7 namespaces, nested sections, tables and lists in text. | B | F1 | `feat/F5-xmldoc-spike` | labels/src/**/medsignal/spike/, docs/decisions/F5-xmldoc-on-spl.md | Decision record docs/decisions/F5-xmldoc-on-spl.md with the case classes that worked and the fallback used for mixed content. |
| F6 | **Define the formulary.** About 150 ingredients in five classes (SGLT2 and DPP-4 diabetes drugs, fluoroquinolones, sleep drugs, gabapentinoids, asthma and allergy) plus common hospital drugs. CSV: rxcui, ingredient, class, reason included. | Both | - | `chore/F6-formulary` | data/reference/formulary.csv | data/reference/formulary.csv reviewed by both; every row has a valid rxcui. |
| F7 | **Common pipeline library.** Delta read/write helpers, run_manifest (watermarks, checksums), run_metrics writer, Reject type and rejects table, SparkSession factory for tests. | A | F1 | `feat/F7-common-library` | pipeline/src/**/medsignal/common/ | Unit tests cover manifest and metrics round trips. |

## E1 Ingestion (bronze) (phase 1)

Every source landed as received, typed, with every rejected row counted.

| ID | Task | Owner | Depends on | Branch | Owns | Done when |
|---|---|---|---|---|---|---|
| I1 | **FAERS downloader.** Download quarterly ASCII zips from 2014 Q3 to the latest quarter and the deleted-case lists; record checksum and size in the manifest; skip files already present. | A | F3 | `feat/I1-faers-downloader` | pipeline/src/**/medsignal/download/faers/ | All quarters on disk; re-running downloads nothing. |
| I2 | **FAERS bronze tables.** Case classes and parsers for DEMO, DRUG, REAC, OUTC and INDI. Bronze Delta tables partitioned by quarter. Every line is loaded or written to rejects with file, line number and reason. | A | F4, F7, I1 | `feat/I2-faers-bronze` | pipeline/src/**/medsignal/bronze/faers/ | Lines in = rows loaded + rows rejected for every file (criterion 1). |
| I3 | **RxNorm and RxClass bronze.** Load RxNorm names (pipe-delimited RXNCONSO, prescribable subset) with TableParser. Pull class membership from RxClass for formulary ingredients. | A | F7 | `feat/I3-rxnorm-bronze` | pipeline/src/**/medsignal/bronze/rxnorm/ | bronze.rxnorm_names and bronze.rxclass populated; counts recorded. |
| I4 | **DailyMed downloader.** For each formulary ingredient, list SPL setIds and fetch every available version (history) as XML. Record setId, version and checksum in the manifest. | B | F6 | `feat/I4-dailymed-downloader` | labels/src/**/medsignal/download/ | Label versions on disk for every formulary drug; count reported. |
| I5 | **labels module: SPL to JSON Lines.** XmlDoc extraction of label metadata and the four sections (boxed warning, warnings and precautions, adverse reactions, drug interactions) into LabelSection records. Write JSON Lines and the SparkSchema.ddl string. Extraction failures are written to a rejects file. | B | F5, I4 | `feat/I5-spl-to-jsonl` | labels/src/**/medsignal/spl/ | Every downloaded label yields records or a reject; schema string checked in. |
| I6 | **Label bronze table.** Spark reads the JSON Lines with the generated DDL into bronze.label_section. | B | I5, F7 | `feat/I6-label-bronze` | pipeline/src/**/medsignal/bronze/labels/ | Row count equals JSON line count; schema test passes. |
| I7 | **Recall ingestion.** Download openFDA drug enforcement records (bulk file for history, API for updates). Explicit Spark schema; bronze.recall_raw. | B | F7 | `feat/I7-recall-ingestion` | pipeline/src/**/medsignal/bronze/recalls/ | Record count matches the openFDA total for the date range. |
| I8 | **FDA warning answer key.** Curate about 20 Drug Safety Communications and label changes for formulary drugs: drug or class, reaction terms, date, source URL. Each row checked by the second engineer. | Both | F6 | `chore/I8-fda-warning-key` | data/reference/fda_warnings.csv | data/reference/fda_warnings.csv with a source link on every row. |
| I9 | **ClinicalTrials.gov adverse events.** Pull trial results with reported adverse events for formulary drugs from the v2 API into bronze. | B | F7 | `feat/I9-trials-bronze` | pipeline/src/**/medsignal/bronze/trials/ | bronze.trial_adverse_event populated for formulary drugs. |
| I10 | **Medicare Part D spending by drug.** Load the yearly CSV (claims and beneficiaries by drug) with TableParser into bronze. | A | F7 | `feat/I10-partd-bronze` | pipeline/src/**/medsignal/bronze/partd/ | bronze.partd_drug populated; years recorded. |

## E2 Cleaning and identity (silver) (phase 2)

Deduplicated cases and one drug ID across all sources.

| ID | Task | Owner | Depends on | Branch | Owns | Done when |
|---|---|---|---|---|---|---|
| S1 | **Case deduplication.** silver.case keeps the highest caseversion per caseid and drops FDA-deleted cases. Partial dates parsed to a quarter. | A | I2 | `feat/S1-case-dedup` | pipeline/src/**/medsignal/silver/cases/ | One row per caseid; duplicate and deleted counts recorded. |
| S2 | **Drug identity resolver (drug_xref).** Resolve distinct name strings to an ingredient rxcui: prod_ai column, exact normalized match, match after stripping dose and form, override file. Store method and confidence. Incremental: only new strings are resolved. Combination products map to each ingredient. | A | I2, I3 | `feat/S2-drug-xref` | pipeline/src/**/medsignal/identity/, data/reference/drug_overrides.csv | At least 95% of formulary-drug mentions resolved (criterion 2); unmatched strings listed by frequency. |
| S3 | **Case detail tables.** silver.case_drug (suspect roles only, rxcui, one row per case and ingredient), case_reaction, case_outcome, case_indication. | A | S1, S2 | `feat/S3-case-detail` | pipeline/src/**/medsignal/silver/casedetail/ | Primary keys unique; row counts recorded. |
| S4 | **Label versions and reference label.** silver.label_version: one row per setId and version with rxcui and effective date. Reference-label rule: brand-name label where one exists, otherwise the most recent single-ingredient label. | B | I6, S2 | `feat/S4-label-versions` | pipeline/src/**/medsignal/silver/labels/ | Every formulary ingredient has exactly one current reference label or is listed as missing. |
| S5 | **Recall silver table.** Normalized recall records; product text resolved through drug_xref; unresolved recalls kept with a null rxcui. | B | I7, S2 | `feat/S5-recall-silver` | pipeline/src/**/medsignal/silver/recalls/ | Resolution rate reported; unresolved recalls visible. |
| S6 | **Data issues log.** For each issue in docs/data-issues.md, measure its size in the real data and record the handling or the decision to leave it. | Both | S1, S2, S3, S4, S5 | `chore/S6-data-issues-log` | docs/data-issues.md | Every issue has a number beside it. |

## E3 Signal statistics (phase 3)

Per-quarter counts and ranked candidate signals for every formulary drug.

| ID | Task | Owner | Depends on | Branch | Owns | Done when |
|---|---|---|---|---|---|---|
| G1 | **AdverseEventStat counts.** Distinct case counts per rxcui, reaction term and quarter, with serious and death counts and cumulative totals by window function. Background totals over all of FAERS. | A | S3 | `feat/G1-event-stat-counts` | pipeline/src/**/medsignal/signals/counts/ | Totals reconcile with silver.case counts. |
| G2 | **Statistics library.** Pure functions: PRR, chi-square, reporting odds ratio with 95% interval, information component (shrinkage). Property tests and worked examples. | A | F1 | `feat/G2-stats-library` | pipeline/src/**/medsignal/stats/ | Specs pass, including zero-cell and small-count cases. |
| G3 | **Signal table.** 2x2 counts from three aggregations and one join. Screen: PRR >= 2, chi-square >= 4, at least 3 cases. Score from the lower bound of the odds ratio, serious share and four-quarter growth. First-flagged quarter, indication flag, spike flag. | A | G1, G2 | `feat/G3-signal-table` | pipeline/src/**/medsignal/signals/signal/ | SGLT2 inhibitors and ketoacidosis appear as a signal; score components shown per row. |
| G4 | **Shrinkage ranking comparison.** Rank by the lower bound of the information component and compare the top 100 with the odds-ratio ranking. | A | G3 | `enhc/G4-shrinkage-ranking` | pipeline/src/**/medsignal/signals/shrinkage/, docs/results/G4.md | Short comparison written; one ranking chosen as default with the reason. |

## E4 Label reaction extraction (phase 3)

Labeled reactions with passages and offsets, scored on a gold set.

| ID | Task | Owner | Depends on | Branch | Owns | Done when |
|---|---|---|---|---|---|---|
| L1 | **Section selection and sentence splitting.** Select sections by LOINC code; split into sentences keeping character offsets into the section text. | B | S4 | `feat/L1-sentence-splitter` | pipeline/src/**/medsignal/labeltext/sentences/ | Offsets reproduce the exact sentence from the stored text in tests. |
| L2 | **Reaction dictionary and synonyms.** Vocabulary = distinct FAERS reaction terms. Synonym file for lay wording in the formulary's classes. Normalization of case, plurals and word order. | B | S3 | `feat/L2-reaction-dictionary` | pipeline/src/**/medsignal/labeltext/dictionary/, data/reference/reaction_synonyms.csv | Dictionary versioned; synonym file reviewed by both. |
| L3 | **Dictionary matcher.** Token trie broadcast to executors; typed mapPartitions over sentences; longest match wins. | B | L1, L2 | `feat/L3-dictionary-matcher` | pipeline/src/**/medsignal/labeltext/matcher/ | Unit tests on hand-made sentences; runs over all label versions. |
| L4 | **Negation rules.** Sentence-window rules (no cases of, was not observed, not associated with, and scope terminators such as but, however). | B | L3 | `feat/L4-negation-rules` | pipeline/src/**/medsignal/labeltext/negation/ | At least 90% of negated mentions in the gold set handled correctly. |
| L5 | **LabeledReaction table and labeled status.** Gold table keyed by setId, version, term and extractor version, with passage and offsets. Join to Signal: labeled, unlabeled, or negated-only, with the deciding passage. | B | L4, G3 | `feat/L5-labeled-reaction` | pipeline/src/**/medsignal/labeltext/labeled/ | Every signal has a labeled status and a passage or the list of sections searched (criterion 6). |
| L6 | **Gold set of 50 labels.** Each engineer annotates the labeled reactions in the adverse reactions and boxed warning sections of 25 labels, plus 10 shared labels to measure agreement. | Both | S4 | `chore/L6-gold-set` | data/reference/gold_labels/ (one file per label) | Gold set checked in; agreement on the shared labels reported. |
| L7 | **Extraction evaluator and drift report.** Precision, recall and negation accuracy against the gold set, recomputed on every extractor version. Drift report: reactions whose status flipped between label versions or extractor versions. | B | L5, L6 | `feat/L7-extraction-evaluator` | pipeline/src/**/medsignal/labeltext/eval/ | Scores written to a table and shown on the health page (criterion 5). |

## E5 Incremental runs, changes, monitoring (phase 4)

Daily, weekly and quarterly runs that agree with a full rebuild, a change feed, and health checks.

| ID | Task | Owner | Depends on | Branch | Owns | Done when |
|---|---|---|---|---|---|---|
| C1 | **Run orchestrator.** Command line entry point: run daily, weekly, quarterly or full. Reads watermarks, runs only the stages that have new input, writes run_metrics. | A | F7 | `feat/C1-run-orchestrator` | pipeline/src/**/medsignal/run/ | A run with no new data does no work and says so. |
| C2 | **FAERS incremental quarter load.** Parse a new quarter into its partition, MERGE into silver.case by caseid when the version is newer, rebuild gold aggregates. | A | S1, G3, C1 | `feat/C2-faers-incremental` | pipeline/src/**/medsignal/incremental/faers/ | Gold after loading quarters one by one equals gold after a full rebuild, row for row (criterion 4). |
| C3 | **Label and recall incremental runs.** Labels: only new setId and version pairs are parsed and extracted. Recalls: records after the watermark plus all open recalls, merged by recall_number. | B | S4, S5, L5, C1 | `feat/C3-label-recall-incremental` | pipeline/src/**/medsignal/incremental/labels/, pipeline/src/**/medsignal/incremental/recalls/ | A new label version triggers extraction for that version only; a status change on a recall is captured. |
| C4 | **ChangeEvent builder.** Compare Signal, Label and Recall with the previous run and append events: new signal, signal now labeled, label updated, recall opened, recall closed. | B | G3, L5, S5 | `feat/C4-change-events` | pipeline/src/**/medsignal/changes/ | A replayed day with a known new recall and label update yields exactly those events (criterion 7). |
| C5 | **Quality checks.** After each stage: schema matches the case class, row count within tolerance of the last run, reject rate under threshold, freshness within cadence, primary keys unique. A failed check fails the run with a message. | A | F7 | `feat/C5-quality-checks` | pipeline/src/**/medsignal/quality/ | Each check has a test that makes it fail. |
| C6 | **Optimization log.** Pipeline: FAERS raw text to AdverseEventStat. Baseline, then columnar bronze with column pruning, broadcast joins, incremental against full. Record wall time, shuffle bytes and peak memory, and what did not help. | A | C2 | `chore/C6-optimization-log` | docs/optimization-log.md | docs/optimization-log.md with before and after numbers from the Spark UI. |

## E6 Serving and application (phase 5)

The safety officer's five pages, with triage that survives a rebuild.

| ID | Task | Owner | Depends on | Branch | Owns | Done when |
|---|---|---|---|---|---|---|
| A1 | **Publish job.** Copy formulary-scoped gold tables to the serving database over JDBC in one transaction (PostgreSQL; H2 in tests). | A | G3, L5, C4 | `feat/A1-publish-job` | pipeline/src/**/medsignal/publish/ | Serving tables match gold counts; app stays readable during publish. |
| A2 | **http4s API.** Endpoints: changes since last run, ranked signals with filters, drug drill-down, recalls, pipeline health, triage POST. JSON with circe. | B | A1 | `feat/A2-http-api` | app/src/**/medsignal/api/ | Endpoint specs pass against a seeded database. |
| A3 | **Web pages.** Today, Signals, Drug drill-down (counts by quarter beside the highlighted label passage), Recalls, Pipeline health. | B | A2 | `feat/A3-web-pages` | app/src/main/resources/web/ | The safety officer's three questions are each answered within two clicks. |
| A4 | **Triage write-back.** Triage events inserted by the API are merged into gold TriageDecision at the start of the next run and joined to Signal. | A | A2 | `feat/A4-triage-writeback` | pipeline/src/**/medsignal/triage/ | A dismissed signal stays dismissed after a full rebuild. |
| A5 | **API latency measurement.** Measure page requests against the full formulary. | B | A2 | `chore/A5-api-latency` | app/src/**/medsignal/perf/ (test), docs/results/A5.md | 95% of requests under 1 second (criterion 8), or the number reported. |
| A6 | **Docker Compose deployment.** PostgreSQL, the app, and a pipeline image; one command to start the demo. | A | A1 | `chore/A6-docker-compose` | docker/, docker-compose.yml | docker compose up serves the app from a clean machine with sample data. |

## E7 Evaluation and advanced analysis (phase 6)

Backtest against FDA history, class and interaction signals, ranking model, extra sources.

| ID | Task | Owner | Depends on | Branch | Owns | Done when |
|---|---|---|---|---|---|---|
| V1 | **As-of-quarter signal rebuild.** Rebuild signals for each quarter using only FAERS partitions and label versions available at that time. | A | G3 | `feat/V1-asof-signals` | pipeline/src/**/medsignal/backtest/asof/ | Signal history table: one row per rxcui, term and as-of quarter. |
| V2 | **Backtest scoring.** For each known FDA warning, the first quarter MedSignal flagged it as an unlabeled signal; share flagged before the FDA and median lead time. | A | V1, I8, L5 | `feat/V2-backtest-scoring` | pipeline/src/**/medsignal/backtest/scoring/ | Backtest table and page; criterion 10 measured. |
| V3 | **Class-effect signals.** The same unlabeled reaction across several drugs of one class, with pooled counts. | A | G3 | `feat/V3-class-effects` | pipeline/src/**/medsignal/advanced/classeffect/ | Known class warnings (for example SGLT2 inhibitors and Fournier's gangrene) appear. |
| V4 | **Drug-pair interaction signals.** Pair counts from a self-join of case_drug restricted to formulary drugs, with minimum counts. Interaction ratio = pair PRR over the higher single-drug PRR. GraphFrames motif version for comparison. | A | S3, G2 | `feat/V4-interaction-signals` | pipeline/src/**/medsignal/advanced/interactions/ | Top 50 pairs listed with counts; run time recorded. |
| V5 | **Interaction validation.** Check top pairs against the drug interactions section of each drug's label, and against random pairs. | B | V4, L5 | `feat/V5-interaction-validation` | pipeline/src/**/medsignal/advanced/interactioncheck/ | Confirmation rate for top 50 against random pairs reported. |
| V6 | **MLlib ranking model.** Predict which unlabeled signals become label changes. GBTClassifier and LogisticRegression against the transparent score. Time split; instance weights; PR-AUC. | A | V2, V3, V4 | `feat/V6-ranking-model` | pipeline/src/**/medsignal/advanced/ranking/ | PR-AUC of each model and the baseline on the held-out years reported. |
| V7 | **Trial evidence on the drill-down.** Show whether the reaction was reported in trial results for the drug, as a second opinion. | B | I9, A2 | `enhc/V7-trial-evidence` | pipeline/src/**/medsignal/publish/trials/, app/src/**/medsignal/api/trials/ | Drill-down shows trial counts with a link to the trial. |
| V8 | **Exposure weighting.** Reports per 100,000 Part D claims beside each signal. | A | I10, G3 | `enhc/V8-exposure-weighting` | pipeline/src/**/medsignal/advanced/exposure/ | Signals page can sort by reporting rate. |

## E8 Delivery (phase 7)

Architecture note, optimization log, acceptance report and demo.

| ID | Task | Owner | Depends on | Branch | Owns | Done when |
|---|---|---|---|---|---|---|
| D1 | **One-page architecture note.** Data flow and ontology diagram, the four decisions that mattered, what was chosen not to do. | Both | A3 | `chore/D1-architecture-note` | docs/architecture-note.md | One page, reviewed by both. |
| D2 | **Acceptance report.** Every criterion in docs/acceptance-criteria.md with its measured value and how it was measured. | Both | A5, C6, L7, V2 | `chore/D2-acceptance-report` | docs/acceptance-report.md | Report checked in; no criterion left unmeasured. |
| D3 | **Demo script and rehearsal.** Twenty minutes: the app as the safety officer uses it, then under the hood. Questions each engineer should expect. | Both | D1, D2 | `chore/D3-demo-script` | docs/demo-script.md | Rehearsed once end to end from a clean checkout. |
| D4 | **README and runbook.** How to run each cadence, how to add a source, what to do when a check fails. | B | A6 | `chore/D4-readme-runbook` | README.md, docs/runbook.md | A new engineer runs the daily job from the README. |
