"""
Synthetic data generation for the Alternative Investment Sales Strategy
Analytics Platform.

Author: Allen Xu

Generates realistic but fully synthetic data simulating the distribution
operations of an alternative investment firm: advisors, relationship managers,
funds, sales activities, opportunities, campaigns, and campaign engagement.

All numbers, names, and identifiers are fictional. The dataset is designed so
that downstream analytics surface plausible patterns (e.g. higher engagement
correlates with stage progression, larger AUM with larger commitments).
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Reference data
# -----------------------------------------------------------------------------

REGIONS = ["Northeast", "West", "Southeast", "Midwest", "Southwest", "International"]
REGION_WEIGHTS = [0.28, 0.22, 0.16, 0.14, 0.10, 0.10]

REGION_CITIES = {
    "Northeast": [("New York", "NY"), ("Boston", "MA"), ("Philadelphia", "PA"),
                  ("Stamford", "CT"), ("Princeton", "NJ")],
    "West": [("San Francisco", "CA"), ("Los Angeles", "CA"), ("Seattle", "WA"),
             ("Denver", "CO"), ("San Diego", "CA")],
    "Southeast": [("Miami", "FL"), ("Atlanta", "GA"), ("Charlotte", "NC"),
                  ("Tampa", "FL"), ("Nashville", "TN")],
    "Midwest": [("Chicago", "IL"), ("Minneapolis", "MN"), ("Cleveland", "OH"),
                ("Indianapolis", "IN"), ("St. Louis", "MO")],
    "Southwest": [("Dallas", "TX"), ("Houston", "TX"), ("Austin", "TX"),
                  ("Phoenix", "AZ"), ("Las Vegas", "NV")],
    "International": [("London", "UK"), ("Toronto", "ON"), ("Zurich", "CH"),
                      ("Singapore", "SG"), ("Hong Kong", "HK")],
}

FIRM_TYPES = ["RIA", "Private Bank", "Wirehouse", "Family Office",
              "Consultant", "Institutional Investor"]
FIRM_TYPE_WEIGHTS = [0.30, 0.16, 0.18, 0.16, 0.08, 0.12]

AUM_SEGMENTS = ["<100M", "100M-500M", "500M-1B", "1B-5B", "5B+"]
AUM_WEIGHTS = [0.22, 0.30, 0.22, 0.18, 0.08]
AUM_MIDPOINTS = {"<100M": 50, "100M-500M": 300, "500M-1B": 750,
                 "1B-5B": 2500, "5B+": 8000}  # millions

EXPERIENCE_LEVELS = ["Low", "Medium", "High"]
EXPERIENCE_WEIGHTS = [0.30, 0.45, 0.25]

ASSET_CLASSES = ["Private Equity", "Private Credit", "Infrastructure", "Real Estate"]

STRATEGIES_BY_CLASS = {
    "Private Equity": ["Buyout", "Growth Equity"],
    "Private Credit": ["Direct Lending", "Opportunistic Credit"],
    "Infrastructure": ["Core Infrastructure"],
    "Real Estate": ["Value-Add Real Estate", "Opportunistic Real Estate"],
}

ACTIVITY_TYPES = ["Intro Call", "Follow-up Call", "In-person Meeting",
                  "Webinar", "Product Education", "Due Diligence Meeting",
                  "Portfolio Review"]
ACTIVITY_WEIGHTS = [0.18, 0.24, 0.16, 0.14, 0.10, 0.10, 0.08]

PIPELINE_STAGES = ["Prospect", "Interested", "Due Diligence", "Soft Circle",
                   "Committed", "Lost"]

CAMPAIGN_TYPES = ["Webinar", "Roadshow", "Email Campaign",
                  "Advisor Education Series", "Market Outlook Event",
                  "Product Launch"]

LOSS_REASONS = ["Liquidity Mismatch", "Allocation Already Filled",
                "Pricing/Fee Concerns", "Competing Manager Selected",
                "Client Risk Appetite", "Timing - Deferred"]

# Deterministic name generators ------------------------------------------------

FIRST_NAMES = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer",
               "Michael", "Linda", "David", "Elizabeth", "William", "Barbara",
               "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah",
               "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
               "Matthew", "Margaret", "Anthony", "Betty", "Mark", "Sandra",
               "Donald", "Ashley", "Steven", "Dorothy", "Paul", "Kimberly",
               "Andrew", "Emily", "Joshua", "Donna", "Kenneth", "Michelle",
               "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
               "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca",
               "Jason", "Sharon", "Jeffrey", "Laura", "Ryan", "Cynthia"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
              "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
              "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
              "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
              "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
              "Walker", "Young", "Allen", "King", "Wright", "Scott",
              "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
              "Nakamura", "Patel", "Kim", "Chen", "Wang", "Singh",
              "Cohen", "Goldberg", "Murphy", "Sullivan", "O'Brien", "Reed"]

FIRM_PREFIXES = ["Summit", "Cascade", "Granite", "Bayview", "Harbor",
                 "Meridian", "Beacon", "Cornerstone", "Heritage", "Compass",
                 "Pinnacle", "Cedar", "Coastal", "Liberty", "Frontier",
                 "Sterling", "Vanguard", "Crescent", "Atlas", "Ironwood",
                 "Evergreen", "Ridge", "Crown", "Northstar", "Trident",
                 "Keystone", "Lighthouse", "Riverstone", "Eaglewood", "Halcyon"]

FIRM_SUFFIXES_BY_TYPE = {
    "RIA": ["Capital Advisors", "Wealth Partners", "Wealth Management",
            "Family Wealth", "Advisors LLC"],
    "Private Bank": ["Private Bank", "Trust & Banking", "Private Wealth"],
    "Wirehouse": ["Securities", "Global Markets", "Wealth Management"],
    "Family Office": ["Family Office", "Private Capital",
                      "Multi-Family Office"],
    "Consultant": ["Investment Consulting", "Advisory Group",
                   "Investment Solutions"],
    "Institutional Investor": ["Pension Trust", "Endowment",
                               "Insurance Investments", "Foundation"],
}


def synth_name() -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def synth_firm_name(firm_type: str) -> str:
    prefix = rng.choice(FIRM_PREFIXES)
    suffix = rng.choice(FIRM_SUFFIXES_BY_TYPE[firm_type])
    return f"{prefix} {suffix}"


# -----------------------------------------------------------------------------
# Generators
# -----------------------------------------------------------------------------

def generate_relationship_managers(n_rms: int = 16) -> pd.DataFrame:
    """Sales force covering wealth and institutional channels across regions."""
    rows = []
    teams = ["Wealth Distribution East", "Wealth Distribution West",
             "Institutional Sales", "Family Office Coverage",
             "International Coverage"]
    coverage_segments = ["Wealth", "Institutional", "Family Office", "Mixed"]

    # Distribute regions roughly evenly with a slight Northeast bias
    region_pool = (["Northeast"] * 4 + ["West"] * 3 + ["Southeast"] * 2
                   + ["Midwest"] * 2 + ["Southwest"] * 2 + ["International"] * 3)
    rng.shuffle(region_pool)
    region_pool = region_pool[:n_rms]

    for i in range(n_rms):
        rm_id = f"RM{i + 1:03d}"
        region = region_pool[i]
        coverage = rng.choice(coverage_segments, p=[0.45, 0.25, 0.15, 0.15])
        if coverage == "Institutional":
            team = "Institutional Sales"
        elif coverage == "Family Office":
            team = "Family Office Coverage"
        elif region == "International":
            team = "International Coverage"
        elif region in ("Northeast", "Southeast"):
            team = "Wealth Distribution East"
        else:
            team = "Wealth Distribution West"
        rows.append({
            "rm_id": rm_id,
            "rm_name": synth_name(),
            "region": region,
            "tenure_years": int(rng.integers(2, 22)),
            "coverage_segment": coverage,
            "sales_team": team,
        })
    return pd.DataFrame(rows)


def generate_advisors(rms: pd.DataFrame, n_advisors: int = 400) -> pd.DataFrame:
    """Advisor universe with firm metadata and assigned relationship manager."""
    rows = []
    for i in range(n_advisors):
        advisor_id = f"A{i + 1:04d}"
        region = rng.choice(REGIONS, p=REGION_WEIGHTS)
        city, state = REGION_CITIES[region][rng.integers(0, len(REGION_CITIES[region]))]
        firm_type = rng.choice(FIRM_TYPES, p=FIRM_TYPE_WEIGHTS)
        client_type = "Institutional" if firm_type in (
            "Consultant", "Institutional Investor") else "Wealth"

        # AUM segment is biased by firm type
        if firm_type == "Family Office":
            aum_p = [0.05, 0.20, 0.30, 0.30, 0.15]
        elif firm_type in ("Private Bank", "Wirehouse"):
            aum_p = [0.10, 0.25, 0.25, 0.25, 0.15]
        elif firm_type == "Institutional Investor":
            aum_p = [0.05, 0.10, 0.20, 0.35, 0.30]
        elif firm_type == "RIA":
            aum_p = [0.30, 0.35, 0.20, 0.12, 0.03]
        else:  # Consultant
            aum_p = [0.20, 0.30, 0.25, 0.20, 0.05]
        aum_segment = rng.choice(AUM_SEGMENTS, p=aum_p)

        # Pick an RM, biased toward same region when possible
        same_region_rms = rms[rms["region"] == region]
        if len(same_region_rms) > 0 and rng.random() < 0.78:
            assigned_rm = rng.choice(same_region_rms["rm_id"].to_numpy())
        else:
            assigned_rm = rng.choice(rms["rm_id"].to_numpy())

        rows.append({
            "advisor_id": advisor_id,
            "advisor_name": synth_name(),
            "firm_name": synth_firm_name(firm_type),
            "firm_type": firm_type,
            "region": region,
            "city": city,
            "state": state,
            "aum_segment": aum_segment,
            "client_type": client_type,
            "years_relationship": int(rng.integers(0, 18)),
            "prior_alt_investment_experience": rng.choice(
                EXPERIENCE_LEVELS, p=EXPERIENCE_WEIGHTS),
            "assigned_rm_id": assigned_rm,
        })
    return pd.DataFrame(rows)


def generate_funds() -> pd.DataFrame:
    """Flagship fund line spanning the four alternative asset classes."""
    fund_specs = [
        ("F001", "Private Equity Buyout Fund VII", "Private Equity", "Buyout",
         2024, "15-20%", "Low", 5_000_000, "High"),
        ("F002", "Growth Equity Partners III", "Private Equity", "Growth Equity",
         2025, "18-22%", "Low", 5_000_000, "Opportunistic"),
        ("F003", "Direct Lending Income Fund V", "Private Credit", "Direct Lending",
         2024, "9-11%", "Medium", 1_000_000, "Moderate"),
        ("F004", "Opportunistic Credit Fund II", "Private Credit",
         "Opportunistic Credit", 2025, "12-15%", "Low", 2_500_000, "High"),
        ("F005", "Senior Direct Lending Fund VI", "Private Credit", "Direct Lending",
         2025, "8-10%", "Medium", 1_000_000, "Moderate"),
        ("F006", "Core Infrastructure Income Fund III", "Infrastructure",
         "Core Infrastructure", 2024, "7-10%", "Low", 2_500_000, "Moderate"),
        ("F007", "Global Infrastructure Partners IV", "Infrastructure",
         "Core Infrastructure", 2025, "8-12%", "Low", 5_000_000, "Moderate"),
        ("F008", "Value-Add Real Estate Fund IV", "Real Estate",
         "Value-Add Real Estate", 2024, "12-15%", "Low", 2_500_000, "High"),
        ("F009", "Opportunistic Real Estate Fund VI", "Real Estate",
         "Opportunistic Real Estate", 2025, "15-20%", "Low", 5_000_000,
         "Opportunistic"),
        ("F010", "Real Estate Income Fund II", "Real Estate",
         "Value-Add Real Estate", 2025, "9-12%", "Medium", 1_000_000, "Moderate"),
    ]
    cols = ["fund_id", "fund_name", "asset_class", "strategy", "vintage_year",
            "target_return_range", "liquidity_profile", "minimum_commitment",
            "risk_profile"]
    return pd.DataFrame(fund_specs, columns=cols)


# -----------------------------------------------------------------------------
# Activities, opportunities, campaigns
# -----------------------------------------------------------------------------

START_DATE = date(2025, 5, 1)
END_DATE = date(2026, 4, 30)
TOTAL_DAYS = (END_DATE - START_DATE).days


def random_date(start: date = START_DATE, end: date = END_DATE) -> date:
    delta = (end - start).days
    return start + timedelta(days=int(rng.integers(0, delta + 1)))


def experience_score(level: str) -> float:
    return {"Low": 0.2, "Medium": 0.55, "High": 0.85}[level]


def aum_score(segment: str) -> float:
    return {"<100M": 0.15, "100M-500M": 0.40, "500M-1B": 0.60,
            "1B-5B": 0.80, "5B+": 0.95}[segment]


def generate_campaigns(n_campaigns: int = 28) -> pd.DataFrame:
    """Marketing programs aimed at advisor segments by product / region."""
    rows = []
    for i in range(n_campaigns):
        campaign_id = f"C{i + 1:03d}"
        ctype = rng.choice(CAMPAIGN_TYPES)
        start = random_date(START_DATE, END_DATE - timedelta(days=30))
        duration = int(rng.integers(1, 45))
        end = start + timedelta(days=duration)
        asset_class = rng.choice(ASSET_CLASSES,
                                 p=[0.25, 0.35, 0.15, 0.25])
        product_focus = rng.choice(STRATEGIES_BY_CLASS[asset_class])
        target_segment = rng.choice(
            ["RIA", "Family Office", "Private Bank / Wirehouse",
             "Institutional", "All Wealth", "All Channels"],
            p=[0.30, 0.18, 0.20, 0.12, 0.12, 0.08])
        region = rng.choice(REGIONS + ["National"],
                            p=[0.18, 0.16, 0.10, 0.10, 0.08, 0.08, 0.30])
        # Cost depends on type
        cost_base = {"Webinar": 15_000, "Roadshow": 90_000,
                     "Email Campaign": 6_000,
                     "Advisor Education Series": 45_000,
                     "Market Outlook Event": 60_000,
                     "Product Launch": 80_000}[ctype]
        cost = int(cost_base * rng.uniform(0.7, 1.4))
        rows.append({
            "campaign_id": campaign_id,
            "campaign_name": f"{asset_class} {product_focus} {ctype} "
                             f"{start.strftime('%b %Y')}",
            "campaign_type": ctype,
            "start_date": start,
            "end_date": end,
            "target_segment": target_segment,
            "product_focus": product_focus,
            "asset_class_focus": asset_class,
            "campaign_cost": cost,
            "region": region,
        })
    return pd.DataFrame(rows)


def generate_campaign_engagement(campaigns: pd.DataFrame,
                                 advisors: pd.DataFrame) -> pd.DataFrame:
    """Per-advisor engagement events for each campaign reach."""
    rows = []
    eng_id = 1
    for _, c in campaigns.iterrows():
        # Define eligible advisor pool by target segment / region
        pool = advisors.copy()
        seg = c["target_segment"]
        if seg == "RIA":
            pool = pool[pool["firm_type"] == "RIA"]
        elif seg == "Family Office":
            pool = pool[pool["firm_type"] == "Family Office"]
        elif seg == "Private Bank / Wirehouse":
            pool = pool[pool["firm_type"].isin(["Private Bank", "Wirehouse"])]
        elif seg == "Institutional":
            pool = pool[pool["firm_type"].isin(
                ["Institutional Investor", "Consultant"])]
        elif seg == "All Wealth":
            pool = pool[pool["client_type"] == "Wealth"]

        if c["region"] != "National":
            pool_region = pool[pool["region"] == c["region"]]
            if len(pool_region) >= 30:
                pool = pool_region

        if len(pool) == 0:
            pool = advisors

        # Sample ~20-50% of pool
        reach_frac = rng.uniform(0.20, 0.50)
        n_reach = max(20, int(len(pool) * reach_frac))
        n_reach = min(n_reach, len(pool))
        sampled = pool.sample(n=n_reach, random_state=int(rng.integers(0, 1e9)))

        ctype = c["campaign_type"]
        # Channel-specific conversion funnels
        if ctype == "Email Campaign":
            open_rate, attend_rate, dl_rate, fu_rate, mtg_rate = 0.40, 0.0, 0.20, 0.12, 0.06
        elif ctype == "Webinar":
            open_rate, attend_rate, dl_rate, fu_rate, mtg_rate = 0.55, 0.30, 0.30, 0.20, 0.12
        elif ctype == "Roadshow":
            open_rate, attend_rate, dl_rate, fu_rate, mtg_rate = 0.65, 0.45, 0.35, 0.32, 0.22
        elif ctype == "Advisor Education Series":
            open_rate, attend_rate, dl_rate, fu_rate, mtg_rate = 0.60, 0.35, 0.45, 0.28, 0.18
        elif ctype == "Market Outlook Event":
            open_rate, attend_rate, dl_rate, fu_rate, mtg_rate = 0.62, 0.40, 0.30, 0.30, 0.20
        else:  # Product Launch
            open_rate, attend_rate, dl_rate, fu_rate, mtg_rate = 0.58, 0.32, 0.40, 0.26, 0.16

        for _, ad in sampled.iterrows():
            exp = experience_score(ad["prior_alt_investment_experience"])
            a_score = aum_score(ad["aum_segment"])
            advisor_lift = 0.5 * exp + 0.5 * a_score  # 0..1
            multiplier = 0.6 + 0.8 * advisor_lift  # 0.6..1.4

            opened = int(rng.random() < min(0.95, open_rate * multiplier))
            attended = int(opened and rng.random() < attend_rate * multiplier)
            downloaded = int(opened and rng.random() < dl_rate * multiplier)
            requested_fu = int(
                (attended or downloaded) and
                rng.random() < fu_rate * multiplier
            )
            scheduled = int(requested_fu and rng.random() < mtg_rate * multiplier)
            engagement = int(np.clip(
                10 * opened + 25 * attended + 20 * downloaded
                + 25 * requested_fu + 20 * scheduled
                + rng.normal(0, 6), 0, 100))

            rows.append({
                "engagement_id": f"E{eng_id:06d}",
                "campaign_id": c["campaign_id"],
                "advisor_id": ad["advisor_id"],
                "opened_email": opened,
                "attended_event": attended,
                "downloaded_materials": downloaded,
                "requested_followup": requested_fu,
                "scheduled_meeting": scheduled,
                "engagement_score": engagement,
            })
            eng_id += 1
    return pd.DataFrame(rows)


def generate_sales_activities(advisors: pd.DataFrame,
                              funds: pd.DataFrame,
                              n_activities: int = 7500) -> pd.DataFrame:
    """RM/advisor touchpoints across the year."""
    advisor_arr = advisors[["advisor_id", "assigned_rm_id",
                            "prior_alt_investment_experience",
                            "aum_segment"]].to_numpy()
    fund_arr = funds[["fund_id", "fund_name", "asset_class"]].to_numpy()
    rows = []

    # Hot advisors — a subset gets disproportionately more touches
    n_advisors = len(advisors)
    weights = rng.gamma(2.0, 1.0, size=n_advisors)
    weights = weights / weights.sum()

    advisor_idx = rng.choice(n_advisors, size=n_activities, p=weights)

    for i in range(n_activities):
        ad_idx = advisor_idx[i]
        ad_id, rm_id, exp, aum = advisor_arr[ad_idx]
        # Random fund discussed
        fund_row = fund_arr[rng.integers(0, len(fund_arr))]
        fund_id, fund_name, asset_class = fund_row

        activity_type = rng.choice(ACTIVITY_TYPES, p=ACTIVITY_WEIGHTS)
        activity_date = random_date()

        # Engagement is influenced by experience + AUM + activity type
        base = 30 + 40 * experience_score(exp) + 20 * aum_score(aum)
        type_lift = {"Intro Call": -8, "Follow-up Call": 0,
                     "In-person Meeting": 12, "Webinar": -5,
                     "Product Education": 5, "Due Diligence Meeting": 18,
                     "Portfolio Review": 8}[activity_type]
        engagement = int(np.clip(base + type_lift + rng.normal(0, 8), 0, 100))

        # Higher engagement → next step required and follow-up completed
        next_step = "Yes" if rng.random() < (0.30 + 0.005 * engagement) else "No"
        if next_step == "Yes":
            completed_fu = "Yes" if rng.random() < (0.45 + 0.004 * engagement) else "No"
            days_to_followup = int(rng.integers(2, 30))
        else:
            completed_fu = "No"
            days_to_followup = None

        # Meeting duration depends on activity type
        if activity_type in ("In-person Meeting", "Due Diligence Meeting",
                              "Portfolio Review"):
            duration = int(rng.normal(75, 18))
        elif activity_type == "Webinar":
            duration = int(rng.normal(50, 10))
        else:
            duration = int(rng.normal(35, 10))
        duration = max(10, duration)

        rows.append({
            "activity_id": f"AC{i + 1:06d}",
            "activity_date": activity_date,
            "advisor_id": ad_id,
            "rm_id": rm_id,
            "activity_type": activity_type,
            "product_discussed": fund_name,
            "asset_class_discussed": asset_class,
            "engagement_score": engagement,
            "next_step_required": next_step,
            "completed_followup": completed_fu,
            "days_to_followup": days_to_followup,
            "meeting_duration_minutes": duration,
        })
    return pd.DataFrame(rows)


def generate_opportunities(advisors: pd.DataFrame,
                           funds: pd.DataFrame,
                           activities: pd.DataFrame,
                           campaigns: pd.DataFrame,
                           n_opps: int = 1500) -> pd.DataFrame:
    """Pipeline opportunities tied to advisor / fund / RM."""
    # Advisor-level engagement summary drives opportunity generation
    eng_by_adv = (activities.groupby("advisor_id")["engagement_score"]
                   .mean().rename("avg_engagement").reset_index())
    advisors_aug = advisors.merge(eng_by_adv, on="advisor_id", how="left")
    advisors_aug["avg_engagement"] = advisors_aug["avg_engagement"].fillna(35)

    # Probability advisor generates opportunities is biased by engagement + AUM + experience
    weights = (
        0.5 * (advisors_aug["avg_engagement"] / 100)
        + 0.3 * advisors_aug["aum_segment"].map({s: aum_score(s) for s in AUM_SEGMENTS})
        + 0.2 * advisors_aug["prior_alt_investment_experience"].map(
            {l: experience_score(l) for l in EXPERIENCE_LEVELS})
    )
    weights = weights / weights.sum()

    sampled_idx = rng.choice(len(advisors_aug), size=n_opps,
                             replace=True, p=weights.values)

    fund_arr = funds.to_numpy()
    fund_cols = funds.columns.tolist()
    campaign_ids = campaigns["campaign_id"].tolist()

    rows = []
    for i in range(n_opps):
        ad = advisors_aug.iloc[sampled_idx[i]]
        fund_idx = rng.integers(0, len(funds))
        fund_row = dict(zip(fund_cols, fund_arr[fund_idx]))

        created = random_date(START_DATE, END_DATE - timedelta(days=15))

        # Stage probabilities depend on engagement
        eng_norm = ad["avg_engagement"] / 100
        # Base probabilities, then shift mass toward later stages with high engagement
        base_p = np.array([0.25, 0.22, 0.18, 0.10, 0.10, 0.15])  # Prospect..Lost
        shift = (eng_norm - 0.5) * 0.6
        # Move mass from Prospect/Interested to DD/Soft Circle/Committed
        adj = base_p.copy()
        adj[0] = max(0.05, adj[0] - 0.10 * shift)
        adj[1] = max(0.05, adj[1] - 0.05 * shift)
        adj[2] = adj[2] + 0.05 * shift
        adj[3] = adj[3] + 0.05 * shift
        adj[4] = adj[4] + 0.05 * shift
        adj[5] = max(0.04, adj[5] - 0.005 * (eng_norm - 0.5))  # high eng → fewer losses
        adj = np.clip(adj, 0.02, 0.6)
        adj = adj / adj.sum()
        stage = rng.choice(PIPELINE_STAGES, p=adj)

        # Expected commitment scales with AUM + experience + fund minimum
        aum_mid = AUM_MIDPOINTS[ad["aum_segment"]]  # in millions
        exp_factor = experience_score(ad["prior_alt_investment_experience"])
        # Allocate roughly 0.5%-3% of AUM × experience × random
        pct = rng.uniform(0.005, 0.03) * (0.5 + exp_factor)
        expected_commitment = int(max(fund_row["minimum_commitment"],
                                      pct * aum_mid * 1_000_000))
        # Round to nearest $250k
        expected_commitment = int(round(expected_commitment / 250_000) * 250_000)

        if stage == "Committed":
            actual = int(expected_commitment * rng.uniform(0.85, 1.10))
            actual = int(round(actual / 250_000) * 250_000)
            close = created + timedelta(days=int(rng.integers(60, 240)))
            days_to_close = (close - created).days
            probability = 100
            loss_reason = None
        elif stage == "Lost":
            actual = None
            close = created + timedelta(days=int(rng.integers(20, 200)))
            days_to_close = (close - created).days
            probability = 0
            loss_reason = rng.choice(LOSS_REASONS)
        else:
            actual = None
            close = None
            days_to_close = None
            probability = {"Prospect": 10, "Interested": 25,
                           "Due Diligence": 50, "Soft Circle": 75}[stage]
            loss_reason = None

        # 35% of opps tied to a campaign
        campaign_id = (rng.choice(campaign_ids)
                       if rng.random() < 0.35 else None)

        rows.append({
            "opportunity_id": f"O{i + 1:05d}",
            "advisor_id": ad["advisor_id"],
            "rm_id": ad["assigned_rm_id"],
            "fund_id": fund_row["fund_id"],
            "created_date": created,
            "current_stage": stage,
            "expected_commitment": expected_commitment,
            "actual_commitment": actual,
            "close_date": close,
            "days_to_close": days_to_close,
            "probability": probability,
            "source_campaign_id": campaign_id,
            "loss_reason": loss_reason,
        })
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    print("Generating synthetic dataset for the Alternative Investment Sales "
          "Strategy Analytics Platform")
    print(f"Random seed: {SEED}")

    rms = generate_relationship_managers(n_rms=16)
    advisors = generate_advisors(rms, n_advisors=400)
    funds = generate_funds()
    campaigns = generate_campaigns(n_campaigns=28)
    activities = generate_sales_activities(advisors, funds, n_activities=7500)
    opportunities = generate_opportunities(advisors, funds, activities,
                                           campaigns, n_opps=1500)
    engagement = generate_campaign_engagement(campaigns, advisors)

    # Persist
    rms.to_csv(RAW_DIR / "relationship_managers.csv", index=False)
    advisors.to_csv(RAW_DIR / "advisors.csv", index=False)
    funds.to_csv(RAW_DIR / "funds.csv", index=False)
    campaigns.to_csv(RAW_DIR / "campaigns.csv", index=False)
    activities.to_csv(RAW_DIR / "sales_activities.csv", index=False)
    opportunities.to_csv(RAW_DIR / "opportunities.csv", index=False)
    engagement.to_csv(RAW_DIR / "campaign_engagement.csv", index=False)

    print("\nRow counts:")
    print(f"  relationship_managers : {len(rms):>7,}")
    print(f"  advisors              : {len(advisors):>7,}")
    print(f"  funds                 : {len(funds):>7,}")
    print(f"  campaigns             : {len(campaigns):>7,}")
    print(f"  sales_activities      : {len(activities):>7,}")
    print(f"  opportunities         : {len(opportunities):>7,}")
    print(f"  campaign_engagement   : {len(engagement):>7,}")
    print(f"\nRaw files written to: {RAW_DIR}")


if __name__ == "__main__":
    main()
