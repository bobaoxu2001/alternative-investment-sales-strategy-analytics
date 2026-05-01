# Executive Report: Alternative Investment Sales Strategy Analytics Platform

**Author:** Allen Xu
**Date:** May 2026
**Prepared for:** Global Client Solutions / Global Wealth Solutions leadership

> All figures in this report are derived from a **synthetic** dataset designed to mirror the distribution operations of an alternative investment firm. No real client, advisor, fund, or firm data is used. The dataset spans 12 months (May 2025 - April 2026) and is regenerated deterministically from `src/generate_synthetic_data.py` (random seed `42`).

---

## 1. Executive Summary

Across the trailing 12 months, the distribution platform produced **$58.8B of expected pipeline** and **$6.75B of committed capital** from 1,500 opportunities sourced by 16 relationship managers covering 400 advisors. Overall conversion from any pipeline stage to *Committed* was **10.87%**, and the average closed deal took **150 days** from creation. Three relationship managers cleared **$700M+ each** in committed capital while three others were flagged as **coaching opportunities** — strong activity volume and engagement, but conversion below the team median. Email-driven product campaigns and Roadshows delivered the bulk of attributable commitments (74% of campaign-attributable capital). The **advisor priority scoring model** identified **132 high-priority advisors** representing **~$9.7B of estimated commitment opportunity** across the next 12 months — the central asset for next-quarter sales planning.

## 2. Business Context

Alternative investment distribution differs from public-market asset gathering in three ways that drive how this analytics platform was built:

1. **Long sales cycles.** Commitments take months — not days — to close, so funnel diagnostics matter more than monthly volume targets.
2. **Concentrated capital.** A small number of advisors (RIAs, family offices, institutional investors) write disproportionately large checks, making advisor prioritization the single highest-leverage sales activity.
3. **Asymmetric channel economics.** Roadshows and product launches absorb most marketing spend, but cheap digital campaigns can punch far above their weight when advisor segments are well-targeted.

The platform was built to serve a Global Client Solutions / Global Wealth Solutions team that needs to (a) measure RM productivity in a long-cycle business, (b) understand product demand across advisor segments and regions, (c) measure campaign ROI rigorously, and (d) hand RMs a defensible weekly priority list.

## 3. Key Findings

| # | Finding | Evidence |
|---|---|---|
| 1 | **Private Equity has the highest conversion** at 13.0% and the largest committed capital pool ($1.92B), followed by Infrastructure ($1.75B). Private Credit and Real Estate generate more opportunities but convert at 9.7% and 10.1%. | `product_demand_summary.csv` |
| 2 | **Family Offices and Institutional Investors are the most capital-dense channels** — together they generate $3.96B of the $6.75B committed (59%), despite representing only 462 of 1,500 opportunities. | `sales_funnel_summary.csv` (firm_type) |
| 3 | **Northeast has the largest pipeline volume but middling conversion** — 432 opportunities (29% of total) yet a 8.6% commit rate, vs. 14.9% in Midwest and 14.7% in Southwest. | `sales_funnel_summary.csv` (region) |
| 4 | **Capital is highly concentrated in $5B+ AUM advisors** — that AUM tier delivers $3.91B (58%) of committed capital from only 215 opportunities at a 13.5% commit rate. | `sales_funnel_summary.csv` (aum_segment) |
| 5 | **Three RMs are coaching opportunities** — Nancy O'Brien (Southwest), Sarah Wright (Southeast), Nancy Sanchez (Northeast) post above-median engagement (66-68 vs. team median 62.9) but conversion of 6.5-9.2% (vs. team median 10.5%). | `rm_productivity_summary.csv` |
| 6 | **Email campaigns crush all other channel types on ROI** — 9 email campaigns spent $56K and generated $1.08B of attributable commitments (multiple 19,000x) with the lowest cost-per-qualified-opportunity at $881. Roadshows and Product Launches absorbed 73% of campaign spend. | `campaign_roi_summary.csv` |
| 7 | **132 advisors are high-priority**, anchored by 7 above-priority-score-0.81 advisors clustered in Northeast and Midwest (Family Office, Private Bank, Institutional). Combined estimated commitment opportunity: **$9.65B**. | `advisor_priority_scores.csv` |

