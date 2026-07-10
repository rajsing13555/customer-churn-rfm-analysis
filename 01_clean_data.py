"""
01_clean_data.py — Clean the raw UCI "Online Retail" transaction export.

Source dataset: UK-based online retailer, transactions from 01/12/2010 to 09/12/2011.
(Chen, D., Sain, S.L., Guo, K. (2012). UCI Machine Learning Repository.)

Usage:
    python notebook/01_clean_data.py

Reads:  data/online_retail_raw.csv
Writes: data/online_retail_clean.csv
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "online_retail_raw.csv"
CLEAN_PATH = ROOT / "data" / "online_retail_clean.csv"


def main():
    print(f"Reading {RAW_PATH} ...")
    df = pd.read_csv(RAW_PATH, encoding="latin1")
    print(f"Raw rows: {len(df):,}")

    # Standardize column names
    df.columns = [c.strip() for c in df.columns]

    # Parse invoice date
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%Y %H:%M")

    # Drop rows with no CustomerID — can't attribute these to a customer for RFM/cohort analysis
    before = len(df)
    df = df.dropna(subset=["CustomerID"])
    print(f"Dropped {before - len(df):,} rows with missing CustomerID")

    # Remove cancellations (InvoiceNo starting with 'C') — these are returns, not purchases
    before = len(df)
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    print(f"Dropped {before - len(df):,} cancellation rows")

    # Remove non-positive quantity or price rows (data entry errors / adjustments)
    before = len(df)
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    print(f"Dropped {before - len(df):,} rows with non-positive quantity/price")

    # Derived columns
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["LineRevenue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)

    print(f"Clean rows: {len(df):,}")
    print(f"Unique customers: {df['CustomerID'].nunique():,}")
    print(f"Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")

    df.to_csv(CLEAN_PATH, index=False)
    print(f"Saved -> {CLEAN_PATH}")


if __name__ == "__main__":
    main()
