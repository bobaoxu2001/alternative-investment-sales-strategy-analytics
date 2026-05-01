-- =============================================================================
-- 04_campaign_roi_analysis.sql
-- Author: Allen Xu
--
-- Campaign ROI: cost efficiency, qualified-opportunity conversion, and
-- attributable committed capital. Uses a 2.5% management-fee proxy on
-- committed capital to estimate annual fee revenue per campaign.
-- =============================================================================

-- 1. Per-campaign engagement and pipeline rollup
WITH engagement_metrics AS (
    SELECT
        campaign_id,
        COUNT(DISTINCT advisor_id)                AS advisors_reached,
        SUM(opened_email)                         AS emails_opened,
        SUM(attended_event)                       AS events_attended,
        SUM(downloaded_materials)                 AS materials_downloaded,
        SUM(requested_followup)                   AS followups_requested,
        SUM(scheduled_meeting)                    AS meetings_scheduled,
        ROUND(AVG(engagement_score), 2)           AS avg_engagement
    FROM campaign_engagement
    GROUP BY campaign_id
),
opportunity_metrics AS (
    SELECT
        source_campaign_id                        AS campaign_id,
        COUNT(*)                                  AS opportunities_generated,
        SUM(CASE WHEN current_stage IN ('Due Diligence', 'Soft Circle', 'Committed')
                  THEN 1 ELSE 0 END)              AS qualified_opps,
        SUM(CASE WHEN current_stage = 'Committed' THEN 1 ELSE 0 END)
                                                  AS committed_opps,
        SUM(expected_commitment)                  AS expected_pipeline_usd,
        SUM(COALESCE(actual_commitment, 0))       AS committed_capital_usd
    FROM opportunities
    WHERE source_campaign_id IS NOT NULL
    GROUP BY source_campaign_id
)

-- 2. Per-campaign ROI
SELECT
    c.campaign_id,
    c.campaign_name,
    c.campaign_type,
    c.target_segment,
    c.asset_class_focus,
    c.region,
    c.campaign_cost,
    COALESCE(e.advisors_reached, 0)               AS advisors_reached,
    COALESCE(e.events_attended, 0)                AS events_attended,
    COALESCE(e.meetings_scheduled, 0)             AS meetings_scheduled,
    COALESCE(o.opportunities_generated, 0)        AS opportunities_generated,
    COALESCE(o.qualified_opps, 0)                 AS qualified_opps,
    COALESCE(o.committed_opps, 0)                 AS committed_opps,
    COALESCE(o.expected_pipeline_usd, 0)          AS expected_pipeline_usd,
    COALESCE(o.committed_capital_usd, 0)          AS committed_capital_usd,
    -- cost-per metrics
    CASE WHEN COALESCE(e.advisors_reached, 0) > 0
         THEN ROUND(c.campaign_cost * 1.0 / e.advisors_reached, 2) END
                                                  AS cost_per_advisor_reached,
    CASE WHEN COALESCE(o.qualified_opps, 0) > 0
         THEN ROUND(c.campaign_cost * 1.0 / o.qualified_opps, 2) END
                                                  AS cost_per_qualified_opportunity,
    CASE WHEN COALESCE(o.committed_opps, 0) > 0
         THEN ROUND(c.campaign_cost * 1.0 / o.committed_opps, 2) END
                                                  AS cost_per_committed_opportunity,
    -- ROI proxy: 2.5% annual management fee on committed capital
    ROUND(COALESCE(o.committed_capital_usd, 0) * 0.025, 0)
                                                  AS fee_revenue_proxy_usd,
    CASE WHEN c.campaign_cost > 0
         THEN ROUND(100.0 * (COALESCE(o.committed_capital_usd, 0) * 0.025
                              - c.campaign_cost) / c.campaign_cost, 1)
         ELSE 0 END                               AS roi_pct
FROM campaigns AS c
LEFT JOIN engagement_metrics  AS e ON c.campaign_id = e.campaign_id
LEFT JOIN opportunity_metrics AS o ON c.campaign_id = o.campaign_id
ORDER BY committed_capital_usd DESC;

-- 3. ROI by campaign type (efficiency comparison)
SELECT
    c.campaign_type,
    COUNT(*)                                      AS campaigns_count,
    SUM(c.campaign_cost)                          AS total_spend_usd,
    SUM(COALESCE(o.qualified_opps, 0))            AS qualified_opps_total,
    SUM(COALESCE(o.committed_capital_usd, 0))     AS committed_capital_usd,
    CASE WHEN SUM(COALESCE(o.qualified_opps, 0)) > 0
         THEN ROUND(SUM(c.campaign_cost) * 1.0
                    / SUM(COALESCE(o.qualified_opps, 0)), 2) END
                                                  AS cost_per_qualified_opportunity,
    CASE WHEN SUM(c.campaign_cost) > 0
         THEN ROUND(SUM(COALESCE(o.committed_capital_usd, 0)) * 1.0
                    / SUM(c.campaign_cost), 2) END
                                                  AS committed_capital_to_cost_multiple
FROM campaigns AS c
LEFT JOIN (
    SELECT
        source_campaign_id AS campaign_id,
        SUM(CASE WHEN current_stage IN ('Due Diligence', 'Soft Circle', 'Committed')
                  THEN 1 ELSE 0 END)              AS qualified_opps,
        SUM(COALESCE(actual_commitment, 0))       AS committed_capital_usd
    FROM opportunities
    WHERE source_campaign_id IS NOT NULL
    GROUP BY source_campaign_id
) AS o ON c.campaign_id = o.campaign_id
GROUP BY c.campaign_type
ORDER BY committed_capital_to_cost_multiple DESC NULLS LAST;

-- 4. ROI by target segment
SELECT
    c.target_segment,
    COUNT(*)                                      AS campaigns_count,
    SUM(c.campaign_cost)                          AS total_spend_usd,
    SUM(COALESCE(o.committed_capital_usd, 0))     AS committed_capital_usd,
    CASE WHEN SUM(c.campaign_cost) > 0
         THEN ROUND(SUM(COALESCE(o.committed_capital_usd, 0)) * 1.0
                    / SUM(c.campaign_cost), 2) END AS committed_to_cost_multiple
FROM campaigns AS c
LEFT JOIN (
    SELECT source_campaign_id AS campaign_id,
           SUM(COALESCE(actual_commitment, 0))    AS committed_capital_usd
    FROM opportunities
    WHERE source_campaign_id IS NOT NULL
    GROUP BY source_campaign_id
) AS o ON c.campaign_id = o.campaign_id
GROUP BY c.target_segment
ORDER BY committed_to_cost_multiple DESC NULLS LAST;
