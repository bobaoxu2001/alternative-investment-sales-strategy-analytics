-- =============================================================================
-- 05_advisor_priority_scoring.sql
-- Author: Allen Xu
--
-- Advisor priority score for sales prioritization. Implements the same
-- weighted formula used in src/run_analysis.py:
--
--   priority_score =
--       0.30 * normalized engagement
--     + 0.25 * normalized AUM
--     + 0.20 * normalized conversion probability
--     + 0.15 * normalized product-fit (asset classes touched / 4)
--     + 0.10 * normalized recency
-- =============================================================================

WITH activity_rollup AS (
    SELECT
        advisor_id,
        COUNT(*)                                     AS activity_count,
        AVG(engagement_score)                        AS avg_engagement,
        MAX(activity_date)                           AS last_activity_date,
        COUNT(DISTINCT asset_class_discussed)        AS classes_touched
    FROM sales_activities
    GROUP BY advisor_id
),
opportunity_rollup AS (
    SELECT
        advisor_id,
        COUNT(*)                                     AS opp_count,
        SUM(expected_commitment)                     AS expected_pipeline,
        SUM(COALESCE(actual_commitment, 0))          AS committed_capital,
        AVG(probability)                             AS avg_probability,
        SUM(CASE WHEN current_stage = 'Committed' THEN 1 ELSE 0 END)
                                                     AS committed_count
    FROM opportunities
    GROUP BY advisor_id
),
horizon AS (
    SELECT MIN(activity_date) AS first_dt,
           MAX(activity_date) AS last_dt
    FROM sales_activities
),
scored AS (
    SELECT
        a.advisor_id,
        a.advisor_name,
        a.firm_name,
        a.firm_type,
        a.region,
        a.aum_segment,
        a.client_type,
        a.assigned_rm_id,
        COALESCE(ar.activity_count, 0)               AS activity_count,
        COALESCE(ar.avg_engagement, 20)              AS avg_engagement,
        COALESCE(or_.opp_count, 0)                   AS opp_count,
        COALESCE(or_.committed_capital, 0)           AS committed_capital,
        COALESCE(or_.expected_pipeline, 0)           AS expected_pipeline,

        -- engagement component (0..1)
        MIN(MAX(COALESCE(ar.avg_engagement, 20) / 100.0, 0), 1)
                                                     AS engagement_norm,

        -- AUM component (0..1)
        CASE a.aum_segment
            WHEN '<100M'     THEN 0.15
            WHEN '100M-500M' THEN 0.40
            WHEN '500M-1B'   THEN 0.60
            WHEN '1B-5B'     THEN 0.80
            WHEN '5B+'       THEN 0.95
            ELSE 0.40
        END                                          AS aum_norm,

        -- conversion probability component
        CASE
            WHEN COALESCE(or_.opp_count, 0) > 0
                THEN COALESCE(or_.avg_probability, 0) / 100.0
            ELSE
                0.7 * CASE a.prior_alt_investment_experience
                          WHEN 'Low' THEN 0.20
                          WHEN 'Medium' THEN 0.55
                          WHEN 'High' THEN 0.85
                          ELSE 0.50 END
                + 0.3 * COALESCE(ar.avg_engagement, 20) / 100.0
        END                                          AS conv_prob_norm,

        -- product fit component (asset classes touched / 4)
        MIN(COALESCE(ar.classes_touched, 0) / 4.0, 1.0)
                                                     AS product_fit_norm,

        -- recency component (1 - days_since_last / horizon)
        CASE
            WHEN ar.last_activity_date IS NULL THEN 0.0
            ELSE 1.0
                 - (julianday((SELECT last_dt FROM horizon))
                    - julianday(ar.last_activity_date))
                   / NULLIF(julianday((SELECT last_dt FROM horizon))
                            - julianday((SELECT first_dt FROM horizon)), 0)
        END                                          AS recency_norm
    FROM advisors AS a
    LEFT JOIN activity_rollup     AS ar  ON a.advisor_id = ar.advisor_id
    LEFT JOIN opportunity_rollup  AS or_ ON a.advisor_id = or_.advisor_id
),
with_score AS (
    SELECT
        s.*,
        ROUND(
            0.30 * engagement_norm
          + 0.25 * aum_norm
          + 0.20 * conv_prob_norm
          + 0.15 * product_fit_norm
          + 0.10 * recency_norm
        , 4) AS priority_score
    FROM scored AS s
),
tiers AS (
    SELECT
        ws.*,
        CASE
            WHEN priority_score >=
                 (SELECT priority_score FROM with_score
                  ORDER BY priority_score DESC
                  LIMIT 1 OFFSET (SELECT CAST(COUNT(*) * 0.33 AS INT) FROM with_score))
                THEN 'High'
            WHEN priority_score >=
                 (SELECT priority_score FROM with_score
                  ORDER BY priority_score DESC
                  LIMIT 1 OFFSET (SELECT CAST(COUNT(*) * 0.67 AS INT) FROM with_score))
                THEN 'Medium'
            ELSE 'Low'
        END AS priority_tier
    FROM with_score AS ws
)

SELECT
    t.advisor_id,
    t.advisor_name,
    t.firm_name,
    t.firm_type,
    t.region,
    t.aum_segment,
    t.assigned_rm_id,
    t.activity_count,
    ROUND(t.avg_engagement, 2)                       AS avg_engagement,
    t.opp_count,
    t.committed_capital,
    t.expected_pipeline,
    ROUND(t.engagement_norm, 4)                      AS engagement_norm,
    ROUND(t.aum_norm, 4)                             AS aum_norm,
    ROUND(t.conv_prob_norm, 4)                       AS conv_prob_norm,
    ROUND(t.product_fit_norm, 4)                     AS product_fit_norm,
    ROUND(t.recency_norm, 4)                         AS recency_norm,
    t.priority_score,
    t.priority_tier,
    -- Recommended next action heuristic
    CASE
        WHEN t.priority_tier = 'High' AND t.committed_capital > 0
            THEN 'Portfolio Review Conversation'
        WHEN t.priority_tier = 'High' AND t.conv_prob_norm >= 0.5
            THEN 'Schedule Due Diligence Meeting'
        WHEN t.priority_tier = 'High'
            THEN 'Relationship Manager Follow-up'
        WHEN t.priority_tier = 'Medium' AND t.recency_norm < 0.5
            THEN 'Re-engagement Campaign'
        WHEN t.priority_tier = 'Medium' AND t.product_fit_norm < 0.5
            THEN 'Send Education Materials'
        WHEN t.priority_tier = 'Medium'
            THEN 'Invite to Market Outlook Webinar'
        WHEN t.activity_count = 0
            THEN 'Send Education Materials'
        ELSE 'Re-engagement Campaign'
    END                                              AS recommended_next_action
FROM tiers AS t
ORDER BY t.priority_score DESC;
