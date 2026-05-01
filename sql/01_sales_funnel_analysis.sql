-- =============================================================================
-- 01_sales_funnel_analysis.sql
-- Author: Allen Xu
--
-- Sales funnel conversion across pipeline stages, regions, firm types, asset
-- classes, and AUM segments. Mirrors the funnel calculations produced by
-- src/run_analysis.py.
-- =============================================================================

-- 1. Overall funnel: opportunity volume and value at each pipeline stage
SELECT
    o.current_stage,
    COUNT(*)                                      AS opportunity_count,
    SUM(o.expected_commitment)                    AS expected_pipeline_usd,
    SUM(COALESCE(o.actual_commitment, 0))         AS committed_capital_usd,
    ROUND(AVG(o.probability), 2)                  AS avg_probability_pct,
    ROUND(AVG(o.days_to_close), 1)                AS avg_days_to_close
FROM opportunities AS o
GROUP BY o.current_stage
ORDER BY
    CASE o.current_stage
        WHEN 'Prospect'      THEN 1
        WHEN 'Interested'    THEN 2
        WHEN 'Due Diligence' THEN 3
        WHEN 'Soft Circle'   THEN 4
        WHEN 'Committed'     THEN 5
        WHEN 'Lost'          THEN 6
    END;

-- 2. Conversion rates by region: % progressing to DD, Soft Circle, Committed
SELECT
    a.region,
    COUNT(o.opportunity_id) AS total_opps,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage IN
            ('Due Diligence', 'Soft Circle', 'Committed') THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)             AS dd_or_later_rate,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage IN
            ('Soft Circle', 'Committed') THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)             AS soft_circle_or_later_rate,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage = 'Committed' THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)             AS committed_rate,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage = 'Lost' THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)             AS lost_rate,
    SUM(o.expected_commitment)                    AS expected_pipeline_usd,
    SUM(COALESCE(o.actual_commitment, 0))         AS committed_capital_usd
FROM opportunities AS o
JOIN advisors AS a ON o.advisor_id = a.advisor_id
GROUP BY a.region
ORDER BY committed_rate DESC;

-- 3. Conversion by firm type: which advisor channels close at the highest rate
SELECT
    a.firm_type,
    COUNT(o.opportunity_id) AS total_opps,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage = 'Committed' THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)             AS committed_rate,
    SUM(o.expected_commitment)                    AS expected_pipeline_usd,
    SUM(COALESCE(o.actual_commitment, 0))         AS committed_capital_usd,
    ROUND(AVG(CASE WHEN o.current_stage = 'Committed'
                    THEN o.days_to_close END), 1) AS avg_days_to_close
FROM opportunities AS o
JOIN advisors AS a ON o.advisor_id = a.advisor_id
GROUP BY a.firm_type
ORDER BY committed_capital_usd DESC;

-- 4. Asset class velocity: how quickly each asset class moves through the funnel
SELECT
    f.asset_class,
    COUNT(o.opportunity_id) AS total_opps,
    SUM(CASE WHEN o.current_stage = 'Committed' THEN 1 ELSE 0 END)
        AS committed_count,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage = 'Committed' THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)             AS committed_rate,
    ROUND(AVG(CASE WHEN o.current_stage = 'Committed'
                    THEN o.days_to_close END), 1) AS avg_days_to_close,
    SUM(o.expected_commitment)                    AS expected_pipeline_usd,
    SUM(COALESCE(o.actual_commitment, 0))         AS committed_capital_usd
FROM opportunities AS o
JOIN funds AS f ON o.fund_id = f.fund_id
GROUP BY f.asset_class
ORDER BY committed_capital_usd DESC;

-- 5. AUM segment funnel: do larger advisors progress further?
SELECT
    a.aum_segment,
    COUNT(o.opportunity_id) AS total_opps,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage IN
            ('Due Diligence', 'Soft Circle', 'Committed') THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)             AS dd_or_later_rate,
    ROUND(100.0 * SUM(CASE WHEN o.current_stage = 'Committed' THEN 1 ELSE 0 END)
        / COUNT(o.opportunity_id), 2)             AS committed_rate,
    SUM(o.expected_commitment)                    AS expected_pipeline_usd,
    SUM(COALESCE(o.actual_commitment, 0))         AS committed_capital_usd
FROM opportunities AS o
JOIN advisors AS a ON o.advisor_id = a.advisor_id
GROUP BY a.aum_segment
ORDER BY committed_rate DESC;
