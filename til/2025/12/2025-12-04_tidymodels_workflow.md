# TIL: Building Machine Learning workflows in R with {tidymodels}
_Date: 2025-12-04_

I'm more trained in conducting ML algorithms in Python than in R, however, in my new time the main language is R. Hence, I started to get to know to `tidymodels` and learned how to create a **complete, scalable Machine Learning workflow** in R using the **{tidymodels}** ecosystem — including `{recipes}`, `{workflows}`, `{tune}`, and `{workflowsets}`.

Coming from a Python background, I wanted to explore how R’s modular approach can be used to streamline model building, tuning, and validation — all within a reproducible, declarative pipeline.

## 🚀 Goal

Design a clean, reproducible workflow that:

1. Preprocesses data consistently (`recipes`)
2. Defines models with flexible hyperparameters (`parsnip`)
3. Combines preprocessing + models into workflows (`workflows`)
4. Automates hyperparameter tuning (`tune`, `dials`)
5. Compares multiple workflows (`workflowsets`)
6. Evaluates model performance (`yardstick`)

## 🧩 Core Idea: Workflows + Workflow Sets

The `{workflowsets}` package is a *game changer* — it lets you define and evaluate multiple model-preprocessing combinations with very little extra code.

```r
# Preprocessing recipes
recipe_norm <- recipe(class ~ ., data = traindf) |>
  step_range(all_numeric_predictors())

recipe_pca <- recipe(class ~ ., data = traindf) |>
  step_normalize(all_numeric_predictors()) |>
  step_pca(num_comp = 10)

# Model specifications
rf_spec <- rand_forest(mtry = tune(), min_n = tune(), trees = 500) |>
  set_engine("ranger") |>
  set_mode("classification")

svm_spec <- svm_rbf(cost = tune(), rbf_sigma = tune()) |>
  set_engine("kernlab") |>
  set_mode("classification")

# Combine into workflow sets
wf_set <- workflow_set(
  preproc = list(normalized = recipe_norm, pca = recipe_pca),
  models  = list(RF = rf_spec, SVM = svm_spec)
)
```

Once the set is defined, you can **tune, resample, and compare** everything in a consistent and parallelized way:

```r
grid_ctrl <- control_grid(
  verbose = TRUE,
  save_pred = TRUE,
  parallel_over = "everything"
)

grid_results <- wf_set |>
  workflow_map(
    seed = 42,
    resamples = vfold_cv(traindf, v = 10, strata = class),
    grid = 10,
    metrics = metric_set(accuracy, f_meas),
    control = grid_ctrl
  )
```

## 📊 Visualization and Evaluation

```r
autoplot(
  grid_results,
  rank_metric = "f_meas",
  metric = "f_meas",
  select_best = TRUE
) +
  geom_text(aes(y = mean - .01, label = wflow_id), angle = 90, hjust = 1) +
  lims(y = c(0.6, 1.0)) +
  theme(legend.position = "none")
```

Extracting and training the best model:

```r
best_rf <- grid_results |>
  extract_workflow_set_result("normalized_RF") |>
  select_best(metric = "f_meas")

final_rf <- grid_results |>
  extract_workflow(id = "normalized_RF") |>
  finalize_workflow(best_rf) |>
  fit(data = traindf)
```

## 💡 Key Takeaways

- **Modular thinking** with `{tidymodels}` mirrors good software design — everything is composable and testable.
- `{workflowsets}` makes model comparison clean, scalable, and reproducible.
- You can go from *raw data → tuning → evaluation → deployment* in a single ecosystem.
- Parallelization (`doFuture`) + clean metrics (`yardstick`) = professional-grade experimentation workflow.

## 🔍 Next Steps

- Explore **ensemble models** using `{stacks}`.
- Integrate this setup into automated reports via `{quarto}` or `{gt}`.
- Experiment with workflowsets for spatial data modelling.
