# Data Dictionary

**Project:** Alternative Investment Sales Strategy Analytics Platform
**Author:** Allen Xu
**Note:** All data is synthetic. No real client, advisor, fund, or firm data is used.

---

## Raw tables (`data/raw/`)

### `advisors.csv` (~400 rows)

| Field | Type | Description |
|---|---|---|
| `advisor_id` | string PK | Unique advisor identifier (e.g., `A0001`) |
| `advisor_name` | string | Synthetic advisor name |
| `firm_name` | string | Synthetic firm name |
| `firm_type` | enum | `RIA`, `Private Bank`, `Wirehouse`, `Family Office`, `Consultant`, `Institutional Investor` |
| `region` | enum | `Northeast`, `West`, `Southeast`, `Midwest`, `Southwest`, `International` |
| `city` | string | Headquarters city |
| `state` | string | Headquarters state / country code |
| `aum_segment` | enum | `<100M`, `100M-500M`, `500M-1B`, `1B-5B`, `5B+` |
| `client_type` | enum | `Wealth` or `Institutional` |
| `years_relationship` | int | Years the advisor has been a client of the firm |
| `prior_alt_investment_experience` | enum | `Low`, `Medium`, `High` |
| `assigned_rm_id` | string FK | Coverage relationship manager (`relationship_managers.rm_id`) |

### `relationship_managers.csv` (16 rows)

| Field | Type | Description |
|---|---|---|
| `rm_id` | string PK | Unique RM identifier (e.g., `RM001`) |
| `rm_name` | string | Synthetic RM name |
| `region` | enum | Coverage region |
| `tenure_years` | int | Years at the firm |
| `coverage_segment` | enum | `Wealth`, `Institutional`, `Family Office`, `Mixed` |
| `sales_team` | string | Distribution team affiliation |

### `funds.csv` (10 rows)

| Field | Type | Description |
|---|---|---|
| `fund_id` | string PK | Fund identifier (e.g., `F001`) |
| `fund_name` | string | Marketing name |
| `asset_class` | enum | `Private Equity`, `Private Credit`, `Infrastructure`, `Real Estate` |
| `strategy` | enum | `Buyout`, `Growth Equity`, `Direct Lending`, `Opportunistic Credit`, `Core Infrastructure`, `Value-Add Real Estate`, `Opportunistic Real Estate` |
| `vintage_year` | int | Vintage year (2024 or 2025) |
| `target_return_range` | string | Target net IRR / yield range |
| `liquidity_profile` | enum | `Low`, `Medium`, `High` |
| `minimum_commitment` | int | Minimum investor commitment, USD |
| `risk_profile` | enum | `Moderate`, `High`, `Opportunistic` |

### `sales_activities.csv` (~7,500 rows)

| Field | Type | Description |
|---|---|---|
| `activity_id` | string PK | Unique activity identifier |
| `activity_date` | date | Date of activity (May 2025 - Apr 2026) |
| `advisor_id` | string FK | Advisor touched |
| `rm_id` | string FK | RM owning the activity |
| `activity_type` | enum | `Intro Call`, `Follow-up Call`, `In-person Meeting`, `Webinar`, `Product Education`, `Due Diligence Meeting`, `Portfolio Review` |
| `product_discussed` | string | Fund name discussed |
| `asset_class_discussed` | enum | One of the four asset classes |
| `engagement_score` | int 0-100 | Activity-level engagement signal |
| `next_step_required` | enum | `Yes` / `No` |
| `completed_followup` | enum | `Yes` / `No` |
| `days_to_followup` | int (nullable) | Days between activity and completed follow-up |
| `meeting_duration_minutes` | int | Activity duration |

### `opportunities.csv` (~1,500 rows)

