# 🧠 TIL: Migrating to Docker Buildx with Registry Cache (and Why It’s Worth Showing)

_Date: 2026-01-25_

Over the last days I migrated a project from a classic  
`docker compose build` + `docker tag/push` workflow to **Docker Buildx** with a
**registry-backed cache** (Harbor), while keeping a fairly complex setup:

- multi-stage Dockerfile (builder + runtime),
- `{renv}`-managed R dependencies,
- private Git dependencies via BuildKit secrets,
- GitLab CI with dev vs prod tagging.

This note captures *why* I did this, *what changed*, and *why this is a good thing to show*.

---

## 🎯 The Original Pain Points

Before Buildx, the pipeline worked — but it had friction:

- builds were **slow**, even when nothing changed
- caching was local and unreliable in CI
- secrets for private repos required awkward workarounds
- tagging (`latest`, `current`, etc.) was confusing
- build and push were separate steps, easy to desync

In short: it worked, but it didn’t scale well.

---

## ⏱️ Before vs After (What Changed in Practice)

Even without exact benchmark numbers, the qualitative difference was clear:

### Before (classic Docker build/push)
- cold builds were **slow** (lots of recompilation)
- CI jobs often started with **empty cache**
- rebuilds didn’t reliably reuse layers across runners
- secrets/auth handling felt hacky
- build + tag + push were separate steps

### After (Buildx + registry cache)
- rebuilds are **much faster** due to shared cache
- cache survives across CI jobs and runners (**registry-backed**)
- secrets are handled cleanly via BuildKit
- build + push happen in **one atomic command**
- tagging is simpler and more explicit

> **Rule of thumb:**  
> the more compiled dependencies you have (R packages, system libs, Rust deps),  
> the bigger the win from a remote Buildx cache.


---

## 🗺️ Diagram: Old vs New Pipeline

```text
BEFORE
======

GitLab CI
  |
  |-- docker compose build (local daemon cache)
  |
  |-- docker tag <image>
  |
  |-- docker push <image>
  |
  '-- (cache mostly lost between runners)


AFTER
=====

GitLab CI
  |
  |-- docker buildx build
  |     --cache-from=registry:<harbor>/<repo>:buildcache
  |     --cache-to=registry:<harbor>/<repo>:buildcache
  |     --secret id=nicverso_token,...
  |     --tag <image:dev|prod|version>
  |     --push
  |
  '-- shared cache persists in Harbor (fast rebuilds)
```

---

## ✅ What Buildx Solved

Migrating to Buildx gave me three major improvements at once:

### 1) Registry-backed cache (Harbor)

By using:

```bash
--cache-from type=registry,ref=...:buildcache
--cache-to   type=registry,ref=...:buildcache,mode=max
```

**I now get:**

- fast rebuilds across CI jobs
- cache reuse between branches and pipelines
- no reliance on runner-local Docker state

This is especially important when compiling R packages or Rust-based deps
(e.g. polars).

---

### 2) First-class secrets with BuildKit

Buildx made it natural to use:


```
RUN --mount=type=secret,id=nicverso_token ...
```

and pass the secret explicitly at build time:

```
--secret id=nicverso_token,src=.secrets/nicverso_token
```

This means:

- no tokens baked into layers
- no credentials leaking into the image history
- secrets exist only for the duration of the build step

This is exactly how private Git dependencies should be handled.

---

### 3) Build + push as a single, atomic step

With Buildx, the pipeline now:

- builds
- tags
- pushes
- updates the cache

in **one command**.

This eliminated:

- extra docker tag steps
- separate push_current logic
- subtle inconsistencies between "what was built" and "what was pushed"

---

### 🧩 Keeping the Complex Parts Working

What made this migration non-trivial (and interesting):

- `{renv}` libraries live in a non-standard path (`/renv/library`)
- runtime images must discover the correct deep `{renv}` folder
- `{polars}` requires Rust tooling at build time
- the same `Dockerfile` must work for `dev` and `prod` images

**The final solution:**

- restore dependencies once in the builder stage
- copy only the library + app into runtime
- set `R_LIBS_SITE` dynamically via `Renviron.site`
- verify packages explicitly in runtime

**This made the runtime image:**

- smaller
- deterministic
- independent of `renv::restore()` at startup

--- 

## 🔍 Key Takeaways

- Buildx is not just for multi-arch builds — cache + secrets are the real win
- Registry-backed cache is a game changer in CI
- Complex dependency setups (like `{renv}`) can work cleanly with Docker
- Good pipelines reduce cognitive load, not just build time