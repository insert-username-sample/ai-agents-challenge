# IMPLEMENTATION PLAN 1: RAG CASE EXTRACTION STRATEGY (v0.0.0.1 ALPHA)

---

## 1. Objective & Case Discovery Focus

This plan defines the retrieval protocol to extract **20 real-world Indian Supreme Court and High Court cases** (dating between 2021 and 2026) to form our empirical backtesting corpus.

```
                  [Clausely Real-time RAG Search]
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
     (10 Popular cases)   (5 Backtest cases)   (5 Procedural cases)
       2024-2026 SC/HC       2021-2023 SC/HC      1-5 Initial Orders
```

### Retrieval Categories:
1.  **10 Popular Recent Cases (2024-2026)**: Focuses on high-impact rulings from the Supreme Court of India and prominent High Courts (Delhi, Bombay, Madras) involving constitutional shifts (such as BNS/BNSS/BSA transitions, single-mother rights, data privacy, and corporate insolvencies).
2.  **5 Backtesting Cases (2021-2023)**: Selects matters with completed final judgments from the last 3-5 years, where we only ingest the first 1-2 initial pleadings to run MCTS simulations and test the simulator's predictive accuracy.
3.  **5 Procedural Cases (2021-2025)**: Evaluates detailed procedural interim orders (e.g. registry defects, maintainability challenges under Article 226) to test early-stage tree forks.

---

## 2. Technical Retrieval Protocol

We utilize the custom `RealtimeSearchClient` in `tools/realtime_rag.py` to fetch fresh records dynamically.

### Target Legal Portals Restrict:
- `sci.gov.in` (Supreme Court of India)
- `bombayhighcourt.nic.in` (Bombay High Court)
- `delhihighcourt.nic.in` (Delhi High Court)
- `indiankanoon.org` (Authoritative Open Law Index)
- `livelaw.in` / `barandbench.com` (Legal reporting)

### Search Query Parameters:
```python
search_queries = [
    "Supreme Court of India judgment 2025 single mother caste certificate",
    "Bombay High Court Nagpur Bench judgment 2024 SC status",
    "Bharatiya Sakshya Adhiniyam Section 61 electronic records certificate judgment 2025",
    "Supreme Court of India Article 226 maintainability alternative remedy 2024",
    "Insolvency and Bankruptcy Code IBC Section 7 recent judgment 2025"
]
```

---

## 3. Data Extraction Schema

For each of the 20 retrieved cases, the RAG client extracts the following structured JSON schema:

```json
{
  "case_id": "SC-CIVIL-2025-1092",
  "title": "State of Maharashtra v. Client Profile",
  "citation": "2025 INSC 144",
  "court": "Supreme Court of India",
  "filing_year": 2023,
  "judgment_year": 2025,
  "initial_facts": "The petitioner filed writ challenging SDO order...",
  "procedural_timeline": [
    "2023-04-12: High Court filing",
    "2023-08-15: Registry objections on delay",
    "2024-02-18: Interim stay granted"
  ],
  "actual_outcome": "Allowed. Mandamus issued directing Caste Scrutiny Committee to verify maternal certificates.",
  "ratio_decidendi": "Strict paternal lineage demands violate constitutional equality when child is raised by a single mother."
}
```

This structured data is passed directly into the **MCTS Swarm Simulator** to evaluate the predictive validation loop.
