"""
03_load_sqlite.py — Load cleaned transactions and RFM table into SQLite,
so the RFM logic can also be demonstrated in pure SQL (see sql/rfm_queries.sql).

Usage:
    python notebook/03_load_sqlite.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = ROOT / "data" / "online_retail_clean.csv"
DB_PATH = ROOT / "data" / "retail_rfm.db"


def main():
    df = pd.read_csv(CLEAN_PATH, parse_dates=["InvoiceDate"])
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("transactions", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_customer ON transactions(CustomerID)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(InvoiceDate)")
    conn.commit()
    conn.close()
    print(f"Loaded {len(df):,} rows into {DB_PATH} (table: transactions)")


if __name__ == "__main__":
    main()
