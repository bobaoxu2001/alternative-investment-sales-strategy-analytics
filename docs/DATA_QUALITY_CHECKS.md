# Data Quality Checks

**Project:** Alternative Investment Sales Strategy Analytics Platform  
**Author:** Allen Xu

This document summarizes the quality controls used to keep the synthetic analytics pipeline reproducible and portfolio-ready.

## 1. Validation Script

The project includes `src/validate_outputs.py`, which checks the generated data and reporting artifacts after the pipeline runs.

The script validates:

- required raw CSV files exist
- required processed CSV files exist
- expected row counts match deterministic outputs
- required chart PNGs exist and are non-empty
- key identifier columns are unique
- foreign-key style relationships are internally consistent
- expected KPI values match the deterministic seed-42 output
- README chart image paths resolve to existing files

## 2. Deterministic Row Count Checks

Expected raw output counts:

| File | Expected Rows |
|---|---:|
| `relationship_managers.csv` | 16 |
| `advisors.csv` | 400 |
| `funds.csv` | 10 |
| `campaigns.csv` | 28 |
| `sales_activities.csv` | 7,500 |
| `opportunities.csv` | 1,500 |
| `campaign_engagement.csv` | 1,408 |

Expected processed output counts:

| File | Expected Rows |
|---|---:|
| `sales_funnel_summary.csv` | 28 |
| `rm_productivity_summary.csv` | 16 |
| `product_demand_summary.csv` | 62 |
| `campaign_roi_summary.csv` | 28 |
| `advisor_priority_scores.csv` | 400 |
| `executive_kpi_summary.csv` | 14 |

## 3. Integrity Checks

The validation script checks that:

- advisor IDs, RM IDs, fund IDs, campaign IDs, opportunity IDs, and activity IDs are unique where expected
- sales activities reference valid advisors and RMs
- opportunities reference valid advisors, RMs, and funds
- campaign engagement rows reference valid campaigns and advisors
- campaign-sourced opportunities reference valid campaigns when a source campaign is present

## 4. KPI Checks

The script verifies the deterministic executive KPI outputs, including:

- total expected pipeline: `$58.811B`
- committed capital: `$6.748B`
- total opportunities: `1,500`
- committed opportunities: `163`
- overall conversion rate: `10.87%`
- total sales activities: `7,500`
- high-priority advisors: `132`
- coaching-opportunity RMs: `3`

## 5. Reporting Artifact Checks

The script confirms that the four chart files exist and are not empty:

- `reports/charts/sales_funnel_conversion.png`
- `reports/charts/rm_productivity.png`
- `reports/charts/campaign_roi.png`
- `reports/charts/product_demand.png`

It also confirms that README embeds for the selected visuals resolve to real chart files.

## 6. GitHub Actions

The GitHub Actions workflow runs the full pipeline and then runs `src/validate_outputs.py` on every push and pull request. This makes the project easier for recruiters, hiring managers, and reviewers to trust because the end-to-end outputs are checked automatically.