| Field | Type | Description |
|---|---|---|
| `opportunity_id` | string PK | Unique opportunity identifier |
| `advisor_id` | string FK | Source advisor |
| `rm_id` | string FK | Owning RM |
| `fund_id` | string FK | Fund being commitment-evaluated |
| `created_date` | date | Pipeline creation date |
| `current_stage` | enum | `Prospect`, `Interested`, `Due Diligence`, `Soft Circle`, `Committed`, `Lost` |
| `expected_commitment` | int | Forecasted commitment, USD |
| `actual_commitment` | int (nullable) | Realized commitment, USD (only for `Committed`) |
| `close_date` | date (nullable) | When `Committed` or `Lost` |
| `days_to_close` | int (nullable) | `close_date - created_date` |
| `probability` | int 0-100 | Stage-mapped close probability |
| `source_campaign_id` | string FK (nullable) | Originating marketing campaign |
| `loss_reason` | string (nullable) | Reason if `Lost` |

### `campaigns.csv` (28 rows)

| Field | Type | Description |
|---|---|---|
| `campaign_id` | string PK | Campaign identifier |
| `campaign_name` | string | Campaign label |
| `campaign_type` | enum | `Webinar`, `Roadshow`, `Email Campaign`, `Advisor Education Series`, `Market Outlook Event`, `Product Launch` |
| `start_date` | date | Campaign launch |
| `end_date` | date | Campaign close |
| `target_segment` | enum | Targeted advisor channel |
| `product_focus` | string | Primary strategy promoted |
| `asset_class_focus` | enum | Primary asset class promoted |
| `campaign_cost` | int | All-in spend, USD |
| `region` | string | Targeted region or `National` |

### `campaign_engagement.csv` (~1,400 rows)

| Field | Type | Description |
|---|---|---|
| `engagement_id` | string PK | Unique row identifier |
| `campaign_id` | string FK | Campaign |
| `advisor_id` | string FK | Advisor reached |
| `opened_email` | int 0/1 | Engagement signal |
| `attended_event` | int 0/1 | Engagement signal |
| `downloaded_materials` | int 0/1 | Engagement signal |
| `requested_followup` | int 0/1 | Engagement signal |
| `scheduled_meeting` | int 0/1 | Engagement signal |
| `engagement_score` | int 0-100 | Composite engagement score |

---

## Processed outputs (`data/processed/`)

### `sales_funnel_summary.csv`

Long format summary of opportunities by `group_label` (`overall`, `stage`, `region`, `firm_type`, `asset_class`, `aum_segment`). Includes total / active / committed / lost counts, expected pipeline, committed capital, and conversion-rate metrics.

### `rm_productivity_summary.csv`

One row per RM. Includes activity volume, average engagement, follow-up completion, total opportunities, committed deals, conversion rate, total pipeline, committed capital, pipeline-per-meeting, commitment-per-meeting, average days-to-close, and a `coaching_flag` for RMs with above-median engagement but below-median conversion.

### `product_demand_summary.csv`

Long format with `dimension`: `asset_class`, `fund`, `firm_type_x_asset_class`, `region_x_asset_class`. Tracks opportunities, pipeline, committed capital, conversion rate, and (for asset-class rows) average engagement.

### `campaign_roi_summary.csv`

One row per campaign. Engagement counts (reached, opened, attended, downloaded, follow-ups, meetings), opportunity counts (qualified / committed), expected pipeline and committed capital, cost-per-advisor / cost-per-qualified / cost-per-committed metrics, fee-revenue proxy at 2.5%, and ROI %.

### `advisor_priority_scores.csv`

One row per advisor. Component scores (engagement, AUM, conversion probability, product fit, recency), weighted `priority_score`, `priority_tier` (`High` / `Medium` / `Low`), `recommended_next_action`, `recommended_asset_class`, and an `estimated_commitment_opportunity` USD figure.

### `executive_kpi_summary.csv`

Flat KPI table consumed by the executive report: total pipeline value, committed capital, conversion rate, days-to-close, total activity engagement, campaign spend and attributable capital, portfolio campaign ROI, and counts of high-priority advisors / coaching-flagged RMs.

---

## Conventions

- Currency: integer USD throughout.
- Dates: ISO `YYYY-MM-DD`.
- Time horizon: 12 months, 2025-05-01 through 2026-04-30.
- Random seed: `42` (deterministic regeneration).
