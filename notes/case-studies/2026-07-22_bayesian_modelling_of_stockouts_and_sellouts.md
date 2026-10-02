# Case Study: Bayesian Modelling of Stockouts and Sellout

_Date: 2026-07-22_  
**Tags:** 


## Context and Motivation

A fictitious client wanted to know whether a specific operational metric — **stockout rate** (the share of a month a product was unavailable at a point of sale) — was meaningfully related to **sellout** (units sold), and whether the evidence was strong enough to justify investing in a stockout-reduction program across their store network.

This is a classic _should we spend money on this?_ business question hiding a genuine inference problem: the data is observational, it has a panel structure (the same stores observed repeatedly over many months), and the client needed an answer they could act on, not just a p-value.

The technical stack:

- **Python** with `uv` for environment/project management
- `{polars}` for data validation and manipulation
- `{plotnine}` for EDA visualization
- `{bambi}` for Bayesian mixed-effects modeling
- `{arviz}` for model diagnostics and posterior visualization
- `{statsmodels}` for an initial OLS sanity check

This was my first time running a Bayesian workflow in Python — I'd previously only done this kind of modeling in R with `{brms}`. Part of the exercise was translating that mental model into `bambi`/`arviz`.

## Problem Framing

The client's data included monthly observations per store, with:

- a target variable, `SELLOUT` (numeric)
- a primary predictor, stockout rate, available both as a count (`QTD_RUPTURA`) and a percentage (`PCT_RUPTURA_MES`)
- store-level and contextual variables: sales channel, region, store profile, store classification, and a month/cycle indicator

The central question: **is there evidence that lower stockout is associated with higher sellout, and is that evidence strong enough across channels to recommend a pilot?**

Before any modeling, this meant answering three sub-questions:

1. Is the data trustworthy (types, ranges, duplicates, missingness)?
2. Does the relationship hold up once other explanations (channel, region, seasonality) are accounted for?
3. Is the relationship stable across reasonable alternative model specifications?

## Why a Bayesian Mixed-Effects Model

Before touching `bambi`, I ran a quick OLS regression to check the assumption of independent observations. Its Durbin–Watson statistic came out at **≈0.43** (far below the acceptable range near 2) which confirmed what the data structure already suggested: each store is observed repeatedly across months, so a standard regression that ignores this would produce overconfident, biased standard errors.

That ruled out plain OLS and pointed toward a **mixed-effects model with a random intercept per store**.

I chose a Bayesian mixed-effects model over a frequentist one, or over a tree-based ML model (Random Forest / XGBoost), for three concrete reasons:

- **Client-facing interpretability.** A credibility interval is a direct probability statement about the parameter (_there's a 96% probability the effect is positive_) which matches how non-technical stakeholders already reason. Frequentist confidence intervals are routinely misinterpreted the same way, so the Bayesian framing avoids a predictable miscommunication.

- **Usable output for a specific decision.** The client needed something like _a 10-point reduction in stockout is associated with an X% increase in sellout, with Y% credible probability_ directly pluggable into an investment decision. Tree-based models produce predictions and (with extra work) feature importances, but not a signed, interpretable effect size with a probabilistic interval attached.

- **Reusable priors for future work.** With weak/uninformative priors and a moderately sized dataset, Bayesian and frequentist point estimates converge closely — so there's no immediate computational payoff for this analysis alone. The long-term value is that this posterior can become an *informative* prior for next year's data from the same client, or for a similar client in the same domain.

## Approach

### Model building progression

Rather than jumping straight to _the_ model, I built five specifications to isolate the effect and stress-test it:

1. **Null model** — all controls (channel, region, cycle, observation count), no stockout term
2. **Baseline model** — stockout rate only, with a per-store random intercept
3. **Controls model** — stockout rate plus all controls (the main model)
4. **Swap model** (robustness check 1) — replaces channel with a grouped store-profile variable
5. **Restricted-data model** (robustness check 2) — same as the controls model, but limited to stores with at least 6 months of history

Each model used the same core structure in `bambi`:

```python
controls_bayes = bmb.Model(
    "sellout_log ~ PCT_RUPTURA_MES + CANAL_PDV + MACRO_REGIONAL + QTD_OBSERVACOES + ciclo_date + (1|CNPJ_CLIENTE)",
    data=model_data_pd,
)
controls_bayes.build()
controls_bayes.graph()
```

### Model comparison

I compared models using PSIS-LOO cross-validation via `arviz`:

```python
comparison = az.compare({
    "null": loo_null,
    "baseline": loo_baseline,
    "controls": loo_controls,
})
```

The controls model clearly outperformed both alternatives (ELPD difference of 60 vs. the null, well above its standard error of 17), confirming that channel, region, and seasonality are the dominant drivers of sales variation — with stockout contributing a smaller, but real and reliable, effect on top of those factors.

### An unexpected data issue, found through diagnostics

LOO's Pareto-k diagnostics flagged roughly 0.7% of observations across models as highly influential. Digging in, this traced to 17 store-month records (9 stores) with exactly zero recorded sellout, concentrated almost entirely in the final two months of the dataset. Comparing those two months against known peak/low months (June and September) showed no broader anomaly — this pointed to a data-delivery lag for a handful of stores rather than a systemic issue. I excluded these 17 rows and refit all models.

This didn't materially change model ranking or the stockout coefficient, but it reduced the incidence of extreme Pareto-k values by roughly 70–75%, and convergence diagnostics (R-hat ≈ 1.00, ESS in the thousands) ruled out sampling itself as an explanation for the remainder.

### Robustness checks

The stockout coefficient was tested against three variations: swapping channel for grouped store profile, restricting to stores with more observation history, and excluding the 17 flagged rows. All three produced essentially identical estimates (≈-0.0034, 94% credible interval [-0.0040, -0.0029]) on the cleaned dataset. The uncontrolled (baseline) estimate was roughly double that — consistent with channel and seasonal confounding inflating the raw relationship, which argues *for* the added controls rather than undermining the conclusion.

### Catching a pooled-effect blind spot: the interaction model

While reviewing the analysis before final submission, I checked something I'd skipped earlier: whether the stockout–sellout relationship itself varied by channel, rather than just checking channel as an additive control. A quick visual check showed that for one channel, the stockout–sellout relationship looked qualitatively different (near-null to slightly positive) than for the others; a sign that the _controls_ model's single pooled coefficient for `PCT_RUPTURA_MES` might be averaging over real differences rather than describing one consistent effect.

That's a meaningfully different claim than _controls vs. no controls_, so it needed its own model rather than a footnote:

```python
interaction_bayes_clean = bmb.Model(
    "sellout_log ~ PCT_RUPTURA_MES * CANAL_PDV + MACRO_REGIONAL + QTD_OBSERVACOES + ciclo_date + (1|CNPJ_CLIENTE)",
    data=model_data_pd_clean,
)
interaction_bayes_clean.build()
```

Two things confirmed this wasn't just visual noise:

1. **The coefficients themselves.** With the interaction term in place, one channel showed a coefficient close to zero while the others showed a clearly *stronger* effect than the pooled model implied — meaning the single-coefficient "controls" model was diluting the true effect for most channels by averaging in one channel where it barely holds.

2. **Model comparison.** Comparing the interaction model against the controls model with `az.compare()` confirmed the interaction model fit the data better, not just differently — this wasn't overfitting noise.

This changes what the _final_ model is: the per-channel effects reported to the client come from the **interaction model**, not from re-running five separate single-channel models. The pooled controls model is still useful for establishing *that* an overall stockout effect exists and is robust — but the interaction model is what tells you it isn't the same effect everywhere, and that mattering enormously for a channel-targeted pilot recommendation.

## Results

Reading the per-channel coefficients off the interaction model (and flipping the sign, since the client cares about the effect of *reducing* stockout) gives a clearly uneven picture across the business:

- **Channels C, E, and F** showed the strongest, most credible effects: a 10-point reduction in stockout was associated with an estimated 8–10% increase in sellout.

- **Channel A** showed real uncertainty about whether an effect exists at all; its 94% credible interval spans zero, even though ~96% of the posterior mass sits on the positive side.

- **Channel B** was the channel that originally triggered the interaction check: its credible interval is wide and roughly straddles zero (~76% of posterior mass positive, ~24% negative); consistent with there simply being few observed cases in that channel.

- **Channel D** showed a statistically consistent effect in the *opposite* direction of expectation (~99.6% posterior probability that reducing stockout is associated with *lower* sellout), which doesn't support inclusion in a pilot and instead flags a need for further investigation; possibly confounders or characteristics specific to that channel.

Without the interaction model, this would have been reported as one number for the whole business — masking exactly the channel-level distinction the client needed to target a pilot sensibly.

## Key Design Decisions and Trade-offs

| Decision                                      | Rationale                                                                                                                                                                                            |
|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Bayesian mixed-effects over OLS               | Panel structure violates independence assumption (Durbin-Watson ≈0.43)                                                                                                                               |
| Bayesian over frequentist framing             | Credible intervals map naturally to client decision-making; avoids CI misinterpretation                                                                                                              |
| Bayesian over tree-based ML                   | Need a signed, interpretable effect size with uncertainty, not just predictions                                                                                                                      |
| Excluding 17 flagged rows                     | Diagnostics (Pareto-k) + investigation showed a data-delivery artifact, not signal                                                                                                                   |
| Adding a stockout × channel interaction model | A single pooled coefficient masked a channel where the effect was near-zero and another where it ran in the opposite direction; LOO confirmed the interaction model fit better, not just differently |
| Recommending a pilot over full rollout        | Association ≠ causation; reverse causality and confounding (well-run stores restock faster *and* sell more) remain plausible                                                                         |

## Lessons Learned

- Diagnostics aren't a formality — the Pareto-k check surfaced a genuine data quality issue that would otherwise have quietly inflated influence from 17 rows.
- A pooled coefficient can quietly average away the exact heterogeneity a client needs to act on — checking for interactions between your main predictor and key categorical variables is worth doing *before* calling an analysis final, not as an afterthought.
- Model comparison (PSIS-LOO) is a much more honest way to justify "which controls matter" — or "which model structure matters" — to a client than eyeballing coefficients.
- A Bayesian framing isn't just a stats preference here — it changes what you can *say* to a non-technical stakeholder without misleading them.
- Robustness checks are most convincing when they're boring: three very different perturbations landing on the same estimate is a stronger argument than any single model's fit statistics.

## Possible Extensions

- For higher-cardinality categorical variables (channel, region) in future similar analyses, target or mean encoding could reduce dimensionality — with care taken to avoid leakage (cross-fold encoding or shrinkage toward the global mean).
- Deeper investigation into channels A, B, and D, either through more data collection or channel-specific feature engineering.
- Using this posterior as an informative prior for next year's data or a similar client in the same domain.

## Summary

This project shows how a Bayesian mixed-effects workflow, chosen deliberately over both classical and ML alternatives, can turn a vague _is X related to Y?_ business question into a specific, defensible, channel-by-channel investment recommendation, while being upfront with the client about where the evidence is strong, where it's inconclusive, and where a pilot (rather than a full rollout) is the right next step.