## 4. Sales Funnel Insights

### 4.1 Stage volumes and pipeline value

| Stage | Opportunities | Expected Pipeline | Committed Capital |
|---|---:|---:|---:|
| Prospect | 367 | $14.08B | — |
| Interested | 324 | $14.13B | — |
| Due Diligence | 280 | $10.74B | — |
| Soft Circle | 148 | $5.68B | — |
| Committed | 163 | $6.94B | $6.75B |
| Lost | 218 | $7.24B | — |

Stage drop-off is **steepest between Due Diligence and Soft Circle** (-47% in count). This is the natural bottleneck — advisors and end-clients are often comfortable evaluating products but slow to submit a signed soft circle. Closing tactics (DD-meeting acceleration, side-letter clarifications) at this stage will move the most absolute capital.

### 4.2 Region

| Region | Opps | Commit Rate | Committed Capital | Avg Days to Close |
|---|---:|---:|---:|---:|
| Southwest | 191 | 14.66% | $1.66B | 143 |
| Northeast | 432 | 8.56% | $1.61B | 156 |
| Midwest | 154 | 14.94% | $1.38B | 145 |
| West | 310 | 13.23% | $1.30B | 147 |
| Southeast | 223 | 8.52% | $0.58B | 161 |
| International | 190 | 7.89% | $0.22B | 150 |

**Northeast under-converts relative to its volume.** The region produces the largest opportunity book but lags Midwest / Southwest / West on commit rate by 5-6 points. This is the single largest funnel-quality lever in the franchise.

### 4.3 Asset class velocity

| Asset Class | Opps | Commit Rate | Committed Capital | Avg Days to Close |
|---|---:|---:|---:|---:|
| Private Equity | 276 | 13.04% | $1.92B | 141 |
| Infrastructure | 318 | 11.64% | $1.75B | 142 |
| Private Credit | 452 | 9.73% | $1.62B | 157 |
| Real Estate | 454 | 10.13% | $1.46B | 157 |

Private Equity and Infrastructure close ~15 days faster than Private Credit and Real Estate, despite higher minimums.

## 5. Relationship Manager Productivity

### 5.1 Top performers

| RM | Region / Team | Activities | Conv Rate | Committed | $ / Meeting |
|---|---|---:|---:|---:|---:|
| Joshua Robinson (RM002) | International / Family Office | 456 | 14.9% | $841.5M | $1.85M |
| Patricia Anderson (RM004) | Midwest / Family Office | 456 | 16.0% | $795.5M | $1.74M |
| Ryan Torres (RM006) | Northeast / Wealth East | 750 | 10.7% | $754.5M | $1.01M |
| Mark Walker (RM012) | West / Wealth West | 375 | 14.7% | $713.5M | $1.90M |
| Nancy O'Brien (RM009) | Southwest / Family Office | 555 | 7.3% | $702.0M | $1.26M |

The top 5 RMs delivered **$3.81B (56%) of committed capital**. Family Office Coverage occupies three of the top five seats — supporting the broader insight that capital concentration tracks advisor segment more than RM tenure.

### 5.2 Coaching opportunities

Three RMs combine strong engagement with weaker conversion:

- **Nancy O'Brien (RM009)** — engagement 68.3 (top quartile), conversion 7.3% (bottom quartile). 555 activities, but follow-up completion is only 46% — pointing to follow-through, not access.
- **Sarah Wright (RM016)** — engagement 66.2, conversion 6.5%, follow-up completion 48%. Same diagnosis.
- **Nancy Sanchez (RM007)** — engagement 66.1, conversion 9.2%, follow-up completion 46%.

