# GitHub Repository Presentation

**Project:** Alternative Investment Sales Strategy Analytics Platform  
**Author:** Allen Xu

This note explains how the repository is organized for a recruiter, hiring manager, or technical reviewer.

## 1. Recommended Review Path

For a 30-second scan:

1. Read the top of `README.md`.
2. Review `Project Highlights`.
3. Look at the selected visuals embedded in the README.
4. Open `reports/executive_report.md` for the senior-stakeholder narrative.

For a technical review:

1. Inspect `src/generate_synthetic_data.py`.
2. Inspect `src/run_analysis.py`.
3. Review the SQL files under `sql/`.
4. Review `src/validate_outputs.py`.
5. Check `.github/workflows/validate.yml`.

For interview preparation:

1. Read `docs/INTERVIEW_NOTES.md`.
2. Review `docs/METHODOLOGY_AND_ASSUMPTIONS.md`.
3. Review `docs/DATA_QUALITY_CHECKS.md`.

## 2. What The Repository Demonstrates

- sales strategy analytics in an alternative investment distribution context
- Python data generation and analytics
- SQL analysis with SQLite-compatible scripts
- dashboard-ready data modeling
- executive communication
- ROI and productivity analysis
- reproducible validation through GitHub Actions

## 3. Files That Matter Most

| File or Folder | Purpose |
|---|---|
| `README.md` | Recruiter-facing overview and run instructions |
| `reports/executive_report.md` | Senior leadership analytics brief |
| `src/` | Python generation, database, analysis, chart, and validation scripts |
| `sql/` | SQLite-compatible analytical queries |
| `data/processed/` | Dashboard-ready marts |
| `dashboard/` | Tableau / Power BI implementation notes |
| `docs/` | Methodology, QA, and interview support |
| `.github/workflows/validate.yml` | Automated pipeline validation |

## 4. Review Notes

The repository intentionally commits synthetic CSV data and processed CSV outputs so reviewers can inspect the results without rerunning the full pipeline. The generated SQLite database is excluded by `.gitignore` because it is reproducible from the CSVs and should not be committed.

The project does not claim to use real KKR, advisor, investor, or fund data. The synthetic data is a safe way to demonstrate the structure, business logic, and communication style of a sales strategy analytics workflow.
