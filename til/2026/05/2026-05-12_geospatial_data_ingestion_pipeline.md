# TIL: Building a reproducible geospatial measurement ingestion pipeline for ML inference

_Date: 2026-05-12_

## What I learned

In my project, I need to conduct repeatedly classifications on updated data. The engineering problem was actually:

> building a reproducible geospatial ingestion pipeline that continuously downloads, aggregates, standardizes, predicts, and publishes connectivity measurements from heterogeneous sources.

To solve this, I built a complete Python-based data pipeline orchestrated in Kubernetes that:

- downloads measurement data from multiple PostgreSQL systems
- aggregates and filters connectivity statistics directly in SQL
- standardizes features with Polars
- runs ML inference through an internal FastAPI classifier service
- exports spatial outputs as GeoPackages
- persists pipeline artifacts to S3
- creates Git-tracked references for reproducibility

This became the operational layer around the classifier system.

---

## Architecture

```
┌──────────────────────┐
│ PostgreSQL Sources   │
│                      │
│ • Schools            │
│ • Health             │
│ • Households         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Download + Aggregate │
│                      │
│ • SQL percentiles    │
│ • Filtering          │
│ • Agent qualification│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Polars Processing    │
│                      │
│ • Feature engineering│
│ • Standardization    │
│ • Parquet storage    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ FastAPI ML Service   │
│                      │
│ • Champion model     │
│ • Streaming parquet  │
│ • Batch inference    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Geospatial Outputs   │
│                      │
│ • GeoPackage export  │
│ • CRS reprojection   │
│ • GIS-ready outputs  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Persistence Layer    │
│                      │
│ • S3 object storage  │
│ • Git reference files│
│ • Reproducibility    │
└──────────────────────┘
```

---

## Why this pipeline mattered

For the end product, updated data is needed repeatedly to consistently map fiber connections in a city. Hence, this product depends on:

- continuously updated measurement data
- multiple infrastructure systems
- spatial consistency
- reproducible outputs
- operational scalability

Instead of manually exporting datasets, I designed the system as a layered data pipeline:

| Layer  | Purpose                             |
|--------|-------------------------------------|
| Bronze | Raw downloaded measurements         |
| Silver | Standardized ML-ready features      |
| Gold   | Final geospatial prediction outputs |

This allowed:

- reproducibility
- debugging
- incremental processing
- versioned artifacts
- easier operationalization

---

## Key engineering decisions

1. Heavy aggregation directly in PostgreSQL

Instead of pulling raw measurements into Python, I computed:

- percentiles
- medians
- filtering
- qualification thresholds

directly in SQL.

**Example:**

- PERCENTILE_CONT
- agent qualification (HAVING COUNT(*) >= 20)
- measurement filtering
- union across multiple measurement systems

This drastically reduced:

- transferred data volume
- memory usage
- Python-side computation

2. Using Polars instead of Pandas

After downloading aggregated measurements, I used Polars for:

- feature engineering
- transformations
- parquet writing
- column selection

**Example features:**

- ratio_dl_ul
- latency metrics
- jitter metrics
- percentile-based throughput measures

Polars significantly improved:

- memory efficiency
- execution speed
- pipeline scalability

especially when processing large geospatial datasets.

3. Serving inference through an internal FastAPI service

Instead of embedding the model directly into the ingestion pipeline, I separated inference into an internal API.

The pipeline:

- uploads parquet data
- requests predictions
- receives parquet prediction outputs

This created:

- loose coupling
- reusable inference
- centralized champion model serving
- easier future scaling

The FastAPI service:

- preloads the champion model at startup
- streams parquet responses
- supports versioned models
- supports CSV and parquet interchange

4. Geospatial export as GeoPackage

After prediction:

- Polars dataframes are converted into GeoDataFrames
- city-specific CRS systems are applied
- outputs are exported as .gpkg

This allowed direct usage in:

- GIS workflows
- spatial analysis pipelines
- QGIS

without additional postprocessing.

5. S3 persistence + Git references

One challenge was:

- how to persist large geospatial artifacts without bloating Git repositories.

The solution:

- store artifacts in S3
- generate lightweight Git reference files pointing to S3 objects

This created:

- reproducibility
- traceability
- lightweight repositories
- immutable historical references

---

## Kubernetes orchestration

The whole workflow runs inside Kubernetes CronJobs, since there isn't an Airflow instance available.

This enabled:

- scheduled updates
- isolated execution
- reproducible environments
- operational automation

The repository itself is managed with:

- uv
- containerized execution
- environment-driven configuration

---

## What this taught me

The biggest realization was: Production ML systems are mostly data engineering and operational engineering problems.

The classifier was important, but the real complexity was:

- orchestration
- reproducibility
- storage
- geospatial interoperability
- scalable ingestion
- operational maintainability

---

## Technologies used

Python
Polars
FastAPI
PostgreSQL
GeoPandas
Shapely
MLflow
Kubernetes CronJobs
S3-compatible object storage
uv
Parquet
GeoPackage