# Tableau / Power BI Build Notes

**Project:** Alternative Investment Sales Strategy Analytics Platform
**Author:** Allen Xu

This document explains how a BI engineer would assemble the Tableau or Power BI workbook on top of the processed CSV outputs in `data/processed/`. No actual `.twbx` / `.pbix` is provided — the deliverables in this repo are the dashboard-ready data files plus the modeling guide below.

---

## 1. Data sources

Connect each processed CSV as its own table:

| BI table | Source file | Grain |
|---|---|---|
| `Opportunities` | `data/raw/opportunities.csv` | Opportunity |
| `Activities` | `data/raw/sales_activities.csv` | Activity |
| `Advisors` | `data/raw/advisors.csv` | Advisor |
| `Relationship Managers` | `data/raw/relationship_managers.csv` | RM |
| `Funds` | `data/raw/funds.csv` | Fund |
| `Campaigns` | `data/raw/campaigns.csv` | Campaign |
| `Campaign Engagement` | `data/raw/campaign_engagement.csv` | Campaign × Advisor |
| `RM Productivity` | `data/processed/rm_productivity_summary.csv` | RM |
| `Campaign ROI` | `data/processed/campaign_roi_summary.csv` | Campaign |
| `Advisor Priority` | `data/processed/advisor_priority_scores.csv` | Advisor |
| `Funnel Summary` | `data/processed/sales_funnel_summary.csv` | Group |
| `Product Demand` | `data/processed/product_demand_summary.csv` | Group |
| `Executive KPIs` | `data/processed/executive_kpi_summary.csv` | KPI |

For Power BI, load each CSV through Power Query and apply data-type cleanup (dates → Date, USD columns → Whole Number).

## 2. Data model relationships

Star-schema-like layout, with `Opportunities` and `Activities` as the primary fact tables.

```
                +-----------+      +-----------+
                |  Funds    |<-----+ Opportunities
                +-----------+      |   (fact)  |
                                   +-----+-----+
                                         |
                                  +------v------+
                                  |  Advisors   |--+
                                  +------+------+  |
                                         |         |
                                  +------v------+  |
                                  | Relationship |  |
                                  |  Managers    |  |
                                  +------+------+  |
                                         |         |
              +-----------+        +------v------+ |
              | Campaigns +<-------+ Campaign     +<+
              +-----+-----+        | Engagement   |
                    |              +------+------+
                    v
                Activities (fact)
```

Relationships (one-to-many):

| From | To | On |
|---|---|---|
| `Advisors` | `Opportunities` | `advisor_id` |
| `Relationship Managers` | `Opportunities` | `rm_id` |
| `Funds` | `Opportunities` | `fund_id` |
| `Campaigns` | `Opportunities` | `campaign_id ↔ source_campaign_id` |
| `Advisors` | `Activities` | `advisor_id` |
| `Relationship Managers` | `Activities` | `rm_id` |
| `Campaigns` | `Campaign Engagement` | `campaign_id` |
| `Advisors` | `Campaign Engagement` | `advisor_id` |

Add a Date dimension joined on `activity_date`, `created_date`, `close_date`, `start_date`.

## 3. Calculated fields (Tableau syntax)

Equivalents in DAX are provided in parentheses.

```text
[Committed Capital]
   SUM(IFNULL([actual_commitment], 0))
   -- DAX: SUM ( Opportunities[actual_commitment] )

[Expected Pipeline]
   SUM([expected_commitment])

[Committed Rate]
   SUM(IF [current_stage] = 'Committed' THEN 1 ELSE 0 END) / COUNT([opportunity_id])

[DD or Later Rate]
   SUM(IF [current_stage] IN ('Due Diligence','Soft Circle','Committed') THEN 1 ELSE 0 END)
     / COUNT([opportunity_id])

[Avg Days to Close]
   AVG(IF [current_stage] = 'Committed' THEN [days_to_close] END)

[Pipeline Per Meeting]
   [Expected Pipeline] / COUNT([activity_id])

[Commitment Per Meeting]
   [Committed Capital] / COUNT([activity_id])

[Cost Per Qualified Opportunity]
   SUM([campaign_cost]) /
     SUM(IF [current_stage] IN ('Due Diligence','Soft Circle','Committed') THEN 1 ELSE 0 END)

[Campaign ROI %]
   ([Committed Capital] * 0.025 - SUM([campaign_cost])) / SUM([campaign_cost])

[Coaching Flag]
   IF [avg_engagement] >= WINDOW_AVG([avg_engagement])
      AND [conversion_rate_pct] < WINDOW_AVG([conversion_rate_pct])
   THEN 'Coaching Opportunity' ELSE 'On Track' END

[Priority Tier Color]
   CASE [priority_tier]
     WHEN 'High'   THEN '#0F2A47'
     WHEN 'Medium' THEN '#2A8C8C'
     WHEN 'Low'    THEN '#5B6B7C'
   END
```

## 4. Suggested filters (workbook-level)

- Date range (created date / activity date)
- Region (`Northeast`, `West`, ... `International`)
- Firm type (`RIA`, `Family Office`, ...)
- Asset class
- AUM segment
- Sales team / Coverage segment
- Pipeline stage
- Priority tier (`High` / `Medium` / `Low`)

## 5. Page recommendations

See `dashboard_wireframe.md` for the four canonical pages and visuals.

## 6. Performance notes

- Pre-aggregate large tables (`Activities`, `Opportunities`) into the processed summaries when serving an enterprise BI deployment.
- For row-level RM views, drive off the raw fact table; for executive views, point at the processed CSVs.
- Add row-level security (RLS) on `rm_id` so RMs only see their own pipelines.
