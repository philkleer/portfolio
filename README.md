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

1. **Modularizing a Large Shiny Application (OBIA)**  
Refactoring and hardening a national-scale analytics application, reducing code size by ~41% and introducing CI/CD, testing, and reproducibility.

2. **Leveling Up an Internal R Package for Team-Scale Use**  
Productionizing an internal analytics package with versioned releases, CI/CD pipelines, and reproducible environments.

3. **Shiny Application – IT Governance (MGI)**  
End-to-end development and deployment of a public-facing Shiny application to assess IT governance across national entities.

4. **Network Technology Analysis & Visualization**  
Statistical analysis and visual storytelling to support technical and policy-oriented decision-making.

5. **End-to-End MLOps Pipeline**  
Implementation of a production-like ML lifecycle with experiment tracking and data/model versioning.

## Detailed Projects

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
- 2026-01-05 — [Case Study: School Detection from Satellite Imagery](notes/case-studies/2026-01-05-school_detection_from_satellite_imagery.md)
- 2025-12-17 — [How I build data-driven presentations with Quarto + revealjs (a real-world example)](notes/case-studies/2025-12-17-nota_estilo_apresentacoes_quarto_revealjs.md)
- 2025-11-20 — [Case Study: Benchmarking Shiny app performance across environments with `shinyloadtest`](notes/case-studies/2025-11-20-shinyloadtest-performance-comparison.md)
- 2025-09-19 — [Case Study: Debugging across multiple R versions with `rig` + `renv`](notes/case-studies/2025-09-19-debugging-multiple-R-versions-with-rig-and-renv.md)
- 2025-09-14 — [From ad‑hoc repo to versioned, CI‑driven R package: nicverso](notes/case-studies/2025-09-14-nicverso-ci-overhaul.md)
- 2025-08-30 — [R big data benchmarks: dplyr/duckplyr/polars & Postgres/DuckDB](notes/case-studies/2025-08-30-r-bigdata-benchmarks-updated.md)
- 2025-08-14 — [Modularizing a Large Shiny App (R)](notes/case-studies/2025-08-14-modularizing-large-shiny-app.md)

## TIL: Latest Lessons
- 2026-01-19 — [🧠 TIL: Shrinking Docker Images with Multi-Stage Builds (Builder + Runtime)](til/2026/01/2026-01-19_splitting_up_docker_image.md)
- 2026-01-15 — [TIL: Using `ellmer`, `gander`, `chores`, and `ensure` to Draft R Docs + Tests with an Ollama Connection](til/2026/01/2026-01-15_R_docs_with_ellmer_ensure_gande_chores.md)
- 2026-01-09 — [TIL: Learning Window Functions in PostgreSQL (with Practical Examples)](til/2026/01/2026-01-09_postgresql_window_functions.md)
- 2026-01-05 — [TIL: Point labels are often better suited for *site detection* than for segmentation](til/2026/01/2026-01-05-point_labels_site_detection.md)
- 2026-01-05 — [TIL: Geographic train/test splits are essential for honest geospatial ML evaluation](til/2026/01/2026-01-05_geo_train_test_split.md)
- 2026-01-05 — [TIL: OpenStreetMap is powerful weak supervision—but it teaches what is *mapped*, not what *exists*](til/2026/01/2026-01-05-osm_weak_supervision.md)
- 2025-12-30 — [🧠 TIL: Getting Docker Image Tags Right in a Company Harbor Registry](til/2025/12/2025-12-30_tagging_docker_production_images.md)
- 2025-12-12 — [Configuring Rate Limiting and IP Restriction in Kong Ingress](til/2025/12/2025-12-12-kong-plugins.md)
- 2025-12-04 — [🧠 Building Machine Learning workflows in R with {tidymodels}](til/2025/12/2025-12-04_tidymodels_workflow.md)
- 2025-11-19 — [TIL: Embedding Shiny elements inside Quarto Dashboards](til/2025/11/2025-11-19-quarto-dashboards-with-shiny.md)
- 2025-11-10 — [Today I Learned: Consistent naming across stack layers improves maintainability](til/2025/11/2025-11-10-consistent-naming.md)
- 2025-11-04 — [TIL: Speeding up Shiny apps with smarter reactive design](til/2025/11/2025-11-04-shiny-performance-tips.md)

_Last updated: 2026-01-29 07:54 UTC_
<!-- END:INDEX -->

## About me

Ph.D.-trained Data Scientist with 8+ years of experience in quantitative analysis, statistical modeling, and applied data science. I specialize in building reproducible analytical workflows and production-grade data applications that support data-driven decision-making.

My work combines advanced statistical and Bayesian modeling, machine learning, and software engineering practices, with hands-on experience in R, Python, SQL, CI/CD, and containerized deployments. I focus on translating complex data into actionable insights through robust analysis, interactive dashboards, and clear analytical narratives.

Currently, I work as a Data Scientist at CEPTRO / NIC.br, where I develop and maintain analytical systems used to understand and monitor internet usage and network quality in Brazil. I collaborate in international and interdisciplinary teams and bring strong experience working across cultural and institutional contexts.

[📄 **CV**](./assets/cv_kleer_en.pdf)

**Github Profile:** https://github.com/philkleer  

**LinkedIn:** https://linkedin.com/in/philkleer  

## License
MIT (see `LICENSE`).
