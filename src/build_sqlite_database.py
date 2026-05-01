"""
Load all raw CSV files into a SQLite database for downstream SQL analysis.

Author: Allen Xu

Output: data/processed/alternative_investment_sales.db
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = PROCESSED_DIR / "alternative_investment_sales.db"

TABLES = {
    "relationship_managers": "relationship_managers.csv",
    "advisors": "advisors.csv",
    "funds": "funds.csv",
    "campaigns": "campaigns.csv",
    "sales_activities": "sales_activities.csv",
    "opportunities": "opportunities.csv",
    "campaign_engagement": "campaign_engagement.csv",
}


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        for table, file_name in TABLES.items():
            csv_path = RAW_DIR / file_name
            df = pd.read_csv(csv_path)
            df.to_sql(table, conn, index=False, if_exists="replace")
            print(f"Loaded {table:<22}: {len(df):>6,} rows")

        # Helpful indexes for analytical joins
        cur = conn.cursor()
        cur.executescript("""
            CREATE INDEX IF NOT EXISTS idx_act_advisor   ON sales_activities(advisor_id);
            CREATE INDEX IF NOT EXISTS idx_act_rm        ON sales_activities(rm_id);
            CREATE INDEX IF NOT EXISTS idx_opp_advisor   ON opportunities(advisor_id);
            CREATE INDEX IF NOT EXISTS idx_opp_rm        ON opportunities(rm_id);
            CREATE INDEX IF NOT EXISTS idx_opp_fund      ON opportunities(fund_id);
            CREATE INDEX IF NOT EXISTS idx_opp_campaign  ON opportunities(source_campaign_id);
            CREATE INDEX IF NOT EXISTS idx_eng_campaign  ON campaign_engagement(campaign_id);
            CREATE INDEX IF NOT EXISTS idx_eng_advisor   ON campaign_engagement(advisor_id);
        """)
        conn.commit()
        print(f"\nSQLite database written to: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
