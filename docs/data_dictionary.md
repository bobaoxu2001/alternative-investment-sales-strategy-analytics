# Data Dictionary Summary

This project uses deterministic synthetic data for a public portfolio/demo workflow. No real client, investor, fund, or firm data is included.

The full field-level data dictionary lives at [`../data/data_dictionary.md`](../data/data_dictionary.md). The main analytical entities are:

| Entity | Grain | Purpose |
|---|---|---|
| Advisors | One advisor or investor relationship | Segment coverage by firm type, region, AUM, client type, and RM owner |
| Relationship managers | One RM | Benchmark coverage productivity, conversion, engagement, and coaching flags |
| Funds | One fund | Evaluate demand by asset class, strategy, vintage, target return, and risk profile |
| Sales activities | One RM-advisor interaction | Measure engagement, follow-up discipline, product interest, and activity volume |
| Opportunities | One sales opportunity | Track expected commitment, stage, probability, close timing, loss reason, and actual commitment |
| Campaigns | One marketing campaign | Evaluate campaign type, cost, target segment, product focus, and region |
| Campaign engagement | One campaign-advisor engagement record | Measure opens, attendance, materials downloads, follow-up requests, meetings, and engagement score |

Processed marts in `data/processed/` support dashboard views for funnel conversion, RM productivity, product demand, campaign ROI, advisor priority scoring, and executive KPIs.
