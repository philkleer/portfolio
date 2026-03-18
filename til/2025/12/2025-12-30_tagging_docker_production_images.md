# TIL: Getting Docker Image Tags Right in a Company Harbor Registry
_Date: 2025-12-30_

Today I learned (the hard way) how **clear Docker image tagging rules** make a big difference when working with a company Harbor registry and CI/CD pipelines for application products.

This note documents the **decisions, rationale, and pitfalls** I encountered while cleaning up image tags for *development* vs *production* builds of applications.

## 🎯 The Core Problem

Over time, our image tagging strategy became cumbersome:

- Using at the same time tags like **`latest`** and **`current`** were ambiguous.
- Development images were versioned, even though they change frequently.
- It wasn’t always obvious which image was **safe for production**.
- CI pipelines sometimes rebuilt the same image twice.

This made it harder to reason about:
- what was deployed,
- what was still under development,
- and which image should be pulled by default.

## 🧩 New Tagging Rules I Introduced

### 1) Non-`main` branches → *development images*

For any branch that is **not** `main`, the pipeline now pushes:

- `dev`
- `dev-<commit-sha>`

```text
image:dev
image:dev-a1b2c3d
```

**Why this works well**
- No need to update the `VERSION` file during development.
- `dev` always points to the *latest development build*.
- Clear that the application in this image is only for development purposes.
- `dev-<commit>` uniquely identifies a specific build for debugging or rollback.

### 2) Merges into `main` → *production images*

For merge requests into `main`:

1. The pipeline still builds a development image (as above).
2. When a release commit is detected:
   - the `VERSION` file changes
   - commit message matches `New version release X.Y.Z`
3. The pipeline:
   - tags the image with the semantic version
   - adds a **`prod`** tag to indicate the production image

**Meaning**
- `prod` = *the image currently used in production*, always points to the *latest production build*
- version tags = immutable historical releases for debugging or rollback.

In this case, the use of `latest` is also common (especially for base images), however, building applications and having in mind that not all colleagues are experienced with image development, clearer tags were chosen. 

## 🔁 Simplifying the Build Tags

Previously, we had multiple mutable tags:
- `DOCKER_DEV_TAG`
- `DOCKER_CURRENT_TAG`

I replaced this with a single, explicit variable:

```makefile
DOCKER_BUILD_TAG
```

Now the pipeline controls intent explicitly:

```bash
make DOCKER_BUILD_TAG=dev docker-push
make DOCKER_BUILD_TAG=prod docker-push-release
```

**Benefits**
- Fewer moving parts
- Clear semantics
- Less accidental misuse of *current* vs *latest*

## 🧠 Naming Matters: `prod` vs `latest`

One key insight: **names encode assumptions**.

Tags like `latest` / `current` refer to time, not to state like `prod` / `dev`. They communicate what the newest build is and, therefore, have a simple mental model which is useful for base images, SDKs, experimentation, or
local development.

On the other hand, `prod`/`dev` communicate the state, where the image is currently deployed. This has clear operational meaning, aligns with CI/CD and deployment concepts. However, it is slightly less convenient for ad-hoc *just pull the newest thing*. The tags `prod`/`dev` encode intent and operational state, they match how deployments actually work, and they reduce accidental rollouts.

Both approaches should be combined with immutable tags:
- ⚖️ They encode different semantics
- 🏆 `dev` / `prod` is superior for deployable application images
- 🧪 `latest` is good for local dev and base images

## 🧠 Key Takeaways

- Separate **development** and **production** tags clearly.
- Development images should be mutable; production images should not.
- Avoid ambiguous tags like `latest` when intent matters.
- Encode meaning in tag names (`dev`, `prod`, version numbers).
- CI/CD pipelines should reflect lifecycle stages explicitly.
- Regularly review pipelines for redundant or duplicated steps.
