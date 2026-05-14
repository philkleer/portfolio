# TIL: Debugging a 9s Shiny Startup — When the Problem Was Kubernetes, Not R

_Date: 2026-04-14_  

---

## 🚀 Context

I spent several days optimizing a **slow Shiny application startup**.

Initial symptom:
- ⏱️ ~9 seconds until the user sees the app

Given prior experience, I assumed the issue was:
- API latency  
- database queries  
- data transfer  

So I started investigating there.

---

## 🔍 Investigation Process

### Step 1: API & Load Testing
- Used K6 to simulate real frontend behavior  
- Measured endpoint latency (p95, avg)  
- Identified server-side waiting time as dominant  

👉 Conclusion: Backend processing matters — but not enough to explain startup delay.

---

### Step 2: Server-Side Instrumentation
- Added detailed timing logs (parse, SQL, DB, total)  
- Confirmed:
  - SQL building negligible  
  - DB time proportional to row count  
  - transfer cost exists (~2µs per row)

👉 Insight: Large datasets slow responses — but still not root cause of startup delay.

---

### Step 3: Data & Pipeline Optimizations

Tried:
- loading data page-wise instead of at startup (small batches of data and not all at once) 
- reducing initial data load  

👉 Result: Improvements — but startup still too slow.

---

## ❗ The Breakthrough

The issue was not in:
- R  
- API  
- database  

👉 It was **cold start behavior in Kubernetes**

Every time a user accessed the app:
- the container started  
- R session initialized  
- Shiny app booted  

➡️ The user waited for all of this.

---

## ⚙️ The Fix

I added a **lifecycle hook** to warm up the container:

```yaml
lifecycle:
  postStart:
    exec:
      command:
        ["/bin/sh", "-c", "curl -s http://localhost:3856/ || true"]
```

👉 This triggers a request when the pod starts → R initializes immediately.

---

## 📊 Before vs After

```
Before (cold start on user request)
---------------------------------
User → Request
       ↓
   Start container
       ↓
   Initialize R
       ↓
   Load Shiny app
       ↓
   Render UI
       ↓
   Response (~9s)

After (pre-warmed container)
---------------------------
Pod starts
   ↓
Lifecycle hook triggers request
   ↓
R initializes in background
   ↓
User → Request
       ↓
App already warm
       ↓
Response (~2.4s)
```

---

## ⏱️ Impact

- ⏱️ 9.0s → 2.4s startup time  
- 🚀 ~73% improvement  
- 🎯 Better user experience immediately  

---

## 🧪 Timeline of Hypotheses

```
Day 1: API is slow → test with K6
Day 2: DB is bottleneck → add instrumentation
Day 3: Data transfer too large → optimize loading
Day 4: 🤯 Real issue = container cold start
```

---

## 🧾 Key Takeaways

- Performance issues are often **not where you expect them**
- Always separate:
  - compute time  
  - data transfer  
  - infrastructure behavior  
- Cold starts in containerized environments can dominate latency
- Small infrastructure changes can outperform complex code optimizations

---

## 🧠 Final Insight

> You don’t optimize performance by guessing —  
> you optimize it by systematically eliminating wrong hypotheses.

---

## 🔥 Why This Matters

This exercise demonstrates:
- structured debugging  
- cross-layer thinking (R, DB, Kubernetes)  
- ability to identify root causes beyond code  

👉 Real-world performance engineering.

