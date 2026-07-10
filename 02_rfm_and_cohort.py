"""
02_rfm_and_cohort.py — Build RFM segmentation and cohort retention tables.

Usage:
    python notebook/02_rfm_and_cohort.py

Reads:  data/online_retail_clean.csv
Writes: data/rfm_table.csv, data/cohort_retention.csv, dashboard/data.json
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = ROOT / "data" / "online_retail_clean.csv"
RFM_PATH = ROOT / "data" / "rfm_table.csv"
COHORT_PATH = ROOT / "data" / "cohort_retention.csv"
DASHBOARD_JSON = ROOT / "dashboard" / "data.json"


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    # Snapshot date = 1 day after the last transaction in the dataset (standard RFM convention)
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("LineRevenue", "sum"),
    ).reset_index()

    # Score each dimension 1-4 using quartiles (4 = best: most recent, most frequent, highest spend)
    rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

    def segment(row):
        if row["R_score"] == 4 and row["F_score"] >= 3 and row["M_score"] >= 3:
            return "Champions"
        if row["R_score"] >= 3 and row["F_score"] >= 3:
            return "Loyal Customers"
        if row["R_score"] >= 3 and row["F_score"] <= 2:
            return "Potential Loyalists"
        if row["R_score"] == 4 and row["F_score"] == 1:
            return "New Customers"
        if row["R_score"] == 2 and row["F_score"] >= 2:
            return "At Risk"
        if row["R_score"] == 1 and row["F_score"] >= 3:
            return "Cannot Lose Them"
        if row["R_score"] <= 2 and row["F_score"] <= 2:
            return "Hibernating / Churned"
        return "Needs Attention"

    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm


def build_cohort_retention(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["OrderPeriod"] = df["InvoiceDate"].dt.to_period("M")
    df["CohortMonth"] = df.groupby("CustomerID")["InvoiceDate"].transform("min").dt.to_period("M")

    def period_diff(row):
        return (row["OrderPeriod"].year - row["CohortMonth"].year) * 12 + (row["OrderPeriod"].month - row["CohortMonth"].month)

    df["CohortIndex"] = df.apply(period_diff, axis=1)

    cohort_data = df.groupby(["CohortMonth", "CohortIndex"])["CustomerID"].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index="CohortMonth", columns="CohortIndex", values="CustomerID")
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0).round(4)

    retention_long = retention.reset_index().melt(id_vars="CohortMonth", var_name="CohortIndex", value_name="RetentionRate")
    retention_long = retention_long.dropna(subset=["RetentionRate"])
    retention_long["CohortMonth"] = retention_long["CohortMonth"].astype(str)
    return retention_long, cohort_size


def main():
    df = pd.read_csv(CLEAN_PATH, parse_dates=["InvoiceDate"])

    rfm = build_rfm(df)
    rfm.to_csv(RFM_PATH, index=False)
    print(f"RFM table saved -> {RFM_PATH} ({len(rfm)} customers)")
    print(rfm["Segment"].value_counts())

    retention_long, cohort_size = build_cohort_retention(df)
    retention_long.to_csv(COHORT_PATH, index=False)
    print(f"Cohort retention saved -> {COHORT_PATH}")

    # ---- Build dashboard JSON ----
    segment_summary = rfm.groupby("Segment").agg(
        customers=("CustomerID", "count"),
        total_revenue=("Monetary", "sum"),
        avg_recency=("Recency", "mean"),
        avg_frequency=("Frequency", "mean"),
    ).reset_index().sort_values("total_revenue", ascending=False)

    churned_mask = rfm["Segment"].isin(["Hibernating / Churned", "At Risk", "Cannot Lose Them"])
    churn_rate = round(churned_mask.sum() / len(rfm) * 100, 1)

    total_revenue = df["LineRevenue"].sum()
    at_risk_revenue = rfm.loc[rfm["Segment"] == "At Risk", "Monetary"].sum()
    champions_revenue = rfm.loc[rfm["Segment"] == "Champions", "Monetary"].sum()

    # Monthly revenue trend
    monthly = df.groupby(df["InvoiceDate"].dt.to_period("M"))["LineRevenue"].sum()
    monthly.index = monthly.index.astype(str)

    # Cohort heatmap matrix (first 8 cohort months, first 6 indices, for readability)
    pivot = retention_long.pivot(index="CohortMonth", columns="CohortIndex", values="RetentionRate")
    pivot = pivot.iloc[:9, :7]  # trim for a clean heatmap

    dashboard_data = {
        "kpis": {
            "total_customers": int(len(rfm)),
            "total_revenue": round(float(total_revenue), 0),
            "churn_rate_pct": churn_rate,
            "champions_revenue": round(float(champions_revenue), 0),
            "at_risk_revenue": round(float(at_risk_revenue), 0),
        },
        "segments": {
            "labels": segment_summary["Segment"].tolist(),
            "customers": segment_summary["customers"].tolist(),
            "revenue": [round(float(x), 0) for x in segment_summary["total_revenue"]],
        },
        "monthly_revenue": {
            "months": monthly.index.tolist(),
            "revenue": [round(float(x), 0) for x in monthly.values],
        },
        "cohort_heatmap": {
            "cohorts": pivot.index.tolist(),
            "columns": [int(c) for c in pivot.columns.tolist()],
            "matrix": [[None if pd.isna(v) else round(float(v) * 100, 1) for v in row] for row in pivot.values],
        },
    }

    with open(DASHBOARD_JSON, "w") as f:
        json.dump(dashboard_data, f, indent=2)
    print(f"Dashboard data written -> {DASHBOARD_JSON}")
    print(json.dumps(dashboard_data["kpis"], indent=2))


if __name__ == "__main__":
    main()
