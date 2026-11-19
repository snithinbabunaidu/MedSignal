# Data sources

All sources are public. No patient-identifying data is used.

| Source | What it gives | Format | Updates | Where |
|---|---|---|---|---|
| FDA Adverse Event Reporting System (FAERS) | Reports that a medicine may have harmed someone, by drug and reaction. The high-volume source | Quarterly zip of `$`-delimited text files | Quarterly | https://www.fda.gov/drugs/fda-adverse-event-reporting-system-faers/fda-adverse-event-reporting-system-faers-latest-quarterly-data-files |
| DailyMed drug labels | The official label of every marketed drug, with version history. The unstructured source | Structured Product Labeling (SPL) XML | Daily | https://dailymed.nlm.nih.gov/dailymed/spl-resources-all-drug-labels.cfm |
| openFDA drug enforcement reports | Recalls with classification, reason, status and product | JSON (API and bulk download) | Weekly | https://open.fda.gov/apis/drug/enforcement/ |
| RxNorm and RxClass | Identifiers linking brand names, generics and ingredients; drug classes | Pipe-delimited files; REST API | Monthly | https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html |
| FDA Drug Safety Communications | Published FDA warnings; the answer key for the backtest | Web pages, curated by hand into a CSV | As issued | https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications |
| ClinicalTrials.gov (phase 6) | Adverse events reported in trial results; a second opinion | JSON API v2 | Daily | https://clinicaltrials.gov/data-api/api |
| Medicare Part D spending by drug (phase 6) | Prescription volume, to weight signals by use | CSV | Yearly | https://data.cms.gov |

## FAERS tables used

| Table | One row per | Key columns |
|---|---|---|
| DEMO | Report version | `primaryid`, `caseid`, `caseversion`, dates, age, sex, country, reporter type |
| DRUG | Drug in a report | `primaryid`, `drug_seq`, `role_cod`, `drugname`, `prod_ai` |
| REAC | Reaction in a report | `primaryid`, `pt` (MedDRA preferred term) |
| OUTC | Outcome | `primaryid`, `outc_cod` |
| INDI | Indication for a drug | `primaryid`, `indi_drug_seq`, `indi_pt` |

Range: 2014 Q3 to the latest quarter. Row counts are measured at task I2 and recorded here; earlier documents estimated about 140 million rows in total.

## Label sections used

| Section | LOINC code |
|---|---|
| Boxed warning | 34066-1 |
| Warnings and precautions | 43685-7 |
| Adverse reactions | 34084-4 |
| Drug interactions | 34073-7 |

Codes are checked against real labels in spike F5.

## Reference files kept in the repository

| File | Contents |
|---|---|
| `data/reference/formulary.csv` | Formulary ingredients with `rxcui`, class and reason included |
| `data/reference/fda_warnings.csv` | Known FDA warnings: drug or class, reaction terms, date, source URL |
| `data/reference/drug_overrides.csv` | Hand-written drug name mappings |
| `data/reference/reaction_synonyms.csv` | Lay wording mapped to reaction terms |
| `data/reference/gold_labels/` | Hand-annotated labeled reactions for 50 labels |

Downloaded data is not committed; it lives under `data/raw` and the Delta directories, which are git-ignored.

## Known FDA warnings in the formulary's classes

| Year | Drugs | Warning |
|---|---|---|
| 2015 | SGLT2 inhibitors | Ketoacidosis |
| 2015 | DPP-4 inhibitors | Severe joint pain |
| 2017 | Canagliflozin | Leg and foot amputation |
| 2018 | SGLT2 inhibitors | Fournier's gangrene |
| 2018 | Fluoroquinolones | Aortic aneurysm and dissection |
| 2019 | Zolpidem, eszopiclone, zaleplon | Complex sleep behaviors |
| 2019 | Gabapentin, pregabalin | Serious breathing problems |
| 2020 | Montelukast | Neuropsychiatric events |

Task I8 extends this to about 20 rows, each with its source link.
