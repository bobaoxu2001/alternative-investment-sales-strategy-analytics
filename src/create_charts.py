"""
Generate executive charts (PNG) from processed analytics outputs.

Author: Allen Xu

Charts:
    1. Sales funnel conversion (volumes by stage)
    2. RM productivity leaderboard (committed capital + conversion)
    3. Campaign ROI vs cost
    4. Asset class demand (engagement + committed capital)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHARTS_DIR = PROJECT_ROOT / "reports" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 130,
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

NAVY = "#0F2A47"
TEAL = "#2A8C8C"
GOLD = "#D6A75E"
SLATE = "#5B6B7C"
SOFT_RED = "#C0504D"


def millions(x_usd: float) -> float:
    return x_usd / 1_000_000


def chart_sales_funnel():
    df = pd.read_csv(PROCESSED_DIR / "sales_funnel_summary.csv")
    stage_df = df[df["group_label"] == "stage"].copy()
    order = ["Prospect", "Interested", "Due Diligence", "Soft Circle",
             "Committed", "Lost"]
    stage_df["group_value"] = pd.Categorical(stage_df["group_value"],
                                              categories=order, ordered=True)
    stage_df = stage_df.sort_values("group_value")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = [NAVY, TEAL, GOLD, "#A86F2D", "#1F7A1F", SOFT_RED]
    bars = ax.bar(stage_df["group_value"].astype(str),
                  stage_df["total_opportunities"], color=colors,
                  edgecolor="white")
    for bar, val, eng in zip(bars, stage_df["total_opportunities"],
                              stage_df["expected_pipeline_usd"]):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 5,
                f"{int(val)} opps\n${millions(eng):.0f}M",
                ha="center", va="bottom", fontsize=9, color=NAVY)

    ax.set_title("Sales Funnel: Opportunities by Stage")
    ax.set_ylabel("Opportunities")
    ax.set_ylim(0, stage_df["total_opportunities"].max() * 1.25)
    ax.grid(axis="y", alpha=0.25)
    ax.text(0.99, -0.15,
            "Source: synthetic dataset | Author: Allen Xu",
            transform=ax.transAxes, ha="right", fontsize=8, color=SLATE)
    plt.tight_layout()
    out = CHARTS_DIR / "sales_funnel_conversion.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    return out


def chart_rm_productivity():
    df = pd.read_csv(PROCESSED_DIR / "rm_productivity_summary.csv")
    df = df.sort_values("committed_capital", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    bars = ax.barh(df["rm_name"], df["committed_capital"] / 1_000_000,
                    color=[GOLD if c == "Coaching Opportunity" else NAVY
                           for c in df["coaching_flag"]])
    ax.set_xlabel("Committed Capital (USD millions)")
    ax.set_title("Relationship Manager Productivity: Committed Capital and "
                  "Conversion")
    ax.grid(axis="x", alpha=0.25)

    for bar, conv, flag in zip(bars, df["conversion_rate_pct"],
                                df["coaching_flag"]):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                f"{conv:.1f}% conv", va="center", fontsize=8, color=SLATE)

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=NAVY),
        plt.Rectangle((0, 0), 1, 1, color=GOLD),
    ]
    ax.legend(handles, ["On Track", "Coaching Opportunity"],
              loc="lower right", frameon=False)
    ax.text(0.99, -0.10,
            "Source: synthetic dataset | Author: Allen Xu",
            transform=ax.transAxes, ha="right", fontsize=8, color=SLATE)
    plt.tight_layout()
    out = CHARTS_DIR / "rm_productivity.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    return out


def chart_campaign_roi():
    df = pd.read_csv(PROCESSED_DIR / "campaign_roi_summary.csv")
    type_df = (df.groupby("campaign_type")
                  .agg(spend=("campaign_cost", "sum"),
                       committed=("committed_capital", "sum"),
                       qualified=("qualified_opps", "sum"))
                  .reset_index())
    type_df["multiple"] = type_df["committed"] / type_df["spend"]
    type_df = type_df.sort_values("multiple", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = [TEAL if m >= type_df["multiple"].median() else SLATE
              for m in type_df["multiple"]]
    bars = ax.barh(type_df["campaign_type"], type_df["multiple"], color=colors)
    ax.set_xlabel("Committed Capital ÷ Campaign Spend (multiple)")
    ax.set_title("Campaign Efficiency by Type: Committed Capital per Dollar "
                  "Spent")
    ax.grid(axis="x", alpha=0.25)
    for bar, m, spend in zip(bars, type_df["multiple"], type_df["spend"]):
        ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height() / 2,
                f"{m:,.0f}x  (spend ${millions(spend):.0f}M)",
                va="center", fontsize=9, color=SLATE)
    ax.text(0.99, -0.15,
            "Source: synthetic dataset | Author: Allen Xu",
            transform=ax.transAxes, ha="right", fontsize=8, color=SLATE)
    plt.tight_layout()
    out = CHARTS_DIR / "campaign_roi.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    return out


def chart_product_demand():
    df = pd.read_csv(PROCESSED_DIR / "product_demand_summary.csv")
    cls = df[df["dimension"] == "asset_class"].copy()
    cls = cls.sort_values("committed_capital", ascending=True)

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    bars = ax1.barh(cls["value"], cls["committed_capital"] / 1_000_000,
                     color=NAVY, label="Committed Capital ($M)")
    ax1.set_xlabel("Committed Capital (USD millions)")
    ax1.grid(axis="x", alpha=0.25)
    ax1.set_title("Product Demand by Asset Class: Committed Capital + "
                   "Engagement")

    ax2 = ax1.twiny()
    ax2.plot(cls["avg_engagement"], cls["value"], "o-", color=GOLD,
             linewidth=2, markersize=8, label="Avg Activity Engagement")
    ax2.set_xlabel("Avg Activity Engagement Score (0-100)")
    ax2.spines["top"].set_visible(True)

    for bar, comm in zip(bars, cls["committed_capital"]):
        ax1.text(bar.get_width() + 25, bar.get_y() + bar.get_height() / 2,
                 f"${millions(comm):.0f}M", va="center", fontsize=9,
                 color=SLATE)

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="lower right",
               frameon=False)
    ax1.text(0.99, -0.18,
             "Source: synthetic dataset | Author: Allen Xu",
             transform=ax1.transAxes, ha="right", fontsize=8, color=SLATE)
    plt.tight_layout()
    out = CHARTS_DIR / "product_demand.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    return out


def main():
    print("Generating charts...")
    for fn in (chart_sales_funnel, chart_rm_productivity, chart_campaign_roi,
                chart_product_demand):
        out = fn()
        print(f"  {out.name}")
    print(f"\nCharts written to: {CHARTS_DIR}")


if __name__ == "__main__":
    main()
