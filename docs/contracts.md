# Contracts

Names and shapes that every task must agree on. If a task needs to change something here, that is its own `[Chore]` pull request, merged first.

Status: proposed. Spikes F4 and F5 may adjust the parsing parts; nothing here has been compiled yet.

## Toolchain

| Item | Value |
|---|---|
| JDK | 21 |
| Build | sbt 1.x, three modules with no `dependsOn` between them |
| `pipeline` | Scala 2.13, Spark 4.0.x (`provided`), Delta Lake for Spark 4.0, TableParser 1.7.2 (`tableparser-core`, `tableparser-spark`), GraphFrames, spark-mllib, ScalaTest |
| `labels` | Scala 3.9, XmlDoc (`xmldoc-core`, `xmldoc-json`), circe, ScalaTest |
| `app` | Scala 3.9, http4s (ember server, dsl, circe), doobie, H2 and PostgreSQL drivers, ScalaTest |
| Root package | `medsignal` in every module |

## Paths

| Path | Holds |
|---|---|
| `data/raw/<source>/` | Downloaded files, never committed |
| `data/bronze/<table>`, `data/silver/<table>`, `data/gold/<table>` | Delta tables |
| `data/ops/<table>` | `run_manifest`, `run_metrics`, `rejects`, `extraction_score` |
| `data/reference/` | Small committed files |
| `data/interchange/labels/` | JSON Lines and `label_section.ddl` written by `labels`, read by `pipeline` |

All paths come from config key `medsignal.dataDir` (default `data`). Code never hard-codes a path.

## Common library (`medsignal.common`, task F7)

```scala
final case class Reject(source: String, file: String, line: Long, raw: String, reason: String, runId: String)

object Tables {                       // one place for table locations
  def bronze(name: String): String
  def silver(name: String): String
  def gold(name: String): String
  def ops(name: String): String
}

object Delta {
  def read[T: Encoder](path: String)(implicit spark: SparkSession): Dataset[T]
  def overwrite[T](ds: Dataset[T], path: String, partitionBy: Seq[String] = Nil): Unit
  def append[T](ds: Dataset[T], path: String, partitionBy: Seq[String] = Nil): Unit
  def merge[T](ds: Dataset[T], path: String, keys: Seq[String]): Unit   // upsert by keys
}

object RunManifest {                  // data/ops/run_manifest
  def loaded(source: String): Set[String]            // unit ids already loaded (quarter, setId:version, file)
  def record(source: String, unit: String, checksum: String, watermark: Option[String]): Unit
  def watermark(source: String): Option[String]
}

object RunMetrics {                   // data/ops/run_metrics
  def record(stage: String, rowsIn: Long, rowsOut: Long, rowsRejected: Long,
             durationMs: Long, newestSourceDate: Option[String]): Unit
}

trait Stage {                         // every pipeline stage implements this
  def name: String                    // e.g. "silver.case"
  def cadences: Set[Cadence]          // Daily, Weekly, Quarterly, Full
  def run(ctx: RunContext): StageResult
}
final case class RunContext(spark: SparkSession, runId: String, cadence: Cadence, asOfQuarter: Option[String])
final case class StageResult(rowsIn: Long, rowsOut: Long, rowsRejected: Long, newestSourceDate: Option[String] = None)

trait SparkTestSession                // ScalaTest mixin: local[2] session, temp dataDir
```

A stage registers by adding one file `pipeline/src/main/resources/stages/<name>.conf` containing `class = "medsignal....MyStage"` and `after = ["other.stage"]`. The orchestrator (C1) loads every file in that folder.

## Conventions

- `rxcui` is a `String` holding the RxNorm ingredient identifier.
- `quarter` is a `String` such as `2024Q3`.
- `term` is a reaction term, upper-cased and trimmed, as reported in FAERS.
- Dates are `java.sql.Date`; timestamps `java.sql.Timestamp`.
- Case classes at stage boundaries; typed `Dataset[T]`. No `var`, no `null`; use `Option`, `Try`, `Either`.
- Every stage returns its counts in `StageResult` (the runner records them), and every input row that fails to parse or validate becomes a `Reject`.
- Tests: ScalaTest `AnyFlatSpec with Matchers`; Spark tests mix in `SparkTestSession` and use small inputs under `src/test/resources/<task id>/`.

## Bronze tables

