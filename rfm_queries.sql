-- rfm_queries.sql
-- Run against data/retail_rfm.db, e.g.: sqlite3 -header -column data/retail_rfm.db < sql/rfm_queries.sql
-- Demonstrates the same RFM logic as notebook/02_rfm_and_cohort.py, in pure SQL.

-- 1. Recency, Frequency, Monetary per customer (raw values)
WITH snapshot AS (
    SELECT date(MAX(InvoiceDate), '+1 day') AS snapshot_date FROM transactions
),
rfm_raw AS (
    SELECT
        t.CustomerID,
        CAST(julianday((SELECT snapshot_date FROM snapshot)) - julianday(MAX(t.InvoiceDate)) AS INTEGER) AS recency_days,
        COUNT(DISTINCT t.InvoiceNo) AS frequency,
        ROUND(SUM(t.Quantity * t.UnitPrice), 2) AS monetary
    FROM transactions t
    GROUP BY t.CustomerID
)
SELECT * FROM rfm_raw ORDER BY monetary DESC LIMIT 20;

-- 2. Quartile scoring using NTILE (SQL equivalent of pandas qcut)
WITH snapshot AS (
    SELECT date(MAX(InvoiceDate), '+1 day') AS snapshot_date FROM transactions
),
rfm_raw AS (
    SELECT
        t.CustomerID,
        CAST(julianday((SELECT snapshot_date FROM snapshot)) - julianday(MAX(t.InvoiceDate)) AS INTEGER) AS recency_days,
        COUNT(DISTINCT t.InvoiceNo) AS frequency,
        SUM(t.Quantity * t.UnitPrice) AS monetary
    FROM transactions t
    GROUP BY t.CustomerID
),
scored AS (
    SELECT
        CustomerID, recency_days, frequency, monetary,
        -- Lower recency_days = better (more recent purchase). Bucket 1 = lowest recency_days = best,
        -- so we flip it to a score of 4 for bucket 1, down to 1 for bucket 4.
        (5 - NTILE(4) OVER (ORDER BY recency_days ASC)) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC)           AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC)            AS m_score
    FROM rfm_raw
)
SELECT
    CustomerID, recency_days, frequency, ROUND(monetary,2) AS monetary,
    r_score, f_score, m_score, (r_score + f_score + m_score) AS rfm_total
FROM scored
ORDER BY rfm_total DESC
LIMIT 20;

-- 3. Revenue concentration — what % of revenue comes from the top 20% of customers? (Pareto check)
WITH customer_revenue AS (
    SELECT CustomerID, SUM(Quantity * UnitPrice) AS revenue
    FROM transactions
    GROUP BY CustomerID
),
ranked AS (
    SELECT *, NTILE(5) OVER (ORDER BY revenue DESC) AS quintile
    FROM customer_revenue
)
SELECT
    CASE WHEN quintile = 1 THEN 'Top 20%' ELSE 'Remaining 80%' END AS customer_group,
    COUNT(*) AS num_customers,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM customer_revenue), 1) AS pct_of_total_revenue
FROM ranked
GROUP BY customer_group;

-- 4. Monthly active customers (simple retention proxy)
SELECT
    strftime('%Y-%m', InvoiceDate) AS month,
    COUNT(DISTINCT CustomerID) AS active_customers,
    ROUND(SUM(Quantity * UnitPrice), 2) AS revenue
FROM transactions
GROUP BY month
ORDER BY month;

-- 5. First-purchase cohort month per customer (building block for cohort retention)
SELECT
    CustomerID,
    strftime('%Y-%m', MIN(InvoiceDate)) AS cohort_month
FROM transactions
GROUP BY CustomerID
ORDER BY cohort_month
LIMIT 20;
