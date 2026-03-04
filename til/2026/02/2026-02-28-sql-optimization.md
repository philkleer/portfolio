# Refactoring a 200-Line SQL Query: Less CTEs, Fewer Scans
_Date: 2026-02-28_

While reviewing a colleague's query recently, I found a great real-world example of a query that *looks* well-structured — and partially is — but hides several silent performance killers. Here's what I learned.

---

## Query Plan Difference

### Original query:

- repeated scans of `agents`
- extra hash aggregates
- unnecessary materialization

### Optimized query:

- single aggregation pass
- fewer joins
- simpler plan tree

## The Original Query

The query aggregates data from a `facilities` monitoring system: it joins agents installed at each facility, their network measurements, and geographic metadata to produce a status dashboard.

```sql
WITH
-- Get the most recently active agent per facility
agente_atual AS (
  SELECT DISTINCT ON (a.facility_id)
    a.facility_id,
    a.agent_id,
    a.install_date,
    a.update_date,
    a.env_version,
    a.engine_version,
    a.env_name,
    a.type
  FROM agents a
  ORDER BY
    a.facility_id,
    (COALESCE(a.update_date, a.install_date)) DESC,
    a.agent_id DESC
),

-- Aggregate measurements per agent
agg_medicoes_por_agente AS (
  SELECT
    m.agent_id,
    max(m."time") AS ultima_medicao,
    count(*) AS total_medicoes
  FROM measurements m
  GROUP BY m.agent_id
),

-- Then re-aggregate measurements per facility
agg_medicoes_por_cnes AS (
  SELECT
    ha.facility_id,
    max(ma.ultima_medicao) AS ultima_medicao,
    sum(ma.total_medicoes)::bigint AS total_medicoes
  FROM agents ha
  JOIN agg_medicoes_por_agente ma
    -- ⚠️ type cast on join key
    -- ⚠️ this needs to be corrected in the schema and will give further improvement due to use of index
    ON ma.agent_id::text = ha.agent_id::text  
  GROUP BY ha.facility_id
),

-- Step 1 of 5: filter out a specific agent type
excluindo_v AS (
  SELECT
    ha.agent_id,
    ha.facility_id,
    ha.install_date,
    ha.update_date,
    ha.env_version,
    ha.engine_version,
    ha.env_name,
    ha.type,
    split_part(ha.engine_version::text, 'v', 2) AS engine_version_v
  FROM agents ha
  WHERE ha.type <> 'legacy_web'
),

-- Step 2 of 5: split version string into parts
separando AS (
  SELECT
    e.*,
    split_part(e.engine_version_v, '.', 1) AS top_level_version,
    split_part(e.engine_version_v, '.', 2) AS second_level_version,
    split_part(e.engine_version_v, '.', 3) AS third_level_version,
    split_part(e.engine_version_v, '.', 4) AS fourth_level_version
  FROM excluindo_v e
),

-- Step 3 of 5: zero-pad parts for sorting
colocando_zeros AS (
  SELECT
    s.facility_id,
    s.agent_id,
    s.engine_version_v,
    s.top_level_version,
    lpad(s.second_level_version, 2, '0') AS second_level_version,
    lpad(s.third_level_version, 2, '0')  AS third_level_version,
    s.fourth_level_version
  FROM separando s
),

-- Step 4 of 5: reconstruct version string, ORDER BY does nothing here
agents_version_final AS (
  SELECT
    cz.agent_id,
    concat_ws('.', cz.top_level_version, cz.second_level_version,
                   cz.third_level_version, cz.fourth_level_version) AS agent_version
  FROM colocando_zeros cz
  ORDER BY -- ⚠️ useless: CTEs are not ordered sets
    concat_ws('.', cz.top_level_version, cz.second_level_version,
                   cz.third_level_version, cz.fourth_level_version) DESC
),

-- Step 5 of 5: join back to agents
health_agents_alt AS (
  SELECT
    ha.agent_id,
    ha.facility_id,
    ha.install_date,
    ha.update_date,
    ha.env_version,
    ha.engine_version,
    ha.env_name,
    ha.type,
    avf.agent_version
  FROM agents ha
  LEFT JOIN agents_version_final avf USING (agent_id)
),

-- Rank agents per facility by update_date + version
medidor_recente AS (
  SELECT
    haa.facility_id,
    nm.agent_id,
    haa.install_date,
    haa.update_date,
    haa.agent_version,
    max(nm."time") AS last_measure,
    row_number() OVER (
      PARTITION BY haa.facility_id
      ORDER BY (ROW(haa.update_date, haa.agent_version)) DESC
    ) AS rnk
  FROM measurements nm
  LEFT JOIN health_agents_alt haa USING (agent_id)
  WHERE haa.type <> 'legacy_web'
  GROUP BY haa.facility_id, nm.agent_id, haa.install_date, haa.update_date, haa.agent_version
),

medidor_recente_filtro AS (
  SELECT mr.facility_id, mr.agent_id, mr.agent_version, mr.update_date
  FROM medidor_recente mr
  WHERE mr.rnk = 1
),

-- Full measurement aggregation per facility
medicoes AS (
  SELECT
    ha.facility_id,
    count(DISTINCT nm.agent_id) AS num_agents,
    array_agg(DISTINCT nm.agent_id) AS agentid_list,
    min(ha.install_date) AS first_install_date,
    max(ha.install_date) AS most_recent_install_date,
    count(*) AS num_measures,
    array_agg(DISTINCT nm.asn) AS asn_list,
    min(nm."time") AS first_measure,
    max(nm."time") AS last_measure,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.tcp_down_median_mbps::double precision) AS tcp_median_down_mbps,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.tcp_up_median_mbps::double precision) AS tcp_median_up_mbps,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.rtt_median_ms::double precision) AS rtt_median_ms,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.rtt_lost_package_pct::double precision) AS rtt_median_lost_pct,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.jitter_download_ms::double precision) AS jitter_median_download_ms,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.jitter_upload_ms::double precision) AS jitter_median_upload_ms,
    max(nm.tcp_down_median_mbps) AS download_max,
    max(nm.tcp_up_median_mbps) AS upload_max,
    percentile_disc(0.95) WITHIN GROUP (ORDER BY nm.tcp_down_median_mbps) AS download_95_percentil,
    percentile_disc(0.95) WITHIN GROUP (ORDER BY nm.tcp_up_median_mbps) AS upload_95_percentil,
    CASE
      WHEN max(ha.install_date) IS NOT NULL AND max(nm."time") IS NULL THEN 'inactive'
      WHEN max(ha.install_date) IS NOT NULL AND max(nm."time") >= now() - interval '7 days' THEN 'active'
      ELSE 'disabled'
    END AS status
  FROM measurements nm
  LEFT JOIN agents ha USING (agent_id)
  WHERE ha.type <> 'legacy_web'
  GROUP BY ha.facility_id
),

-- ⚠️ This CTE does nothing but pass data through
la AS (
  SELECT m.*, mrf.agent_id, mrf.agent_version, mrf.update_date
  FROM medicoes m
  LEFT JOIN medidor_recente_filtro mrf USING (facility_id)
)

SELECT
  h.facility_id,
  h.state_code,
  h.municipality_code,
  hug.ibge_municipality_code,
  hug.municipality_name,
  hug.uf AS sg_uf,
  hug.region_code,
  hug.region_name,
  h.trade_name AS nome,
  COALESCE(NULLIF(h.unit_type_name::text, ''), h.establishment_type_name::text) AS tipo,
  CASE
    WHEN h.facility_type_code::text = ANY (ARRAY['1','2','15','71']::text[]) THEN 'Basic Health Unit'
    ELSE 'Other'
  END AS facility_group,
  h.management_code,
  CASE WHEN aa.agent_id IS NOT NULL THEN 'Installed' ELSE NULL END AS installation,
  h.internet,
  aa.install_date,
  mc.ultima_medicao,
  COALESCE(mc.total_medicoes, 0::bigint) AS total_measures,
  CASE
    WHEN aa.agent_id IS NULL THEN 'not installed'
    WHEN aa.install_date IS NOT NULL AND mc.ultima_medicao IS NULL THEN 'inactive'
    WHEN aa.install_date IS NOT NULL AND mc.ultima_medicao >= now() - interval '7 days' THEN 'active'
    ELSE 'disabled'
  END AS status,
  round(la.tcp_median_down_mbps::numeric, 2) AS tcp_median_down_mbps,
  round(la.tcp_median_up_mbps::numeric, 2) AS tcp_median_up_mbps,
  round(la.rtt_median_ms::numeric, 2) AS rtt_median_ms,
  round(la.rtt_median_lost_pct::numeric, 2) AS rtt_median_lost_pct,
  round(la.jitter_median_download_ms::numeric, 2) AS jitter_median_download_ms,
  round(la.jitter_median_upload_ms::numeric, 2) AS jitter_median_upload_ms,
  round(la.download_95_percentil::numeric, 2) AS download_95_percentil,
  round(la.upload_95_percentil::numeric, 2) AS upload_95_percentil,
  la.first_install_date,
  la.most_recent_install_date,
  la.first_measure,
  la.last_measure,
  la.num_measures,
  de.geo_ref_latitude,
  de.geo_ref_longitude,
  de.source_georef,
  de.last_update AS geo_last_update
FROM facilities h
LEFT JOIN agente_atual aa ON aa.facility_id = h.facility_id
LEFT JOIN agg_medicoes_por_cnes mc ON mc.facility_id = h.facility_id
LEFT JOIN facilities_geo hug ON hug.facility_id = h.facility_id
LEFT JOIN la ON la.agent_id::text = aa.agent_id::text  -- ⚠️ type cast again
LEFT JOIN geo_enrichment de ON de.facility_id = h.facility_id
WHERE aa.agent_id IS NOT NULL
  AND h.facility_type_code IN ('1','2','15','71');
```

