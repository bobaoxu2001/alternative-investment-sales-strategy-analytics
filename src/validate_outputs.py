"""
Validate generated outputs for the Alternative Investment Sales Strategy
Analytics Platform.

Author: Allen Xu

This script is intended for local QA and GitHub Actions. It verifies that the
deterministic synthetic pipeline produced the expected files, row counts, key
relationships, KPI values, and chart artifacts.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHARTS_DIR = PROJECT_ROOT / "reports" / "charts"
SITE_DATA_DIR = PROJECT_ROOT / "site" / "data"
README_PATH = PROJECT_ROOT / "README.md"

RAW_EXPECTED_ROWS = {
    "relationship_managers.csv": 16,
    "advisors.csv": 400,
    "funds.csv": 10,
    "campaigns.csv": 28,
    "sales_activities.csv": 7_500,
    "opportunities.csv": 1_500,
    "campaign_engagement.csv": 1_408,
}

PROCESSED_EXPECTED_ROWS = {
    "sales_funnel_summary.csv": 28,
    "rm_productivity_summary.csv": 16,
    "product_demand_summary.csv": 62,
    "campaign_roi_summary.csv": 28,
    "advisor_priority_scores.csv": 400,
    "executive_kpi_summary.csv": 14,
}

EXPECTED_KPIS = {
    "total_pipeline_value_usd": 58_811_000_000.0,
    "committed_capital_usd": 6_748_000_000.0,
    "opportunities_total": 1_500.0,
    "opportunities_committed": 163.0,
    "opportunities_lost": 218.0,
    "overall_conversion_rate_pct": 10.87,
    "avg_days_to_close": 149.8,
    "total_activities": 7_500.0,
    "avg_activity_engagement": 63.78,
    "total_campaign_spend_usd": 1_456_057.0,
    "campaign_attributable_committed_capital_usd": 2_769_500_000.0,
    "portfolio_campaign_roi_pct": 4_655.14,
    "high_priority_advisors": 132.0,
    "coaching_opportunity_rms": 3.0,
}

EXPECTED_CHARTS = [
    "sales_funnel_conversion.png",
    "rm_productivity.png",
    "campaign_roi.png",
    "product_demand.png",
]


def check(condition: bool, message: str, errors: list[str]) -> None:
    """Collect validation failures while printing readable pass/fail output."""
    if condition:
        print(f"PASS: {message}")
    else:
        print(f"FAIL: {message}")
        errors.append(message)


def read_csv(path: Path, errors: list[str]) -> pd.DataFrame:
    if not path.exists():
        errors.append(f"Missing file: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


def validate_row_counts(errors: list[str]) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    raw = {}
    processed = {}

    for file_name, expected_rows in RAW_EXPECTED_ROWS.items():
        df = read_csv(RAW_DIR / file_name, errors)
        raw[file_name] = df
        check(len(df) == expected_rows, f"{file_name} has {expected_rows:,} rows", errors)

    for file_name, expected_rows in PROCESSED_EXPECTED_ROWS.items():
        df = read_csv(PROCESSED_DIR / file_name, errors)
        processed[file_name] = df
        check(len(df) == expected_rows, f"{file_name} has {expected_rows:,} rows", errors)

    return raw, processed


def validate_unique_keys(raw: dict[str, pd.DataFrame], processed: dict[str, pd.DataFrame], errors: list[str]) -> None:
    unique_checks = [
        (raw["relationship_managers.csv"], "rm_id", "relationship manager IDs are unique"),
        (raw["advisors.csv"], "advisor_id", "advisor IDs are unique"),
        (raw["funds.csv"], "fund_id", "fund IDs are unique"),
        (raw["campaigns.csv"], "campaign_id", "campaign IDs are unique"),
        (raw["sales_activities.csv"], "activity_id", "activity IDs are unique"),
        (raw["opportunities.csv"], "opportunity_id", "opportunity IDs are unique"),
        (raw["campaign_engagement.csv"], "engagement_id", "campaign engagement IDs are unique"),
        (processed["advisor_priority_scores.csv"], "advisor_id", "advisor priority rows are unique by advisor"),
    ]

    for df, col, message in unique_checks:
        check(col in df.columns and df[col].is_unique, message, errors)


def validate_relationships(raw: dict[str, pd.DataFrame], errors: list[str]) -> None:
    advisors = set(raw["advisors.csv"]["advisor_id"])
    rms = set(raw["relationship_managers.csv"]["rm_id"])
    funds = set(raw["funds.csv"]["fund_id"])
    campaigns = set(raw["campaigns.csv"]["campaign_id"])

    activities = raw["sales_activities.csv"]
    opportunities = raw["opportunities.csv"]
    engagement = raw["campaign_engagement.csv"]

    check(set(activities["advisor_id"]).issubset(advisors), "sales activities reference valid advisors", errors)
    check(set(activities["rm_id"]).issubset(rms), "sales activities reference valid RMs", errors)
    check(set(opportunities["advisor_id"]).issubset(advisors), "opportunities reference valid advisors", errors)
    check(set(opportunities["rm_id"]).issubset(rms), "opportunities reference valid RMs", errors)
    check(set(opportunities["fund_id"]).issubset(funds), "opportunities reference valid funds", errors)
    check(set(engagement["campaign_id"]).issubset(campaigns), "campaign engagement references valid campaigns", errors)
    check(set(engagement["advisor_id"]).issubset(advisors), "campaign engagement references valid advisors", errors)

    sourced = opportunities["source_campaign_id"].dropna()
    check(set(sourced).issubset(campaigns), "campaign-sourced opportunities reference valid campaigns", errors)


def validate_kpis(processed: dict[str, pd.DataFrame], errors: list[str]) -> None:
    kpi_df = processed["executive_kpi_summary.csv"]
    if not {"kpi", "value"}.issubset(kpi_df.columns):
        check(False, "executive_kpi_summary.csv includes kpi and value columns", errors)
        return

    actual = kpi_df.set_index("kpi")["value"].to_dict()
    for kpi, expected in EXPECTED_KPIS.items():
        value = actual.get(kpi)
        check(value is not None and abs(float(value) - expected) < 0.01, f"KPI {kpi} matches expected value", errors)


def validate_charts_and_readme(errors: list[str]) -> None:
    for chart_name in EXPECTED_CHARTS:
        chart_path = CHARTS_DIR / chart_name
        check(chart_path.exists() and chart_path.stat().st_size > 0, f"{chart_name} exists and is non-empty", errors)

    readme = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    for image_path in [
        "reports/charts/sales_funnel_conversion.png",
        "reports/charts/campaign_roi.png",
    ]:
        check(image_path in readme, f"README embeds {image_path}", errors)
        check((PROJECT_ROOT / image_path).exists(), f"README image path exists: {image_path}", errors)


def validate_site_summary_metrics(processed: dict[str, pd.DataFrame],
                                  raw: dict[str, pd.DataFrame],
                                  errors: list[str]) -> None:
    summary_path = SITE_DATA_DIR / "summary_metrics.json"
    check(summary_path.exists(), "site/data/summary_metrics.json exists", errors)
    if not summary_path.exists():
        return

    import json

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    actual = processed["executive_kpi_summary.csv"].set_index("kpi")["value"].to_dict()
    priority = processed["advisor_priority_scores.csv"]

    comparisons = [
        ("expected_pipeline", "total_pipeline_value_usd"),
        ("committed_capital", "committed_capital_usd"),
        ("conversion_rate", "overall_conversion_rate_pct"),
        ("campaign_spend", "total_campaign_spend_usd"),
        ("avg_days_to_close", "avg_days_to_close"),
    ]
    for json_key, kpi_key in comparisons:
        value = summary.get(json_key, {}).get("value")
        expected = actual.get(kpi_key)
        check(value is not None and expected is not None and abs(float(value) - float(expected)) < 0.01,
              f"summary_metrics.json {json_key} matches {kpi_key}", errors)

    check(summary.get("advisor_count", {}).get("value") == len(raw["advisors.csv"]),
          "summary_metrics.json advisor_count matches raw advisors", errors)
    check(summary.get("relationship_manager_count", {}).get("value") == len(raw["relationship_managers.csv"]),
          "summary_metrics.json relationship_manager_count matches raw RMs", errors)
    check(summary.get("high_priority_advisor_count", {}).get("value")
          == int((priority["priority_tier"] == "High").sum()),
          "summary_metrics.json high priority count matches advisor mart", errors)
    check("synthetic" in summary.get("synthetic_data_disclaimer", "").lower(),
          "summary_metrics.json includes synthetic data disclosure", errors)


def main() -> None:
    errors: list[str] = []
    print("Validating analytics pipeline outputs...\n")

    raw, processed = validate_row_counts(errors)
    validate_unique_keys(raw, processed, errors)
    validate_relationships(raw, errors)
    validate_kpis(processed, errors)
    validate_charts_and_readme(errors)
    validate_site_summary_metrics(processed, raw, errors)

    if errors:
        print("\nValidation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("\nAll validation checks passed.")


if __name__ == "__main__":
    main()
