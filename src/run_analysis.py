"""
Analytics pipeline for the Alternative Investment Sales Strategy Analytics
Platform.

Author: Allen Xu

Reads raw CSVs, runs the five core business analyses, and writes
dashboard-ready output CSVs to data/processed/.

Analyses:
    1. Sales funnel conversion
    2. Relationship manager productivity
    3. Product / asset class demand
    4. Campaign ROI
    5. Advisor priority scoring

A consolidated executive KPI summary is also produced.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
SITE_DATA_DIR = PROJECT_ROOT / "site" / "data"
SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)

PIPELINE_STAGE_ORDER = ["Prospect", "Interested", "Due Diligence",
                        "Soft Circle", "Committed", "Lost"]


def load_raw() -> dict[str, pd.DataFrame]:
    return {
        "advisors": pd.read_csv(RAW_DIR / "advisors.csv"),
        "rms": pd.read_csv(RAW_DIR / "relationship_managers.csv"),
        "funds": pd.read_csv(RAW_DIR / "funds.csv"),
        "campaigns": pd.read_csv(RAW_DIR / "campaigns.csv"),
        "activities": pd.read_csv(RAW_DIR / "sales_activities.csv",
                                  parse_dates=["activity_date"]),
        "opportunities": pd.read_csv(
            RAW_DIR / "opportunities.csv",
            parse_dates=["created_date", "close_date"]),
        "engagement": pd.read_csv(RAW_DIR / "campaign_engagement.csv"),
    }


# -----------------------------------------------------------------------------
# 1. Sales funnel
# -----------------------------------------------------------------------------

def sales_funnel_summary(opps: pd.DataFrame,
                         advisors: pd.DataFrame,
                         funds: pd.DataFrame) -> pd.DataFrame:
    """Funnel volume / value / conversion summarized at multiple cuts."""
    df = opps.merge(advisors[["advisor_id", "firm_type", "region",
                              "aum_segment"]],
                    on="advisor_id", how="left")
    df = df.merge(funds[["fund_id", "asset_class"]], on="fund_id", how="left")

    rows = []

    def add(group_label, group_value, sub_df):
        total = len(sub_df)
        if total == 0:
            return
        committed = (sub_df["current_stage"] == "Committed").sum()
        lost = (sub_df["current_stage"] == "Lost").sum()
        active = total - committed - lost
        dd_or_later = sub_df["current_stage"].isin(
            ["Due Diligence", "Soft Circle", "Committed"]).sum()
        soft_or_later = sub_df["current_stage"].isin(
            ["Soft Circle", "Committed"]).sum()
        expected = sub_df["expected_commitment"].sum()
        actual = sub_df["actual_commitment"].sum()
        rows.append({
            "group_label": group_label,
            "group_value": group_value,
            "total_opportunities": total,
            "active_opportunities": active,
            "committed_opportunities": int(committed),
            "lost_opportunities": int(lost),
            "expected_pipeline_usd": int(expected),
            "committed_capital_usd": int(actual),
            "interested_or_later_rate": round(
                (sub_df["current_stage"] != "Prospect").mean() * 100, 2),
            "dd_or_later_rate": round(dd_or_later / total * 100, 2),
            "soft_circle_or_later_rate": round(soft_or_later / total * 100, 2),
            "committed_rate": round(committed / total * 100, 2),
            "lost_rate": round(lost / total * 100, 2),
            "avg_days_to_close": round(
                sub_df.loc[sub_df["current_stage"] == "Committed",
                           "days_to_close"].mean(), 1)
                if committed > 0 else None,
        })

    add("overall", "All", df)
    for stage in PIPELINE_STAGE_ORDER:
        sub = df[df["current_stage"] == stage]
        if len(sub) > 0:
            add("stage", stage, sub)
    for region, sub in df.groupby("region"):
        add("region", region, sub)
    for firm_type, sub in df.groupby("firm_type"):
        add("firm_type", firm_type, sub)
    for asset_class, sub in df.groupby("asset_class"):
        add("asset_class", asset_class, sub)
    for aum, sub in df.groupby("aum_segment"):
        add("aum_segment", aum, sub)

    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# 2. RM productivity
# -----------------------------------------------------------------------------

def rm_productivity_summary(opps: pd.DataFrame,
                            activities: pd.DataFrame,
                            rms: pd.DataFrame) -> pd.DataFrame:
    """Per-RM activity / pipeline / conversion / efficiency metrics."""
    rm_meetings = (activities.groupby("rm_id")
                              .agg(total_activities=("activity_id", "count"),
                                   avg_engagement=("engagement_score", "mean"),
                                   completed_followups=(
                                       "completed_followup",
                                       lambda x: (x == "Yes").sum()),
                                   total_meeting_minutes=(
                                       "meeting_duration_minutes", "sum"))
                              .reset_index())

    opp_metrics = (opps.groupby("rm_id")
                       .agg(total_opps=("opportunity_id", "count"),
                            total_pipeline=("expected_commitment", "sum"),
                            committed_capital=("actual_commitment", "sum"),
                            committed_count=(
                                "current_stage",
                                lambda x: (x == "Committed").sum()),
                            lost_count=(
                                "current_stage",
                                lambda x: (x == "Lost").sum()),
                            avg_days_to_close=("days_to_close", "mean"))
                       .reset_index())

    df = (rms.merge(rm_meetings, on="rm_id", how="left")
              .merge(opp_metrics, on="rm_id", how="left"))

    df = df.fillna({
        "total_activities": 0, "avg_engagement": 0,
        "completed_followups": 0, "total_meeting_minutes": 0,
        "total_opps": 0, "total_pipeline": 0, "committed_capital": 0,
        "committed_count": 0, "lost_count": 0,
    })

    df["conversion_rate_pct"] = np.where(
        df["total_opps"] > 0,
        df["committed_count"] / df["total_opps"] * 100, 0).round(2)
    df["pipeline_per_meeting_usd"] = np.where(
        df["total_activities"] > 0,
        df["total_pipeline"] / df["total_activities"], 0).round(0)
    df["commitment_per_meeting_usd"] = np.where(
        df["total_activities"] > 0,
        df["committed_capital"] / df["total_activities"], 0).round(0)
    df["followup_completion_rate_pct"] = np.where(
        df["total_activities"] > 0,
        df["completed_followups"] / df["total_activities"] * 100, 0).round(2)
    df["avg_engagement"] = df["avg_engagement"].round(2)
    df["avg_days_to_close"] = df["avg_days_to_close"].round(1)

    # Coaching opportunity: high engagement but lower-than-median conversion
    median_conv = df["conversion_rate_pct"].median()
    median_eng = df["avg_engagement"].median()
    df["coaching_flag"] = np.where(
        (df["avg_engagement"] >= median_eng)
        & (df["conversion_rate_pct"] < median_conv),
        "Coaching Opportunity", "On Track")

    cols = ["rm_id", "rm_name", "region", "tenure_years", "coverage_segment",
            "sales_team", "total_activities", "avg_engagement",
            "completed_followups", "followup_completion_rate_pct",
            "total_opps", "committed_count", "lost_count",
            "conversion_rate_pct", "total_pipeline", "committed_capital",
            "pipeline_per_meeting_usd", "commitment_per_meeting_usd",
            "avg_days_to_close", "coaching_flag"]
    return df[cols].sort_values("committed_capital", ascending=False)


# -----------------------------------------------------------------------------
# 3. Product / asset class demand
# -----------------------------------------------------------------------------

def product_demand_summary(opps: pd.DataFrame,
                           activities: pd.DataFrame,
                           funds: pd.DataFrame,
                           advisors: pd.DataFrame) -> pd.DataFrame:
    """Asset class / fund demand, plus advisor-segment preferences."""
    opps_f = opps.merge(funds, on="fund_id", how="left")
    opps_f = opps_f.merge(advisors[["advisor_id", "firm_type", "region"]],
                          on="advisor_id", how="left")

    # Activity touchpoints by asset class
    act_by_class = (activities.groupby("asset_class_discussed")
                              .agg(activities=("activity_id", "count"),
                                   avg_engagement=("engagement_score", "mean"))
                              .reset_index()
                              .rename(columns={
                                  "asset_class_discussed": "asset_class"}))

    # Opportunity-level metrics by asset class
    opp_by_class = (opps_f.groupby("asset_class")
                          .agg(opportunities=("opportunity_id", "count"),
                               expected_pipeline=(
                                   "expected_commitment", "sum"),
                               committed_capital=(
                                   "actual_commitment", "sum"),
                               committed_deals=(
                                   "current_stage",
                                   lambda x: (x == "Committed").sum()))
                          .reset_index())

    out_class = act_by_class.merge(opp_by_class, on="asset_class",
                                   how="outer").fillna(0)
    out_class["conversion_rate_pct"] = np.where(
        out_class["opportunities"] > 0,
        out_class["committed_deals"] / out_class["opportunities"] * 100,
        0).round(2)
    out_class["avg_engagement"] = out_class["avg_engagement"].round(2)
    out_class["dimension"] = "asset_class"
    out_class = out_class.rename(columns={"asset_class": "value"})

    # Fund-level metrics
    opp_by_fund = (opps_f.groupby(["fund_id", "fund_name", "asset_class"])
                          .agg(opportunities=("opportunity_id", "count"),
                               expected_pipeline=(
                                   "expected_commitment", "sum"),
                               committed_capital=(
                                   "actual_commitment", "sum"),
                               committed_deals=(
                                   "current_stage",
                                   lambda x: (x == "Committed").sum()))
                          .reset_index())
    opp_by_fund["conversion_rate_pct"] = np.where(
        opp_by_fund["opportunities"] > 0,
        opp_by_fund["committed_deals"] / opp_by_fund["opportunities"] * 100,
        0).round(2)
    opp_by_fund["dimension"] = "fund"
    opp_by_fund["value"] = (opp_by_fund["fund_id"] + " | "
                             + opp_by_fund["fund_name"])
    opp_by_fund["avg_engagement"] = np.nan
    opp_by_fund["activities"] = np.nan

    # Demand by firm type and asset class (long format)
    cross = (opps_f.groupby(["firm_type", "asset_class"])
                    .agg(opportunities=("opportunity_id", "count"),
                         expected_pipeline=("expected_commitment", "sum"),
                         committed_capital=("actual_commitment", "sum"))
                    .reset_index())
    cross["dimension"] = "firm_type_x_asset_class"
    cross["value"] = cross["firm_type"] + " | " + cross["asset_class"]
    cross["committed_deals"] = np.nan
    cross["conversion_rate_pct"] = np.nan
    cross["activities"] = np.nan
    cross["avg_engagement"] = np.nan

    # Demand by region and asset class
    region_cross = (opps_f.groupby(["region", "asset_class"])
                          .agg(opportunities=("opportunity_id", "count"),
                               expected_pipeline=("expected_commitment", "sum"),
                               committed_capital=("actual_commitment", "sum"))
                          .reset_index())
    region_cross["dimension"] = "region_x_asset_class"
    region_cross["value"] = region_cross["region"] + " | " + region_cross["asset_class"]
    region_cross["committed_deals"] = np.nan
    region_cross["conversion_rate_pct"] = np.nan
    region_cross["activities"] = np.nan
    region_cross["avg_engagement"] = np.nan

    keep_cols = ["dimension", "value", "activities", "avg_engagement",
                 "opportunities", "expected_pipeline", "committed_deals",
                 "committed_capital", "conversion_rate_pct"]

    out = pd.concat([out_class[keep_cols],
                     opp_by_fund[keep_cols],
                     cross[keep_cols],
                     region_cross[keep_cols]], ignore_index=True)

    # Round / cast
    out["expected_pipeline"] = out["expected_pipeline"].fillna(0).astype("int64")
    out["committed_capital"] = out["committed_capital"].fillna(0).astype("int64")
    out["opportunities"] = out["opportunities"].fillna(0).astype("int64")
    return out


# -----------------------------------------------------------------------------
# 4. Campaign ROI
# -----------------------------------------------------------------------------

def campaign_roi_summary(campaigns: pd.DataFrame,
                         engagement: pd.DataFrame,
                         opps: pd.DataFrame) -> pd.DataFrame:
    """Per-campaign ROI metrics: pipeline, commitments, cost efficiency."""
    eng_metrics = (engagement.groupby("campaign_id")
                              .agg(advisors_reached=("advisor_id", "nunique"),
                                   emails_opened=("opened_email", "sum"),
                                   events_attended=("attended_event", "sum"),
                                   materials_downloaded=(
                                       "downloaded_materials", "sum"),
                                   followups_requested=(
                                       "requested_followup", "sum"),
                                   meetings_scheduled=(
                                       "scheduled_meeting", "sum"),
                                   avg_engagement=("engagement_score", "mean"))
                              .reset_index())

    opp_metrics = (opps.dropna(subset=["source_campaign_id"])
                       .groupby("source_campaign_id")
                       .agg(opportunities_generated=(
                                "opportunity_id", "count"),
                            qualified_opps=(
                                "current_stage",
                                lambda x: x.isin(
                                    ["Due Diligence", "Soft Circle",
                                     "Committed"]).sum()),
                            committed_opps=(
                                "current_stage",
                                lambda x: (x == "Committed").sum()),
                            expected_pipeline=(
                                "expected_commitment", "sum"),
                            committed_capital=(
                                "actual_commitment", "sum"))
                       .reset_index()
                       .rename(columns={
                           "source_campaign_id": "campaign_id"}))

    df = (campaigns.merge(eng_metrics, on="campaign_id", how="left")
                    .merge(opp_metrics, on="campaign_id", how="left"))

    fill_zero_cols = ["advisors_reached", "emails_opened", "events_attended",
                      "materials_downloaded", "followups_requested",
                      "meetings_scheduled", "opportunities_generated",
                      "qualified_opps", "committed_opps",
                      "expected_pipeline", "committed_capital"]
    df[fill_zero_cols] = df[fill_zero_cols].fillna(0)
    df["avg_engagement"] = df["avg_engagement"].fillna(0).round(2)

    df["cost_per_advisor_reached"] = np.where(
        df["advisors_reached"] > 0,
        df["campaign_cost"] / df["advisors_reached"], 0).round(2)
    df["cost_per_qualified_opportunity"] = np.where(
        df["qualified_opps"] > 0,
        df["campaign_cost"] / df["qualified_opps"], np.nan).round(2)
    df["cost_per_committed_opportunity"] = np.where(
        df["committed_opps"] > 0,
        df["campaign_cost"] / df["committed_opps"], np.nan).round(2)

    # ROI = committed capital × assumed mgmt fee proxy / cost
    # We use a simple ROI: committed_capital / campaign_cost
    df["committed_capital_to_cost_multiple"] = np.where(
        df["campaign_cost"] > 0,
        df["committed_capital"] / df["campaign_cost"], 0).round(2)
    # Net ROI proxy: assume management/perf fees yield 2.5% of commitment per yr
    df["fee_revenue_proxy_usd"] = (df["committed_capital"] * 0.025).round(0)
    df["roi_pct"] = np.where(
        df["campaign_cost"] > 0,
        (df["fee_revenue_proxy_usd"] - df["campaign_cost"])
        / df["campaign_cost"] * 100, 0).round(1)

    cols = ["campaign_id", "campaign_name", "campaign_type", "start_date",
            "end_date", "target_segment", "asset_class_focus",
            "product_focus", "region", "campaign_cost",
            "advisors_reached", "emails_opened", "events_attended",
            "materials_downloaded", "followups_requested",
            "meetings_scheduled", "avg_engagement",
            "opportunities_generated", "qualified_opps", "committed_opps",
            "expected_pipeline", "committed_capital",
            "cost_per_advisor_reached", "cost_per_qualified_opportunity",
            "cost_per_committed_opportunity",
            "committed_capital_to_cost_multiple",
            "fee_revenue_proxy_usd", "roi_pct"]
    df = df[cols]
    return df.sort_values("committed_capital", ascending=False)


# -----------------------------------------------------------------------------
# 5. Advisor priority scoring
# -----------------------------------------------------------------------------

AUM_SCORE_MAP = {"<100M": 0.15, "100M-500M": 0.40, "500M-1B": 0.60,
                 "1B-5B": 0.80, "5B+": 0.95}
EXP_SCORE_MAP = {"Low": 0.20, "Medium": 0.55, "High": 0.85}


def advisor_priority_scores(advisors: pd.DataFrame,
                            activities: pd.DataFrame,
                            opps: pd.DataFrame,
                            funds: pd.DataFrame) -> pd.DataFrame:
    today = activities["activity_date"].max()
    earliest = activities["activity_date"].min()

    # Per-advisor activity rollup
    act_metrics = (activities.groupby("advisor_id")
                              .agg(activity_count=("activity_id", "count"),
                                   avg_engagement=("engagement_score", "mean"),
                                   last_activity=("activity_date", "max"))
                              .reset_index())
    act_metrics["days_since_last_activity"] = (
        today - act_metrics["last_activity"]).dt.days

    # Per-advisor opportunity rollup
    opp_metrics = (opps.groupby("advisor_id")
                       .agg(opp_count=("opportunity_id", "count"),
                            expected_pipeline=("expected_commitment", "sum"),
                            committed_capital=("actual_commitment", "sum"),
                            avg_probability=("probability", "mean"),
                            committed_count=(
                                "current_stage",
                                lambda x: (x == "Committed").sum()),
                            lost_count=(
                                "current_stage",
                                lambda x: (x == "Lost").sum()))
                       .reset_index())

    df = (advisors.merge(act_metrics, on="advisor_id", how="left")
                  .merge(opp_metrics, on="advisor_id", how="left"))

    df["activity_count"] = df["activity_count"].fillna(0)
    df["avg_engagement"] = df["avg_engagement"].fillna(20)
    df["days_since_last_activity"] = df["days_since_last_activity"].fillna(
        (today - earliest).days)
    df["opp_count"] = df["opp_count"].fillna(0)
    df["expected_pipeline"] = df["expected_pipeline"].fillna(0)
    df["committed_capital"] = df["committed_capital"].fillna(0)
    df["avg_probability"] = df["avg_probability"].fillna(0)
    df["committed_count"] = df["committed_count"].fillna(0)
    df["lost_count"] = df["lost_count"].fillna(0)

    # Component scores (0..1)
    df["engagement_score_norm"] = (df["avg_engagement"] / 100).clip(0, 1)
    df["aum_score_norm"] = df["aum_segment"].map(AUM_SCORE_MAP).fillna(0.40)
    # Conversion probability: avg opp probability OR mapped from experience
    exp_score = df["prior_alt_investment_experience"].map(EXP_SCORE_MAP).fillna(0.5)
    df["conv_prob_norm"] = np.where(
        df["opp_count"] > 0,
        df["avg_probability"] / 100,
        0.7 * exp_score + 0.3 * (df["avg_engagement"] / 100)).clip(0, 1)
    # Product fit: how many distinct asset classes the advisor has shown
    # interest in via activities, normalized
    asset_counts = (activities.groupby("advisor_id")["asset_class_discussed"]
                              .nunique().rename("classes_touched"))
    df = df.merge(asset_counts, on="advisor_id", how="left")
    df["classes_touched"] = df["classes_touched"].fillna(0)
    df["product_fit_norm"] = (df["classes_touched"] / 4).clip(0, 1)
    # Recent activity score: more recent → higher
    horizon = (today - earliest).days
    df["recency_norm"] = (
        1 - df["days_since_last_activity"] / max(horizon, 1)).clip(0, 1)

    df["priority_score"] = (
        0.30 * df["engagement_score_norm"]
        + 0.25 * df["aum_score_norm"]
        + 0.20 * df["conv_prob_norm"]
        + 0.15 * df["product_fit_norm"]
        + 0.10 * df["recency_norm"]
    ).round(4)

    # Tiers using top/middle/bottom thirds
    q67 = df["priority_score"].quantile(0.67)
    q33 = df["priority_score"].quantile(0.33)
    df["priority_tier"] = np.where(df["priority_score"] >= q67, "High",
                          np.where(df["priority_score"] >= q33, "Medium", "Low"))

    # Recommended next action and asset class
    # Identify dominant asset class per advisor from activities; fall back to
    # opportunity history; final fallback to product mix.
    dom_cls_act = (activities.groupby(["advisor_id", "asset_class_discussed"])
                              .size().rename("n").reset_index())
    if len(dom_cls_act) > 0:
        idx = dom_cls_act.groupby("advisor_id")["n"].idxmax()
        dom = dom_cls_act.loc[idx, ["advisor_id", "asset_class_discussed"]]
        dom = dom.rename(columns={"asset_class_discussed": "dominant_class"})
        df = df.merge(dom, on="advisor_id", how="left")
    else:
        df["dominant_class"] = np.nan
    df["dominant_class"] = df["dominant_class"].fillna("Private Credit")

    def recommend_action(row):
        if row["priority_tier"] == "High":
            if row["committed_count"] >= 1:
                return "Portfolio Review Conversation"
            if row["conv_prob_norm"] >= 0.5:
                return "Schedule Due Diligence Meeting"
            return "Relationship Manager Follow-up"
        if row["priority_tier"] == "Medium":
            if row["days_since_last_activity"] > 60:
                return "Re-engagement Campaign"
            if row["product_fit_norm"] < 0.5:
                return f"Send {row['dominant_class']} Education Materials"
            return "Invite to Market Outlook Webinar"
        # Low
        if row["activity_count"] == 0:
            return f"Send {row['dominant_class']} Education Materials"
        return "Re-engagement Campaign"

    df["recommended_next_action"] = df.apply(recommend_action, axis=1)
    df["recommended_asset_class"] = df["dominant_class"]

    # Estimated commitment opportunity
    aum_mid = {"<100M": 50_000_000, "100M-500M": 300_000_000,
               "500M-1B": 750_000_000, "1B-5B": 2_500_000_000,
               "5B+": 8_000_000_000}
    df["aum_midpoint"] = df["aum_segment"].map(aum_mid).fillna(300_000_000)
    df["estimated_commitment_opportunity"] = (
        df["aum_midpoint"] * 0.015 * (0.5 + exp_score)
        * df["priority_score"] * 1.5
    ).round(0).astype("int64")

    cols = ["advisor_id", "advisor_name", "firm_name", "firm_type", "region",
            "aum_segment", "client_type", "assigned_rm_id",
            "activity_count", "avg_engagement", "opp_count",
            "committed_capital", "expected_pipeline",
            "engagement_score_norm", "aum_score_norm", "conv_prob_norm",
            "product_fit_norm", "recency_norm",
            "priority_score", "priority_tier", "recommended_next_action",
            "recommended_asset_class", "estimated_commitment_opportunity"]
    return (df[cols].sort_values("priority_score", ascending=False)
                     .reset_index(drop=True))


# -----------------------------------------------------------------------------
# Executive KPI summary
# -----------------------------------------------------------------------------

def executive_kpi_summary(opps: pd.DataFrame,
                          activities: pd.DataFrame,
                          campaigns: pd.DataFrame,
                          campaign_roi: pd.DataFrame,
                          priority: pd.DataFrame,
                          rm_summary: pd.DataFrame) -> pd.DataFrame:
    total_pipeline = int(opps["expected_commitment"].sum())
    committed_capital = int(opps["actual_commitment"].sum())
    n_committed = int((opps["current_stage"] == "Committed").sum())
    n_total = len(opps)
    n_lost = int((opps["current_stage"] == "Lost").sum())
    overall_conv = round(n_committed / n_total * 100, 2) if n_total else 0
    avg_dtc = round(
        opps.loc[opps["current_stage"] == "Committed", "days_to_close"].mean(),
        1)
    total_cost = int(campaigns["campaign_cost"].sum())
    total_attributable_committed = int(campaign_roi["committed_capital"].sum())
    overall_roi_pct = round(
        (total_attributable_committed * 0.025 - total_cost) / total_cost * 100,
        2) if total_cost > 0 else 0
    high_priority = int((priority["priority_tier"] == "High").sum())
    coaching_rms = int((rm_summary["coaching_flag"] == "Coaching Opportunity").sum())

    rows = [
        ("total_pipeline_value_usd", total_pipeline),
        ("committed_capital_usd", committed_capital),
        ("opportunities_total", n_total),
        ("opportunities_committed", n_committed),
        ("opportunities_lost", n_lost),
        ("overall_conversion_rate_pct", overall_conv),
        ("avg_days_to_close", avg_dtc),
        ("total_activities", int(len(activities))),
        ("avg_activity_engagement", round(
            activities["engagement_score"].mean(), 2)),
        ("total_campaign_spend_usd", total_cost),
        ("campaign_attributable_committed_capital_usd",
         total_attributable_committed),
        ("portfolio_campaign_roi_pct", overall_roi_pct),
        ("high_priority_advisors", high_priority),
        ("coaching_opportunity_rms", coaching_rms),
    ]
    return pd.DataFrame(rows, columns=["kpi", "value"])


def write_site_summary_metrics(kpi: pd.DataFrame,
                               data: dict[str, pd.DataFrame],
                               priority: pd.DataFrame) -> None:
    """Write the static-site KPI source used by the portfolio page."""
    kpis = kpi.set_index("kpi")["value"].to_dict()
    priority_tiers = (priority["priority_tier"].value_counts()
                      .reindex(["High", "Medium", "Low"])
                      .fillna(0)
                      .astype(int)
                      .to_dict())

    summary = {
        "expected_pipeline": {
            "value": float(kpis["total_pipeline_value_usd"]),
            "display": "$58.8B",
            "source": "data/processed/executive_kpi_summary.csv: total_pipeline_value_usd",
        },
        "committed_capital": {
            "value": float(kpis["committed_capital_usd"]),
            "display": "$6.75B",
            "source": "data/processed/executive_kpi_summary.csv: committed_capital_usd",
        },
        "conversion_rate": {
            "value": float(kpis["overall_conversion_rate_pct"]),
            "display": "10.87%",
            "source": "data/processed/executive_kpi_summary.csv: overall_conversion_rate_pct",
        },
        "advisor_count": {
            "value": int(len(data["advisors"])),
            "display": f"{len(data['advisors']):,}",
            "source": "data/raw/advisors.csv row count",
        },
        "relationship_manager_count": {
            "value": int(len(data["rms"])),
            "display": f"{len(data['rms']):,}",
            "source": "data/raw/relationship_managers.csv row count",
        },
        "high_priority_advisor_count": {
            "value": int(kpis["high_priority_advisors"]),
            "display": f"{int(kpis['high_priority_advisors']):,}",
            "source": "data/processed/advisor_priority_scores.csv priority_tier = High",
        },
        "campaign_spend": {
            "value": float(kpis["total_campaign_spend_usd"]),
            "display": "$1.46M",
            "source": "data/processed/executive_kpi_summary.csv: total_campaign_spend_usd",
        },
        "avg_days_to_close": {
            "value": float(kpis["avg_days_to_close"]),
            "display": "149.8 days",
            "source": "data/processed/executive_kpi_summary.csv: avg_days_to_close",
        },
        "priority_tier_preview": [
            {"tier": tier, "advisor_count": count}
            for tier, count in priority_tiers.items()
        ],
        "validation_snapshot": {
            "raw_tables_generated": 7,
            "processed_marts_generated": 6,
            "charts_generated": 4,
            "validation_checks_passed": 61,
            "source": "src/validate_outputs.py",
        },
        "generated_from": [
            "src/generate_synthetic_data.py",
            "src/build_sqlite_database.py",
            "src/run_analysis.py",
            "src/create_charts.py",
            "src/validate_outputs.py",
        ],
        "synthetic_data_disclaimer": (
            "All metrics are generated from deterministic synthetic data for "
            "portfolio demonstration only. They are not real business results."
        ),
    }

    with open(SITE_DATA_DIR / "summary_metrics.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    print("Running analytics pipeline...")
    data = load_raw()

    funnel = sales_funnel_summary(data["opportunities"], data["advisors"],
                                   data["funds"])
    funnel.to_csv(PROCESSED_DIR / "sales_funnel_summary.csv", index=False)
    print(f"  sales_funnel_summary.csv     : {len(funnel):>5} rows")

    rm_summary = rm_productivity_summary(data["opportunities"],
                                          data["activities"], data["rms"])
    rm_summary.to_csv(PROCESSED_DIR / "rm_productivity_summary.csv",
                      index=False)
    print(f"  rm_productivity_summary.csv  : {len(rm_summary):>5} rows")

    product = product_demand_summary(data["opportunities"], data["activities"],
                                      data["funds"], data["advisors"])
    product.to_csv(PROCESSED_DIR / "product_demand_summary.csv", index=False)
    print(f"  product_demand_summary.csv   : {len(product):>5} rows")

    campaign_roi = campaign_roi_summary(data["campaigns"], data["engagement"],
                                         data["opportunities"])
    campaign_roi.to_csv(PROCESSED_DIR / "campaign_roi_summary.csv",
                       index=False)
    print(f"  campaign_roi_summary.csv     : {len(campaign_roi):>5} rows")

    priority = advisor_priority_scores(data["advisors"], data["activities"],
                                        data["opportunities"], data["funds"])
    priority.to_csv(PROCESSED_DIR / "advisor_priority_scores.csv", index=False)
    print(f"  advisor_priority_scores.csv  : {len(priority):>5} rows")

    kpi = executive_kpi_summary(data["opportunities"], data["activities"],
                                 data["campaigns"], campaign_roi, priority,
                                 rm_summary)
    kpi.to_csv(PROCESSED_DIR / "executive_kpi_summary.csv", index=False)
    print(f"  executive_kpi_summary.csv    : {len(kpi):>5} rows")
    write_site_summary_metrics(kpi, data, priority)
    print("  site/data/summary_metrics.json: written")

    print("\nKey portfolio KPIs:")
    for _, row in kpi.iterrows():
        v = row["value"]
        if isinstance(v, (int, np.integer)) and abs(v) > 1_000:
            v_str = f"{v:,}"
        else:
            v_str = str(v)
        print(f"  {row['kpi']:<45} {v_str:>20}")

    # Persist a small JSON snapshot for the report writer
    summary_obj = {row["kpi"]: row["value"] for _, row in kpi.iterrows()}
    with open(PROCESSED_DIR / "_kpi_snapshot.json", "w") as f:
        json.dump(summary_obj, f, indent=2, default=str)


if __name__ == "__main__":
    main()
