# Dashboard Wireframe

**Project:** Alternative Investment Sales Strategy Analytics Platform
**Author:** Allen Xu

The dashboard ships as four pages. Each page below shows a layout sketch in ASCII, the visuals, and the underlying data source.

---

## Page 1: Executive Overview

Audience: Head of Global Client Solutions / Global Wealth Solutions, sales leadership.
Goal: 10-second view of pipeline health, distribution efficiency, and where attention is needed.

```
+----------------------------------------------------------------------------------+
|                EXECUTIVE OVERVIEW   |  Region: All  |  Period: TTM  |  Refresh   |
+----------+----------+----------+----------+----------+-------------+-------------+
|  Pipeline |  Committed |  Conv    |  Avg Days |  Campaign  |  High-Priority   |
|  Value    |  Capital   |  Rate    |  to Close |  ROI       |  Advisors        |
|  $58.8B   |  $6.75B    |  10.9%   |  150      |  4655%     |  132             |
+-----------+-----------+----------+-----------+------------+------------------+
|                                                                                  |
|   Funnel by stage (bar)                |   Committed capital by region (map)   |
|                                        |                                        |
+-----------------------------------------------------------------------+----------+
|   Committed capital by asset class (bar)  |  Coaching-flagged RMs (table)       |
+----------------------------------------------------------------------------------+
```

Visuals:

- KPI tiles driven by `Executive KPIs` (`executive_kpi_summary.csv`).
- Funnel by stage from `Funnel Summary` where `group_label = 'stage'`.
- Region map from `Funnel Summary` where `group_label = 'region'`.
- Asset-class bar from `Product Demand` where `dimension = 'asset_class'`.
- Coaching table from `RM Productivity` filtered to `coaching_flag = 'Coaching Opportunity'`.

---

## Page 2: Sales Funnel & Product Demand

Audience: Sales strategy + product distribution leads.
Goal: Diagnose stage drop-off and where demand is concentrated.

```
+----------------------------------------------------------------------------------+
|                SALES FUNNEL & PRODUCT DEMAND                                     |
+----------------------------------------+-----------------------------------------+
|   Funnel chart (Prospect → Committed)  |   Conversion by region (bar)            |
|                                        |                                          |
+----------------------------------------+-----------------------------------------+
|                                                                                   |
|   Asset-class engagement vs committed capital (dual axis)                         |
|                                                                                   |
+----------------------------------------------------------------------------------+
|   Fund-level commitment table (sortable, $ committed, conv rate, days to close)  |
+----------------------------------------------------------------------------------+
```

Visuals:

- Funnel chart from `Funnel Summary` (`group_label='stage'`).
- Conversion by region from `Funnel Summary` (`group_label='region'`).
- Dual-axis from `Product Demand` (`dimension='asset_class'`).
- Fund table from `Product Demand` (`dimension='fund'`).

Filters: region, firm type, AUM segment.

---

## Page 3: Relationship Manager Productivity

Audience: Sales managers, RM coverage leadership.
Goal: Leaderboard, efficiency benchmarking, coaching identification.

```
+----------------------------------------------------------------------------------+
|                RELATIONSHIP MANAGER PRODUCTIVITY                                 |
+----------------------------------------------+-----------------------------------+
|   Committed-capital leaderboard (bar)        |   Conversion rate by RM (bar)    |
+----------------------------------------------+-----------------------------------+
|   Commitment per meeting (bar)               |   Days to close by RM (bar)      |
+----------------------------------------------+-----------------------------------+
|   Coaching matrix:                                                                |
|     X-axis: avg engagement     Y-axis: conversion rate                            |
|     Highlight quadrant: high engagement + low conversion                          |
+----------------------------------------------------------------------------------+
```

Visuals:

- All bars driven by `RM Productivity` (`rm_productivity_summary.csv`).
- Coaching matrix is a scatter colored by `coaching_flag`.

Filters: region, sales team, coverage segment.

---

## Page 4: Campaign ROI & Advisor Prioritization

Audience: Marketing, sales enablement, RMs.
Goal: Allocate next-quarter spend and outreach.

```
+----------------------------------------------------------------------------------+
|                CAMPAIGN ROI & ADVISOR PRIORITIZATION                             |
+----------------------------------------------+-----------------------------------+
|   ROI multiple by campaign type (bar)        |   Cost per qualified opp (bar)   |
+----------------------------------------------+-----------------------------------+
|   Top campaigns table:                                                            |
|   campaign_name | type | spend | qualified_opps | committed_capital | ROI %      |
+----------------------------------------------------------------------------------+
|   Priority advisor table (top 50):                                                |
|   advisor | firm | tier | priority_score | next_action | est. commitment $$      |
+----------------------------------------------------------------------------------+
|   Recommended next-action breakdown (donut)                                       |
+----------------------------------------------------------------------------------+
```

Visuals:

- Campaign-type bars from `Campaign ROI` aggregated to `campaign_type`.
- Top campaigns table from `Campaign ROI`.
- Priority advisor table and donut from `Advisor Priority`.

Filters: priority tier, region, firm type, recommended next action.
