# report-cli

A command-line tool that parses a sales CSV file, validates every row, and
computes summary statistics — revenue totals, per-product breakdown, monthly
trends, and a data-quality report of anything that didn't parse cleanly.

Built as a Python learning project (standard library only, no dependencies).

## Status

Work in progress. The data pipeline — parsing, validation, duplicate/refund
detection, and aggregation — is implemented and tested against
`sales_demo.csv`. Formatted report output and CLI options beyond the file
path are still being built.

## Features

- **CSV parsing** with a stable per-row ID (the original file line number),
  including correct handling of blank lines.
- **Field validation**, per row:
  - `date` — accepts `YYYY-MM-DD` or `MM/DD/YYYY`; rejects anything else,
    including impossible calendar dates (e.g. month 13).
  - `amount` — strips `$` and `,` before parsing; rejects empty or
    non-numeric values; negative amounts (refunds) are accepted.
  - `product` — rejects empty/blank values.
  - Invalid rows are **excluded from calculations** but never silently
    dropped — each is recorded with the reason(s) it failed.
- **Duplicate detection** — rows with an identical (date, product, amount)
  are kept in the totals (legitimate repeat sales) but flagged and grouped
  under the first occurrence for reporting.
- **Refund detection** — negative amounts are kept in the totals and flagged
  separately.
- **Aggregation**:
  - Row counts (total / valid / invalid)
  - Revenue sum, average, min, max
  - Per-product count and revenue, ranked by revenue
  - Revenue grouped by month (chronological)
  - Date range (earliest / latest sale)

## Planned

- Formatted, human-readable report output (current output is raw data for
  development/testing)
- `--top N` CLI option to control how many products appear in the ranking
- Expense-file support (grouping by category instead of product)

## Requirements

- Python 3.10+
- No external dependencies

## Usage

```
python3 cli.py <path-to-csv>
```

Example:

```
python3 cli.py sales_demo.csv
```

## Input format

A CSV file with a header row: `date,product,amount`

| Column  | Accepted formats |
|---------|-------------------|
| date    | `2026-01-05` or `01/05/2026` |
| product | any non-empty text |
| amount  | `120.50`, `$120.50`, `1,200.50`, `-45.00` (refund) |

## Project files

- `cli.py` — CLI entry point and all logic
- `sales_demo.csv` — sample data deliberately exercising every validation
  and edge case (bad amounts, bad dates, duplicates, refunds, a blank line)
- `.vscode/launch.json` — VS Code debug configuration (runs against
  `sales_demo.csv`)
