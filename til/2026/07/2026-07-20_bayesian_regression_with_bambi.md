# TIL: Bayesian Mixed-Effects Regression with `bambi`

*Date: 2026-07-20*

While analyzing whether store-level stockout rates were related to sales, I needed a Bayesian mixed-effects model in Python for the first time — previously I'd only done this kind of modeling in R with `{brms}`. This note captures what I learned translating that workflow to `bambi`.

---

## 🎯 1. Check Whether You Even Need Mixed Effects

Before reaching for `bambi`, I ran a plain OLS regression as a sanity check on the independence assumption:

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
# ... fit OLS, then:
durbin_watson(ols_fit.resid)
```

A Durbin-Watson statistic of **≈0.43** (well below the acceptable range near 2) confirmed substantial residual autocorrelation — expected, since each store is observed repeatedly across months. That's the signal to move to a panel-aware model rather than plain OLS.

---

## 🧱 2. `bambi` Model Syntax Mirrors `{brms}` Formulas

If you know `{brms}`, `bambi`'s formula syntax will feel immediately familiar — including the `(1|group)` random-intercept notation:

```python
import bambi as bmb

controls_bayes = bmb.Model(
    "sellout_log ~ PCT_RUPTURA_MES + CANAL_PDV + MACRO_REGIONAL + QTD_OBSERVACOES + ciclo_date + (1|CNPJ_CLIENTE)",
    data=model_data_pd,
)
controls_bayes.build()
controls_bayes.graph()  # renders the model structure as a graph
```

Key gotcha: `bambi` expects a **pandas** DataFrame, so if your pipeline is `polars`-based (mine is, end to end), you need an explicit conversion step before fitting.

---

## 🪜 3. Build Up Model Complexity Deliberately

Instead of fitting one "final" model, I built a small ladder of models to isolate the effect of interest:

- **Null**: all controls, no stockout term
- **Baseline**: stockout rate only, with the random intercept
- **Controls**: stockout rate + all controls
- **Robustness variants**: swap one control for an alternative encoding, or restrict to better-observed stores

This makes it possible to answer *"how much of the effect is really about stockout, versus channel/region/season?"* — rather than just reporting one coefficient and hoping it's not confounded.

---

## 📊 4. Compare Models with PSIS-LOO via `arviz`

`bambi` models integrate directly with `arviz` for model comparison:

```python
import arviz as az

comparison = az.compare({
    "null": loo_null,
    "baseline": loo_baseline,
    "controls": loo_controls,
})
```

The output ranks models by expected log predictive density (ELPD), with standard errors — so you can say something like *"the controls model beats the null by 60 ELPD, well above its standard error of 17"* instead of eyeballing R².

---

## ⚖️ 5. Why Bother with Bayesian at All Here?

With weak priors and a moderately sized dataset, Bayesian and frequentist point estimates converge closely — so there's no accuracy advantage in this single analysis. The real payoff is twofold:

- **Communication**: a 94% credible interval is a direct probability statement about the parameter, which matches how clients already (mis)read confidence intervals anyway — so the Bayesian framing removes a predictable miscommunication rather than introducing a new one.
- **Reusability**: this posterior can become an *informative* prior for next year's data, or for a similar client in the same domain — something a one-off frequentist fit doesn't naturally give you.

---

## 📈 Key Takeaways

- Check the independence assumption (e.g. Durbin-Watson) before deciding you need mixed effects at all
- `bambi`'s formula syntax closely mirrors `{brms}` — including `(1|group)` — but expects pandas, not polars
- Build a ladder of models (null → baseline → controls → robustness variants) instead of one final model
- Use `az.compare()` (PSIS-LOO) to justify model choice quantitatively, not just by inspecting coefficients
- The case for Bayesian here isn't better point estimates — it's better client communication and reusable priors

## 🧠 Final Insight

> The value of going Bayesian wasn't in a better number — it was in a number I could hand to a client and trust they'd interpret correctly.