| Table | Case class | Columns |
|---|---|---|
| `faers_demo` | `FaersDemo` | primaryid: Long, caseid: Long, caseversion: Int, fda_dt: Option[String], init_fda_dt: Option[String], event_dt: Option[String], age: Option[Double], age_cod: Option[String], sex: Option[String], occr_country: Option[String], occp_cod: Option[String], quarter: String |
| `faers_drug` | `FaersDrug` | primaryid: Long, caseid: Long, drug_seq: Int, role_cod: String, drugname: String, prod_ai: Option[String], quarter: String |
| `faers_reac` | `FaersReac` | primaryid: Long, caseid: Long, pt: String, quarter: String |
| `faers_outc` | `FaersOutc` | primaryid: Long, caseid: Long, outc_cod: String, quarter: String |
| `faers_indi` | `FaersIndi` | primaryid: Long, caseid: Long, indi_drug_seq: Int, indi_pt: String, quarter: String |
| `faers_deleted` | `FaersDeleted` | caseid: Long, quarter: String |
| `rxnorm_names` | `RxNormName` | rxcui: String, tty: String, name: String, sab: String |
| `rxnorm_ingredient_map` | `RxNormIngredientMap` | rxcui: String, ingredientRxcui: String, tty: String (maps brand, salt and product concepts to their ingredient; written by I3) |
| `rxclass` | `RxClassMember` | rxcui: String, classId: String, className: String |
| `label_section` | `LabelSection` | setId: String, version: Int, effectiveDate: String, title: String, activeIngredients: Seq[String], isBrand: Boolean, loinc: String, sectionTitle: Option[String], text: String |
| `recall_raw` | `RecallRaw` | recall_number: String, classification: String, status: String, reason_for_recall: String, product_description: String, recalling_firm: String, recall_initiation_date: String, report_date: String, termination_date: Option[String], openfda_rxcui: Seq[String] |
| `fda_warning` | `FdaWarning` | warningId: String, scope: String (drug or class), target: String, terms: Seq[String], warningDate: Date, sourceUrl: String |
| `formulary` | `FormularyDrug` | rxcui: String, ingredient: String, drugClass: String, reason: String |
| `trial_adverse_event` | `TrialAdverseEvent` | nctId: String, intervention: String, rxcui: Option[String], term: String, serious: Boolean, affected: Long, atRisk: Long |
| `partd_drug` | `PartDDrug` | year: Int, genericName: String, brandName: String, totalClaims: Long, totalBeneficiaries: Option[Long] |

FAERS bronze tables are partitioned by `quarter`. `recall_raw` is upserted by `recall_number` (the one bronze table that is not append-only, because the source re-publishes changed records). `label_section` is unpartitioned.

## Silver tables

| Table | Case class | Key | Columns |
|---|---|---|---|
| `drug_xref` | `DrugXref` | rawName, rxcui | rawName: String, rxcui: Option[String], method: String (override, prod_ai, exact, stripped, none), confidence: Double |
| `case` | `Case` | caseid | caseid: Long, primaryid: Long, caseversion: Int, quarter: String, receivedDate: Option[Date], dateIsPartial: Boolean, ageYears: Option[Double], sex: Option[String], country: Option[String], reporterType: Option[String] |
| `case_drug` | `CaseDrug` | caseid, rxcui | caseid: Long, rxcui: String, role: String |
| `case_reaction` | `CaseReaction` | caseid, term | caseid: Long, term: String |
| `case_outcome` | `CaseOutcome` | caseid, outcome | caseid: Long, outcome: String |
| `case_indication` | `CaseIndication` | caseid, rxcui, term | caseid: Long, rxcui: String, term: String |
| `label_version` | `LabelVersion` | setId, version | setId: String, version: Int, rxcui: String, effectiveDate: Date, isBrand: Boolean, isSingleIngredient: Boolean, isReference: Boolean |
| `recall` | `RecallClean` | recallNumber | recallNumber: String, rxcui: Option[String], classification: String, status: String, reason: String, productText: String, firm: String, initiationDate: Option[Date], reportDate: Date, terminationDate: Option[Date], sourceUrl: String |

## Gold tables