In all three cases, **follow-up completion is the leading indicator**. Coaching should focus on the post-meeting funnel discipline rather than top-of-funnel activity.

## 6. Product Demand Analysis

| Asset Class | Activities | Avg Engagement | Opportunities | Expected Pipeline | Committed | Conv Rate |
|---|---:|---:|---:|---:|---:|---:|
| Private Equity | 1,510 | 63.5 | 276 | $10.8B | $1.92B | 13.0% |
| Private Credit | 2,310 | 63.8 | 452 | $16.7B | $1.62B | 9.7% |
| Real Estate | 2,189 | 63.8 | 454 | $17.2B | $1.46B | 10.1% |
| Infrastructure | 1,491 | 64.0 | 318 | $14.1B | $1.75B | 11.6% |

**Activity engagement is roughly balanced across the four asset classes (63.5-64.0).** The differentiation shows up at the conversion stage: Private Equity converts at 13% with the lowest activity and opportunity volume, while Real Estate gets the most activities but converts at 10%. The team is currently spending **the most time on the lowest-yielding asset classes**.

Top funds by committed capital:

| Fund | Asset Class | Opps | Committed | Conv Rate |
|---|---|---:|---:|---:|
| Private Equity Buyout Fund VII | Private Equity | 136 | $1.17B | 12.5% |
| Global Infrastructure Partners IV | Infrastructure | 164 | $0.94B | 11.6% |
| Core Infrastructure Income Fund III | Infrastructure | 154 | $0.80B | 11.7% |
| Growth Equity Partners III | Private Equity | 140 | $0.74B | 13.6% |
| Real Estate Income Fund II | Real Estate | 152 | $0.58B | 11.8% |

## 7. Campaign ROI Analysis

Campaign spend totaled **$1.46M** with **$2.77B of attributable committed capital** — a 1,902x committed-capital-to-cost multiple, or a 4,655% ROI under a 2.5% management-fee proxy. Channel breakdown:

| Campaign Type | n | Spend | Qualified Opps | Committed Capital | Multiple | Cost / Qualified Opp |
|---|---:|---:|---:|---:|---:|---:|
| Email Campaign | 9 | $56K | 64 | $1.08B | 19,133x | $881 |
| Webinar | 2 | $38K | 20 | $0.18B | 4,725x | $1,884 |
| Market Outlook Event | 2 | $128K | 14 | $0.20B | 1,551x | $9,139 |
| Roadshow | 6 | $642K | 50 | $0.78B | 1,208x | $12,846 |
| Product Launch | 5 | $417K | 37 | $0.44B | 1,058x | $11,268 |
| Advisor Education Series | 4 | $175K | 18 | $0.10B | 558x | $9,713 |

**Email campaigns are wildly more efficient than every other channel** on the platform — even after adjusting for the long-tail of attributable capital. Roadshows and Product Launches still earn their place because they are the only channels that drive deep large-ticket relationships, but **the franchise is over-allocated to high-cost channels relative to attributable returns.**

## 8. Advisor Prioritization Model

Each advisor is scored on a 0-1 scale using:

```
priority_score =
    0.30 × engagement_norm          (avg activity engagement / 100)
  + 0.25 × aum_norm                 (AUM segment lookup, 0.15-0.95)
  + 0.20 × conversion_prob_norm     (avg opp probability or experience proxy)
  + 0.15 × product_fit_norm         (asset classes touched / 4)
  + 0.10 × recency_norm             (1 - days_since_last / horizon)
```

Advisors are bucketed into tiers using the score's 33rd and 67th percentiles:

| Tier | Advisors | Recommended Action Examples |
|---|---:|---|
| High | 132 | Portfolio Review · Schedule DD Meeting · RM Follow-up |
| Medium | 136 | Re-engagement · Market Outlook Webinar · Education Materials |
| Low | 132 | Re-engagement Campaign · Education Materials |

Recommended-action breakdown across all 400 advisors:

