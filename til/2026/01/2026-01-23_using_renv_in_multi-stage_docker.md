# TIL: Making {renv} Work in a Multi-Stage Docker Build (Builder → Runtime)
_Date: 2026-01-23_


In a previous step I split my Docker image into a **builder image** and a **runtime image** to reduce size and improve clarity.

That worked well — but it introduced a new problem: getting a project `{renv}` environment to work correctly in the final runtime container.

This note documents the approach that worked for me and why it matters.

---

## 🎯 The Problem

In the builder stage, `{renv}` restored all dependencies successfully.

In the runtime stage, I wanted to **avoid running `renv::restore()` again**, because:

- restoring packages at runtime is slow and fragile
- it requires network access and build tools
- it is harder to make reproducible in production
- it increases container startup time

So the goal was:

✅ restore packages once in builder  
✅ copy the `{renv}` library to runtime  
✅ ensure R can find it reliably

---

## 🧱 My Setup: Two Stages (Same Base Image)

I used the same base image for both stages:

```dockerfile
FROM rocker/shiny:4.5.2 AS builder
...
FROM rocker/shiny:4.5.2 AS runtime
```

This is important because it keeps:
- R version consistent
- platform and system library ABI consistent
- fewer surprises when copying compiled packages

---

## ✅ Builder Stage: Restore into a Custom {renv} Library

The key trick: define stable `{renv}` library + cache paths **explicitly**:

```dockerfile
ENV RENV_PATHS_LIBRARY=/renv/library     
    RENV_PATHS_CACHE=/renv/cache     
    RENV_CONFIG_PAK_ENABLED=TRUE     
    PAK_CACHE_DIR=/pak/cache     
    RENV_CONFIG_AUTOLOADER_ENABLED=FALSE
```

Then I create the directories early:

```dockerfile
RUN mkdir -p /renv/library /renv/cache /pak/cache
```

### Why I set these paths
- `/renv/library` becomes the **single source of truth** for installed packages
- I can copy it into the runtime image without guessing R’s default paths
- `/renv/cache` and `/pak/cache` can be mounted as caches to speed up builds

---

## 📦 Restoring with {renv} + {pak}

Inside the builder stage I restored with:

```r
renv::consent(provided = TRUE)
renv::load(project = "/build")
renv::restore(
  project  = "/build",
  lockfile = "/tmp/renv.lock",
  prompt   = FALSE,
  exclude  = "polars"
)
```

### Why `exclude = "polars"`
Some packages can be tricky with certain installers (or need extra toolchains).  
In my case, `polars` caused issues with `{pak}`, so I installed it separately:

```r
install.packages("polars", repos = "https://community.r-multiverse.org")
```

---

## ✅ Verification Step (Fail Fast)

Before leaving the builder stage, I verify that the library looks correct:

```r
p <- renv::paths$library()
stopifnot(file.exists(file.path(p, "tidyverse", "DESCRIPTION")))
```

This catches restore failures **during the build**, not later at runtime.

---

## 🚚 Runtime Stage: Copy Library + App

In the runtime stage, I install only runtime system libs and then copy:

```dockerfile
COPY --from=builder /renv/library /renv/library
COPY --from=builder /srv/shiny-server /srv/shiny-server
```

So the runtime container has:
- the app code
- the pre-installed R packages
- none of the builder-only tooling

---

## 🧠 The Crucial Fix: Ensure R *sees* the {renv} Library

Even after copying `/renv/library`, R does not automatically use it.

The tricky part is that `{renv}` libraries are stored under a platform + version structure like:

```text
/renv/library/<hash>/R-4.5/x86_64-pc-linux-gnu
```

So I added a robust detection step in the runtime image that:

1. detects platform + R version
2. finds the matching renv library path
3. writes it to `Renviron.site` via `R_LIBS_SITE`

```dockerfile
RUN mkdir -p /usr/local/lib/R/etc && \
    PLAT="$(Rscript -e 'cat(R.version$platform)')" && \
    RVER="$(Rscript -e 'cat(paste0("R-", R.Version()$major, ".", strsplit(R.Version()$minor, "\\.")[[1]][1]))')" && \
    RENV_ROOT="${RENV_PATHS_LIBRARY:-/renv/library}" && \
    RENV_LIB="$(find "$RENV_ROOT" -maxdepth 4 -type d -path "$RENV_ROOT/*/$RVER/$PLAT" | head -n 1)" && \
    echo "Detected renv lib: $RENV_LIB" && \
    test -n "$RENV_LIB" && \
    test -d "$RENV_LIB" && \
    printf '%s\n' \
        "R_LIBS_SITE=$RENV_LIB" \
        > /usr/local/lib/R/etc/Renviron.site
```

### Why this works
- it decouples runtime from `renv::activate()`
- it makes R find packages even if the project isn't loaded through `{renv}`
- it’s deterministic and doesn't require execution of R code at container startup

---

## 👤 Permissions (Shiny user)

Since Shiny containers often run as the `shiny` user, I also fixed ownership:

```dockerfile
RUN chown -R shiny:shiny /srv/shiny-server /renv/library
```

This prevents weird permission issues when Shiny touches files or logs.

---

## ✅ What I Would Do Again

- Use the same base image for builder + runtime (avoid compiled package mismatch)
- Restore into an explicit directory (`/renv/library`)
- Add a strict verification step before finishing builder stage
- Set `R_LIBS_SITE` explicitly in runtime

---

## 🔍 Key Takeaways

- Multi-stage builds are great, but `{renv}` is **path- and platform-sensitive**
- Copying `/renv/library` is not enough unless the runtime **library paths match**
- Setting `R_LIBS_SITE` is a clean and robust way to make runtime containers work
- Don’t rely on "it works on my machine" — validate during build

