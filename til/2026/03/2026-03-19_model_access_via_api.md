# TIL: Building a Lightweight Internal ML API with FastAPI + MLflow

_Date: 2026-03-19_  

---

## 🧠 Context

After building a production-ready ML pipeline (training, evaluation, deployment, monitoring), the next step was clear:

> Make the model easily usable by other systems and analysts.

Instead of embedding prediction logic everywhere, I built a **lightweight internal API** using FastAPI.

---

## 💡 Why an Internal API?

- Centralizes model access  
- Ensures consistent predictions  
- Decouples model logic from consumers  
- Makes updates (new models) transparent  

👉 The API becomes the **single entry point for inference**.

---

## ⚙️ Core Design

The API is built with **FastAPI** and integrates directly with MLflow:

- Loads models dynamically from MLflow  
- Supports batch predictions via file upload  
- Returns results in efficient formats (Parquet/CSV)  
- Provides model inspection and download endpoints  

---

## 🔑 Key Features

### 1. Model Loading via MLflow

Models are not stored locally — they are loaded from MLflow:

- Uses model aliases (e.g. `champion`)  
- Downloads artifacts dynamically  
- Loads bundled model (model + calibrator + threshold)  

```python
bundle, version = load_model("champion")
```

📎 Implementation: see loader module

---

### 2. Startup Optimization (Model Caching)

The API preloads the champion model on startup:

```python
model_cache["bundle"] = bundle
```

Benefits:
- avoids repeated MLflow calls  
- reduces latency  
- ensures fast inference  

---

### 3. Batch Predictions via File Upload

Users can upload `.parquet` or `.csv` files:

- validated input schema  
- vectorized predictions with Polars  
- calibrated probabilities + threshold  

```python
df_result = run_predictions(bundle, df, id_column)
```

---

### 4. Efficient Data Handling (Polars + Parquet)

- Uses **Polars** for fast computation  
- Supports **Parquet output** (smaller + faster than JSON)  

👉 Designed for **large datasets and performance**.

---

### 5. Flexible Output

Users can choose:

- Parquet → efficient for pipelines  
- CSV → easy for manual usage  

---

### 6. Model Introspection

Additional endpoints:

- `/models` → list available model versions  
- `/download` → download model bundle  

---

## 🔁 End-to-End Flow

```text
Client → Upload file → API
        ↓
   Validate schema
        ↓
   Load model (cached or MLflow)
        ↓
   Predict (model + calibration + threshold)
        ↓
   Return results (Parquet/CSV)
```

---

## 📊 What This Enables

- Easy integration into pipelines  
- Consistent inference across teams  
- Fast batch predictions  
- Decoupled architecture  

---

## 🧾 Key Takeaways

- APIs are essential to operationalize ML models  
- MLflow + FastAPI is a powerful lightweight combination  
- Caching models improves performance significantly  
- File-based batch APIs are often more practical than JSON APIs for data workflows  

---

## 🧠 Final Insight

> A model in production is only useful if it is easy to consume.

Building an API turns a model into a **service** — not just an artifact.

