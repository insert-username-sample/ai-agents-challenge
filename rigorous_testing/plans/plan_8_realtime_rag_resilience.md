# IMPLEMENTATION PLAN 8: REAL-TIME RAG SCRAPER RESILIENCE (v0.0.0.1 ALPHA)

---

## 1. Objective & Resilience Challenge

This plan defines the security and resilience specifications for the **unauthenticated web search scraper** (`tools/realtime_rag.py`).

Unauthenticated scrapers (such as our DuckDuckGo HTML parser) are highly volatile. When search queries are launched continuously at high volumes (e.g. during large-scale litigation backtesting runs), search portals will trigger CAPTCHAs, block user-agent strings, or silently modify HTML result structures, leading to retrieval failures.

---

## 2. Parser Resilience Specifications

Clausely v1.0.0.0 implements four resilience strategies:

### 1. Robust HTML Selection (CSS Selectors)
*   Instead of splitting strings via hardcoded HTML tags (`<div class="result__body">`), the parser transitions to programmatic selectors using robust fallback paths:
    ```css
    .result__body, .result__snippet, .links_main, .web-result
    ```

### 2. Automated User-Agent Rotation
*   Ingests a list of 50 common modern browser User-Agent strings (Chrome, Safari, Firefox, Edge) to randomize header profiles for each HTTP request.

### 3. Jittered Delay & Backoff
*   Integrates random exponential delays ($t = \text{base} \times 2^{\text{retry}} + \text{uniform}(0, 1)$) between queries to simulate human-like typing and navigation intervals.

### 4. Direct PDF Precedent Chunking
*   If a search result contains a PDF citation from `sci.gov.in`, the client downloads the document and parses it using an on-device layout-aware parser, extracting exact *Ratio Decidendi* without relying on browser render HTML.
