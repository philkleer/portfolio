# TIL: Translating UI Paradigms (iOS → React)

_Date: 2026-04-15_

## 🚀 Context

As a small side private project, I rebuilt a simple iOS-based Portuguese conjugation tool as a web application:

🔗 [https://conjugador-portugues.vercel.app](https://conjugador-portugues.vercel.app)
🔗 [https://github.com/philkleer/portuguese-conjugation-react](https://github.com/philkleer/portuguese-conjugation-react)

The goal was **not** to move into frontend development, but to understand how the same logic translates across different UI paradigms.

---

## 💡 What I Explored

### 1. Imperative → Declarative Thinking

In iOS-style development, UI updates are often:

* stateful
* event-driven
* explicitly controlled

In React, the approach is different:

* UI is a **function of state**
* rendering is **declarative**
* changes propagate automatically

👉 The challenge was not rewriting code, but **changing how I think about UI updates**.

---

### 2. Separating Logic from Presentation

The core problem (verb conjugation) is:

* deterministic
* rule-based
* independent of UI

Rebuilding the app forced a clearer separation:

* **pure logic layer** (conjugation rules)
* **UI layer** (components)

👉 This made the structure cleaner than in the original version.

---

### 3. Component-Based Design

Instead of one flow, the app becomes:

* small reusable components
* driven by props and state

👉 This naturally enforces modularity.

---

## 🧾 Key Takeaways

* The main difficulty was not syntax, but **mental models**
* Declarative UI simplifies many update patterns
* Rebuilding small tools is a great way to understand new paradigms
* Separating logic from UI improves maintainability — regardless of framework
* Learning a new framework is less about learning APIs  and more about understanding the underlying **paradigm shift**.
