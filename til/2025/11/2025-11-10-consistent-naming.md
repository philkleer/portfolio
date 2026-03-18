# TIL: Consistent naming across stack layers improves maintainability
_Date: 2025-11-10_

By aligning naming conventions across the **portal → API → database** layers of a project for a Shiny application (portal), I removed unnecessary complexity in the data flow.

Restructuring the SQL schema and API endpoints to mirror the object names used in the R code reduced translation steps, simplified caching logic, and made debugging easier.

Consistency in naming not only improves readability but also creates a shared mental model across the entire stack — from UI to database.

**Key takeaway:** keep data objects conceptually and linguistically consistent across layers to minimize friction when maintaining or extending an app.