| Table | Case class | Key | Columns |
|---|---|---|---|
| `Drug` | `Drug` | rxcui | rxcui, name, drugClass: Option[String], onFormulary: Boolean |
| `Label` | `Label` | setId, version | setId, version, rxcui, effectiveDate, isReference, sections: Map[String, String] (loinc to text) |
| `LabeledReaction` | `LabeledReaction` | setId, version, term, extractorVersion | plus loinc, passage, startOffset: Int, endOffset: Int, negated: Boolean |
| `AdverseEventStat` | `AdverseEventStat` | rxcui, term, quarter | plus cases: Long, seriousCases: Long, deathCases: Long, cumulativeCases: Long |
| `Signal` | `Signal` | rxcui, term | a, b, c, d: Long; prr, chiSquare, ror, rorLower, rorUpper: Double; seriousShare, growth4q, score: Double; firstFlaggedQuarter: Option[String]; indicationFlag, spikeFlag: Boolean; labeledStatus: String (labeled, unlabeled, negated_only, no_label); decidingSetId: Option[String]; decidingVersion: Option[Int]; passage: Option[String]; sectionsSearched: Seq[String]; triageStatus: String (open, review, escalate, dismiss) |
| `Recall` | `Recall` | recallNumber | same columns as silver `recall`, plus onFormulary: Boolean |
| `ChangeEvent` | `ChangeEvent` | runDate, kind, objectKey | runDate: Date, kind: String (new_signal, signal_labeled, label_updated, recall_opened, recall_closed), objectKey: String, rxcui: Option[String], before: Option[String], after: Option[String] |
| `TriageDecision` | `TriageDecision` | eventId | eventId: String, rxcui, term, decision: String, note: Option[String], user: String, decidedAt: Timestamp |

Phase 6 adds `SignalHistory` (Signal columns plus asOfQuarter), `BacktestResult`, `ClassSignal`, `InteractionSignal`, `TrialEvidence`, `Exposure`; each is defined in the brief of the task that creates it.

## Statistics (`medsignal.stats`, task G2)

```scala
final case class TwoByTwo(a: Long, b: Long, c: Long, d: Long)
object Disproportionality {
  def prr(t: TwoByTwo): Option[Double]                 // None when a denominator is zero
  def chiSquare(t: TwoByTwo): Option[Double]           // Yates-corrected
  def ror(t: TwoByTwo): Option[Double]
  def rorInterval(t: TwoByTwo): Option[(Double, Double)]   // 95%
  def informationComponent(t: TwoByTwo): Double        // shrinkage, +0.5 on observed and expected
  def ic025(t: TwoByTwo): Double
  def isCandidate(t: TwoByTwo): Boolean                // prr >= 2, chiSquare >= 4, a >= 3
}
```

## Serving database (written by A1, read by `app`)

Tables mirror gold, lower-snake-case: `drug`, `signal`, `adverse_event_stat`, `labeled_reaction`, `recall`, `change_event`, `run_metrics`, `extraction_score`. One table written by the app: `triage_event(event_id, rxcui, term, decision, note, user_name, decided_at)`.

Connection from config: `medsignal.serving.url`, `.user`, `.password` (H2 file by default).

## HTTP API (`medsignal.api`, task A2)

| Method and path | Returns |
|---|---|
| `GET /api/changes?since=<date>` | Change events, newest first |
| `GET /api/signals?class=&status=&labeled=&limit=` | Ranked signals |
| `GET /api/drugs/{rxcui}` | Drug, its signals, counts by quarter, labeled reactions with passages |
| `GET /api/recalls?status=open` | Recalls for formulary drugs |
| `GET /api/health` | Latest run metrics per stage, check results, extraction scores |
| `POST /api/triage` | Body `{rxcui, term, decision, note, user}`; inserts a triage event |

JSON field names are the camelCase case-class field names.

## Repository rules every task follows

- Branch, owned files and commit format: [branching.md](branching.md).
- Commit message and pull request title: `[Feat]: ...`, `[Enhc]: ...`, `[Chore]: ...` or `[Fix]: ...`, four or five words, no attribution lines.
- A task changes only the paths it owns.

## Decisions settled after the first draft of the briefs

These resolve gaps the task briefs exposed. Where a brief disagrees with this section, this section wins.

### Ownership

1. Besides its `owns` paths, every task also owns: the stage file(s) it registers (`pipeline/src/main/resources/stages/<stage name>.conf`), its config defaults (`pipeline/src/main/resources/conf.d/<task id>.conf`), its test fixtures (`<module>/src/test/resources/<task id>/`) and its results file (`docs/results/<task id>.md`).
2. A case class lives in the package of the task that writes its table (for example `medsignal.silver.cases.Case`, `medsignal.signals.signal.Signal`). Other tasks import it; they do not redefine it.
3. Reference loaders: F6 owns `pipeline/src/**/medsignal/bronze/reference/formulary/` and loads `data/reference/formulary.csv` into `bronze.formulary` (stage `bronze.formulary`). I8 owns `pipeline/src/**/medsignal/bronze/reference/warnings/` and loads `fda_warnings.csv` into `bronze.fda_warning` (stage `bronze.fda_warning`). Other tasks read the bronze tables, not the CSV files.
4. I2 loads `bronze.faers_deleted` along with the five FAERS tables. I3 writes `bronze.rxnorm_ingredient_map`.
5. C3 owns `scripts/run-labels.sh`, which runs the `labels` module commands (I4 download, I5 extract) before the pipeline's daily run. `labels` is Scala 3 and cannot use the pipeline's common library: it takes `--data-dir`, keeps its own `data/raw/dailymed/manifest.tsv`, and writes rejects to `data/interchange/labels/rejects.jsonl`. I1 likewise keeps `data/raw/faers/manifest.tsv` for downloads; `RunManifest` source `faers` is written only by I2 when a quarter is loaded.

