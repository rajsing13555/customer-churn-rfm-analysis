# Insights Report — Customer Churn & RFM Segmentation

*Dataset: UK-based online retailer, transactions Dec 2010 – Dec 2011 (Chen, Sain & Guo, 2012, UCI Machine Learning Repository). All figures below come directly from `notebook/02_rfm_and_cohort.py` and are reproducible via `sql/rfm_queries.sql`.*

## Executive Summary

Nearly half of this retailer's customer base (49.6%) is currently At Risk, Hibernating, or in the "Cannot Lose Them" danger zone — but revenue is heavily concentrated in a loyal core: the top 18.4% of customers (the "Champions" segment) generate 55.1% of total revenue. The business's growth is currently much more dependent on retaining a small core of high-value customers than on broad-based repeat purchasing, which has real implications for where a retention budget should go.

| Metric | Value |
|---|---|
| Total customers analyzed | 4,338 |
| Total revenue | £8.91M |
| Overall "at risk or churned" rate | 49.6% |
| Revenue from Champions segment | £4.91M (55.1% of total, from 18.4% of customers) |
| Revenue currently in "At Risk" segment | £955K |
| Average month-1 cohort retention | 20.6% |

## Finding 1 — RFM segment breakdown

| Segment | Customers | Revenue | Share of revenue |
|---|---|---|---|
| Champions | 799 | £4,911,049 | 55.1% |
| Loyal Customers | 724 | £1,690,327 | 19.0% |
| At Risk | 759 | £955,225 | 10.7% |
| Hibernating / Churned | 1,210 | £581,539 | 6.5% |
| Potential Loyalists | 665 | £501,953 | 5.6% |
| Cannot Lose Them | 181 | £271,316 | 3.0% |

**Read:** Champions (recent, frequent, high-spend customers) are only 18% of the base but drive over half of all revenue — a textbook Pareto pattern, even sharper than the classic 80/20 rule. Meanwhile, Hibernating/Churned is the *largest single segment by customer count* (1,210 customers, 28% of the base) but contributes only 6.5% of revenue — confirming that these customers were mostly low-value even before they churned, which should shape how much retention spend is justified per customer in this group.

## Finding 2 — "Cannot Lose Them" is small but high-value — the clearest action segment

The "Cannot Lose Them" segment (181 customers: historically high frequency and spend, but haven't purchased recently) represents £271,316 in historical revenue concentrated in very few customers. This is the highest-leverage, lowest-effort segment to target: a small, personalized win-back campaign here has a clear, calculable revenue ceiling and a short customer list to execute against.

## Finding 3 — Retention drops sharply after month 1, across every cohort

Every monthly cohort loses 63–89% of its customers by the second month (average month-1 retention: 20.6%, ranging from 11.2% in the weakest cohort to 36.6% in the strongest). No cohort in the dataset shows a fundamentally different retention curve — this is a structural, company-wide pattern rather than a one-off bad month, which matters for how a fix should be scoped (a broad onboarding/second-purchase intervention, not a fix targeted at one cohort or time period).

**Read:** the biggest single lever this business has is not acquisition — it's converting a customer's *first* purchase into a *second* one. Even a modest improvement in month-1 retention compounds across every future cohort.

## Finding 4 — Revenue concentration confirms the segment story

A pure revenue-based Pareto check (independent of the RFM segment labels, see `sql/rfm_queries.sql` Q3) shows the top 20% of customers by revenue generate 74.6% of total revenue — consistent with, and validating, the Champions-segment finding above using a completely different method.

## Recommendations, prioritized

1. **Immediate — win back "Cannot Lose Them" (181 customers, historically high-value):** A targeted, personal outreach campaign (not a mass email) — these customers have a proven track record and a small enough list to make 1:1 outreach economically viable.
2. **Short-term — fix the second-purchase gap:** Since every cohort loses ~80% of customers by month 2 regardless of when they joined, prioritize a lifecycle campaign (discount, reminder, or personalized recommendation) timed specifically around the 3–5 week mark after a customer's first purchase.
3. **Medium-term — protect the Champions segment:** With 55% of revenue concentrated in 18% of customers, even a small increase in Champions churn would materially hurt revenue. Consider a loyalty/VIP program specifically for this segment, since losing them is disproportionately costly compared to any other segment.
4. **De-prioritize:** Broad win-back campaigns aimed at the full "Hibernating/Churned" segment (1,210 customers) are likely to have poor ROI given their historically low spend (£581K total spread across 1,210 people, i.e. under £500 lifetime value each) — this budget is better spent on Finding 1 and 2 above.

## Methodology notes

- **RFM scoring:** Recency, Frequency, and Monetary values were each split into quartiles (1=worst, 4=best) using `pandas.qcut`; segments were then assigned using standard RFM segment logic (see `notebook/02_rfm_and_cohort.py`).
- **Cohort retention:** Customers are grouped into monthly cohorts by their first purchase date; retention at month N is the % of that cohort's customers who made at least one purchase in month N after joining.
- **"Churn" definition:** since this is a non-subscription retail business (no explicit cancellation event), churn is inferred from recency — customers in the "At Risk," "Cannot Lose Them," and "Hibernating/Churned" segments have not purchased recently relative to their own historical pattern. This is standard practice for RFM-based churn inference in non-contractual retail businesses.
