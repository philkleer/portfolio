# TIL: Adding data validation and drift detection to an ML retraining pipeline

_Date: 2026-05-24_

## What I learned

The classifier pipeline retrains every 14 days on new data. The engineering problem was:

> how to detect silently degrading input data — class imbalance, feature drift, and distribution shifts — before they affect model quality, without adding operational complexity.

To solve this, I added a dedicated validation step between feature engineering and model training that:

- checks data quality on the gold dataset
- tracks class imbalance over time with threshold warnings
- computes Population Stability Index (PSI) per feature against the champion's training distribution
- runs Kolmogorov-Smirnov tests per feature as a secondary drift signal
- tracks per-class medians per feature to catch directional shifts
- logs all metrics to MLflow as first-class experiment metrics
- pushes a focused subset to a Prometheus Pushgateway as a future Grafana alerting bridge
- sends a Slack summary after every run and a warning alert when checks fail

---

## Architecture

```
extract.py          → raw data (bronze)
transform.py        → processed features (gold)
validate.py         → data quality & drift checks   ← new
train.py            → model training
evaluate.py         → model performance & champion comparison
```

```
validate_data()
    │
    ├── _check_data_quality()         row count, duplicates, null rates
    │
    ├── _check_class_imbalance()      fiber ratio, absolute counts, warning flag
    │
    ├── _check_feature_drift()        PSI + KS test + per-class medians
    │       │
    │       └── _load_reference_distribution()    from MLflow champion run
    │
    ├── mlflow.log_metrics()          full metric set
    │
    ├── _push_to_prometheus()         focused subset → Pushgateway
    │
    └── check_validation_alert()      Slack summary + warning if needed
```

---

## Why this mattered

The pipeline runs unattended as a Kubernetes CronJob. Without validation:

- a class imbalance shift could silently bias the retrained model
- a feature distribution change could invalidate model assumptions
- data quality issues from upstream sources would propagate into training

None of these failures raise exceptions. They produce a model that looks valid but performs worse in production.

The validation step makes these failures visible before training happens.

---

## Key engineering decisions

1. Separate script between transform and train

Instead of adding checks inside `train.py` or `evaluate.py`, I created a dedicated `validate.py`.

This separated concerns cleanly:

| Script         | Responsibility                         |
|----------------|----------------------------------------|
| `transform.py` | Feature engineering, gold dataset      |
| `validate.py`  | Input data health before training      |
| `train.py`     | Model training                         |
| `evaluate.py`  | Model performance, champion comparison |

The main function returns a dict with a `data_quality_passed` flag, allowing the pipeline orchestrator to hard-stop on quality failures while treating drift and imbalance warnings as non-blocking signals.

2. PSI as the primary drift metric

Population Stability Index compares the current batch distribution against the reference (training) distribution using fixed bin edges:

```
PSI = Σ (current_prob - reference_prob) × ln(current_prob / reference_prob)
```

Thresholds used:

| PSI range | Interpretation       |
|-----------|----------------------|
| < 0.10    | No significant shift |
| 0.10–0.20 | Moderate shift       |
| > 0.20    | Significant drift ⚠️ |

PSI uses the reference bin edges from training, so comparisons stay consistent across runs regardless of how the current data is distributed.

3. Storing the reference distribution as an MLflow artifact

The reference distribution (bin edges, proportions, value sample, per-class medians) is saved as a JSON artifact on the champion's MLflow run when the model is first promoted.

Every subsequent `validate.py` run loads it from there:

```python
mv = client.get_model_version_by_alias("classifier_fiber_v1", "champion")
local_path = mlflow.artifacts.download_artifacts(
    artifact_uri=f"{run.info.artifact_uri}/reference_distribution.json",
    dst_path=tmp,
)
```

This ties the reference directly to the model version it belongs to. If a new champion is promoted, the reference updates automatically.

On the very first run — no champion yet — the current batch is saved as the baseline and drift checks are skipped. The pipeline proceeds without blocking.

4. KS test as a secondary signal

The KS test (`scipy.stats.ks_2samp`) detects distributional differences that PSI can miss — particularly shape changes like bimodality forming within a feature.

To enable this, the reference distribution saves a capped sample of up to 5,000 raw values per feature alongside the binned PSI data.

Both PSI and KS p-value are logged per feature. PSI drives the `drift_warning` flag; KS provides supporting evidence for investigation.

5. MLflow as source of truth, Prometheus as a passive bridge

All metrics are logged to MLflow as first-class experiment data. This keeps drift metrics fully coupled to the model run that produced them — useful for understanding why a model degraded months later.

A focused subset is also pushed to the Prometheus Pushgateway:

- `data_quality_passed`
- `class_imbalance_warning`
- `drift_warning`
- `class_ratio_fiber`
- `psi_<feature>` per feature

The Pushgateway sits quietly in the namespace. Nobody needs to look at it until a Grafana alert becomes a real requirement — at which point the data source already exists and it becomes a dashboard configuration problem, not a pipeline change.

Prometheus push failures are non-blocking by design:

```python
except Exception as e:
    console.print(f"⚠️  Could not push to Prometheus (non-blocking): {e}")
```

6. Class imbalance tracked as ratio and absolute counts

The class ratio alone hides volume changes. A 22% fiber ratio in a 500-row batch is very different from the same ratio in a 50,000-row batch.

Both are logged:

- `class_ratio_fiber` — the drift signal
- `class_count_fiber` / `class_count_not_fiber` — the volume context

---

## What this taught me

The retraining pipeline was already handling model performance comparison well. What it was missing was visibility into the input side of the loop.

Model evaluation answers: *is the new model better than the old one?*

Data validation answers: *is the data this model trained on trustworthy?*

Both questions matter. A model can improve on test metrics while training on a distribution that is silently drifting away from production reality. Logging drift metrics alongside model metrics in the same MLflow run makes that relationship traceable over time.

---

## Technologies used

Python  
Polars  
MLflow  
Prometheus  
prometheus-client  
scipy  
NumPy  
Kubernetes CronJobs  
Parquet