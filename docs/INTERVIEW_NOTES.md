# Interview Notes: Alternative Investment Sales Strategy Analytics Platform

Author: Allen Xu

## 1. 30-Second Pitch

I built this project to simulate the type of analytics work a sales strategy team in alternative asset management would do. The project creates a synthetic but realistic distribution dataset with advisors, relationship managers, funds, sales activities, opportunities, and campaigns. The goal was not just to build a dashboard, but to answer business questions: where the funnel drops off, which RMs are productive, which products generate demand, which campaigns have the best ROI, and which advisors should be prioritized next.

## 2. Why I Built It

- The project is tailored to sales strategy analytics rather than generic dashboarding.
- It reflects the economics and operating model of alternative investment distribution.
- It demonstrates SQL, Python, BI-ready reporting, ROI analysis, and executive communication.
- It avoids confidential real client data by using deterministic synthetic data.

## 3. Business Problem

Alternative investment sales cycles are long, capital commitments are concentrated, and relationship managers need a practical way to prioritize coverage. Sales leadership also needs visibility into funnel health, relationship manager productivity, product demand, and campaign ROI so resources can be allocated to the highest-impact channels and advisor segments.

## 4. What I Built

- Synthetic data generator
- SQLite analytics database
- SQL analysis scripts
- Python analysis pipeline
- Processed dashboard-ready marts
- Executive charts
- Executive report
- Tableau / Power BI wireframe and data model
- Advisor priority scoring model

## 5. Key Metrics

- 400 advisors
- 16 relationship managers
- 10 funds
- 7,500 sales activities
- 1,500 opportunities
- 28 campaigns
- $58.8B expected pipeline
- $6.75B committed capital
- 10.87% conversion rate
- 132 high-priority advisors

## 6. Main Insights

- Northeast has the largest opportunity volume but weaker conversion than several smaller regions.
- Private Equity and Infrastructure show stronger conversion and capital efficiency in the modeled dataset.
- Some RMs show high engagement but lower conversion, suggesting a coaching opportunity around follow-up discipline.
- Email campaigns show the strongest modeled efficiency, but the ROI magnitude is synthetic and should be interpreted directionally.
- High-priority advisors represent a major next-quarter planning opportunity for RM coverage.

## 7. Technical Approach

Python generated deterministic synthetic data from a fixed random seed. pandas produced the processed analytics marts, SQLite supported SQL analysis and reproducible querying, Tableau / Power BI-ready CSV outputs were created for dashboard implementation, and matplotlib generated executive charts for the report and README.

## 8. How I Would Improve It

- Replace the rule-based priority score with logistic regression or gradient boosting.
- Connect the pipeline to CRM data from Salesforce or HubSpot.
- Use actual fund-level fee schedules instead of a 2.5% management-fee proxy.
- Add row-level security for RM-specific dashboard views.
- Deploy the dashboard to Tableau Server or Power BI Service.

## 9. How To Answer "Why Synthetic Data?"

Real advisor, investor, fund, and CRM data is confidential. I used synthetic data to demonstrate the analytical structure and business logic safely. The goal was not to claim real KKR results, but to show how I would structure the data, metrics, dashboards, and recommendations for a sales strategy analytics team.

## 10. How To Answer "What Was The Hardest Part?"

The hardest part was making the synthetic dataset realistic enough that the downstream insights were meaningful. I had to design relationships between AUM, advisor experience, engagement, pipeline stage, commitment size, campaign engagement, and RM activity so the analysis behaved like a real distribution business rather than random rows.
