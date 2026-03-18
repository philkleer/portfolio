# TIL: A Practical Workflow for Finding a Production-Ready Binary Classifier

_Date: 2026-03-10_

While developing a binary classifier to detect fiber connections, I realized that finding a _good model_ is not just about accuracy — it’s about **defining the right objective, evaluating properly, and making probabilities usable in production**.

This note summarizes the workflow I used.

---

## 🎯 1. Start with the Objective (Not the Model)

Before training anything, I defined what _good_ means:

- **High precision** → if the model predicts fiber, it should *really* be fiber  
- Recall is secondary  

This directly influenced:

- evaluation metrics  
- hyperparameter tuning  
- threshold selection  

I constructed a scorer for the algorithms to test: 

```python
fiber_precision_scorer = make_scorer(
    precision_score,
    pos_label=1,
    zero_division=0,
)
```

---

## 🧪 2. Use a Proper Data Split (Train / Calibration / Test)

Instead of the usual train/test split, I used:

- **Train** (70%) → fit models  
- **Calibration set** (15%)  → calibrate probabilities
- **Test** (15%) → final evaluation  

```python
X_train, X_temp, y_train, y_temp = train_test_split(...)
X_calib, X_test, y_calib, y_test = train_test_split(...)
```

This avoids leakage when calibrating probabilities.

---

## ⚖️ 3. Establish Baselines First

I trained multiple baseline models:

- Logistic Regression (interpretable)  
- Random Forest (robust)  
- LightGBM & XGBoost (strong learners)  

Key insight:

> Boosting models clearly outperformed linear models in precision.

---

## 🔍 4. Optimize for the Right Metric (Not Default Metrics)

Instead of optimizing for accuracy or ROC-AUC, I explicitly optimized for:

> **Precision on the positive class**

```python
scoring=fiber_precision_scorer
```

This aligns model selection with the real-world objective, because we want to be certain in the prediction of the positive case. 

---

## ⚙️ 5. Hyperparameter Tuning: Random + Bayesian Search

I used two strategies:

### Random Search (fast baseline)
```python
RandomizedSearchCV(...)
```

### Bayesian Optimization (`{optuna}`)
```python
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

Key takeaway:

> Bayesian search consistently found better configurations than random search.

---

## 📉 6. Threshold Tuning (Critical for Production)

Default threshold (0.5) is rarely optimal.

I explicitly analyzed:

```python
precision, recall, thresholds = precision_recall_curve(...)
```

Then selected a threshold achieving:

> **precision ≥ 0.95**

This is crucial:

- model ≠ decision rule  
- threshold defines business behavior  

---

## 📊 7. Calibration: Making Probabilities Trustworthy

Raw model probabilities were poorly calibrated:

- overconfident predictions  
- skewed probability distributions  

I used **Isotonic Regression**:

```python
iso_reg = IsotonicRegression(out_of_bounds="clip")
iso_reg.fit(y_proba_calib, y_calib)
```

After calibration:

- probabilities became meaningful  
- threshold decisions became stable  

---

## 📏 8. Evaluate with Brier Score + Calibration Curves

Instead of only classification metrics, I also checked:

- **Calibration curves**  
- **Brier score**  

```python
brier_score_loss(y_test, proba)
```

Key insight:

> A model with slightly worse model fit but better calibration is often more useful in production.

---

## 🏁 9. Final Model = Model + Calibration + Threshold

The final model is not just the estimator:

```python
{
  "model": best_model,
  "calibrator": iso_reg,
  "threshold": threshold
}
```

This ensures:
- reproducibility  
- correct decision logic  
- production-ready behavior  

---

## 📈 Key Takeaways

- Define the **objective first** (precision vs recall)  
- Use **train / calibration / test** splits  
- Optimize for the **right metric**, not defaults  
- Tune both **model parameters and thresholds**  
- Always **check calibration**  
- A production model = **model + calibration + threshold**  

---

## 🧠 Final Insight

> Finding a good model is less about algorithms  
> and more about aligning evaluation with the real-world decision problem.

