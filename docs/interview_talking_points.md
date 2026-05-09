# Interview Talking Points

## 30-Second Pitch

This project is a portfolio-ready analytics dashboard for alternative investment sales strategy. It uses deterministic synthetic CRM-style data to show how a sales strategy team could monitor funnel conversion, evaluate investor segment demand, benchmark relationship-manager productivity, measure campaign ROI, and prioritize advisor outreach. The emphasis is not real investment performance; it is the analytical framework, data modeling, business storytelling, and reproducibility.

## 2-Minute Walkthrough

Start with the business problem: alternative investment sales cycles are long, commitments are concentrated, and RM time is expensive. Then show the data model: advisors, RMs, funds, activities, opportunities, campaigns, and engagement. Explain the five analysis modules: funnel conversion, RM productivity, product demand, campaign ROI, and advisor priority scoring. Move to the dashboard: KPI strip, analysis tabs, chart gallery, recommendation summary, and documentation. Close with validation: the dataset is synthetic, regenerated from a fixed seed, and checked through Python validation plus static-site linting.

## Key Business Metrics

- Expected pipeline
- Committed capital
- Overall conversion rate
- Average days to close
- Campaign spend and campaign-attributable committed capital
- Cost per qualified opportunity
- RM follow-up completion and conversion
- High-priority advisor count
- Advisor priority score and recommended next action

## Dashboard Design Tradeoffs

- Chose a static site because the project is a portfolio artifact and should be easy for recruiters to load.
- Kept interactions lightweight: module tabs, chart previews, and active navigation.
- Used executive-style KPI hierarchy so the page communicates quickly within 10 seconds.
- Added synthetic data disclosure near the top to avoid overclaiming.
- Used recommendation cards to make the project feel decision-oriented, not chart-only.

## How to Explain the Data Limitation

"The dataset is synthetic by design because real investor and CRM data would be confidential. I generated correlated demo data with a fixed seed to make the project reproducible and public-safe. I would not present these metrics as real business performance. The value of the project is the analytics structure: KPI definitions, data model, pipeline, validation, dashboard logic, and the way insights are translated into sales strategy decisions."

## Likely Interview Questions and Strong Answers

### 1. Why did you use synthetic data?

Real alternative investment sales and investor data is confidential. Synthetic data lets me demonstrate realistic analytics patterns while keeping the project safe to publish. I clearly disclose the limitation and focus on the framework rather than pretending the numbers are real.

### 2. How would this change with real CRM data?

I would add ingestion from Salesforce or HubSpot, data quality rules for account and opportunity ownership, scheduled refreshes, role-based access, and audit logs. I would also validate campaign attribution and priority scoring against historical closed/lost outcomes.

### 3. What is the most important KPI?

Conversion rate by segment is the most strategic KPI because it links coverage decisions to outcomes. Expected pipeline matters, but a large pipeline with weak conversion can mislead leadership.

### 4. Why use a rules-based advisor priority score?

For a portfolio/demo project, a rules-based score is transparent and easy to explain. In production, I would use it as a baseline and compare it with predictive models trained on real historical opportunity outcomes.

### 5. What would you improve next?

I would add cohort analysis for opportunity progression, predictive lead scoring, scenario modeling for RM coverage capacity, and a live data refresh pipeline connected to CRM engagement signals.
