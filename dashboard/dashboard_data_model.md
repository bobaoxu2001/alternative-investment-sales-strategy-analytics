# Dashboard Data Model

**Project:** Alternative Investment Sales Strategy Analytics Platform
**Author:** Allen Xu

## 1. Modeling approach

The workbook is built on a denormalized star-style model. Two fact tables (`Opportunities`, `Activities`) connect to shared dimensions (`Advisors`, `Relationship Managers`, `Funds`, `Campaigns`). Pre-computed summary tables (`RM Productivity`, `Campaign ROI`, `Advisor Priority`, `Funnel Summary`, `Product Demand`, `Executive KPIs`) drive the executive pages so heavy aggregation does not run at view time.

```
Dimensions:
  Advisors           (advisor_id PK)
  Relationship Managers (rm_id PK)
  Funds              (fund_id PK)
  Campaigns          (campaign_id PK)
  Date               (date PK)

Facts:
  Opportunities      (advisor_id, rm_id, fund_id, source_campaign_id)
  Activities         (advisor_id, rm_id, activity_date)
  Campaign Engagement (campaign_id, advisor_id)

Summary marts (one row per natural key):
  RM Productivity    (rm_id)
  Campaign ROI       (campaign_id)
  Advisor Priority   (advisor_id)
  Funnel Summary     (group_label, group_value)
  Product Demand     (dimension, value)
  Executive KPIs     (kpi)
```

## 2. Key relationships

| From → To | Cardinality | Field |
|---|---|---|
| Advisors → Opportunities | 1 : N | `advisor_id` |
| Advisors → Activities | 1 : N | `advisor_id` |
| Advisors → Campaign Engagement | 1 : N | `advisor_id` |
| Advisors → Advisor Priority | 1 : 1 | `advisor_id` |
| Relationship Managers → Opportunities | 1 : N | `rm_id` |
| Relationship Managers → Activities | 1 : N | `rm_id` |
| Relationship Managers → RM Productivity | 1 : 1 | `rm_id` |
| Funds → Opportunities | 1 : N | `fund_id` |
| Campaigns → Opportunities | 1 : N | `campaign_id ↔ source_campaign_id` |
| Campaigns → Campaign Engagement | 1 : N | `campaign_id` |
| Campaigns → Campaign ROI | 1 : 1 | `campaign_id` |

## 3. Recommended materialized views

If deploying on a warehouse (Snowflake, BigQuery, Redshift), promote these to scheduled materialized views or `dbt` models so the BI layer does not recompute them every refresh:

1. `mart__rm_productivity` (refresh daily)
2. `mart__campaign_roi` (refresh daily)
3. `mart__advisor_priority` (refresh weekly — scoring inputs change slowly)
4. `mart__funnel_summary` (refresh daily)
5. `mart__product_demand` (refresh daily)
6. `mart__executive_kpis` (refresh daily)

## 4. Field naming

- Currency suffix: `_usd`.
- Rate suffix: `_pct` for percent, `_rate` for proportion.
- Counts: plural noun (`opportunities`, `meetings_scheduled`).
- IDs: `<entity>_id`.
- Foreign keys: keep entity prefix (`source_campaign_id`, `assigned_rm_id`).

## 5. Date handling

A standalone `Date` dimension (calendar table) should join the four date columns (`activity_date`, `created_date`, `close_date`, `start_date`). For Tableau, build separate role-playing date relationships rather than a unioned table to keep aggregations fast.
