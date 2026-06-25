# TIL: Orchestrating Production Data Pipelines with Kubernetes CronJobs (Without Airflow)

_Date: 2026-06-25_

## What I learned

One of the biggest infrastructure constraints of this project was that **Apache Airflow was not available** in our Kubernetes cluster.

Instead of introducing another orchestration platform, I designed the pipeline around **Kubernetes CronJobs**, where each processing stage is packaged as an independent container that communicates through versioned artifacts stored in S3-compatible object storage.

The result is a lightweight orchestration architecture that is reproducible, easy to maintain, and naturally aligned with Kubernetes.

---

## Architecture

```
        Kubernetes CronJobs

                │
                ▼

      OvertureMaps Pipeline (bi-annual)
                │
                ▼
        Road Network Dataset
                │
                ▼
      Access Point Pipeline (monthly)
                │
                ▼
       Measurement Aggregation
                │
                ▼
        FastAPI Prediction Service
                │
                ▼
      GIS Product Generation (monthly)
                │
                ▼
        GeoPackages + S3 Storage
                │
                ▼
          Slack Notifications
```

Each stage is its own repository, Docker image, and CronJob.

Instead of sharing files between containers, every stage publishes artifacts that become the input for the next pipeline.

---

## Why this mattered

The overall workflow consists of multiple independent data engineering tasks:

- downloading OvertureMaps data
- generating the road network
- downloading measurement data
- generating access points
- running ML inference
- producing GIS-ready products

Although these tasks depend on one another, they execute at different frequencies and evolve independently.

Using Kubernetes CronJobs allowed me to orchestrate this workflow without introducing additional operational complexity.

---

## Key engineering decisions

### 1. One responsibility per pipeline

Instead of creating one large monolithic pipeline, I separated the project into independent repositories:

| Pipeline      | Responsibility                      |
|---------------|-------------------------------------|
| OvertureMaps  | Download and prepare road network   |
| Access Points | Download and aggregate measurements |
| FastAPI       | Model inference                     |
| Products      | Generate GIS products               |

Each repository owns exactly one responsibility.

This makes development, testing, and deployment considerably simpler.

---

### 2. Artifact-based communication

Instead of sharing volumes or databases between jobs, every pipeline publishes versioned artifacts.

```
Pipeline A
    │
    ▼
GeoPackage / Parquet
    │
    ▼
S3 Object Storage
    │
    ▼
Pipeline B
```

Advantages:

- loose coupling
- reproducible runs
- independent retries
- easier debugging
- historical artifacts remain available

---

### 3. Kubernetes as the scheduler

Every repository is deployed as a CronJob.

Kubernetes already provides:

- scheduling
- retries
- concurrency control
- resource limits
- logging
- monitoring

For this workload, introducing Airflow would have duplicated functionality already available in Kubernetes.

---

### 4. Explicit dependency chain

Rather than building one giant DAG, dependencies are expressed through generated artifacts.

```
Map data
    ↓

Access points
    ↓

Prediction API
    ↓

GIS Products
```

Each stage simply consumes the latest successful artifact from the previous stage.

This keeps the architecture modular and allows each component to evolve independently.

---

### 5. Operational monitoring

Every CronJob reports its execution status to Slack.

Instead of manually checking Kubernetes Jobs, the engineering team receives immediate feedback whenever:

- a pipeline finishes successfully
- a pipeline fails
- generated artifacts are uploaded

Using the team's existing communication platform makes operational monitoring much more practical than requiring another dashboard.

---

### 6. Reproducible execution

Every pipeline executes inside a versioned Docker image built through GitLab CI.

Combined with `uv` for dependency management, every scheduled execution runs inside exactly the same environment.

This greatly reduces "works on my machine" problems.

---

## What this taught me

Before this project I tended to associate workflow orchestration with tools such as Airflow.

This project changed that perspective.

For containerized data engineering workloads that already run on Kubernetes, CronJobs can provide a surprisingly capable orchestration layer when combined with:

- modular repositories
- immutable artifacts
- clear ownership between pipeline stages
- lightweight operational monitoring

Rather than adding infrastructure, I learned that choosing the **simplest architecture capable of solving the problem** often results in systems that are easier to understand, operate, and maintain.

---

## Technologies used

Python
uv
Docker
Kubernetes CronJobs
GitLab CI/CD
S3-compatible Object Storage
Slack
FastAPI
GeoPandas
Polars
PostgreSQL
OvertureMaps