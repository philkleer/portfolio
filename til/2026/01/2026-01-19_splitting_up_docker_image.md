# TIL: Shrinking Docker Images with Multi-Stage Builds (Builder + Runtime)
_Date: 2026-01-19_

Over the past few days I built a Docker image that initially became **way too large**.  
After some iterations, I switched to a **multi-stage build** approach using:

- a **builder image** (heavy: compilers, system deps, package installation)
- a **runtime image** (light: only what is needed to run)

This dramatically improved image size, build clarity, and separation of responsibilities.

---

## 🎯 The Problem

My initial image contained everything:

- build tools (`gcc`, `make`, headers)
- R packages compilation toolchain
- runtime dependencies
- dev utilities

It worked, but resulted in:
- large image sizes
- slow CI builds
- unclear separation between build and runtime concerns

---

## ✅ The Fix: Multi-Stage Builds

The new pattern:

### Stage 1: Builder
- install system build dependencies
- install R packages (often compiled)
- cache results for faster rebuilds

### Stage 2: Runtime
- install only runtime system libraries
- copy only the outputs needed to run
- avoid shipping compilers or build tooling

---

## 🧩 Benefits I noticed

- Much smaller final image
- Faster pushes/pulls in CI
- Cleaner Dockerfile structure
- More reliable runtime environment

---

## 🔍 Key Takeaway

If an image is too big: don’t only "optimize layers", **split the concerns**: build vs run.

Multi-stage builds are the cleanest way to do that.