---

## What's Good

Before diving into problems, credit where it's due:

- **CTEs for readability.** Breaking complex logic into named steps is far better than nested subqueries. Each block has a clear, single purpose.
- **`DISTINCT ON` in `agente_atual`** is an efficient PostgreSQL idiom for "latest record per group" — cleaner and often faster than `ROW_NUMBER()` for this use case.
- **The final `WHERE` clause is tight.** Filtering on `agent_id IS NOT NULL` and `facility_type_code` at the end keeps the result set focused.

---

## The Pitfalls

### 1. Five CTEs to format a version string

`excluindo_v → separando → colocando_zeros → agents_version_final → health_agents_alt` — five steps, five table scans of `agents`, all to zero-pad a version string like `1.2.3.4` into `1.02.03.4`. This entire pipeline can be a single expression.

### 2. `agents` is scanned five or more times

That same table appears across `agente_atual`, `excluindo_v`, `agg_medicoes_por_cnes`, `medidor_recente`, and `medicoes`. In PostgreSQL, CTEs are optimization fences in older versions (pre-14), meaning the planner may materialize each one independently rather than folding them together.

### 3. Two aggregation CTEs where one would do

`agg_medicoes_por_agente` aggregates by `agent_id`, and then `agg_medicoes_por_cnes` re-aggregates that result by `facility_id`. This is two full passes over `measurements` when one join would suffice.

