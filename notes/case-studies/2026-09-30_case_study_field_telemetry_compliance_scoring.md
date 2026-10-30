# Case Study: Building a Multi-Pillar Field Telemetry Compliance & Anomaly Scoring System with Snowpark

_Date: 2026-09-30_  
**Tags:** snowpark, snowflake, python, MLOps, analytics-engineering, anomaly-detection, telemetry

---

## 🚀 Overview

In large-scale field service operations (e.g., store audits, technical maintenance, delivery networks), organizations rely on mobile telemetry logs to monitor operational coverage and quality. However, evaluating field compliance manually across millions of events is unscalable, while rigid rule-based systems generate excessive false positives and fail to handle real-world edge cases like coordinate clusters or missing timestamps.

This case study documents the architectural design and implementation of an **end-to-end Field Telemetry Compliance & Anomaly Scoring System**. Built entirely using **Snowpark for Python**, the system processes millions of raw event records directly inside Snowflake to generate deterministic, multi-pillar compliance scores.

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│ Raw Event Logs (Snowflake Data Lakehouse)               │
│ • Telemetry / Check-in events                           │
│ • Task execution & survey responses                     │
│ • Location dimension metadata                           │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ In-Database Snowpark Pipeline Engine                    │
│                                                         │
│                5 pillars of evaluation                  │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Dynamic Weight Redistribution Layer                      │
│ • Validates pillar availability (min. 3 required)       │
│ • Normalizes weights for missing/null signals           │
│ • Computes composite COMPLIANCE_SCORE (0.0 - 1.0)       │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Analytical Outputs & Downstream Layer                    │
│ • Materialized Snowflake Tables (Gold Layer)            │
│ • Operational Dashboards & High-Risk Anomaly Alerts     │
│ • Polars/Parquet exports for secondary reporting        │
└─────────────────────────────────────────────────────────┘
```

---

## Key Engineering Decisions

### 1. 100% In-Database Processing (Zero Driver Transfer)
Instead of pulling raw telemetry data into local Pandas memory, all transformations, spatial calls, and aggregations are built as lazy-evaluated Snowpark DataFrames. Data remains within Snowflake's compute engine until final materialization.

### 2. Fault-Tolerant Weight Redistribution
When evaluating composite compliance, specific pillars may be non-applicable (e.g., the first visit of a day has no prior travel distance). The pipeline dynamically detects valid pillar flags and scales their relative weights proportionally:

```python
# Re-normalize valid weights dynamically
df_global_score = df_scores.with_column(
    "COMPOSITE_SCORE",
    spf.when(included_scores < 3, spf.lit(None).cast(FloatType()))
       .otherwise(spf.round(weighted_sum / valid_weight_sum, 4))
)
```

### 3. Decoupled & Testable Architecture
Each scoring pillar is encapsulated within a pure Python function accepting Snowpark DataFrames and returning enriched DataFrames. This design enables isolated unit testing, modular maintenance, and parameter tuning without side effects.

---

## Operational Results & Key Takeaways

1. **Reduced False Positive Rate:** Incorporating spatial clustering checks and dynamic workload denominators eliminated widespread false non-compliance flags caused by data logging edge cases.
2. **Scalability:** By avoiding driver memory transfers and custom Python UDF overhead, the pipeline processes millions of event logs efficiently using standard Snowflake Virtual Warehouses.
3. **Actionable Compliance Insights:** Rather than generating binary "pass/fail" decisions, the multi-pillar continuous score ($0.0 - 1.0$) allows operations teams to differentiate between systemic logging issues, training needs, and high-risk anomalies.

---

## Tech Stack

- **Data Processing:** Snowpark Python, Snowflake SQL
- **Analytics & Export:** Polars, PyArrow
- **Visualizations & Diagnostics:** Plotnine, Great Tables