# TIL: Building a Production Geospatial Pipeline with OvertureMaps, uv, and Kubernetes

_Date: 2026-05-05_  
_Tags: geospatial, overturemaps, python, kubernetes, mlops, data-engineering_

--- 

## Context

As part of a larger production ML system for detecting fiber connectivity patterns, I needed a scalable and reproducible way to generate geospatial road-network datasets for Brazilian municipalities.

Originally, I explored approaches based on raw OpenStreetMap extraction and custom segmentation workflows. While flexible, these approaches became increasingly difficult to maintain and scale across many municipalities.

The main problems were:

- inconsistent geometries across municipalities
- large preprocessing overhead
- slow segmentation workflows
- complicated graph creation
- brittle municipality-specific logic
- difficult reproducibility

To simplify the workflow, I started experimenting with **OvertureMaps** combined with `city2graph`.

That turned out to be a major improvement.

---

## Architecture Overview

The pipeline is fully containerized and runs inside a:

- `uv`-managed Python repository
- Kubernetes CronJob environment
- bronze / silver / gold data architecture
- S3-backed storage layer
- GitLab-integrated metadata workflow

The main orchestration entrypoint is a simple CLI:

```bash
python -m src.main --city "Recife"
```

The pipeline then:

1. downloads OvertureMaps layers
2. reprojects data into municipality-specific CRS
3. creates graph/network structures
4. computes road difficulty metrics
5. exports processed GeoPackages
6. creates visualization artifacts
7. uploads outputs to S3
8. commits lightweight GitLab references

---

## Why OvertureMaps Instead of Raw OSM?

The biggest advantage was operational simplicity. Instead of manually orchestrating:

- OSM extraction
- geometry cleanup
- topology correction
- segmentation
- graph consistency checks

I could directly consume structured geospatial layers from OvertureMaps.

The download step became surprisingly clean:

```python
data = c2g.load_overture_data(
    place_name=f"{city}, Brazil",
    types=[
        "segment",
        "connector",
        "building",
        "water",
        "land_use",
        "infrastructure",
    ],
    save_to_file=False,
    return_data=True,
)
```

### Advantages I observed

#### 1. Better structured geospatial primitives

OvertureMaps already exposes:

- segments
- connectors
- infrastructure
- buildings
- water bodies

This dramatically reduced preprocessing complexity.

---

#### 2. Easier graph construction

Using `city2graph`, I could directly create:

- road graphs
- edge structures
- segment relationships

without implementing custom topology logic.

---

#### 3. Faster scaling to multiple municipalities

The pipeline became municipality-agnostic.

The same orchestration now works for:

- Recife
- Manaus
- São Paulo
- Goiânia
- Porto Alegre

with almost no custom logic.

---

#### 4. Cleaner production architecture

The project naturally evolved into a layered architecture:

| Layer  | Purpose                               |
|--------|---------------------------------------|
| Bronze | raw downloaded layers                 |
| Silver | cleaned / reprojected geospatial data |
| Gold   | enriched network datasets + outputs   |

This made debugging and reproducibility significantly easier.

---

## CRS Handling Was Surprisingly Important

One operational issue I encountered was CRS management across Brazil. Different municipalities require different projected coordinate systems for accurate distance and topology calculations. I ended up implementing municipality-aware CRS selection:

```python
CITY_CRS_MAP = {
    "recife": "EPSG:31985", 
    "manaus": "EPSG:31975",
    "sao_paulo": "EPSG:31984",
    "porto_alegre": "EPSG:31988",
}
```

This ensured:

- proper spatial joins
- accurate length calculations
- stable graph generation
- correct routing distances

---

## Computing Road Difficulty Scores

One interesting part of the workflow was enriching road segments with a _difficulty_ metric. The score combines:

- road class
- segment length
- bridges
- tunnels
- construction zones
- water crossings
- accessibility constraints

Example:

```python
bridge_penalty = 10 if "is_bridge" in flags else 0
tunnel_penalty = 15 if "is_tunnel" in flags else 0
construction_penalty = 25 if "is_under_construction" in flags else 0
```

This generated a weighted representation of network complexity that is later consumed by downstream ML workflows.

---

## Bronze → Silver → Gold

One thing that worked extremely well was separating artifacts into stages.

### Bronze

Raw downloaded Overture layers:

- `map.gpkg`

### Silver

Cleaned intermediate outputs:

- `segments_clean.gpkg`
- `edges_clean.gpkg`

### Gold

Final enriched artifacts:

- `segments.gpkg`
- `edges.gpkg`
- `difficulty_map.png`

This made:

- debugging easier
- failures more localized
- artifact reuse possible
- downstream ML integration cleaner

---

## Kubernetes + S3 Workflow

The pipeline runs inside Kubernetes CronJobs, since there is no Airflow instance available in the cluster. Instead of storing large geospatial artifacts directly in Git repositories, I used:

- S3-compatible object storage
- lightweight GitLab reference files

The workflow:

1. upload artifacts to S3
2. generate metadata reference files
3. commit only references to GitLab

This avoided repository bloat while preserving traceability.

---

### Why This Matters for ML Systems

This pipeline is not _just_ geospatial ETL. It became the geospatial foundation for a larger ML system. The generated outputs are later used for:

- feature engineering
- network classification
- fiber connectivity prediction
- routing difficulty estimation
- model serving APIs
- production inference workflows

The important lesson for me was:

> production ML systems are often mostly data engineering systems.

Reliable geospatial ingestion and reproducible preprocessing became more important than the model itself.

---

## Key Technical Stack

### Infrastructure

- Kubernetes
- S3 object storage
- GitLab CI/CD

### Python ecosystem

- uv
- geopandas
- polars
- city2graph
- shapely
- matplotlib

### Geospatial data

- OvertureMaps
- GeoPackage
- graph/network structures

---

## Lessons Learned

### 1. OvertureMaps dramatically simplifies geospatial production workflows

Especially when compared to raw OSM extraction + manual segmentation.

---

### 2. Reproducibility matters more than clever scripts

The bronze/silver/gold layering improved debugging more than any micro-optimization.

---

### 3. CRS handling becomes critical at national scale

Spatial calculations silently fail when projections are wrong.

---

### 4. Production ML systems require robust data pipelines first

The model is only one layer of the system.

---

## Final Thoughts

This project changed how I think about geospatial ML systems. The real engineering challenge turned out to be:

- reproducible ingestion
- scalable orchestration
- geospatial consistency
- artifact management
- operational maintainability

OvertureMaps helped reduce a large amount of operational complexity and allowed me to focus more on the actual analytical and ML workflows.
