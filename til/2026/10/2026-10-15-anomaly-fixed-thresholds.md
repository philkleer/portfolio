# TIL: Why Fixed Thresholds Fail at Detecting Unusually Fast Survey Completion

*Date: 2026-10-30*

Detecting unusually fast survey completion sounds straightforward: define a minimum duration and flag everything below it. During the development of a compliance scoring framework for trade marketing field operations, I learned why that approach can introduce systematic bias — and why even percentile-based thresholds need careful design.

The challenge was not simply identifying fast surveys. It was distinguishing genuinely unusual behavior from legitimate differences between survey types, workflows, and employees.

---

## 🔍 1. A Global Threshold Creates Unnecessary Bias

A naive approach might look like this:

```python
is_suspicious = time_spent < 60
```

But consider two surveys:

- **Survey A:** A short form with only a few questions.
- **Survey B:** A long form with multiple questions and photo requirements.

A completion time of 45 seconds might be entirely plausible for Survey A but highly unusual for Survey B.

The same issue occurs between manual and pre-automated workflows.

**Takeaway:** Before defining a threshold, determine whether the observations are actually comparable.

---

## 📊 2. Segment the Timing Distributions

Instead of estimating one global timing distribution, I explored more meaningful groupings:

- Survey type  
- Workflow mode  
- Employee behavior, where appropriate for validation

The idea is to compare an observation against a relevant reference population.

However, finer segmentation comes with a cost: smaller groups mean less reliable estimates.

This led to a practical hierarchy:

1. Use survey-type-specific timing distributions when sample-size requirements are met.
2. Otherwise, fall back to workflow-specific distributions.

For the scoring methodology, I used the following minimum requirements for survey-type-level assessment:

- At least 30 employees.
- More than 500 completed surveys.

These are implementation choices for this scoring framework, not universal statistical guarantees.

---

## ⚠️ 3. Percentiles Are Not Automatically Meaningful Thresholds

A tempting approach is to penalize every survey below P10:

```python
threshold = group["TIME_SPENT"].quantile(0.10)

group["is_fast"] = group["TIME_SPENT"] < threshold
```

The problem is that percentile-based thresholds always divide a distribution in a predefined way.

If completion times are tightly concentrated, the bottom 10% may differ from the rest by only a negligible amount.

If the distribution is wide, however, unusually short completion times may be much more informative.

This motivated a distribution-aware approach:

- Evaluate whether the timing distribution exhibits meaningful variation.
- Apply penalization only when the distribution is sufficiently wide.
- Avoid forcing a distinction where the observed differences are not operationally meaningful.

**Important:** Distribution width is a scoring heuristic, not proof of suspicious behavior. A wide distribution may also reflect legitimate differences in task complexity or working conditions.

---

## 🧪 4. Data Quality Comes Before Threshold Optimization

During the investigation, I found implausible combinations of response volume and completion time, including 165 answers recorded in 48 seconds.

I also identified 12 problematic survey forms for exclusion from the timing analysis.

This highlighted another important lesson: a sophisticated thresholding methodology cannot compensate for unreliable input data.

A practical workflow should include:

1. Validate timestamps and duration calculations.
2. Investigate impossible or implausible response volumes.
3. Identify problematic forms and automated completion behavior.
4. Establish a clean analytical baseline.
5. Recalculate timing distributions.
6. Validate the resulting scores against reviewed cases.

Exclusions should be documented and their effects assessed rather than applied simply because they improve the distributions.

---

## 📐 5. Separate Anomaly Detection From Score Calibration

An unusual completion time is not necessarily evidence of misconduct.

I would distinguish three stages:

1. **Anomaly detection:** Is this observation unusual relative to comparable behavior?
2. **Scoring:** How strongly should this deviation affect the compliance score?
3. **Validation:** Does the indicator actually distinguish relevant operational outcomes?

This separation makes the framework easier to interpret and prevents the scoring methodology from implicitly treating statistical rarity as wrongdoing.

---

## 📈 Key Takeaways

- A single global threshold can systematically disadvantage legitimate short surveys.
- Segment timing distributions by meaningful operational characteristics.
- Percentiles do not automatically define meaningful decision boundaries.
- Require sufficient observations before estimating granular distributions.
- Validate data quality before tuning thresholds.
- Anomaly scores are indicators for investigation, not evidence of misconduct.

## 🧠 Final Insight

> The hardest part of anomaly detection is often not finding what is unusual. It is defining what normal should mean in the first place.
