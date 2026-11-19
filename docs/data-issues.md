# Data issues

Problems we expect in the data, what we do about each, and what we leave. The "Measured" column is filled in from the real data (task S6).

| # | Issue | Handling | Status | Measured |
|---|---|---|---|---|
| 1 | FAERS cases are re-sent as new versions | Keep the highest `caseversion` per `caseid` | Handled | |
| 2 | FAERS cases are later deleted by the FDA | Apply the deleted-case lists | Handled | |
| 3 | Malformed lines in some quarterly files | Reject with reason and count | Handled | |
| 4 | FAERS header columns differ between years | Columns found by header name (TableParser) | Handled | |
| 5 | Free-text drug names: brands, doses, misspellings | Layered resolver and override file; unmatched rate reported | Handled, residue reported | |
| 6 | Combination products | Map to each ingredient | Handled | |
| 7 | Partial dates (year only, year and month) | Parse to the earliest quarter consistent with the value; flag | Handled | |
| 8 | One ingredient has many labels (one per manufacturer) | One reference label per ingredient | Handled; differences between generic labels left | |
| 9 | Labels paraphrase reactions | Synonym file; recall measured on the gold set | Partly handled | |
| 10 | Negated mentions in labels | Negation rules | Handled, accuracy measured | |
| 11 | Reaction is the reason for treatment | Flag from the indications table; shown, not removed | Flagged | |
| 12 | Reports surge after news or an FDA warning | Spike flag; not corrected | Flagged | |
| 13 | Recall records lack structured drug identifiers | Product text through the resolver; unresolved recalls listed separately | Handled, residue shown | |
| 14 | Reports are not proof of cause | Stated on every signal | Left, by nature of the data | |
| 15 | No count of patients exposed | Medicare Part D claims as a proxy (phase 6) | Left until phase 6 | |
| 16 | Reaction vocabulary changes between MedDRA versions | Terms used as reported; no remapping | Left | |

New issues found during the build are added here with their size.