- 150 Re-engagement Campaign (drift / aging coverage)
- 115 Invite to Market Outlook Webinar
- 62 Portfolio Review Conversation
- 50 Relationship Manager Follow-up
- 20 Schedule Due Diligence Meeting
- 3 Send Private Credit Education Materials

Total **estimated commitment opportunity from the 132 high-priority advisors: $9.65B**, or roughly 1.4× the trailing-12-month committed-capital total. This is the central planning artifact for next-quarter sales coverage.

## 9. Strategic Recommendations

1. **Rebalance Northeast pipeline quality, not volume.** The region produces 29% of opportunities but only 24% of committed capital. Run a 90-day pilot focused on tightening DD-to-Soft-Circle conversion in Northeast Family Office and Institutional advisors before any further headcount expansion.

2. **Double Email Campaign budget; redirect from Advisor Education Series.** Email is currently 4% of campaign spend and 39% of attributable committed capital. Advisor Education Series is 12% of spend and 4% of attributable capital. Reallocate ~$100K from Education Series to high-velocity Private Credit / Private Equity email campaigns.

3. **Reweight RM time toward Private Equity and Infrastructure.** The team spends the largest share of activity hours on Private Credit and Real Estate (60% of activities) but those asset classes deliver only 46% of committed capital. A 1:1 rebalancing toward Private Equity / Infrastructure could lift portfolio commit rate by 100-150 bps.

4. **Coach the three flagged RMs on follow-up discipline, not access.** The diagnostic in Section 5.2 shows the gap is 46-48% follow-up completion — well below the 50%+ that the top performers exceed. Six-week structured coaching with mandatory weekly pipeline reviews.

5. **Use the priority score in weekly RM pipeline reviews.** Push the 132 High-tier advisors and the recommended-next-action column into the CRM; require RMs to log activity against the prescribed action within the cycle.

6. **Track campaign ROI at segment × product level.** The current ROI summary aggregates by campaign type. Push attribution down one level to *segment × asset class* so marketing can see where Family Office Private Credit campaigns dominate vs. RIA Real Estate.

7. **Build a re-engagement cohort.** 150 advisors (38% of the book) are flagged for re-engagement. A targeted Q3 nurture program with mid-tier campaigns (webinars, market outlook) is the cheapest near-term lever for refilling the pipeline.

## 10. Tools Used

- **Python** (pandas, numpy) — synthetic data generation, analytics pipeline.
- **SQL** (SQLite) — five portable analytics scripts mirroring the Python pipeline.
- **Matplotlib** — executive PNG charts.
- **Excel-style modeling** — weighted scoring and ROI proxies designed to mirror finance-team conventions.
- **Tableau / Power BI-ready outputs** — six processed CSV marts shaped for direct BI ingestion.
- **Synthetic data** — deterministic generation under random seed 42; no real data used.

## 11. Limitations and Next Steps

**Limitations:**

- The dataset is fully synthetic. Correlations are designed (not learned), so the magnitude of certain effects (e.g. Email Campaign ROI) is amplified relative to a production environment with realistic noise and competition for advisor attention.
- The campaign ROI uses a 2.5% management-fee proxy; in production, fee streams should be calculated by fund using actual mgmt + performance fee schedules over fund life.
- The priority score weights are a defensible default but not optimized. A real deployment should learn weights from historical commit outcomes (logistic regression, gradient-boosted trees).
- No competitor or market-share data is included.

**Next steps:**

1. Replace synthetic data with CRM exports (Salesforce / HubSpot) and fund administration data.
2. Train a probabilistic conversion model on closed/lost opportunities and replace the static `conv_prob_norm` component.
3. Add a fee-stream model with fund-level mgmt and perf fee schedules.
4. Deploy the four dashboard pages to Tableau Server / Power BI Service with row-level security on `rm_id`.
5. Wire the priority score into weekly CRM "next best action" workflows for RMs.
