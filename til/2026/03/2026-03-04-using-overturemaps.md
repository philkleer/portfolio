# TIL: Using Overture Maps instead of raw OSM for scalable network analysis

_Date: 2026-03-04_

While working on routing fiber networks across municipalities, I moved from a traditional **OpenStreetMap (OSM) + custom segmentation workflow** to using **Overture Maps via `{city2graph}`**.

This significantly simplified the pipeline and made it easier to scale to new cities.

---

## 🚧 The Problem with Raw OSM Workflows

Using OSM directly often required:

- heavy **post-processing / segmentation**
- manual handling of **topology issues** (dangling edges, misaligned nodes)
- limited or inconsistent metadata (e.g. bridges, tunnels, restrictions)
- fragile pipelines when scaling to new municipalities

In practice, a lot of time was spent **cleaning the network** before even starting analysis.

---

## 🗺️ The New Approach: Overture Maps + `{city2graph}`

Instead of starting from raw OSM, I now:

1. Load structured Overture data:

```python
data = c2g.load_overture_data(
    place_name="Recife, Brazil",
    types=["segment", "connector", "building", "water", "land_use", "infrastructure"],
    save_to_file=True
)
```

2. Process segments into a clean graph:

```python
segments_processed = c2g.process_overture_segments(
    segments_gdf,
    connectors_gdf=connectors_gdf,
    threshold=1.0,
    get_barriers=True
)
```

3. Build a routable graph:

```python
nodes, edges = public_to_public_graph(segments_processed)
```

4. Enrich edges with domain-specific logic (fiber difficulty):

```python
segments_processed["difficulty"] = segments_processed.apply(compute_difficulty, axis=1)
```

5. Run routing using NetworkX:

```python
nx.shortest_path(G, source, target, weight="difficulty")
```

---

## ⚡ Why Overture Maps Works Better

### 1. Clean topology out of the box

- structured segments + connectors  
- graph-ready geometry  

---

### 2. Rich semantic attributes

- road flags (bridge, tunnel, indoor, construction)  
- consistent classification  

---

### 3. Built-in graph preparation

- snapping  
- connectors  
- barrier extraction  

---

### 4. Easier scaling

Change only:

```python
place_name="Recife, Brazil"
```

---

### 5. Better spatial modeling

```python
crosses_water = water_gdf.intersects(row.geometry).any()
```

---

## 📈 Impact

- less preprocessing  
- more robust pipelines  
- easier scaling  
- focus on modeling instead of cleaning  

---

## 🧾 Key Takeaways

- OSM → flexible but messy  
- Overture → structured and scalable  
- `{city2graph}` → fast graph workflows  
