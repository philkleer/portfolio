# TIL: Optimizing Large-Scale Behavioral Metric Pipeline Calculations in Snowflake using Snowpark

_Date: 2026-09-15_

## What I learned

When building large-scale data pipelines to evaluate sequence-based behavioral metrics, pulling raw logs into local Pandas DataFrames quickly causes severe memory bottlenecks and slow execution.

I learned how to write an end-to-end analytics engineering pipeline using **Snowpark for Python** that executes 100% in-database. By combining window functions, native SQL function pushdowns (`HAVERSINE`, `PERCENTILE_CONT`), and vectorized expressions, I eliminated data transfers and achieved scalable, deterministic compute directly inside Snowflake.

---

## Pipeline Flow

```
     Raw Event Logs (Snowflake Tables)
                    │
                    ▼
  Snowpark In-Database Processing Engine
                    │
                    ▼
    calculation of behavioral metrics        
                    │
                    ▼
   Dynamic Weight Redistribution Layer
                    │
                    ▼
   Gold Data Tables / Parquet Artifacts
```

---

## Key Engineering Decisions & Patterns

### 1. In-Database Sequence Modeling via Snowpark Windows

Instead of processing agent check-ins in Python loops, sequential metrics are computed using Snowpark Window specifications:

```python
from snowflake.snowpark import Window
import snowflake.snowpark.functions as spf

w_agent_date = Window.partition_by("ID", "EVENT_DATE").order_by("CHECK_IN_TIME")

prev_check_out = spf.lag(spf.col("CHECK_OUT_TIME")).over(w_agent_date)
prev_lat = spf.lag(spf.col("LATITUDE")).over(w_agent_date)
prev_long = spf.lag(spf.col("LONGITUDE")).over(w_agent_date)
```

This allows calculating time differences (`spf.datediff`) and travel sequences across millions of records without fetching data to the driver node.

---

### 2. Native Geodesic Distance Pushdown

Rather than using local spatial libraries (like GeoPandas or Shapely) which force driver collection, I pushed spatial distance math directly to Snowflake's native `HAVERSINE` function:

```python
haversine_dist = spf.call_function(
    "HAVERSINE",
    prev_lat,
    prev_long,
    spf.col("LATITUDE"),
    spf.col("LONGITUDE"),
)
```

---

### 3. Statistical Bound Calculation with Gaussian Decay Curves

To evaluate whether tasks were completed too quickly ("rushed") or too slowly ("delayed"), population percentiles ($P_{25}$ and $P_{75}$) were calculated in a single aggregate pass using `spf.percentile_cont()`. 

Symmetric Gaussian penalties were then applied to out-of-bound durations:

```python
# Population bounds derived in-database
t_floor = p25
t_upper = p75

rush_penalty = spf.exp(
    -spf.pow((spf.lit(t_floor) - time_spent_sec) / spf.lit(sigma_low), 2.0)
)
delay_penalty = spf.exp(
    -spf.pow((time_spent_sec - spf.lit(t_upper)) / spf.lit(sigma_high), 2.0)
)
```

---

### 4. Vectorized Text Quality Auditing

To audit missing-task justifications without invoking external LLMs or slow Python UDFs, regex patterns were executed directly in Snowflake:

```python
alpha_only = spf.regexp_replace(cleaned_text, spf.lit(r"[^a-zA-Z0-9]"), spf.lit(""))
alpha_len = spf.length(alpha_only)

# Flag empty strings, single characters, repeated characters ("aaaa"), or placeholder words
is_bad_justification = (
    (alpha_len <= 1)
    | (spf.length(spf.regexp_replace(alpha_only, spf.substr(alpha_only, 1, 1), spf.lit(""))) == 0)
    | spf.regexp_like(cleaned_text, spf.lit(r"^(ok|0k|tempo|outro|sim|nao)$"))
)
```

---

### 5. Dynamic Weight Re-normalization for Missing Metric Signals

In real-world telemetry, not every event has all metric pillars available (e.g., the first stop of a day has no prior travel segment). Instead of discarding incomplete records, the final score dynamically redistributes missing weights across valid pillars:

```python
# Redistribute weight dynamically across available pillars
df_final = df_scores.with_column(
    "COMPOSITE_SCORE",
    spf.when(included_scores < 3, spf.lit(None).cast(FloatType()))
       .otherwise(spf.round(weighted_sum / valid_weight_sum, 4))
)
```

---

## Key Takeaways

1. **Avoid Driver Bottlenecks:** Snowpark DataFrames are lazily evaluated representations of SQL query graphs. Keeping transformations within Snowpark functions keeps execution distributed across Snowflake warehouses.
2. **Prefer Built-in SQL Functions over Custom UDFs:** Calling SQL functions via `spf.call_function()` or `spf.call_builtin()` performs significantly better than custom Python UDFs.
3. **Statistical Scaling Reduces False Positives:** Bounding metrics using population percentiles ($P_{25}$–$P_{75}$) creates robust, adaptable operational scoring that auto-calibrates over time.

---

## Technologies used

- Python
- Snowpark for Python
- Snowflake Data Cloud
- Polars / PyArrow (for local export validation)
- Plotnine