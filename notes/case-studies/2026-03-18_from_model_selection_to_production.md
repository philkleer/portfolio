# 📊 Case Study: Serving ML in Production — From Model Selection to Reliable Inference

_Date: 2026-03-20_

---

## 🚀 Context

In this project, I developed and deployed a **binary classifier to detect fiber connections** and operationalized it end-to-end within a constrained infrastructure environment.

What started as a modeling task evolved into a full system covering:

👉 **Modeling → MLOps Pipeline → Monitoring → Serving (API)**

Two main challenges emerged:

1. Finding a production-ready model  
2. Building a complete system without standard tools (Airflow, managed MLflow)  

---

# 🧠 Part 1: Finding a Production-Ready Model

## 🎯 Objective Definition

> If the model predicts fiber → it must be correct

- Optimize for **precision**
- Treat recall as a constraint

---

## ⚙️ Modeling Workflow

- Train / Calibration / Test split  
- Boosting models (XGBoost) performed best  
- Bayesian optimization (Optuna) improved results  
- Threshold tuned to **precision ≥ 95%**  
- Calibration (Isotonic Regression) ensured reliable probabilities  

---

## 🏁 Final Model

```python
{
  "model": model,
  "calibrator": calibrator,
  "threshold": threshold
}
```

---

# ⚙️ Part 2: MLOps Pipeline (Without Standard Stack)

## 🚧 Constraints

- No Airflow  
- No shared MLflow  
- Limited Kubernetes support  

---

## 💡 Solution: Kubernetes-Native Pipeline

```
CronJob → Docker → Retrain → Evaluate → Compare → Deploy
```

---

## 🔁 Workflow

- Detect new data (file-based versioning)  
- Retrain + calibrate model  
- Evaluate at business threshold  
- Compare against champion  

---

## ⚖️ Promotion Logic

```
precision_new ≥ precision_old
AND recall_new ≥ recall_old - 0.02
```

---

## 📦 Infrastructure

- MLflow (SQLite + S3)  
- GitLab CI/CD  
- Docker + Kubernetes  

---

# 🔔 Part 3: Monitoring & Alerting

To make the system operational:

## 📊 Notifications

Each training run sends:
- metrics (precision, recall, etc.)
- promotion decision  

## 🚨 Alerts

Triggered when:

```
precision < 0.90 OR recall < 0.80
```

This enables:
- early detection of drift  
- fast investigation  
- operational visibility  

---

# 🌐 Part 4: Serving the Model via API

## 💡 Motivation

A model is only useful if it is **easy to consume**.

Instead of embedding logic everywhere:

👉 Built a **FastAPI-based internal API**

---

## ⚙️ API Design

- Loads models dynamically from MLflow  
- Supports batch predictions via file upload  
- Returns results in **Parquet / CSV**  
- Provides model inspection endpoints  

---

## 🔑 Key Features

### Model Loading
- Uses MLflow aliases (`champion`)  
- Dynamically downloads model bundles  

### Startup Optimization
- Caches model in memory  
- Reduces latency  

### Efficient Predictions
- Uses **Polars** for performance  
- Handles large datasets  

### Output Design
- Parquet → efficient pipelines  
- CSV → usability  

---

## 🔁 Inference Flow

```
Client → Upload file → API
        ↓
   Validate schema
        ↓
   Load model (MLflow/cache)
        ↓
   Predict (model + calibration + threshold)
        ↓
   Return results
```

---

# 🧾 Key Takeaways

### Modeling
- Define objective first  
- Tune thresholds explicitly  
- Always calibrate probabilities  

### MLOps
- Work within constraints  
- Lightweight infrastructure can be enough  
- Automate retraining and deployment  

### Serving
- APIs are essential for usability  
- File-based batch inference scales well  
- Performance matters (Polars, Parquet)  

### Operations
- Monitoring is mandatory  
- Alerts turn systems into operable services  

---

# 🧠 Final Insight

> Serving ML in production is not about a single tool or step —  
> it is about connecting modeling, pipelines, monitoring, and serving into a coherent system.

---

# 🔥 Impact

This system enabled:

- reproducible training  
- automated retraining  
- controlled deployment decisions  
- real-time monitoring  
- scalable and efficient model consumption  

—all within a constrained environment.