### Common library (F7) additions

```scala
sealed trait Cadence
object Cadence { case object Daily extends Cadence; case object Weekly extends Cadence
                 case object Quarterly extends Cadence; case object Full extends Cadence }

object Settings {                      // typesafe config: application.conf plus every conf.d/*.conf
  def dataDir: String
  def config: com.typesafe.config.Config
}
object Delta {                         // in addition to read / overwrite / append / merge
  def exists(path: String): Boolean
  def readOrEmpty[T: Encoder](path: String)(implicit spark: SparkSession): Dataset[T]
  // overwrite with partitionBy is a dynamic partition overwrite: only partitions present in ds are replaced
  // merge creates the table when it does not exist
}
object Rejects { def write(rejects: Dataset[Reject]): Unit }      // appends to data/ops/rejects
object Checksum { def sha256(path: String): String }
object RunContext { def start(spark: SparkSession, cadence: Cadence, asOfQuarter: Option[String] = None): RunContext }
object StageRunner { def run(stage: Stage, ctx: RunContext): StageResult }   // runs one stage, times it, records metrics
```

6. **Metrics are recorded by the runner, not by the stage.** A stage returns `StageResult`; `StageRunner` (and through it the C1 orchestrator) calls `RunMetrics.record`. Stages never call `RunMetrics.record` themselves.
7. For a `Reject` raised by a stage that reads a table rather than a file: `file` is the input table name and `line` is 0.
8. Parsing returns a serializable wrapper defined by F4 (Spark has no encoder for `Either`); the sketch in pipeline-spec is illustrative.
9. Thresholds and other tunables are read from `Settings.config`, with defaults in the task's own `conf.d/<task id>.conf`. F3 owns `application.conf` (paths and connection settings only).

### Toolchain additions (F1)

`com.typesafe:config` in all modules; `scalatestplus-scalacheck` for property tests; H2 and PostgreSQL JDBC drivers in `pipeline` as well as `app`; logback in `app`; sbt plugins scalafmt, scoverage and assembly. F1 records in `docs/results/F1.md` which library coordinates resolved.

### Stage names

`bronze.formulary`, `bronze.fda_warning`, `bronze.faers`, `bronze.rxnorm`, `bronze.labels`, `bronze.recalls`, `bronze.trials`, `bronze.partd`, `identity.drug_xref`, `silver.case`, `silver.case_drug`, `silver.case_reaction`, `silver.case_outcome`, `silver.case_indication`, `silver.label_version`, `silver.recall`, `signals.counts`, `signals.signal`, `labeltext.extract`, `labeltext.status`, `labeltext.eval`, `triage.merge`, `triage.status`, `changes.events`, `quality.checks`, `publish.serving`. Phase 6 stages are named by their tasks under `backtest.*` and `advanced.*`.

There is no monthly cadence; RxNorm (`bronze.rxnorm`) runs under Quarterly and Full.

### Data rules

