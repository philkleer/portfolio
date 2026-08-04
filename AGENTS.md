# Agent Instructions

> If a `CONTRIBUTING.md` exists at the project root, read it before starting any task.

## Environment

- Python version: see `.python-version`
- Package manager: `uv`. **Never** run `pip install` directly.
- Add packages: `uv add <package>`
- Sync environment: `uv sync`
- Run code: `uv run python main.py` — `main.py` is the **sole entry point**. Do not run scripts under `src/` directly.
- Run tests: `uv run pytest` (or check Makefile)

## Project Structure

```
.
├── data/
│   ├── bronze/         # Never modify files here
│   ├── silver/         # Processed data here
│   └── gold/           # finalized data for product here
├── docs/               # PDFs, notes, supplementary documents
├── output/             # Results, tables, figures
│   ├── diagnostics/    # Model diagnostics
│   ├── images/         # Figures and plots
│   └── models/         # Model files and results
├── src/
│   ├── python/         # Function definitions
│   ├── modules/        # Module definitions (if applicable)
│   └── project_name/   # Project package
├── tests/              # pytest tests
├── main.py             # Sole entry point
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── Makefile
└── .gitlab-ci.yml
```

### Commands — Check Makefile First

Before running any command manually, check if a `make` target exists.
**Do not modify** `Makefile`, `Dockerfile`, or `.gitlab-ci.yml` unless explicitly asked.
Common commands (if no Makefile target exists):

- Add dependency: `uv add <package>`
- Run: `uv run python main.py`
- Tests: `uv run pytest`
- Format: `uv run ruff format .`
- Lint: `uv run ruff check .`

## Secrets
- Secrets live in `.env` at the project root (gitignored). If absent, no secrets are needed.
- **Never hardcode credentials** in scripts or config files.
- Document new env vars in `.env.example`.
- If `.env` exists in the project root, load it with:

```python
from dotenv import load_dotenv

load_dotenv()
```
- Access secrets only via `os.getenv()`
---

## PRIMARY DIRECTIVE: Keep Each Step Simple

**Pipelines are fine. Complexity within steps is not.**

Each step in a data-processing workflow should do **ONE simple thing**. Do not write steps that transform many variables at once or contain deeply nested logic. Data manipulation **MUST** use Polars.

A 'simple thing' means:

- one conceptual operation (e.g. filtering rows, cleaning one variable, computing one feature group),
- not a full feature-engineering pipeline.

If you have different stages (e.g. cleaning, feature creation, aggregation), write them as **separate, readable steps**.

### ✅ GOOD: Simple, readable steps (Polars)

```python
import polars as pl

df = df.filter(pl.col('x') > 0)

df = df.with_columns(
    y_log=pl.col('x').log()
)

result = (
    df.group_by('group')
    .agg(pl.col('y_log').mean().alias('mean_y'))
)
```

### ❌ BAD: Complex transformations crammed into one step

```python
df = df.with_columns(
    outcome=(
        (pl.col('x').clip(lower_bound=0).log1p()
        - pl.col('x').log().mean())
        / pl.col('x').log().std()
        * pl.col('y').clip(
            lower_bound=pl.col('y').quantile(0.01),
            upper_bound=pl.col('y').quantile(0.99),
        ).log()
        + pl.col('z').replace({'low': 1, 'med': 2, 'high': 3})
    )
)
```

### ✅ GOOD: Break complex transformations into stages

```python
# Clean x
df = df.with_columns(
    x_clean=pl.when(pl.col('x') >= 0)
            .then(pl.col('x'))
            .otherwise(None),
    x_log=pl.when(pl.col('x') >= 0)
            .then(pl.col('x').log1p())
             .otherwise(None),
)

# Scale x (compute stats once)
x_stats = df.select(
    x_mean=pl.col('x_log').mean(),
    x_std=pl.col('x_log').std(),
).row(0)

df = df.with_columns(
    x_scaled=(pl.col('x_log') - x_stats[0]) / x_stats[1]]
)

# Winsorize y (compute bounds once)
y_bounds = df.select(
    y_low=pl.col('y').quantile(0.01),
    y_high=pl.col('y').quantile(0.99),
).row(0)

df = df.with_columns(
    y_clean=pl.col('y').clip(
        lower_bound=y_bounds[0], upper_bound=y_bounds[1]
    ),
    y_log=pl.col('y_clean').log(),
)
```

### When to add verification output

Add `df.shape`, `df.head()`, `df.describe()`, or explicit assertions after steps that:

- Filter rows (check how many remain)
- Merge / join data (check row counts)
- Create variables that could produce `NaN` / `inf`
- Involve non-trivial logic

---

## SECOND DIRECTIVE: Visualization (plotnine)

### Colorblind-Friendly Visualization

**ALL visualizations MUST use colorblind-friendly palettes.**

- Do NOT use plotnine defaults
- Do NOT use rainbow palettes
- Do NOT rely on implicit color cycling

Define and use an explicit palette:

