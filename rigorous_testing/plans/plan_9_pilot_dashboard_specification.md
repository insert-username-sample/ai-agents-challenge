# IMPLEMENTATION PLAN 9: PILOT ADVOCATE DASHBOARD SPECIFICATION (v0.0.0.1 ALPHA)

---

## 1. Objective & Interactive Workspaces

This plan specifies the user interface and data visualization modules for Clausely's **paid pilot phase (50-500 advocates)**.

```
 [Pilot Advocate Brief] ──> [Interactive Sidebar] ──> [Telemetry db Buffer]
                                                                │
                                                                ▼
                                                     [Central developer Sync]
```

To capture high-quality training signals, the dashboard must render clear, actionable feedback options without disrupting the advocate's drafting workflow.

---

## 2. Interface Layout & Components

### 1. The Dynamic Generation Viewport
*   Renders the compiled Legal AST document drafts.
*   Integrates interactive, red-bordered **Grounding Warning Banners** whenever Mediator Melaquera triggers prior overrides or clocks mismatch corrections.

### 2. The Pilot Feedback Sidebar
*   **Action Toggles**:
    *   `[Accept Draft]`: Marks the generated brief as ground-truth court-ready.
    *   `[Edit Clause]`: Opens a side-by-side comparative editor.
    *   `[Report Objections]`: A dropdown checklist logging court counter rejection sheets (Registry stamp errors, formatting objections).

### 3. The Local Telemetry SQLite Logger
*   Saves interaction logs locally inside `telemetry_buffer.db` to protect client privacy before syncing anonymized preference pairs.

---

## 3. Telemetry Event Registry

| Event Key | Trigger | Telemetry Value | Target Database Table |
|---|---|---|---|
| `CLAUSE_ACCEPT` | Lawyer accepts draft without modification. | `+1.0` | `accepted_clauses` |
| `CLAUSE_EDIT` | Lawyer opens comparative editor and alters text. | `+0.5` | `edited_clauses` |
| `ROLE_OVERRIDE` | Lawyer corrects advocate/petitioner standing tags. | `-1.0` | `role_corrections` |
| `COURT_REJECT` | Registry counter returns document with objections. | `-3.0` | `registry_failures` |