10. **Drug identity order:** override file first, then `prod_ai`, then exact normalized match, then dose and form stripped. An override always wins, and adding an override re-resolves that string. A combination product yields one `drug_xref` row per ingredient; an unmatched string has one row with `rxcui` empty. S2 exposes `DrugIdentity.ensureResolved(names: Dataset[String])` for S4 and S5 to call with label and recall names.
11. **`Case.quarter`** is the quarter of `init_fda_dt` (first received), falling back to `fda_dt`, then to the file quarter. A case that is followed up later stays in its first quarter.
12. **Deleted cases:** a `caseid` on any deleted list is removed.
13. **`LabelVersion.isReference`** is true for every version of the chosen reference `setId` of an ingredient, so an as-of rebuild can pick the version current at an earlier date. A combination label is never the reference.
14. **Label sections:** besides the four LOINC codes in data-sources.md, old-format labels are believed to use 34071-1 (warnings) and 42232-9 (precautions). F5 verifies; if confirmed, both are treated as warnings and precautions.
15. **Background totals:** G1 also writes gold `DrugQuarterTotal(rxcui, quarter, cases)`, `ReactionQuarterTotal(term, quarter, cases)` and `QuarterTotal(quarter, cases)` over all of FAERS. `AdverseEventStat` holds formulary drugs only.
16. **`Signal` is rebuilt in full by `signals.signal`** with `labeledStatus = no_label` and `triageStatus = open`. `labeltext.status` (L5) and `triage.status` (A4) run after it on every run and merge their columns back with `Delta.merge` on (`rxcui`, `term`). Neither edits G3's code.
17. **Reference file formats:** `formulary.csv` header is `rxcui,ingredient,drugClass,reason`. `fda_warnings.csv` header is `warningId,scope,target,terms,warningDate,sourceUrl`; `target` is an `rxcui` when `scope` is `drug` and a formulary `drugClass` when `scope` is `class`; `terms` are separated by `;`; `warningDate` is `yyyy-MM-dd`.
18. **Unresolved suspect drugs** in FAERS are counted in the stage result, not written as `Reject` rows (there are too many). `Reject` is for rows that fail to parse or validate.

### Second round

19. **Gold tables that had no writer.** I3 writes `gold.Drug` (stage `gold.drug`, package `medsignal.gold.drug`) from RxNorm names, RxClass and `bronze.formulary`. S4 writes `gold.Label` (stage `gold.label`, package `medsignal.gold.label`) from `silver.label_version` and `bronze.label_section`. S5 writes `gold.Recall` (stage `gold.recall`, package `medsignal.gold.recall`) from `silver.recall` and `bronze.formulary`.
20. **More stage names:** `gold.drug`, `gold.label`, `gold.recall`, `incremental.faers`, `incremental.labels`, `incremental.recalls`, `advanced.trial_evidence`, `advanced.exposure`.
21. **Reference tables** `bronze.formulary` and `bronze.fda_warning` are full snapshots: each run overwrites them from the CSV.
22. **Exception to "read the bronze table":** the `labels` module (I4) cannot read Delta, so it reads `data/reference/formulary.csv` directly.
23. **Ops table schemas.** `run_metrics`: `RunMetric(runId, stage, cadence, rowsIn, rowsOut, rowsRejected, durationMs, newestSourceDate: Option[String], recordedAt: Timestamp)`. `run_manifest`: `ManifestEntry(source, unit, checksum, watermark: Option[String], loadedAt: Timestamp)`. `check_result` is defined by C5 and `extraction_score` by L7 in their briefs; A1 publishes them as defined there.
24. **Quality checks run once per run** as the stage `quality.checks`, after the data stages. This replaces "after each stage" in pipeline-spec section 8.
25. **Unknown `after` entries are ignored.** If a stage file names a stage in `after` that is not registered (its task is not merged yet), the orchestrator skips that entry with a warning. This lets A1 list `triage.status` before A4 exists.
26. **Shared config keys** live in F3's `application.conf`: `medsignal.evaluation.enabled` (default false; read by the phase 6 stages) and `medsignal.recalls.closedStatuses` (read by C3 and C4; one key, not two).
27. **`app` config:** the app reads its settings with typesafe config (`ConfigFactory.load()`) and environment variables; it cannot use the pipeline's `Settings`.
28. **Counts that are not rejects** (for example unresolved suspect drugs in S3) are reported in `StageResult.rowsRejected` without writing `Reject` rows. Extra per-stage numbers (per-table publish counts, timing comparisons) go to the log and to `docs/results/<task id>.md`.
29. **Pages for phase 6.** V2 also owns `pipeline/src/**/medsignal/publish/backtest/`, `app/src/**/medsignal/api/backtest/` and `app/src/main/resources/web/backtest.html`. V8 also owns `pipeline/src/**/medsignal/publish/exposure/` and `app/src/**/medsignal/api/exposure/`. Each adds one line to A2's route list, as branching.md allows.
30. **`TrialAdverseEvent.rxcui`** is the formulary ingredient whose name appears in the trial arm title; empty for placebo and comparator arms.
31. **Old-format label codes** (34071-1, 42232-9) keep their original code in `loinc`; L1 treats them as warnings and precautions.
32. **`DrugIdentity.ensureResolved`** takes `Dataset[NameCandidate]` (raw name plus optional `prod_ai`), as defined in S2's brief; this replaces the `Dataset[String]` form in decision 10.
