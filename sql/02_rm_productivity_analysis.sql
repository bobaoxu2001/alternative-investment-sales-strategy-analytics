-- =============================================================================
-- 02_rm_productivity_analysis.sql
-- Author: Allen Xu
--
-- Relationship-manager productivity: activity volume, conversion, pipeline
-- per meeting, and a coaching-opportunity flag for RMs whose engagement is
-- strong but conversion is below the team median.
-- =============================================================================

-- 1. Activity rollup per RM
WITH rm_activity AS (
    SELECT
        rm_id,
        COUNT(*)                                       AS total_activities,
        ROUND(AVG(engagement_score), 2)                AS avg_engagement,
        SUM(CASE WHEN completed_followup = 'Yes' THEN 1 ELSE 0 END)
                                                       AS completed_followups,
        SUM(meeting_duration_minutes)                  AS total_meeting_minutes
    FROM sales_activities
    GROUP BY rm_id
),

-- 2. Pipeline rollup per RM
rm_pipeline AS (
    SELECT
        rm_id,
        COUNT(*)                                       AS total_opps,
        SUM(expected_commitment)                       AS total_pipeline,
        SUM(COALESCE(actual_commitment, 0))            AS committed_capital,
        SUM(CASE WHEN current_stage = 'Committed' THEN 1 ELSE 0 END)
                                                       AS committed_count,
        SUM(CASE WHEN current_stage = 'Lost' THEN 1 ELSE 0 END)
                                                       AS lost_count,
        ROUND(AVG(CASE WHEN current_stage = 'Committed'
                        THEN days_to_close END), 1)    AS avg_days_to_close
    FROM opportunities
    GROUP BY rm_id
),

-- 3. Combine and derive productivity metrics
rm_metrics AS (
    SELECT
        r.rm_id,
        r.rm_name,
        r.region,
        r.coverage_segment,
        r.sales_team,
        r.tenure_years,
        COALESCE(a.total_activities, 0)                AS total_activities,
        COALESCE(a.avg_engagement, 0)                  AS avg_engagement,
        COALESCE(a.completed_followups, 0)             AS completed_followups,
        COALESCE(p.total_opps, 0)                      AS total_opps,
        COALESCE(p.total_pipeline, 0)                  AS total_pipeline,
        COALESCE(p.committed_capital, 0)               AS committed_capital,
        COALESCE(p.committed_count, 0)                 AS committed_count,
        COALESCE(p.lost_count, 0)                      AS lost_count,
        p.avg_days_to_close,
        CASE WHEN COALESCE(p.total_opps, 0) > 0
             THEN ROUND(100.0 * p.committed_count / p.total_opps, 2)
             ELSE 0 END                                AS conversion_rate_pct,
        CASE WHEN COALESCE(a.total_activities, 0) > 0
             THEN ROUND(p.total_pipeline * 1.0 / a.total_activities, 0)
             ELSE 0 END                                AS pipeline_per_meeting_usd,
        CASE WHEN COALESCE(a.total_activities, 0) > 0
             THEN ROUND(p.committed_capital * 1.0 / a.total_activities, 0)
             ELSE 0 END                                AS commitment_per_meeting_usd,
        CASE WHEN COALESCE(a.total_activities, 0) > 0
             THEN ROUND(100.0 * a.completed_followups / a.total_activities, 2)
             ELSE 0 END                                AS followup_completion_rate_pct
    FROM relationship_managers AS r
    LEFT JOIN rm_activity AS a ON r.rm_id = a.rm_id
    LEFT JOIN rm_pipeline AS p ON r.rm_id = p.rm_id
)

-- 4. Final output with coaching-opportunity flag
SELECT
    m.*,
    CASE
        WHEN m.avg_engagement >= (SELECT AVG(avg_engagement) FROM rm_metrics)
         AND m.conversion_rate_pct < (SELECT AVG(conversion_rate_pct) FROM rm_metrics)
        THEN 'Coaching Opportunity'
        ELSE 'On Track'
    END AS coaching_flag
FROM rm_metrics AS m
ORDER BY m.committed_capital DESC;
