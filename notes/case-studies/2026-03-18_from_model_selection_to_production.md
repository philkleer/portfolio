# 📊 Case Study: From Model Selection to Production MLOps under Real-World Constraints

_Date: 2026-03-18_  
_Author: Philipp Kleer_

---

## 🚀 Context

In this project, I developed a **binary classifier to detect fiber connections** and brought it into production within a constrained infrastructure environment.

Two main challenges emerged:

1. **Finding a production-ready model**
2. **Deploying it without standard MLOps tools (Airflow, managed MLflow)**

This case study combines both aspects into a single, end-to-end workflow.

---

# 🧠 Part 1: Finding a Production-Ready Model

## 🎯 Defining the Objective

The key requirement was:

> If the model predicts fiber → it must be correct

This led to:
- optimizing for **precision**, not accuracy  
- making recall a secondary constraint  

---

## 🧪 Data Splitting Strategy

Instead of a simple train/test split:

- Train (70%) → model training  
- Calibration (15%) → probability calibration  
- Test (15%) → final evaluation  

---

## ⚖️ Model Benchmarking

Tested models:
- Logistic Regression  
- Random Forest  
- LightGBM / XGBoost  

➡️ Boosting models performed best in precision.

---

## 🔍 Metric Alignment

Optimized explicitly for:

> **Precision (positive class)**

This aligned model selection with real-world needs.

---

## ⚙️ Hyperparameter Optimization

- Random Search → baseline  
- Optuna (Bayesian) → improved performance  

---

## 📉 Threshold Tuning

Instead of default 0.5:

- Used precision-recall curve  
- Selected threshold with **precision ≥ 95%**

---

## 📊 Calibration

Applied **Isotonic Regression** to fix probability estimates.

Result:
- stable probabilities  
- meaningful thresholds  

---

## 🏁 Final Model Structure

```python
{
  "model": model,
  "calibrator": calibrator,
  "threshold": threshold
}
```

---

# ⚙️ Part 2: Building an MLOps Pipeline Without Standard Tools

## 🚧 Constraints

- No Airflow support  
- No shared MLflow instance  
- Limited Kubernetes environment  

---

## 💡 Architecture Decision

Instead of forcing tools:

👉 Designed a **Kubernetes-native pipeline**

```
CronJob (monthly)
   ↓
Docker container
   ↓
Retrain → Evaluate → Compare → Deploy
```

---

## 🔁 Workflow

Each run:

1. Detect new data (file-based versioning)
2. Load current production model (MLflow)
3. Retrain model
4. Calibrate probabilities
5. Evaluate metrics at threshold
6. Compare with champion

---

## ⚖️ Champion / Challenger Logic

```text
precision_new ≥ precision_old
AND recall_new ≥ recall_old - 0.02
```

- Ensures precision improvements  
- Limits recall degradation  

---

## 🗂️ Data Versioning

Simple but effective:

- Files never overwritten  
- Version = filename (`eace_YYYY-MM-DD.xlsx`)  
- Logged in MLflow  

---

## 📦 MLflow Setup (Minimal)

- SQLite (PVC) → metadata  
- S3 → artifacts  
- Single pod → sufficient  

---

## 📡 Deployment Flow

If model is better:

- Register in MLflow as Production  
- Trigger GitLab CI  
- Redeploy API  
- Notify stakeholders  

---

## 📉 Monitoring

- Monthly evaluation on fresh data  
- Detect drift  
- Alert on degradation  

---

# 🧾 Key Takeaways

### Modeling
- Define objective first (precision vs recall)
- Tune threshold explicitly
- Always calibrate probabilities

### MLOps
- You don’t need a perfect stack
- Kubernetes CronJobs can replace Airflow
- Simple solutions (file versioning, SQLite MLflow) can be sufficient

---

# 🧠 Final Insight

> Building production ML systems is not about tools —  
> it’s about aligning modeling, evaluation, and infrastructure with real-world constraints.

---

# 🔥 Why This Matters

This approach enabled within a constrained environment:

- reproducible training  
- automated retraining  
- controlled deployment decisions  
- stable production predictions  
