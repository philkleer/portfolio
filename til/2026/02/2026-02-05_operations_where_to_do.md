# TIL: Where to Run Data Operations (PostgreSQL vs R engines like DuckDB/Polars)

_Date: 2026-02-05_

In the last months, I worked with a data pipeline that involves:

- a **PostgreSQL** database (sometimes with **PostGIS**),
- R queries using **{DBI} + {dbplyr}**,
- local processing with **DuckDB/{duckplyr}** and **{polars}**,
- and API exports (JSON and Parquet).

A recurring question is:

> Should I do this operation in the database, or should I pull data into R and do it locally?

This note summarizes my current rules of thumb.

---

## 🧭 General Rule

**Do expensive reduction as early as possible.**

If data is still in PostgreSQL:

✅ Filter, aggregate, and join *in the DB*  
✅ Transfer only the smallest necessary result

If the data is already extracted (e.g., Parquet locally):

✅ Use **Polars/DuckDB** for fast iterative analysis  
✅ Avoid repeated round-trips to the DB

---

## 📌 Quick Comparison Table

| Operation / Task                           | Best place (default)               | Why                                               | When to do it elsewhere                                      |
|--------------------------------------------|------------------------------------|---------------------------------------------------|--------------------------------------------------------------|
| `WHERE` filtering on indexed columns       | **PostgreSQL**                     | avoids transferring rows; uses indexes            | if columns are not indexed and data is already local         |
| `WHERE` filtering on computed predicates   | **Polars / DuckDB** (if extracted) | vectorized local scan can be fast *after extract* | usually better to fix DB indexes or materialize features     |
| `SELECT` only needed columns               | **PostgreSQL**                     | reduces bytes transferred                         | local only if you already downloaded everything              |
| `GROUP BY` + aggregates                    | **PostgreSQL**                     | designed for reduction before transfer            | local if working on Parquet lake / offline analysis          |
| joins between DB tables                    | **PostgreSQL**                     | better join planning + indexes                    | local only if both datasets already extracted                |
| join DB ↔ small lookup table               | **PostgreSQL**                     | push small table into DB and join there           | local if DB access is constrained or offline                 |
| `ORDER BY` (full dataset)                  | **Avoid if possible**              | sorting is expensive everywhere                   | only do at the end for presentation                          |
| `ORDER BY ... LIMIT n`                     | **PostgreSQL**                     | DB can stop early if it can use an index          | local if results are already in memory/parquet               |
| window functions (`LAG`, `RANK`, etc.)     | **PostgreSQL**                     | optimized + avoids pulling raw history            | local for repeated experimentation on Parquet                |
| spatial filters (`ST_Intersects`, bbox)    | **PostGIS**                        | spatial indexes are the whole point               | local only if you already have geoparquet and need iteration |
| spatial aggregation (by polygons, buffers) | **PostGIS**                        | authoritative, efficient, indexed                 | export aggregated result for downstream analysis             |
| API / serving layer for bulk exports       | **Parquet + caching**              | avoids JSON parsing overhead                      | JSON only if clients truly need it                           |

---

## 🐢 Why `ORDER BY` Often Feels Slow

Sorting is naturally expensive because it needs:
- comparisons across many rows
- memory or disk spill
- no _early stop_ unless combined with `LIMIT`

Practical strategy:

- do **no order** for bulk exports
- use `ORDER BY + LIMIT` for Top-N reporting
- use **keyset pagination** for APIs instead of sorting entire datasets

---

## 🧠 Working Model I’m Using

### If I still have the data in PostgreSQL

**Push down**:
- filters (`WHERE`)
- joins
- aggregations
- spatial operations

Then export:

- only columns needed
- only the reduced result

### If I already extracted data to Parquet locally

**Do locally**:
- iteration-heavy transformations
- feature engineering with many steps
- multiple “what-if” variations

Tools I reach for:

- **Polars** for fast dataframe-style transformations
- **DuckDB** for SQL-style analytics across Parquet files

---

## ✅ Key Takeaways

- If reduction is possible: **do it in PostgreSQL first**
- Avoid exporting huge tables when you only need aggregates
- `ORDER BY` is expensive: prefer _sort at the end_ or _Top-N_
- PostGIS belongs in the database (use spatial indexes)
- `{polars}`/`{duckdb}` shine when the data is already local (Parquet)
