# TIL: Better GPS Coordinates Don't Automatically Mean Better Distance Estimates

*Date: 2026-10-30*

During the development of travel times, I investigated the quality of locations and GPS coordinates.

The initial problem appeared simple: some locations had missing or incorrect coordinates. But enriching the data with geocoding introduced another challenge: how do you decide whether a newly retrieved coordinate is actually better than the original one?

This note covers the data-quality workflow and why geospatial enrichment requires more than filling null values.

---

## 📍 1. Missing Coordinates Are Only One Part of the Problem

The original dataset contained several types of data-quality issues:

- Missing longitude/latitude
- Incomplete addresses
- Inconsistent postal codes
- Missing or unreliable address numbers
- Duplicate entries
- Incorrect or inconsistent GPS positions

Checking only coordinate completeness would miss many of these problems.

I therefore investigated address quality across these columns.

An address with valid-looking coordinates is not necessarily correct, and an incomplete address may still contain enough information for a reliable match.

**Takeaway:** Data completeness and data correctness are different dimensions of quality.

---

## 🧹 2. Normalize Addresses Before Matching

Address normalization can improve matching rates substantially.

For example:

```python
import re

def normalize_address(address: str) -> str:
    if not address:
        return ""

    address = address.strip().upper()

    address = re.sub(r"\bR\.", "RUA", address)
    address = re.sub(r"\bAV\.", "AVENIDA", address)

    # Illustrative only:
    # Remove apartment/block details only if they
    # are not required for the intended matching task.

    return address
```

In the actual data-cleaning workflow, I standardized street abbreviations and removed block/apartment information for address matching, pulled complements like `BLOCK 123` or similar and standardized address fields for planned cities.

However, normalization must preserve information that can distinguish locations.

For example, removing apartment information may be reasonable for matching a street-level location, but removing building or unit identifiers indiscriminately could merge distinct locations.

Additional checks included:

- City consistency
- State consistency
- Postal-code consistency
- Address-number agreement

**Takeaway:** Normalization should improve comparability without destroying identifying information.

---

## 🗺️ 3. Geocoding Is an Enrichment Source, Not Ground Truth

Using `{geocodebr}`, I explored recovering missing address components and retrieving alternative coordinates.

Examples included:

- Recovering city and state from ZIP code
- Recovering ZIP code from city and address (for larger cities)
- Retrieving alternative longitude/latitude coordinates

But a geocoder can return a plausible coordinate for an approximate address, street centroid, or ambiguous match.

Therefore, this is not necessarily a valid replacement:

```python
# Too simplistic
longitude = geocoded_longitude or original_longitude
latitude = geocoded_latitude or original_latitude
```

The presence of a coordinate does not tell us whether it is more accurate.

A better approach is to preserve both sources and evaluate their quality.

---

## 🔎 4. Coordinate Confidence Needs Explicit Rules

I implemented rules to decide whether to use original or geocoded coordinates and introduced address confidence into the ETL process.

A conceptual decision framework might look like this:

| Situation                                 | Possible treatment                                  |
|-------------------------------------------|-----------------------------------------------------|
| Original coordinates validated            | Retain original                                     |
| Original missing, geocoded match reliable | Use enriched coordinates                            |
| Sources disagree materially               | Flag for review or apply additional validation      |
| No usable address                         | Keep coordinates null                               |
| Ambiguous match                           | Retain uncertainty rather than assuming correctness |

This is an illustrative framework, not a complete description of every implemented matching rule.

One particularly important point is that coordinate confidence and address confidence are related but not identical.

A confidently matched address may still have imprecise coordinates.

---

## 📐 5. Coordinate Errors Propagate Into Distance Calculations

Suppose two consecutive locations are used to estimate travel distance.

A coordinate error at either location affects the estimated distance between them.

For example, if one location is incorrectly geocoded to another street, the resulting distance can become implausibly large or small.

That can propagate into:

- Travel-time estimates
- Route-level estimations

This is why I recalculated distances after adjusting the original data and compared results based on original and `{geocodebr}` coordinates.

Useful validation checks include:

- Distribution of distances before and after enrichment
- Maximum and extreme distances
- Number of affected routes
- Differences by confidence level
- Cases with changes large enough to affect scoring

A change in distance is not automatically an improvement. It needs to be interpreted against the quality of the underlying match.

---

## 🧪 6. Data Quality Should Be Measurable and Reproducible

The cleaning workflow also included indicators such as `DATA_QUALITY` and `FLAG_AFTER`, allowing address completeness to be compared before and after processing.

A robust data-quality pipeline should retain:

- Original values
- Cleaned values
- Enriched values
- Source of the selected coordinates
- Matching confidence
- Reason for selection or rejection
- Before/after quality indicators

This enables the downstream scoring pipeline to use the improved data while preserving traceability.

It also creates the foundation for a reusable data-quality product rather than a one-off cleaning exercise.

---

## 📈 Key Takeaways

- Completeness does not imply correctness
- Normalize addresses carefully before matching
- Geocoded coordinates are candidate values, not ground truth
- Preserve original and enriched values for validation
- Coordinate confidence and address confidence should not be conflated
- Measure how data-quality improvements affect downstream distance calculations
- Uncertainty should be retained rather than hidden by automatic filling

## 🧠 Final Insight

> Geospatial data cleaning is not about maximizing the number of coordinates. It is about maximizing the number of coordinates you can reasonably trust.
