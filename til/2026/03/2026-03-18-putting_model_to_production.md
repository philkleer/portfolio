# TIL: Building an MLOps Pipeline Without Airflow or Managed MLflow

_Date: 2026-03-18_

While working on deploying a binary classifier into production, I ran into a common real-world problem:

> The _standard stack_ (Airflow + managed MLflow) was not available.

- Kubernetes version incompatible with Airflow  
- No shared MLflow infrastructure  
- Limited platform support  

Instead of forcing tools that don’t fit, I designed a **Kubernetes-native MLOps pipeline**.

---

## ⚙️ The Core Idea

Use a **Kubernetes CronJob** as the orchestration layer.

```
CronJob (monthly)
   ↓
Docker container
   ↓
Retrain → Evaluate → Compare → Deploy
```

No Airflow needed.

---

## 🔁 The Workflow

Each monthly run does:

1. Detect new data (based on file naming convention)
2. Load latest production model (MLflow registry)
3. Retrain model (XGBoost + Optuna)
4. Calibrate probabilities (Isotonic Regression)
5. Compute metrics at optimal threshold
6. Compare with current production model

Decision logic:

- ✅ **Better** → promote to production  
- ❌ **Worse** → keep as challenger  
- ⚠️ **Both tracked** → monitor drift over time  

---

## 🧠 Key Design Decisions

### 1. MLflow as Single Source of Truth

- No models stored in Git  
- API loads directly from MLflow  
- Registry controls production state  

---

### 2. Explicit Champion/Challenger Logic

```
precision_new ≥ precision_old
AND recall_new ≥ recall_old - 0.02
```

This encodes business trade-offs directly into the system.

---

### 3. Model = More Than an Estimator

Each model is stored as a bundle:

```python
{
  "model": model,
  "calibrator": calibrator,
  "threshold": threshold
}
```

This ensures:
- reproducibility  
- correct decision behavior  
- production consistency  

---

### 4. Data Versioning Without a Data Platform

Instead of complex pipelines:

- Data files are **never overwritten**  
- Version = filename (`eace_YYYY-MM-DD.xlsx`)  
- Logged in MLflow  

Simple, but effective.

---

### 5. Self-Hosted MLflow (Minimal Setup)

- SQLite + PVC → metadata  
- S3 bucket → artifacts  
- Single pod → sufficient for batch workloads  

---

## 📡 Deployment Trigger

When a better model is found:

- Register as **Production** in MLflow  
- Trigger GitLab CI  
- Redeploy API  
- Notify via Slack/email  

---

## 📉 Monitoring

Monthly checks on production data:

- detect performance drift  
- alert on degradation  

---

## 🧾 Key Takeaways

- You don’t need a _perfect_ stack to build MLOps  
- Kubernetes CronJobs can replace Airflow for batch pipelines  
- MLflow can be self-hosted with minimal infrastructure  
- The most important part is **decision logic, not tooling**  

---

## 🧠 Final Insight

> Good MLOps is not about tools — it’s about designing a system that works within your constraints.
