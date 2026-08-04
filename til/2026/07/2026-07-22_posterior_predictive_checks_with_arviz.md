# TIL: Posterior Predictive Checks and Diagnostics with `arviz`

*Date: 2026-07-21*

Fitting a Bayesian model is the easy part. Trusting it — and knowing when *not* to trust it — is where `arviz` earned its keep during a stockout/sellout analysis for a retail client. This note covers the diagnostic workflow I used before reporting any coefficient.

---

## 🔍 1. Convergence First, Always

Before looking at a single coefficient, I checked whether the sampler actually converged:

```python
az.summary(fit, var_names=["PCT_RUPTURA_MES"])
```

Two numbers matter most:

- **R-hat ≈ 1.00** — chains agree with each other
- **ESS (effective sample size) in the thousands** — enough independent-ish draws to trust the posterior shape

If either looks off, no downstream diagnostic (LOO, PPC) is worth interpreting yet — fix sampling first.

---

## ⚠️ 2. Pareto-k via LOO Flags Influential Observations

`arviz`'s LOO computation doubles as an influence diagnostic: each observation gets a Pareto-k value, and values above 1 mean "this point is disproportionately shaping the fit."

```python
loo_result = az.loo(fit, pointwise=True)
influential = loo_result.pareto_k[loo_result.pareto_k > 1]
```

In this analysis, ~0.7% of observations were flagged this way. Investigating them turned up 17 store-month records with exactly zero recorded sales, concentrated in the last two months of the dataset — a data-delivery lag, not a modeling problem. After excluding those rows and refitting, extreme Pareto-k incidence dropped by roughly 70–75%.

**Takeaway**: don't treat Pareto-k warnings as something to silence — treat them as a lead to investigate. Sometimes it's genuine model misspecification; sometimes it's a data artifact worth fixing before it quietly biases the fit.

---

## 📐 3. Model Comparison Isn't a Diagnostic — But It Uses the Same Machinery

Once individual models are validated, `az.compare()` uses the same LOO computation to rank models:

```python
comparison = az.compare({
    "null": loo_null,
    "baseline": loo_baseline,
    "controls": loo_controls,
    "interaction": loo_interaction
})
```

This is where I confirmed the interaction model genuinely beat simpler alternatives, rather than just having more parameters.

---

## 🎲 4. Reading the Posterior Directly for Client-Facing Claims

Rather than reporting only a point estimate and interval, I used the posterior draws directly to make probability statements that map to plain language:

```python
posterior_ruptura = fit.posterior["PCT_RUPTURA_MES"]
prob_positive = (posterior_ruptura > 0).mean().item()
```

This is what let me write client-facing lines like *"~96% of the posterior mass is positive"* for one channel, versus *"~76% positive, 24% negative"* for another — directly communicating *how sure* we are, per channel, rather than forcing a single binary "significant or not" call.

---

## 🧪 5. Robustness Checks Are a Diagnostic Too

I don't think of robustness checks as separate from model diagnostics — they answer the same question ("can I trust this coefficient?") from a different angle. I compared the same coefficient across:

- swapping one categorical control for an alternative grouping
- restricting to better-observed stores (≥6 months of history)
- excluding the 17 flagged rows

All three landed on essentially the same estimate. A coefficient that survives several unrelated perturbations is more convincing than one with a narrow credible interval and nothing else checked.

---

## 🧩 6. Slicing an Interaction's Posterior by Group

When a model includes an interaction term (e.g. `PCT_RUPTURA_MES * CANAL_PDV`), the group-specific effect isn't a separate model output; it's the reference-category posterior plus that group's interaction offset, computed directly from the posterior draws:

```python
posterior_ruptura = fit.posterior["PCT_RUPTURA_MES"]
posterior_interactions = fit.posterior["PCT_RUPTURA_MES:CANAL_PDV"]

for channel in posterior_interactions.coords["PCT_RUPTURA_MES:CANAL_PDV_dim"].values:
    beta_channel = posterior_ruptura + posterior_interactions.sel(
        {"PCT_RUPTURA_MES:CANAL_PDV_dim": channel}
    )
    prob_positive = (beta_channel > 0).mean().item()
```

This is what let me report *per-channel* probability statements (e.g. "~96% positive" for one channel, "~99.6% positive but in the unexpected direction" for another) straight from one fitted model, rather than fitting a separate model per group and losing the shared partial pooling on the other controls.

---

## 📈 Key Takeaways

- Check R-hat and ESS before interpreting anything else
- Use Pareto-k from LOO to find influential observations — then *investigate*, don't just exclude
- `az.compare()` reuses LOO machinery to rank models on out-of-sample predictive fit, not in-sample fit
- Posterior draws let you make direct probability statements ("96% positive") that are more honest and more useful to a client than a p-value
- Robustness checks and diagnostics are answering the same underlying question from different angles

## 🧠 Final Insight

> A Pareto-k warning isn't a problem to make go away — it's the model telling you exactly where to look next.