### 4. `la` is a no-op CTE

The `la` CTE does nothing except `SELECT *` from `medicoes` and join `medidor_recente_filtro`. It adds a named step with zero logic — it can be eliminated entirely by inlining the join.

### 5. `ORDER BY` inside a CTE is meaningless

```sql
-- Inside agents_version_final:
ORDER BY concat_ws(...) DESC  -- does nothing
```

CTEs are not ordered sets. This `ORDER BY` is silently ignored by the planner unless the CTE is used in a context that respects order (e.g., inside `LIMIT`). It wastes parse and planning time.

### 6. Casting both sides of a join key blocks index usage

```sql
ON ma.agent_id::text = ha.agent_id::text
```

If `agent_id` is `uuid` in one table and `text` in another, the planner cannot use an index on either column — it has to evaluate the cast for every row. This is a schema inconsistency being patched at query time, which is the wrong layer to fix it.

---

## The Optimized Query

The key changes:
- Collapse the 5-CTE version pipeline into a single expression using `CASE`/inline `concat_ws`
- Combine the two measurement aggregation CTEs into one direct join
- Remove the `la` pass-through CTE
- Remove the pointless `ORDER BY` in the version CTE
- Fix the join key cast (noted inline — ideally fixed at schema level)

```sql
WITH
-- Most recent agent per facility
current_agent AS (
  SELECT DISTINCT ON (a.facility_id)
    a.facility_id,
    a.agent_id,
    a.install_date,
    a.update_date,
    a.env_version,
    a.engine_version,
    a.env_name,
    a.type,
    -- ✅ Entire version formatting in one expression
    concat_ws('.',
      split_part(split_part(a.engine_version::text, 'v', 2), '.', 1),
      lpad(split_part(split_part(a.engine_version::text, 'v', 2), '.', 2), 2, '0'),
      lpad(split_part(split_part(a.engine_version::text, 'v', 2), '.', 3), 2, '0'),
      split_part(split_part(a.engine_version::text, 'v', 2), '.', 4)
    ) AS agent_version
  FROM agents a
  WHERE a.type <> 'legacy_web'
  ORDER BY
    a.facility_id,
    COALESCE(a.update_date, a.install_date) DESC,
    a.agent_id DESC
),

-- ✅ Single aggregation pass over measurements, directly by facility
facility_measurements AS (
  SELECT
    ha.facility_id,
    count(DISTINCT nm.agent_id) AS num_agents,
    array_agg(DISTINCT nm.agent_id) AS agentid_list,
    min(ha.install_date) AS first_install_date,
    max(ha.install_date) AS most_recent_install_date,
    count(*) AS num_measures,
    array_agg(DISTINCT nm.asn) AS asn_list,
    min(nm."time") AS first_measure,
    max(nm."time") AS last_measure,
    max(nm."time") AS ultima_medicao,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.tcp_down_median_mbps::double precision) AS tcp_median_down_mbps,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.tcp_up_median_mbps::double precision) AS tcp_median_up_mbps,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.rtt_median_ms::double precision) AS rtt_median_ms,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.rtt_lost_package_pct::double precision) AS rtt_median_lost_pct,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.jitter_download_ms::double precision) AS jitter_median_download_ms,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY nm.jitter_upload_ms::double precision) AS jitter_median_upload_ms,
    max(nm.tcp_down_median_mbps) AS download_max,
    max(nm.tcp_up_median_mbps) AS upload_max,
    percentile_disc(0.95) WITHIN GROUP (ORDER BY nm.tcp_down_median_mbps) AS download_95_percentil,
    percentile_disc(0.95) WITHIN GROUP (ORDER BY nm.tcp_up_median_mbps) AS upload_95_percentil
  FROM measurements nm
  JOIN agents ha USING (agent_id)   -- ✅ INNER JOIN: we only want agents that have measurements
  WHERE ha.type <> 'legacy_web'
  GROUP BY ha.facility_id
),

-- Most recent agent per facility (by update_date + version), with its last measurement
most_recent_active_agent AS (
  SELECT DISTINCT ON (ca.facility_id)
    ca.facility_id,
    ca.agent_id,
    ca.agent_version,
    ca.update_date,
    max(nm."time") OVER (PARTITION BY ca.facility_id) AS last_measure
  FROM current_agent ca
  JOIN measurements nm ON nm.agent_id = ca.agent_id  -- ✅ no cast needed if types match
  ORDER BY
    ca.facility_id,
    ca.update_date DESC,
    ca.agent_version DESC
)

SELECT
  h.facility_id,
  h.state_code,
  h.municipality_code,
  hug.ibge_municipality_code,
  hug.municipality_name,
  hug.uf AS sg_uf,
  hug.region_code,
  hug.region_name,
  h.trade_name AS nome,
  COALESCE(NULLIF(h.unit_type_name::text, ''), h.establishment_type_name::text) AS tipo,
  CASE
    WHEN h.facility_type_code = ANY (ARRAY['1','2','15','71']) THEN 'Basic Health Unit'
    ELSE 'Other'
  END AS facility_group,
  h.management_code,
  'Installed' AS installation,
  h.internet,
  ca.install_date,
  fm.ultima_medicao,
  COALESCE(fm.num_measures, 0) AS total_measures,
  CASE
    WHEN fm.ultima_medicao IS NULL THEN 'inactive'
    WHEN fm.ultima_medicao >= now() - interval '7 days' THEN 'active'
    ELSE 'disabled'
  END AS status,
  round(fm.tcp_median_down_mbps::numeric, 2) AS tcp_median_down_mbps,
  round(fm.tcp_median_up_mbps::numeric, 2) AS tcp_median_up_mbps,
  round(fm.rtt_median_ms::numeric, 2) AS rtt_median_ms,
  round(fm.rtt_median_lost_pct::numeric, 2) AS rtt_median_lost_pct,
  round(fm.jitter_median_download_ms::numeric, 2) AS jitter_median_download_ms,
  round(fm.jitter_median_upload_ms::numeric, 2) AS jitter_median_upload_ms,
  round(fm.download_95_percentil::numeric, 2) AS download_95_percentil,
  round(fm.upload_95_percentil::numeric, 2) AS upload_95_percentil,
  fm.first_install_date,
  fm.most_recent_install_date,
  fm.first_measure,
  fm.last_measure,
  fm.num_measures,
  de.geo_ref_latitude,
  de.geo_ref_longitude,
  de.source_georef,
  de.last_update AS geo_last_update
FROM facilities h
JOIN current_agent ca  ON ca.facility_id  = h.facility_id   -- ✅ INNER: WHERE aa.agent_id IS NOT NULL becomes a JOIN
LEFT JOIN facility_measurements fm  ON fm.facility_id  = h.facility_id
LEFT JOIN facilities_geo  hug ON hug.facility_id = h.facility_id
LEFT JOIN most_recent_active_agent mraa ON mraa.facility_id = h.facility_id
LEFT JOIN geo_enrichment  de  ON de.facility_id  = h.facility_id
WHERE h.facility_type_code = ANY (ARRAY['1','2','15','71']);
```

---

## Summary Table

| Issue                     | Original                  | Optimized                    |
|---------------------------|---------------------------|------------------------------|
| Version formatting        | 5 CTEs, 3+ table scans    | 1 inline expression          |
| Measurement aggregation   | 2 CTEs (agent → facility) | 1 CTE (direct to facility)   |
| Pass-through CTE (`la`)   | Present                   | Removed                      |
| Useless `ORDER BY` in CTE | Present                   | Removed                      |
| Join key type cast        | `::text` on both sides    | Native types (fix at schema) |
| `WHERE agent IS NOT NULL` | Post-join filter          | Promoted to `INNER JOIN`     |
| `agents` table scans      | 5+                        | 2                            |


The performance improvement is moderate (2.069s → 1.448s, ~30% faster), but the main benefit is structural:

- fewer scans of the same tables
- simpler query plan
- easier to maintain and reason about
- avoids planner pitfalls (type casts, useless `ORDER BY`)

These improvements become more important as the dataset grows.
