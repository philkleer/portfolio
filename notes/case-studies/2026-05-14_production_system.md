# Case Study: Building a Production Geospatial ML Pipeline for Fiber Connectivity Classification

_Date: 2026-05-14_
Tags: mlops, geospatial, overturemaps, fastapi, kubernetes, polars, production-ml

## 🚀 Context

This project evolved around a standalone machine learning classifier that is used in this project to classify internet measurements into fiber/non-fiber. In the end, this is used in mapping internet connections in a city, but it needs to repeatedly be updated by new data input. The real engineering challenge quickly became operational:

- reproducible geospatial ingestion
- scalable data processing
- orchestration without Airflow
- model serving in constrained infrastructure
- artifact persistence
- geospatial interoperability
- automated inference workflows

The final system became a fully containerized and Kubernetes-native ML pipeline composed of:

- geospatial base-map ingestion with OvertureMaps
- measurement ingestion and feature engineering
- model inference through an internal FastAPI service
- geospatial export and persistence
- automated orchestration and reproducibility

---

## System Architecture

```
┌────────────────────────────────────┐
│ OvertureMaps Pipeline              │
│                                    │
│ • segments                         │
│ • connectors                       │
│ • infrastructure                   │
│ • graph generation                 │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│ Measurement Ingestion Pipeline     │
│                                    │
│ • PostgreSQL aggregation           │
│ • percentile metrics               │
│ • feature engineering              │
│ • parquet datasets                 │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│ Internal FastAPI ML Service        │
│                                    │
│ • champion model                   │
│ • parquet inference                │
│ • streaming predictions            │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│ Geospatial Outputs                 │
│                                    │
│ • GeoPackages                      │
│ • GIS-ready artifacts              │
│ • classified road segments         │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│ Persistence + Orchestration        │
│                                    │
│ • Kubernetes CronJobs              │
│ • S3 artifact storage              │
│ • Git reference tracking           │
└────────────────────────────────────┘
```

---

## Part 1 — Geospatial Foundation with OvertureMaps

The first stage focused on building reproducible geospatial base layers. Originally, I experimented with:

- raw OpenStreetMap extraction
- manual segmentation
- topology reconstruction

This became operationally expensive and difficult to scale. Switching to OvertureMaps dramatically simplified the workflow because transportation data already exposes:

- segments
- connectors
- infrastructure primitives

instead of requiring heavy topology reconstruction from raw OSM ways. The orchestration pipeline:

- downloads municipality data
- reprojects geometries
- generates graph structures
- computes road difficulty metrics
- exports GeoPackages
- uploads artifacts to S3

The workflow runs entirely inside:

- Kubernetes CronJobs (since no other orchestration was available)
- a uv-managed Python repository
- bronze/silver/gold architecture

### Key lesson

> production geospatial systems benefit more from reproducibility and operational simplicity than from overly flexible raw extraction workflows.

[Related TIL](../../til/2026/05/2026-05-05_overturemaps_pipeline.md)

---

## Part 2 — Measurement Ingestion and Feature Engineering

The second stage focused on downloading and standardizing connectivity measurements from heterogeneous PostgreSQL systems. The engineering challenge was not the classifier itself, it was continuously generating reproducible and scalable feature datasets.

The ingestion pipeline:

- aggregates measurements directly in PostgreSQL
- computes percentiles and medians in SQL
- filters invalid agents
- standardizes features with Polars
- exports parquet datasets
- requests predictions from the internal ML service

This architecture drastically reduced:
- transferred data volume
- Python-side computation
- memory usage

while improving:
- scalability
- reproducibility
- operational maintainability


Instead of downloading raw measurements into Python, the system computes percentiles, medians, thresholds and does filtering directly in SQL using `PERCENTILE_CONT`,  aggregation pipelines, and grouped agent qualification. This significantly reduced processing overhead.

Polars replaced Pandas for feature engineering, transformations, parquet generation, and high-volume processing. The benefits were especially visible for memory efficiency, execution speed, and large-scale geospatial datasets. 

[Related TIL](../../til/2026/05/2026-05-12_geospatial_data_ingestion_pipeline.md)

--- 

## Part 3 — Internal ML Serving Architecture

To avoid tightly coupling inference logic to the ingestion pipeline, I created an internal FastAPI service.

The API:

- preloads the champion model at startup
- supports parquet and CSV interchange
- streams prediction results
- supports model versioning
- allows reusable inference endpoints

The ingestion pipeline uploads parquet datasets, requests predictions, and receives parquet prediction outputs. This separation created reusable inference, centralized serving, easier scaling, and controlled model promotion.

---

## Why Kubernetes CronJobs?

The infrastructure environment did not provide Airflow or centralized MLflow services. Therefore, I designed the entire orchestration around Kubernetes CronJobs and a project-specific MLflow instance. The project relies on container-native execution and S3 object storage. This became a lightweight but production-grade orchestration solution.

## Technical Stack

### Infrastructure
Kubernetes
Docker
S3-compatible object storage
GitLab CI/CD

### Python ecosystem
uv
FastAPI
Polars
GeoPandas
Shapely
city2graph

### Geospatial
OvertureMaps
GeoPackage

### ML / Serving
MLflow
parquet-based inference
Champion/Challenger workflows

--- 

## Key Takeaways

1. Production ML systems are mostly data engineering systems

1. Loose coupling simplifies evolution

Separating ingestion, inference, storage, and orchestration made the system easier to maintain and extend. 

1. Infrastructure constraints can still produce robust systems

Even without Airflow, managed MLflow or a dedicated orchestration service, it was possible to build reproducible, scalable, and production-grade ML pipelines. 

---

## Final Thoughts

This project fundamentally changed how I think about ML systems. The real engineering challenge turned out to be:

- operational reproducibility
- scalable ingestion
- geospatial consistency
- orchestration
- artifact lifecycle management

The final system became a complete geospatial ML platform capable of continuously generating production-ready spatial inference outputs.