```python
CB_PALETTE = [
    '#E69F00',  # Orange
    '#56B4E9',  # Light Blue
    '#009E73',  # Green
    '#D55E00',  # Vermillion
    '#F0E442',  # Yellow
    '#0072B2',  # Blue
    '#CC79A7',  # Pink
    '#970756',  # Magenta
    '#26EAE2',  # Teal
    '#C7AA55',  # Gold
    '#259585',  # Turquoise
    '#A64DE8',  # Purple
    '#A2D8FF',  # Pale Blue
]
```

Always apply it explicitly:

```python
from plotnine import (
    ggplot, aes, geom_point, scale_color_manual, theme_minimal
)

p = (
    ggplot(df, aes('x', 'y', color='group'))
    + geom_point()
    + scale_color_manual(values=CB_PALETTE)
    + theme_minimal()
)
```

---

## THIRD DIRECTIVE: Code Style

- Use `polars` for all data manipulation/wrangling (not pandas)
- Prefer vectorized operations over loops
- Use `snake_case` for variables and functions
- Keep lines ≤ 80 characters
- Never mutate global state implicitly
- Use explicit imports — **never** `import *`
- Set random seeds for reproducibility:
```python
import numpy as np
np.random.seed(12345)
```

---

## FOURTH DIRECTIVE: Console Output

1. Use `rich.console.Console` for all user-facing status output.

```python
from rich.console import Console

console = Console()
```

Message conventions:

- Start of a task: [bold blue]
- Intermediate process steps: [cyan]
- Success messages: [bold green]
- Error messages: [bold red]

Example:

```python
console.print(
    'Starting data processing ...', style='bold blue'
)

console.print('Loading source data ...', style='cyan')

console.print(
    'Pipeline completed successfully.',
    style='bold green'
)

console.print(
    'Failed to load input data.',
    style='bold red'
)
```

2. Use logging for persistent/system logs and rich.console for interactive CLI feedback.

3. Avoid excessive console output inside loops unless debugging.

---


## FIFTH DIRECTIVE: Script Structure

```python
'''
Title
Author: Philipp Kleer
Last change: 01/01/2026
'''

# Libraries --------------------------------------------------------------------
import polars as pl

# Graphics settings ------------------------------------------------------------
CB_PALETTE = [
    '#E69F00', '#56B4E9', '#009E73', '#D55E00', '#F0E442',
    '#0072B2', '#CC79A7', '#970756', '#26EAE2', '#C7AA55',
    '#259585', '#A64DE8', '#A2D8FF',
]

# Local functions --------------------------------------------------------------
# ... (defined here or imported from src/python/)

# Loading data -----------------------------------------------------------------
df = pl.read_csv('data/raw/datafile.csv')

print(df.shape)
print(df.head())

# Data manipulation ------------------------------------------------------------
# ...

# Analysis (step-by-step with verification) ------------------------------------
# import numpy as np
# np.random.seed(12345)

# ...
```

---

## SIXTH DIRECTIVE: Documentation

All non-trivial functions must have **Google-style docstrings**.

Required sections: `Args`, `Returns`, and at least one `Example`.
Include `Raises` when the function can raise exceptions.

```python
def calc_group_means(
    data: pl.DataFrame,
    outcome: str,
    group: str,
) -> pl.DataFrame:
    '''Calculate group means from a Polars DataFrame.

    Args:
        data: A Polars DataFrame containing the variables.
        outcome: Name of the outcome variable column.
        group: Name of the grouping variable column.

    Returns:
        A Polars DataFrame with group means and standard deviations.

    Raises:
        ValueError: If outcome or group are not columns in data.

    Example:
        >>> calc_group_means(df, outcome='score', group='cohort')
    '''
```

---

## SEVENTH DIRECTIVE: Testing

Write tests for any function longer than ~10 lines.

- Framework: `pytest`
- Run: `uv run pytest` (or check Makefile)
- Location: `tests/` with subfile `__init__.py` to start the tests and `conftest.py` for configurations and fixtures
- Any environment variables need to be mocked and included in `conftest.py`
- Include edge cases:
  - Empty inputs
  - Missing / null values
  - Single-row inputs

```python
def test_handles_empty_dataframe():
    with pytest.raises(ValueError, match='Data must have'):
        my_function(pl.DataFrame())

def test_handles_null_values():
    result = my_function(df_with_nulls)
    assert result['estimate'].is_null().sum() == 0
```

---

## EIGHT DIRECTIVE: Error Handling

- Validate inputs at function start
- Fail fast with informative messages that say what was expected AND what was received
- Catch external I/O and API errors explicitly
- Do NOT silence warnings without justification

```python
def my_function(data: pl.DataFrame, var: str) -> pl.DataFrame:
    if not isinstance(data, pl.DataFrame):
        raise TypeError(
            f'Expected pl.DataFrame, got {type(data).__name__}'
        )
    if data.is_empty():
        raise ValueError('data must not be empty')
    if var not in data.columns:
        raise ValueError(
            f'Column '{var}' not found. '
            f'Available columns: {data.columns}'
        )

    try:
        result = pl.read_csv('data/raw/file.csv')
    except Exception as e:
        raise RuntimeError(f'Failed to read data file: {e}') from e
```

