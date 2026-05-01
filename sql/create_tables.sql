-- =============================================================================
-- Alternative Investment Sales Strategy Analytics Platform
-- create_tables.sql
-- Author: Allen Xu
--
-- DDL for the SQLite analytics database. The Python loader
-- (src/build_sqlite_database.py) writes these tables directly from CSV via
-- pandas.to_sql, so this file is provided as a reference / portable schema.
-- =============================================================================

DROP TABLE IF EXISTS relationship_managers;
DROP TABLE IF EXISTS advisors;
DROP TABLE IF EXISTS funds;
DROP TABLE IF EXISTS sales_activities;
DROP TABLE IF EXISTS opportunities;
DROP TABLE IF EXISTS campaigns;
DROP TABLE IF EXISTS campaign_engagement;

CREATE TABLE relationship_managers (
    rm_id              TEXT PRIMARY KEY,
    rm_name            TEXT NOT NULL,
    region             TEXT,
    tenure_years       INTEGER,
    coverage_segment   TEXT,
    sales_team         TEXT
);

CREATE TABLE advisors (
    advisor_id                          TEXT PRIMARY KEY,
    advisor_name                        TEXT,
    firm_name                           TEXT,
    firm_type                           TEXT,
    region                              TEXT,
    city                                TEXT,
    state                               TEXT,
    aum_segment                         TEXT,
    client_type                         TEXT,
    years_relationship                  INTEGER,
    prior_alt_investment_experience     TEXT,
    assigned_rm_id                      TEXT,
    FOREIGN KEY (assigned_rm_id) REFERENCES relationship_managers(rm_id)
);

CREATE TABLE funds (
    fund_id              TEXT PRIMARY KEY,
    fund_name            TEXT,
    asset_class          TEXT,
    strategy             TEXT,
    vintage_year         INTEGER,
    target_return_range  TEXT,
    liquidity_profile    TEXT,
    minimum_commitment   INTEGER,
    risk_profile         TEXT
);

CREATE TABLE sales_activities (
    activity_id              TEXT PRIMARY KEY,
    activity_date            DATE,
    advisor_id               TEXT,
    rm_id                    TEXT,
    activity_type            TEXT,
    product_discussed        TEXT,
    asset_class_discussed    TEXT,
    engagement_score         INTEGER,
    next_step_required       TEXT,
    completed_followup       TEXT,
    days_to_followup         INTEGER,
    meeting_duration_minutes INTEGER,
    FOREIGN KEY (advisor_id) REFERENCES advisors(advisor_id),
    FOREIGN KEY (rm_id)      REFERENCES relationship_managers(rm_id)
);

CREATE TABLE opportunities (
    opportunity_id        TEXT PRIMARY KEY,
    advisor_id            TEXT,
    rm_id                 TEXT,
    fund_id               TEXT,
    created_date          DATE,
    current_stage         TEXT,
    expected_commitment   INTEGER,
    actual_commitment     INTEGER,
    close_date            DATE,
    days_to_close         INTEGER,
    probability           INTEGER,
    source_campaign_id    TEXT,
    loss_reason           TEXT,
    FOREIGN KEY (advisor_id)         REFERENCES advisors(advisor_id),
    FOREIGN KEY (rm_id)              REFERENCES relationship_managers(rm_id),
    FOREIGN KEY (fund_id)            REFERENCES funds(fund_id),
    FOREIGN KEY (source_campaign_id) REFERENCES campaigns(campaign_id)
);

CREATE TABLE campaigns (
    campaign_id          TEXT PRIMARY KEY,
    campaign_name        TEXT,
    campaign_type        TEXT,
    start_date           DATE,
    end_date             DATE,
    target_segment       TEXT,
    product_focus        TEXT,
    asset_class_focus    TEXT,
    campaign_cost        INTEGER,
    region               TEXT
);

CREATE TABLE campaign_engagement (
    engagement_id          TEXT PRIMARY KEY,
    campaign_id            TEXT,
    advisor_id             TEXT,
    opened_email           INTEGER,
    attended_event         INTEGER,
    downloaded_materials   INTEGER,
    requested_followup     INTEGER,
    scheduled_meeting      INTEGER,
    engagement_score       INTEGER,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY (advisor_id)  REFERENCES advisors(advisor_id)
);

CREATE INDEX IF NOT EXISTS idx_act_advisor   ON sales_activities(advisor_id);
CREATE INDEX IF NOT EXISTS idx_act_rm        ON sales_activities(rm_id);
CREATE INDEX IF NOT EXISTS idx_opp_advisor   ON opportunities(advisor_id);
CREATE INDEX IF NOT EXISTS idx_opp_rm        ON opportunities(rm_id);
CREATE INDEX IF NOT EXISTS idx_opp_fund      ON opportunities(fund_id);
CREATE INDEX IF NOT EXISTS idx_opp_campaign  ON opportunities(source_campaign_id);
CREATE INDEX IF NOT EXISTS idx_eng_campaign  ON campaign_engagement(campaign_id);
CREATE INDEX IF NOT EXISTS idx_eng_advisor   ON campaign_engagement(advisor_id);
