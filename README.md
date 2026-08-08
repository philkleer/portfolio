# Data Science Notes & Project Portfolio

This repository contains curated **Today I Learned (TIL) insights**, **case studies**, and detailed project overviews from my work as a **Data Scientist**, focusing on reproducible workflows, applied analytics, data engineering, and production-grade systems.

Visit the individual case studies below to explore:
- how I refactor and optimize data applications (e.g., Shiny),
- how I build full ML pipelines,
- and how I benchmark performance across tools and environments.

Each entry includes technical explanations, code snippets, results, and lessons learned.

👤 **Profile:** https://github.com/philkleer  
📄 **LinkedIn:** https://linkedin.com/in/philkleer  

## Table of Contents
1. [⭐ Featured Projects](#featured-projects)
2. [📂 Detailed Projects](#detailed-projects)
3. [📚 Case Studies](#case-studies)
4. [🧠 Learning Notes (TIL)](#til-latest-lessons)
5. [🙋🏻‍♂️ About Me](#about-me)


## Featured Projects

These projects represent my most relevant work as an applied Data Scientist, with a focus on **production systems**, **reproducible analytics**, and **decision support**.

1. **Production Geospatial ML Pipeline for Fiber Connectivity Classification**
Designing and operationalizing an end-to-end geospatial ML system with OvertureMaps, PostgreSQL, FastAPI, Kubernetes, and scalable inference workflows.

1. **MLOps Pipeline: Fiber Detection Model — From Training to Production**
Designing end-to-end ML classifier in production environment (Kubernetes, MLflow, CI/CD).

1. **Redesigning an Application in Production: Instalometro na Conectividade na Saúde**
Designing, hardening, and shipping a production-ready data application with a focus on performance, reproducibility, and maintainability.

1. **Modularizing a Large Shiny Application (OBIA)**  
Refactoring and hardening a national-scale analytics application, reducing code size by ~41% and introducing CI/CD, testing, and reproducibility.

1. **Leveling Up an Internal R Package for Team-Scale Use**  
Productionizing an internal analytics package with versioned releases, CI/CD pipelines, and reproducible environments.

1. **Shiny Application – IT Governance (MGI)**  
End-to-end development and deployment of a public-facing Shiny application to assess IT governance across national entities.

1. **Network Technology Analysis & Visualization**  
Statistical analysis and visual storytelling to support technical and policy-oriented decision-making.

1. **End-to-End MLOps Pipeline**  
Implementation of a production-like ML lifecycle with experiment tracking and data/model versioning.

## Detailed Projects

<details>

<summary><h3>🗺️ Production Geospatial Data & ML Platform for Fiber Connectivity Analysis</h3></summary>

*Designing and operationalizing a Kubernetes-native geospatial data and ML platform that continuously generates production-ready GIS products from large-scale map, connectivity, and machine learning data.*

### Overview

This project evolved from a standalone machine learning classifier into a complete **production-grade geospatial data platform** capable of continuously generating GIS products for fiber connectivity analysis across Brazilian municipalities.

The platform integrates every stage of the data lifecycle:

- large-scale geospatial ingestion with **OvertureMaps**
- connectivity measurement aggregation from **PostgreSQL**
- scalable feature engineering with **Polars**
- machine learning inference through an internal **FastAPI** service
- automated product generation for GIS analysis
- reproducible orchestration with **Kubernetes CronJobs**
- artifact persistence using **S3-compatible object storage**
- operational monitoring through **Slack**

Rather than focusing solely on model development, the project emphasizes **reproducibility, scalability, modular architecture, and operational automation**, enabling continuous production of GIS-ready datasets under constrained infrastructure (without Airflow or centrally managed MLflow).

### Key Contributions

- Designed and implemented an end-to-end **production geospatial data and ML architecture**
- Built scalable geospatial ingestion workflows using **OvertureMaps** and `city2graph`
- Developed a layered **bronze/silver/gold** data architecture
- Aggregated high-volume connectivity measurements directly in **PostgreSQL**
- Implemented memory-efficient feature engineering pipelines using **Polars**
- Built an internal **FastAPI** inference service supporting batch predictions with Parquet
- Operationalized model serving using **Champion/Challenger** workflows with MLflow
- Designed modular product pipelines that generate reusable GIS artifacts
- Built Kubernetes-native orchestration using **CronJobs**
- Implemented automated publishing to **S3-compatible object storage**
- Integrated operational monitoring and failure notifications through **Slack**
- Generated GIS-ready **GeoPackages** for downstream spatial analysis and planning

### Architecture Highlights

```
OvertureMaps
        │
        ▼
Geospatial Data Pipeline
        │
        ▼
Connectivity Measurements
        │
        ▼
Feature Engineering (Polars)
        │
        ▼
FastAPI ML Inference
        │
        ▼
GIS Product Generation
        │
        ▼
GeoPackages
        │
        ▼
S3 + Slack + Kubernetes
```

### Tech Stack

- **Languages:** Python, SQL
- **Data Processing:** Polars, PostgreSQL
- **Geospatial:** OvertureMaps, GeoPandas, Shapely, H3, igraph, GeoPackage
- **ML / Serving:** MLflow, FastAPI
- **Infrastructure:** Docker, Kubernetes, GitLab CI/CD, S3-compatible object storage
- **Environment Management:** `uv`

### Results & Impact

- Built a fully automated geospatial data platform for continuous GIS product generation
- Reduced operational complexity compared to OpenStreetMap-based segmentation workflows
- Established reproducible city-by-city geospatial processing pipelines
- Enabled scalable production of machine learning inference datasets and planning products
- Demonstrated production-grade orchestration without Airflow using lightweight Kubernetes-native components
- Created reusable infrastructure that can easily be extended with additional GIS products

### Related Notes & Case Studies

#### Case Studies

- [Production Geospatial ML Pipeline](notes/case-studies/2026-05-14_production_system.md)
- [Geospatial Terrain Classification System](notes/case-studies/2026-06-20_production_implementation.md)
- [From Data Pipelines to Production GIS Products](notes/case-studies/2026-06-25_from_data_pipelines_to_production_gis_products.md)

#### Today I Learned

- [OvertureMaps Pipeline](til/2026/05/2026-05-05_overturemaps_pipeline.md)
- [Geospatial Data Ingestion Pipeline](til/2026/05/2026-05-12_geospatial_data_ingestion_pipeline.md)

</details>

<details>

<summary><h3>⬇️ MLOps Pipeline <i>Fiber Detection Model — From Training to Production</i></h3></summary>

*Designing and deploying a production-ready machine learning pipeline under real-world infrastructure constraints.*

### Overview
This project focused on developing and operationalizing a **binary classification model to detect fiber connections**, along with a **fully automated MLOps pipeline** for continuous retraining and deployment.

Due to platform constraints (no Airflow support and no shared MLflow instance), I designed a **Kubernetes-native MLOps architecture** that ensures reproducibility, automation, and robustness without relying on a standard stack.

The result is a **self-contained production system** that aligns model development with real-world decision-making requirements.

---

### Key Contributions
- Developed a **production-ready binary classifier** with a focus on high precision
- Designed a **complete model selection workflow**, including:
  - custom evaluation metrics (precision-first)
  - threshold optimization based on business requirements
  - probability calibration (Isotonic Regression)
- Built an **automated retraining pipeline** using Kubernetes CronJobs
- Implemented a **Champion/Challenger framework** for controlled model promotion
- Established **MLflow as a single source of truth** for model versioning and deployment
- Created a **lightweight, self-hosted MLflow infrastructure** (SQLite + S3)
- Integrated **CI/CD deployment triggers** via GitLab pipelines
- Designed **data versioning strategy** without a dedicated data platform

---

### Tech Stack
- **Language:** Python  
- **Modeling:** XGBoost, scikit-learn, Optuna  
- **MLOps:** MLflow (self-hosted), Kubernetes CronJobs  
- **Infrastructure:** Docker, Kubernetes, S3-compatible storage  
- **CI/CD:** GitLab CI  

---

### Results & Impact
- Delivered a **fully automated ML pipeline** from data ingestion to deployment  
- Enabled **robust and reproducible model retraining** under constrained infrastructure  
- Ensured **high-confidence predictions** through precision-focused modeling and calibration  
- Reduced dependency on heavy tooling by leveraging **lightweight, scalable architecture**  
- Established a **reusable MLOps blueprint** adaptable to similar environments  

---

### Notes
📄 **Case study:**  
See detailed write-up [here](notes/case-studies/2026-03-18_from_model_selection_to_production.md)

See TIL note about model selection [here](til/2026/03/2026-03-11-workflow_choosing_model.md)

See TIL note about production [here](til/2026/03/2026-03-18-putting_model_to_production.md)

</details>


<details>

<summary><h3>⬇️ Redesigning an Application in Production: Instalometro na Conectividade na Saúde</h3></summary>
Designing, hardening, and shipping a production-ready data application with a focus on performance, reproducibility, and maintainability.

---

### Overview

**Instalometro** (inside the project _Conectividade na Saúde_) was an established application monitoring connection data of health institutions. However, over time, functionality slowed down as data volume, usage expectations, and operational requirements increased, the original setup revealed clear limitations in performance, scalability, and reproducibility.

This project documents the transition from a working prototype to a **production-grade data application**, emphasizing architectural decisions, data engineering practices, and infrastructure reliability rather than feature growth.

The goal was to deliver a **maintainable, performant, and deployable system** that could be confidently operated and handed over to a broader team.

---

### Key Challenges

* Large datasets causing slow startup times and high memory usage
* JSON-based APIs creating heavy payloads and long response times
* Unclear separation between data access and reactive application logic
* Fragile dependency restoration at runtime
* Slow and unreliable CI builds with compiled dependencies
* Need for measurable performance guarantees before production release

---

### Key Contributions

* Re-architected data access using **Parquet-based pipelines** instead of large JSON payloads
* Introduced **Polars with lazy evaluation** for scalable, on-demand data loading
* Clearly separated data engineering concerns from Shiny reactive logic
* Implemented **load testing with `shinyloadtest`** to validate performance under concurrent usage
* Designed deterministic, multi-stage Docker builds using `{renv}` for reproducible environments
* Migrated CI pipelines to **Docker Buildx with registry-backed cache** for faster, more reliable builds
* Verified CI/CD workflows and documented clean handover instructions for the team

---

### Tech Stack

**Languages**

* R

**Frameworks & Libraries**

* Shiny
* Polars
* Arrow
* DBI / dbplyr

**Data & Storage**

* PostgreSQL / PostGIS
* Parquet

**Testing & Validation**

* shinyloadtest

**Reproducibility**

* renv

**CI/CD & Infrastructure**

* GitLab CI
* Docker (multi-stage builds)
* Docker Buildx (registry-backed cache)
* Kubernetes

---

### Results & Impact

* Significantly reduced application startup time and memory footprint
* Improved scalability and predictability under multi-user load
* Reduced API payload sizes by an order of magnitude through Parquet exports
* Deterministic, reproducible builds independent of runtime package restoration
* Faster and more reliable CI pipelines
* Clear documentation enabling smooth handover and future maintenance

Most importantly, **Instalometro na Conectividade na Saúde developed into an optimized data product** ready for long-term operation.

---

### Notes

This project prioritized **architectural correctness and operational stability** over rapid feature expansion.

Many performance issues were solved not through micro-optimizations, but through better placement of responsibilities between databases, data pipelines, and the Shiny application layer.

Several of the patterns developed here have since informed reusable tooling and shared infrastructure.

---

🔎 Detailed walkthrough:
[Case study — Redesignin an Application in Production](notes/case-studies/2026-02-10_redesign_application_in_production.md)


🔗 **Live application:** [https://conectividadenasaude.nic.br](https://conectividadenasaude.nic.br/saudeinstalada/)

</details>

<details>

<summary><h3>⬇️ Modularizing a Large Shiny Application <i>Observatório de Inteligência Artificial (OBIA)</i></h3></summary>

*Refactoring and hardening a production-grade Shiny application for long-term maintainability, collaboration, and reliability.*

### Overview
This project documents the refactoring of a large, production Shiny application used in a national analytics context. 

The original codebase had grown organically into a monolithic structure that was difficult to maintain, test, and extend.

The goal was to transform the application into a **modular, testable, and reproducible system**, suitable for multi-developer collaboration and continuous deployment.

### Key Contributions
- Refactored a monolithic Shiny application into a **fully modular architecture**
- Reduced total lines of code by **~41%** while improving readability and extensibility
- Introduced **automated testing**, linting, and formatting standards
- Implemented **reproducible dependency management** using `renv`
- Set up **CI/CD pipelines** to ensure code quality and deployment safety
- Improved application performance and load behavior

### Tech Stack
- **Languages:** R  
- **Frameworks:** Shiny, plotly
- **Testing:** testthat  
- **Reproducibility:** renv  
- **CI/CD:** GitLab CI  
- **Deployment:** Docker, Kubernetes  

### Results & Impact
- Significantly improved maintainability and onboarding for new contributors
- Enabled reliable multi-developer workflows
- Increased confidence in production releases through automated checks
- Established a reusable architectural pattern for future Shiny applications

### Notes
This refactor prioritizes **long-term sustainability over short-term feature additions** and serves as a reference architecture for future analytical applications. 

🔎 **Detailed walkthrough:** 
- [Case study](notes/case-studies/2025-08-14-modularizing-large-shiny-app.md)

🔗 **Live application:**  
https://obia.nic.br/s/indicadores
</details>

<details>
<summary><h3>⬇️ Levelling up the team's own R package</h3></summary>

*Standardizing, hardening, and productionizing an internal R package to support reproducible analytics, CI/CD, and multi-developer collaboration.*

### Overview
When joining a new team, I inherited an internal R package used to centralize shared analytical functionality across multiple products. While the package was already in use, it lacked **standardization**, **clear role separation between users and contributors**, and a **reliable CI/CD and release process**.

The goal of this project was to transform the package into a **stable, versioned, and reproducible internal dependency**, suitable for long-term maintenance and safe use across production systems.

### Key Contributions
- Standardized package structure, formatting, and development conventions across the entire codebase  
- Introduced **CI/CD pipelines** to automate checks, builds, and versioned internal releases  
- Established a **clear separation between user-facing and contributor-facing logic and documentation**  
- Implemented **reproducible dependency management** using `renv`, compatible with multiple R versions  
- Added **unit testing** with `testthat` and enforced code quality via formatting, linting, and pre-commit hooks  
- Designed and implemented a **safe versioning strategy** to prevent breaking changes in dependent products  

### Tech Stack
- **Language:** R  
- **Package tooling:** testthat, roxygen2  
- **Reproducibility:** renv, rig  
- **Code quality:** Air (formatting), lintr (linting), pre-commit  
- **CI/CD:** GitLab CI  
- **Distribution:** pak, internal release artifacts  

### Results & Impact
- Enabled **versioned installation** of the package, allowing teams to pin stable releases and avoid regressions  
- Reduced onboarding time through clear **README** and **CONTRIBUTING** documentation  
- Established **reproducible builds** with downloadable artifacts produced by the CI pipeline  
- Improved development consistency across contributors and environments  
- Made internal analytics workflows **more reliable, scalable, and maintainable**

This work turned the package from a loosely maintained codebase into a **production-ready internal dependency**, supporting both rapid development and long-term stability.

### Notes
- Older products could safely continue using pinned package versions while new releases evolved independently  
- The separation of *users vs. contributors* clarified responsibilities and reduced friction in collaboration  
- The CI/CD setup now serves as a **reference template** for other internal R packages  

🔎 **Detailed walkthrough:**  
[CI/CD overhaul case study](notes/case-studies/2025-09-14-nicverso-ci-overhaul.md)

</details>

<details>

<summary><h3>⬇️ Shiny application <i>Autodiagnóstico do Sistema de Administração dos Recursos de Tecnologia da Informação</i></h3></summary>

*Designing and deploying a production-grade analytical application to evaluate IT governance across national entities.*

### Overview
This project involved the development and deployment of a **public-facing, production-grade R Shiny application** designed to assess and analyze IT governance practices among national public-sector entities.

I was responsible for the **entire application lifecycle**, from data integration and analytical logic to visual design, automation, and deployment. The goal was to deliver a **stable, maintainable, and transparent analytics platform** that supports evidence-based evaluation and comparison.

### Key Contributions
- Developed a **production-grade Shiny application** covering the full analytical workflow
- Integrated and processed data from **multiple heterogeneous sources**
- Designed a **consistent visual design system** to ensure clarity, comparability, and usability
- Implemented **CI/CD pipelines** to automate testing, builds, and deployments
- Ensured application **stability, maintainability, and reproducibility** across environments
- Delivered a **publicly accessible analytics portal** for ongoing use and updates

### Tech Stack
- **Language:** R  
- **Frameworks:** Shiny, ggplot2, ggiraph
- **Data:** Relational databases, structured datasets  
- **CI/CD:** GitLab CI  
- **Deployment:** Docker, Kubernetes  

### Results & Impact
- Delivered a **robust and maintainable analytics platform** for assessing IT governance at national scale  
- Enabled consistent and transparent comparison across entities  
- Reduced operational overhead through automated deployment and quality checks  
- Established a reusable blueprint for future public-sector analytical applications  

### Notes
🔗 **Live application:**  
https://obia.nic.br/s/indicadores-mgi

</details>

<details>
<summary><h3>⬇️ Network Technology Analysis & Visualization</i></h3></summary>

*Statistical and exploratory analysis of network technologies with a focus on communication and decision support.*

### Overview
This project analyzes network technology data to identify patterns, quality indicators, and trends relevant for technical and policy-oriented audiences.

### Key Contributions
- Conducted exploratory and statistical analyses
- Applied regression-based methods where appropriate
- Translated analytical results into clear visual narratives
- Prepared presentation-ready outputs for non-technical stakeholders

### Tech Stack
- R
- tidyverse, ggplot2, brms
- revealJS 
- Quarto

### Results & Impact
- Supported evidence-based discussions on network technologies
- Improved accessibility of complex analytical results through visualization

### Notes
🔎 **Presentation at IX Forum 2025 (10min):**  
[Link to presentation](http://philkleer.quarto.pub/ix_forum_25/)
</details>

<details>
<summary><h3>⬇️ End-to-End MLOps Pipeline</h3></summary>

*Implementing a production-like machine learning lifecycle with model tracking and versioning.*

### Overview
This project explores the design of an end-to-end MLOps workflow, covering model training, experiment tracking, data and model versioning, and reproducibility.

### Key Contributions
- Implemented experiment tracking with MLflow
- Versioned data and models using DVC
- Simulated a production-style model lifecycle
- Documented pipeline structure and design choices

### Tech Stack
- Python
- MLflow
- DVC
- Git

### Results & Impact
- Demonstrates practical understanding of MLOps concepts
- Provides a reference implementation for small-to-medium ML projects

### Notes
- [Link to project](https://dagshub.com/philkleer/deepleaf_mlops/src/main)

</details>

---

<!-- START:INDEX -->
## Case studies
- 2026-06-25 — [Case Study: From Data Pipelines to Production GIS Products](notes/case-studies/2026-06-25_from_data_pipelines_to_production_gis_products.md)
- 2026-05-14 — [Case Study: Building a Production Geospatial ML Pipeline for Fiber Connectivity Classification](notes/case-studies/2026-05-14_production_system.md)
- 2026-03-18 — [📊 Case Study: Serving ML in Production — From Model Selection to Reliable Inference](notes/case-studies/2026-03-18_from_model_selection_to_production.md)
- 2026-02-10 — [Redesigning an Application in Production: _Instalometro na Conectividade na Saúde_](notes/case-studies/2026-02-10_redesign_application_in_production.md)
- 2026-01-05 — [Case Study: School Detection from Satellite Imagery](notes/case-studies/2026-01-05-school_detection_from_satellite_imagery.md)
- 2025-12-17 — [How I build data-driven presentations with Quarto + revealjs (a real-world example)](notes/case-studies/2025-12-17-nota_estilo_apresentacoes_quarto_revealjs.md)
- 2025-11-20 — [Case Study: Benchmarking Shiny app performance across environments with `shinyloadtest`](notes/case-studies/2025-11-20-shinyloadtest-performance-comparison.md)
- 2025-09-19 — [Case Study: Debugging across multiple R versions with `rig` + `renv`](notes/case-studies/2025-09-19-debugging-multiple-R-versions-with-rig-and-renv.md)
- 2025-09-14 — [From ad‑hoc repo to versioned, CI‑driven R package: nicverso](notes/case-studies/2025-09-14-nicverso-ci-overhaul.md)
- 2025-08-30 — [R big data benchmarks: dplyr/duckplyr/polars & Postgres/DuckDB](notes/case-studies/2025-08-30-r-bigdata-benchmarks-updated.md)
- 2025-08-14 — [Modularizing a Large Shiny App (R)](notes/case-studies/2025-08-14-modularizing-large-shiny-app.md)

## TIL: Latest Lessons
- 2026-07-22 — [TIL: Posterior Predictive Checks and Diagnostics with `arviz`](til/2026/07/2026-07-22_posterior_predictive_checks_with_arviz.md)
- 2026-07-20 — [TIL: Bayesian Mixed-Effects Regression with `bambi`](til/2026/07/2026-07-20_bayesian_regression_with_bambi.md)
- 2026-06-15 — [TIL: Orchestrating Production Data Pipelines with Kubernetes CronJobs (Without Airflow)](til/2026/06/2026-06-15_cronjob_orchestration_k8s.md)
- 2026-05-24 — [TIL: Adding data validation and drift detection to an ML retraining pipeline](til/2026/05/2026-05-24_data_validation_and_drift_detection.md)
- 2026-05-12 — [TIL: Building a reproducible geospatial measurement ingestion pipeline for ML inference](til/2026/05/2026-05-12_geospatial_data_ingestion_pipeline.md)
- 2026-05-05 — [TIL: Building a Production Geospatial Pipeline with OvertureMaps, uv, and Kubernetes](til/2026/05/2026-05-05_overturemaps_pipeline.md)
- 2026-04-14 — [TIL: Debugging a 9s Shiny Startup — When the Problem Was Kubernetes, Not R](til/2026/04/2026-04-14_shiny_cold_start_kubernetes.md)
- 2026-03-20 — [TIL: Integrating Slack Alerts into an MLOps Pipeline for Real-Time Monitoring](til/2026/03/2026-03-20_monitoring_and_alerts.md)
- 2026-03-19 — [TIL: Building a Lightweight Internal ML API with FastAPI + MLflow](til/2026/03/2026-03-19_model_access_via_api.md)
- 2026-03-18 — [TIL: Building an MLOps Pipeline Without Airflow or Managed MLflow](til/2026/03/2026-03-18-putting_model_to_production.md)
- 2026-03-11 — [TIL: A Practical Workflow for Finding a Production-Ready Binary Classifier](til/2026/03/2026-03-11-workflow_choosing_model.md)
- 2026-03-04 — [TIL: Using Overture Maps instead of raw OSM for scalable network analysis](til/2026/03/2026-03-04-using-overturemaps.md)
- 2026-03-01 — [TIL: Translating UI Paradigms (iOS → React)](til/2026/03/2026-03-01-translating-ui-paradigms.md)
- 2026-02-28 — [TIL Refactoring a 200-Line SQL Query: Less CTEs, Fewer Scans](til/2026/02/2026-02-28-sql-optimization.md)
- 2026-02-24 — [TIL: Scaling OSM-Based Weak Label Generation for Semantic Segmentation](til/2026/02/2026-02-24_scaling_osm_based_weak_label.md)
- 2026-02-20 — [TIL: Speeding Up a Plumber API by Switching from JSON to Parquet](til/2026/02/2026-02-20_speeding_up_api.md)
- 2026-02-05 — [TIL: Where to Run Data Operations (PostgreSQL vs R engines like DuckDB/Polars)](til/2026/02/2026-02-05_operations_where_to_do.md)
- 2026-01-25 — [TIL: Migrating to Docker Buildx with Registry Cache (and Why It’s Worth Showing)](til/2026/01/2026-01-25_using_buildx_docker.md)
- 2026-01-23 — [TIL: Making {renv} Work in a Multi-Stage Docker Build (Builder → Runtime)](til/2026/01/2026-01-23_using_renv_in_multi-stage_docker.md)
- 2026-01-19 — [TIL: Shrinking Docker Images with Multi-Stage Builds (Builder + Runtime)](til/2026/01/2026-01-19_splitting_up_docker_image.md)

_Last updated: 2026-08-08 07:59 UTC_
<!-- END:INDEX -->

## About me

I'm a Data Scientist (PhD) with 8+ years of experience in quantitative research, statistical modeling, and data-driven decision support. Expert in bridging the gap between complex statistical modeling and production-grade MLOps, translating complex analyses into actionable insights for diverse stakeholders. Experienced in international and interdisciplinary environments.

My work combines advanced statistical and Bayesian modeling, machine learning, and software engineering practices, with hands-on experience in R, Python, SQL, CI/CD, and containerized deployments. I focus on translating complex data into actionable insights through robust analysis, interactive dashboards, and clear analytical narratives.

Currently, I work as a Data Scientist at CEPTRO / NIC.br, where I develop and maintain analytical systems used to understand and monitor internet usage and network quality in Brazil. I collaborate in international and interdisciplinary teams and bring strong experience working across cultural and institutional contexts.

[📄 **CV**](./assets/cv_kleer_en.pdf)

**Github Profile:** https://github.com/philkleer  

**LinkedIn:** https://linkedin.com/in/philkleer  

## License
MIT (see `LICENSE`).
