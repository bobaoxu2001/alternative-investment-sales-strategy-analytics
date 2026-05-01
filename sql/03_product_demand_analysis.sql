-- =============================================================================
-- 03_product_demand_analysis.sql
-- Author: Allen Xu
--
-- Product demand by asset class, by individual fund, and across advisor
-- segments. Surfaces where committed capital is concentrated and where
-- engagement is highest.
-- =============================================================================

-- 1. Asset-class demand: activity engagement and committed capital
SELECT
    f.asset_class,
    COUNT(DISTINCT o.opportunity_id)              AS opportunities,
    SUM(o.expected_commitment)                    AS expected_pipeline_usd,
    SUM(COALESCE(o.actual_commitment, 0))         AS committed_capital_usd,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage = 'Committed' THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)             AS conversion_rate_pct
FROM opportunities AS o
JOIN funds AS f ON o.fund_id = f.fund_id
GROUP BY f.asset_class
ORDER BY committed_capital_usd DESC;

-- 2. Activity touchpoints by asset class (different table; engagement focus)
SELECT
    asset_class_discussed AS asset_class,
    COUNT(*)                          AS activities,
    ROUND(AVG(engagement_score), 2)   AS avg_engagement,
    SUM(CASE WHEN next_step_required = 'Yes' THEN 1 ELSE 0 END)
                                      AS next_steps_required,
    SUM(CASE WHEN completed_followup = 'Yes' THEN 1 ELSE 0 END)
                                      AS followups_completed
FROM sales_activities
GROUP BY asset_class_discussed
ORDER BY avg_engagement DESC;

-- 3. Fund-level demand
SELECT
    f.fund_id,
    f.fund_name,
    f.asset_class,
    f.strategy,
    COUNT(o.opportunity_id)                     AS opportunities,
    SUM(o.expected_commitment)                  AS expected_pipeline_usd,
    SUM(COALESCE(o.actual_commitment, 0))       AS committed_capital_usd,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage = 'Committed' THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)           AS conversion_rate_pct,
    ROUND(AVG(CASE WHEN o.current_stage = 'Committed'
                    THEN o.days_to_close END), 1) AS avg_days_to_close
FROM opportunities AS o
JOIN funds AS f ON o.fund_id = f.fund_id
GROUP BY f.fund_id, f.fund_name, f.asset_class, f.strategy
ORDER BY committed_capital_usd DESC;

-- 4. Demand by firm type x asset class — which channels prefer which products
SELECT
    a.firm_type,
    f.asset_class,
    COUNT(o.opportunity_id)                     AS opportunities,
    SUM(o.expected_commitment)                  AS expected_pipeline_usd,
    SUM(COALESCE(o.actual_commitment, 0))       AS committed_capital_usd,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage = 'Committed' THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)           AS conversion_rate_pct
FROM opportunities AS o
JOIN advisors AS a ON o.advisor_id = a.advisor_id
JOIN funds    AS f ON o.fund_id    = f.fund_id
GROUP BY a.firm_type, f.asset_class
ORDER BY a.firm_type, committed_capital_usd DESC;

-- 5. Demand by region x asset class
SELECT
    a.region,
    f.asset_class,
    COUNT(o.opportunity_id)                     AS opportunities,
    SUM(o.expected_commitment)                  AS expected_pipeline_usd,
    SUM(COALESCE(o.actual_commitment, 0))       AS committed_capital_usd
FROM opportunities AS o
JOIN advisors AS a ON o.advisor_id = a.advisor_id
JOIN funds    AS f ON o.fund_id    = f.fund_id
GROUP BY a.region, f.asset_class
ORDER BY a.region, committed_capital_usd DESC;