---

## NINTH DIRECTIVE: Preferred Packages

Use these packages by default unless the project requirements dictate otherwise.

### Essential

`polars`, `pathlib`, `rich`, `pytest`, `dotenv`, `pydantic`,

### Machine Learning

`scikit-learn`, `xgboost`, `lightgbm`, `optuna`

### ML OPs

`mlflow`

### Visualization

`plotnine`, `plotly`, `matplotlib`, `patchworklib`,

### Spatial Analysis

`geopandas`, `shapely`, `libpysal`

### Database Handling

`sqlalchemy`, `psycopg`, `duckdb`, `connectorx`, `orjson`, `fastapi`

### Data Handling

`pyarrow` for large files and parquet datasets;
`polars` for tabular data processing

### Web Applications / Dashboards

`shinyexpress`, `shiny`,  `fastapi`

### Statistical Modeling

`statsmodels`, `linearmodels`, `bambi`, `pymc`

---

### Dependency Rules

- Minimize dependencies — prefer standard library or established ecosystem packages over niche libraries
- Prefer:
  - `pathlib` over `os.path`
  - `subprocess` over shell calls
  - `polars` over `pandas`
- If suggesting a new dependency, explicitly mention it:

```python
# uv add package_name
```

- Never import entire modules with `*`
- Prefer explicit imports:

```python
from pathlib import Path
```

instead of:

```python
import pathlib
```

- Avoid imports inside functions unless required for:
  - optional dependencies
  - performance reasons
  - circular import prevention

---

## Before Finishing Any Task

- Run formatter: `uv run ruff format .`
- Run linter: `uv run ruff check .`
- Run tests: `uv run pytest`
- Confirm the code would pass CI (lint + tests)

---

## Agent Compliance Checklist (Python, MANDATORY)

This checklist is **binding**.

Before responding, the agent MUST internally verify compliance with all applicable items below.

If a checklist item conflicts with:
1. Earlier conversation instructions, or
2. Default agent behavior,

**AGENTS.md takes precedence unless explicitly overridden by the user.**

Do not mention the checklist in the final response. If an item is not applicable, it may be skipped. Comply silently.

### 1. Response Behavior

- [ ] Provide complete, runnable code (no fragments)
- [ ] Explain reasoning before the code
- [ ] Show full functions/sections when modifying code
- [ ] Ask at most ONE clarifying question if requirements are unclear
- [ ] Match the existing code style exactly

### 2. Project & Entry Point

- [ ] `main.py` is the sole entry point — do not run `src/` scripts directly
- [ ] Use `uv run python main.py` to run the project
- [ ] Check Makefile before constructing any run/test/lint command
- [ ] Do not modify `Makefile`, `Dockerfile`, or `.gitlab-ci.yml` unless explicitly asked
- [ ] Secrets go in `.env` / `.env.example` — never hardcoded

### 3. Data Transformation

- [ ] Each step does ONE simple thing
- [ ] No complex multi-variable logic crammed into one step
- [ ] Transformations broken into conceptual stages
- [ ] Verification output (`df.shape`, `df.head()`, assertions) added after:
  - [ ] Filters
  - [ ] Joins / merges
  - [ ] NaN / inf–prone transformations
  - [ ] Complex logic

### 4. Code Style

- [ ] `polars` for all wrangling (not pandas)
- [ ] `snake_case` naming
- [ ] Explicit imports — no `import *`
- [ ] Lines ≤ 80 characters
- [ ] Seed set for reproducibility (`np.random.seed()`)
- [ ] No hidden global state mutations
- [ ] No silent refactors of unrelated code

### 5. Visualization

- [ ] Use `plotnine`
- [ ] `CB_PALETTE` applied explicitly
- [ ] No default plotnine colors, no rainbow palettes

### 6. Documentation

- [ ] Google-style docstrings on all non-trivial functions
- [ ] `Args`, `Returns`, `Raises` (if relevant), `Example` present

### 7. Testing & Error Handling

- [ ] `pytest` tests for functions > ~10 lines
- [ ] Tests cover empty input, nulls, edge cases
- [ ] Input validation at function start
- [ ] Informative error messages (expected vs received)
- [ ] try/except for external I/O or APIs

### 8. Project & Reproducibility

- [ ] `pyproject.toml` and `uv.lock` kept in sync
- [ ] Correct directory usage (`data/raw/` read-only, outputs to `output/`)
- [ ] Code runs from project root via `main.py`
- [ ] Seed set wherever randomness is involved

### 9. Modification Rules

- [ ] Preserve variable names and structure
- [ ] Do not refactor unrelated code silently
- [ ] Mention unrelated bugs — do not fix silently
- [ ] Follow AGENTS.md over default agent preferences