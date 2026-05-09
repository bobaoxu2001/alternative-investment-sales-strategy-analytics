# Portfolio Case Study: Alternative Investment Sales Strategy Analytics

## Problem

Alternative investment distribution teams need to decide which advisor and investor segments deserve coverage, where opportunities are stalling, which strategies have the strongest demand, and which outreach channels are worth additional investment. Raw activity counts do not answer those questions because high activity can still produce weak conversion.

## Why It Matters for Alternative Investment Sales

Alternative investment sales cycles are long, commitments are large, and relationship-manager time is expensive. A sales strategy team needs funnel visibility, segment-level performance, and prioritization logic so coverage resources are aimed at the highest-potential relationships.

## Data and Assumptions

This is a synthetic/demo portfolio project. The dataset is generated deterministically and includes advisors, relationship managers, funds, sales activities, opportunities, campaigns, and campaign engagement. The data is designed to resemble CRM-style distribution data, but it does not contain real client, investor, fund, or firm records.

Key assumptions include a 12-month analysis window, stage-based opportunity probabilities, a simplified campaign attribution model, and a 2.5% fee-revenue proxy for campaign ROI.

## Dashboard Design

The dashboard is structured for recruiter and hiring-manager review:

- Executive KPI strip for pipeline, committed capital, conversion, advisor universe, and priority targets.
- Business problem section that frames why the analytics matter.
- Interactive analysis modules for funnel, RM productivity, product demand, campaign ROI, and advisor priority scoring.
- Executive chart gallery with concise insight callouts.
- Recommendation summary that turns findings into sales strategy actions.
- Quality and documentation section for methodology, validation, and reproducibility.

## Analytical Methods

- Funnel conversion analysis by stage, region, firm type, asset class, and AUM segment.
- RM productivity benchmarking using activity, engagement, follow-up completion, conversion, and committed capital.
- Product demand analysis comparing activity volume, engagement, pipeline, and committed capital.
- Campaign ROI analysis using spend, qualified opportunities, committed capital, and fee-revenue proxy.
- Advisor priority scoring using engagement, AUM segment, conversion probability, product fit, and recency.

## Key Insights

- Family Office and Institutional Investor segments are more capital-dense in the synthetic data.
- Northeast has the largest opportunity volume but weaker modeled conversion than Midwest and Southwest.
- Private Equity and Infrastructure show stronger conversion and capital efficiency in the demo dataset.
- Three relationship managers combine strong engagement with weaker conversion, suggesting follow-up discipline as a coaching theme.
- Email campaigns show high modeled efficiency, but synthetic ROI magnitude should be interpreted directionally.

## Limitations

- Results are computed from synthetic data and should not be treated as real investment sales performance.
- Campaign attribution is simplified and does not model multi-touch influence.
- Priority scoring is explainable and rules-based rather than trained on real closed/lost outcomes.
- The dashboard is static and does not connect to a live CRM or permissioned investor data source.

## Future Improvements

- Add CRM integration for real opportunity, activity, and engagement refreshes.
- Add cohort analysis for opportunity progression over time.
- Add predictive lead scoring using real historical closed/lost outcomes.
- Add scenario modeling for RM coverage and campaign budget allocation.
- Add access control, audit logs, and row-level security for production use.

## What This Project Demonstrates

This project demonstrates analytics engineering, SQL and Python analysis, synthetic data design, KPI modeling, executive dashboard storytelling, product-minded prioritization, and portfolio-grade documentation for investment analytics and sales strategy roles.
