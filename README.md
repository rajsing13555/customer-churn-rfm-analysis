# Customer Churn & RFM Segmentation Analysis
### Python (pandas) + SQL + Tableau — cohort retention, RFM segmentation, and win-back recommendations for a UK online retailer

**Role:** Solo Data Analyst (full pipeline) | **Dataset:** UK online retailer, Dec 2010 – Dec 2011 (397,884 cleaned transactions, 4,338 customers)

---

## 🧭 TL;DR

This project segments a retailer's customers using **RFM (Recency, Frequency, Monetary) analysis**, builds a **monthly cohort retention model** to see how purchasing behavior decays over time, and translates both into a prioritized, budget-aware retention strategy.

**Headline finding:** the top 18.4% of customers ("Champions") generate 55.1% of all revenue, while every monthly cohort loses ~80% of its customers by the second month — meaning the single highest-leverage fix is improving the first-to-second-purchase conversion, not broad win-back campaigns. Full breakdown in [`reports/insights_report.md`](./reports/insights_report.md).

## 📁 What's inside

| Path | What it is |
|---|---|
| [`notebook/01_clean_data.py`](./notebook/01_clean_data.py) | Cleans the raw transaction export (removes cancellations, nulls, bad rows) |
| [`notebook/02_rfm_and_cohort.py`](./notebook/02_rfm_and_cohort.py) | Computes RFM scores/segments and monthly cohort retention; exports dashboard data |
| [`notebook/03_load_sqlite.py`](./notebook/03_load_sqlite.py) | Loads cleaned data into SQLite for the SQL-based analysis |
| [`sql/rfm_queries.sql`](./sql/rfm_queries.sql) | Pure-SQL RFM scoring using window functions (`NTILE`), revenue concentration, cohort building blocks |
| [`dashboard/index.html`](./dashboard/index.html) | Interactive dashboard — segment revenue, cohort retention heatmap, KPIs. Open directly in any browser |
| [`tableau/TABLEAU_INSTRUCTIONS.md`](./tableau/TABLEAU_INSTRUCTIONS.md) | Step-by-step guide to rebuild the segment view and cohort heatmap in Tableau |
| [`reports/insights_report.md`](./reports/insights_report.md) | Full findings, methodology, and prioritized recommendations |
| `data/rfm_table.csv`, `data/cohort_retention.csv` | Processed outputs — small enough to commit and reuse directly |

## 🖥️ View the dashboard

Open `dashboard/index.html` directly in any browser — it reads `dashboard/data.json` and renders instantly, no server or install needed.

## 🗄️ Reproducing from scratch

The raw dataset (~43MB) isn't committed to this repo (see `.gitignore`) to keep it lightweight. To rebuild everything from the original source:

1. Download the "Online Retail" dataset from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online+retail) (Chen, D., 2015) and save it as `data/online_retail_raw.csv`.
2. Run the pipeline:
   ```bash
   cd notebook
   python 01_clean_data.py       # raw -> data/online_retail_clean.csv
   python 02_rfm_and_cohort.py   # clean -> rfm_table.csv, cohort_retention.csv, dashboard/data.json
   python 03_load_sqlite.py      # clean -> data/retail_rfm.db (for SQL queries)
   ```
3. Run the SQL analysis directly:
   ```bash
   sqlite3 -header -column data/retail_rfm.db < sql/rfm_queries.sql
   ```

## 📊 Key numbers

| Metric | Value |
|---|---|
| Total revenue analyzed | £8.91M |
| Customers currently At Risk / Hibernating / Cannot Lose Them | 49.6% |
| Revenue share from top 18.4% of customers (Champions) | 55.1% |
| Average month-1 cohort retention | 20.6% |

Full breakdown, segment definitions, and prioritized recommendations in [`reports/insights_report.md`](./reports/insights_report.md).

## 🛠️ Tools & techniques used

`Python (pandas)` · `SQLite / SQL (window functions, CTEs)` · `Tableau` · `RFM Segmentation` · `Cohort Retention Analysis` · `Chart.js`

---
*Built by Raj Singh — [LinkedIn](https://linkedin.com/in/rajsingh-dataanalyst) · [GitHub](https://github.com/rajsing13555)*
