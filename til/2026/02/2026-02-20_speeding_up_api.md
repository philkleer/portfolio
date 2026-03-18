# TIL: Speeding Up a Plumber API by Switching from JSON to Parquet

_Date: 2026-02-20_

I built a small `{plumber}` API in R that exposes a dataset with ~500k rows.

The first version returned JSON — it worked, but it was **slow**.

---

## 🐢 Baseline: JSON Was Expensive

I measured the end-to-end time for the JSON workflow:

- fetch: **14.492 s**
- rawToChar: **0.308 s**
- fromJSON: **5.386 s**
- decode: **5.695 s**
- total: **20.199 s**
- HTTP status: **200**
- payload size: **187,565,338 bytes (~187 MB)**

The conclusion was clear:

✅ network transfer is large  
✅ JSON parsing is expensive  
✅ end-to-end latency becomes painful for repeated analysis

---

## 📊 Benchmark: JSON vs Parquet (Measured)

### JSON baseline (500k rows)

- fetch: **14.492 s**
- rawToChar: **0.308 s**
- fromJSON: **5.386 s**
- decode: **5.695 s**
- total: **20.199 s**
- payload size: **187,565,338 bytes (~187 MB)**

### Parquet + Arrow (same dataset)

- fetch: **5.263 s**
- write raw → file: **0.013 s**
- `arrow::read_parquet()`: **0.488 s**
- `as.data.frame()`: **0.001 s**
- total (sum): **5.765 s**
- payload size: **9,271,744 bytes (~9.3 MB)**

### Quick comparison

| Format         | Payload size | Total time | Main bottleneck         |
|----------------|-------------:|-----------:|-------------------------|
| JSON           |      ~187 MB |    ~20.2 s | download + JSON parsing |
| Parquet (zstd) |      ~9.3 MB |     ~5.8 s | mostly download         |

**Result:** Switching to Parquet reduced the payload size by ~20× and improved end-to-end latency by ~3.5×.


## ✅ The Fix: Return Parquet Instead of JSON

Instead of sending JSON, I changed the endpoint to:

- query PostgreSQL
- write a temporary **Parquet** file using `{arrow}`
- return the Parquet bytes (compressed with `zstd`)

This is the new API endpoint:

```r
#* Instalômetro - Establishments list (ALL Brazil) as Parquet
#*
#* @serializer contentType list(type="application/vnd.apache.parquet")
#* @get /v1/healthUnitsMonitoringStatusAll.parquet
function(res) {
  sql <- QUERY_PARQUET

  tryCatch(
    {
      df <- DBI::dbGetQuery(pool_postgres, sql)

      tf <- tempfile(fileext = ".parquet")
      on.exit(unlink(tf), add = TRUE)

      arrow::write_parquet(
        arrow::Table$create(df),
        sink = tf,
        compression = "zstd"
      )

      res$setHeader(
        "Content-Disposition",
        'inline; filename="healthUnitsMonitoringStatusAll.parquet"'
      )

      readBin(tf, "raw", n = file.info(tf)$size)
    },
    error = function(e) {
      res$status <- 500
      res$setHeader("Content-Type", "application/json; charset=utf-8")
      jsonlite::toJSON(
        list(error = "Internal Server Error", details = as.character(e)),
        auto_unbox = TRUE
      )
    }
  )
}
```

---

## 📥 Client-side: Fetching Raw Bytes in R

I also wrote a small helper that downloads raw bytes efficiently:

```r
get_raw_by_endpoint <- function(url, contenttype) {
  h <- curl::new_handle(failonerror = TRUE)
  curl::handle_setheaders(h, "Accept" = contenttype)
  resp <- curl::curl_fetch_memory(url, handle = h)
  resp$content
}
```

This lets me download Parquet in memory and then load it with Arrow / DuckDB / Polars.

---

## 💡 Why Parquet Helped

Compared to JSON, Parquet is:
- **columnar**
- **binary** (no text parsing)
- much easier to scan efficiently
- compresses well (especially with `zstd`)

It also enables downstream optimizations such as:
- selecting only needed columns
- filtering after download much faster than JSON parsing

---

## 🔍 What I’d Improve Next

This endpoint still returns *everything*, which is useful for bulk exports — but for repeated use I’d add optional query parameters, such as:

- `state=...`
- `region=...`
- `since=...&until=...`
- `columns=...`
- `limit=...`

That would allow:
- push-down filtering in PostgreSQL
- smaller payloads
- faster API response times

---

## ✅ Key Takeaways

- JSON is human-readable, but expensive at scale
- For big tables, Parquet exports are usually much faster
- `{plumber}` + `{arrow}` makes it straightforward to serve Parquet
- If the dataset is large, add filters/params to avoid _download everything_
