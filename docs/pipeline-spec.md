# Pipeline specification

Each stage lists its input, rules, output and the tests that must exist.

## 1. Bronze

| Source | Parser | Output | Partition |
|---|---|---|---|
| FAERS DEMO, DRUG, REAC, OUTC, INDI | TableParser row parser in a Spark `map` | `bronze.faers_*` | quarter |
| RxNorm names | TableParser | `bronze.rxnorm_names` | none |
| Label sections | XmlDoc in `labels`, then Spark JSON with generated schema | `bronze.label_section` | none |
| Recalls | Spark JSON with explicit schema | `bronze.recall_raw` | none |
| FDA warnings, formulary | TableParser | `bronze.fda_warning`, `bronze.formulary` | none |

Rules: append only; no cleaning; every input line becomes a row or a reject.

```scala
// sketch; confirmed by spike F4
val parsed: Dataset[Either[Reject, FaersDrug]] =
  spark.read.textFile(path)
    .map(line => rowParser.parse(header)(line).toEither.left.map(Reject(quarter, line, _)))
```

Tests: a file with a known bad line produces exactly one reject; lines in = rows + rejects.

## 2. Drug identity (`drug_xref`)

Input: distinct drug name strings from FAERS, labels and recalls. Output: `silver.drug_xref(rawName, rxcui, method, confidence)`.

Order of resolution:

1. FAERS active-ingredient column (`prod_ai`), matched to RxNorm ingredient names.
2. Exact match on the normalized string (upper case, punctuation and extra spaces removed).
3. Match after stripping dose, unit and form words.
4. Override file checked into the repository.

Combination products map to each ingredient. New strings are resolved on each run; resolved strings are never recomputed. Unmatched strings are kept with a null `rxcui`.

Tests: each method on hand-made names; a combination product yields two rows; idempotent on re-run.

## 3. FAERS cleaning (silver)

- `case`: highest `caseversion` per `caseid`; cases on the FDA deleted lists removed; report date parsed to a quarter.
- `case_drug`: suspect roles only (primary and secondary); joined to `drug_xref`; one row per case and ingredient.
- `case_reaction`, `case_outcome`, `case_indication`: one row per case and term.

Tests: two versions of a case leave one; a deleted case disappears; a drug listed twice in one case counts once.

## 4. Signal statistics

For each drug and reaction, with N total cases, n_d cases with the drug, n_r with the reaction, n_dr with both:

```
a = n_dr      b = n_d - a      c = n_r - a      d = N - n_d - n_r + a
PRR = (a / (a + b)) / (c / (c + d))
ROR = (a * d) / (b * c),  95% interval = exp(ln(ROR) ± 1.96 * sqrt(1/a + 1/b + 1/c + 1/d))
```

Three aggregations and one join give every 2x2 table; there is no cross join. Background counts use all of FAERS. Only formulary drugs are kept after the join, with the formulary broadcast.

Screen: PRR ≥ 2, chi-square ≥ 4, a ≥ 3. Score: lower bound of the odds ratio interval, raised by the share of serious outcomes and by growth over the last four quarters. Each component is stored so the app can show why a signal ranks where it does.

Flags: `indicationFlag` when the reaction is also a recorded reason for taking the drug; `spikeFlag` on a sharp quarter-over-quarter jump.

Tests: the worked example (300 of 10,000 against 1% elsewhere gives PRR 3.0); zero cells; property tests (PRR is 1 when rates are equal; the interval contains the point estimate).

## 5. Label reaction extraction

1. Select sections by LOINC code: boxed warning, warnings and precautions, adverse reactions, drug interactions.
2. Split into sentences, keeping character offsets.
3. Dictionary: distinct FAERS reaction terms plus a synonym file. Normalize case, plurals and word order.
4. Match with a broadcast token trie in a typed `mapPartitions`; longest match wins.
5. Negation: sentence-window rules mark a mention as negated.
6. Decide: a reaction is labeled for a drug when a non-negated mention exists on its reference label.

Output: `gold.LabeledReaction` with passage, offsets and `extractorVersion`. Extraction runs only for (`setId`, `version`, `extractorVersion`) triples not already present.

Tests: offsets reproduce the passage exactly for every row; "No cases of pancreatitis were observed" is negated; a rule change re-runs extraction and leaves FAERS tables untouched.

## 6. Incremental runs

| Feed | New input | Action | Rebuilt in full |
|---|---|---|---|
| FAERS | A quarter not in the manifest | Parse to a new partition; `MERGE` into `silver.case` when the version is newer | Gold aggregates, from silver |
| Labels | New (`setId`, `version`) | Parse and extract those only | Nothing |
| Recalls | Report date after watermark, plus open recalls | `MERGE` by `recallNumber` | Nothing |
| RxNorm | New monthly release | Replace names; re-resolve unmatched strings | Name table |

Test: gold after loading quarters one at a time equals gold after a full rebuild, row for row.

## 7. Change feed

After each run, compare `Signal`, `Label` and `Recall` with the previous run (Delta table history) and append `ChangeEvent` rows. Kinds: new signal, signal now labeled, label updated, recall opened, recall closed.

Test: a replayed day with a known new recall and a known label update yields exactly those events.

## 8. Quality checks

Run after each stage; a failure stops the run with a message.

| Check | Rule |
|---|---|
| Schema | Table schema equals the case class schema |
| Row count | Within a tolerance of the previous run |
| Rejects | Reject rate under a threshold per source |
| Freshness | Newest source date within the source's cadence |
| Keys | Primary key unique in every silver and gold table |
| Extraction | Gold-set scores not below the last accepted scores |

## 9. Publish and serve

The publish job copies formulary-scoped gold tables to the serving database over JDBC in one transaction. The API reads only that database. Triage events are inserted by the API and merged into `gold.TriageDecision` at the start of the next run.

| Page | Shows |
|---|---|
| Today | Change events since the last run; freshness per source; open Class I recalls |
| Signals | Unlabeled candidates ranked by score; filters for class and triage status |
| Drug drill-down | Counts by quarter beside the label passage with the matched term highlighted, or the sections searched |
| Recalls | Open recalls for formulary drugs, linked to the FDA record |
| Pipeline health | Last run per source, row counts, rejects, check results, extraction scores |

## 10. Evaluation and advanced analysis

- **Backtest.** Rebuild signals as of each quarter from the partitions and label versions available then. For each known FDA warning, record the first quarter it was flagged as unlabeled.
- **Class effects.** The same unlabeled reaction across drugs of one class, with pooled counts.
- **Interactions.** Pair counts from a self-join of `case_drug` on formulary drugs with minimum counts. Interaction ratio = pair PRR over the higher single-drug PRR. A GraphFrames motif version for comparison:

  ```scala
  g.find("(a)-[ab]->(b); (a)-[ar]->(r); (b)-[br]->(r)")
    .filter("ab.pairPrr >= 2 and ar.prr < 2 and br.prr < 2")
  ```
- **Ranking model.** Spark MLlib `GBTClassifier` and `LogisticRegression` against the transparent score; time split; instance weights; PR-AUC.
- **Trial evidence and exposure.** ClinicalTrials.gov adverse events on the drill-down; reports per 100,000 Medicare Part D claims.
