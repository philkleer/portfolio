# Case Study: From Data Pipelines to Production GIS Products

_Date: 2026-06-25_  
**Tags:** geospatial, GIS, Kubernetes, orchestration, H3, igraph, Polars, production

## 🚀 Context

This case study describes the final stage of the **Mapeamento Fibra** platform: transforming processed geospatial and connectivity data into production-ready GIS products.

It builds directly on two previous case studies:

- **Production Geospatial ML Pipeline** (`2026-05-14_production_system.md`)
- **Geospatial Terrain Classification System: From Model Development to Production-Ready Implementation** (`2026-06-20_production_implementation.md`)

Those projects generate processed road networks, access-point datasets, and ML predictions. This repository orchestrates the final step by producing reusable GIS artifacts.

---

# System Architecture

```text
Map Pipeline
      │
      ▼
Measurement Pipeline
      │
      ▼
ML Prediction API
      │
      ▼
Product Orchestrator (main.py)
      │
      ├── Product 1: Fiber Evidence
      ├── Product 2: Street Connectability
      └── Product 3: Public Institutions
      │
      ▼
GeoPackage (.gpkg)
      │
      ▼
S3 Object Storage
      │
      ▼
Slack Notifications
```

---

# Design Goals

- Modular product generation
- Reproducible GIS artifacts
- City-by-city execution
- Automatic publishing
- Operational monitoring

---

# Pipeline Orchestration

A single `main.py` orchestrates the workflow by loading the latest datasets, resolving dependencies between products, executing only the requested products, publishing outputs to S3, and notifying the team through Slack.

Example:

```bash
python main.py --city Recife --product1 --product2 --product3
```

---

# Product 1 — Fiber Evidence

Aggregates predicted fiber access points into H3 hexagons to create an interpretable evidence map instead of displaying all points.

Technologies:
- H3
- Polars
- GeoPandas

---

# Product 2 — Fiber Connectability

Creates a street-level connectability map by:

1. Building an igraph road network
2. Snapping fiber endpoints
3. Running multi-source Dijkstra
4. Scoring road segments
5. Normalizing scores
6. Classifying with Jenks–Caspall

---

# Product 3 — Public Institution Prioritization

Reuses Product 2 instead of recomputing routing.

Non-fiber public institutions are matched to the nearest scored road segment, producing an operational planning layer.

---

# Operational Engineering

The repository also automates:

- dependency management
- S3 publication
- Slack notifications
- Kubernetes execution
- reproducible folder structure

This keeps ingestion, inference, and product generation cleanly separated.

---

# Technology Stack

**Infrastructure**

- Kubernetes
- Docker
- GitLab CI/CD
- S3

**Python**

- uv
- Polars
- GeoPandas
- Shapely

**Geospatial**

- H3
- igraph
- GeoPackage

---

# Key Takeaways

1. Product generation deserves its own production pipeline.
2. Modular orchestration simplifies maintenance.
3. Reusing intermediate products avoids unnecessary computation.
4. Production GIS systems combine software engineering, data engineering, and geospatial analysis.

---

# Related Reading

- `case-studies/2026-05-14_production_system.md`
- `case-studies/2026-06-20_production_implementation.md`
- `til/2026/05/2026-05-05_overturemaps_pipeline.md`
- `til/2026/05/2026-05-12_geospatial_data_ingestion_pipeline.md`
