# Legal AI Target Feature Set & User Feedback Analysis

This document outlines key product requirements, features, and UX paradigms derived from real-world usage patterns of platforms like Harvey AI, Jurisphere, and the unique workflow pain points of Indian legal practitioners.

## 1. High-Priority Features Needed (Global Core)

### A. Chronology Builder (Litigation & Arbitration)
*   **Goal:** Automatically compile structural timelines from disorganized files.
*   **Requirements:**
    *   Accepts multi-file PDF/Word inputs (pleadings, emails, contracts).
    *   Generates a clean timeline table: `[Date] | [Event Description] | [Source Document Reference]`.
    *   Option to export directly to Excel or CSV.

### B. Interactive Side-by-Side PDF Viewer & Citation Grounding
*   **Goal:** Solve lawyer trust issues by removing black-box hallucination.
*   **Requirements:**
    *   Split-screen UI showing the AI Draft/Analysis on the left and the source PDF viewer on the right.
    *   Interactive citation links. Clicking `[Doc A, Page 4]` automatically scrolls the PDF viewer to Page 4 and highlights the target sentence.

---

## 2. Indian Legal Market Specific Features (The "What They Hate" Killers)

### A. e-Courts PDF Compliance Compiler
*   **Problem:** Advocates face constant rejections from e-filing registries due to formatting issues (non-OCR, bad margins, size >20MB).
*   **Feature Goal:** A one-click pre-filing compliance formatter.
*   **Requirements:**
    *   **Automated OCR & PDF/A Export:** Ensures every page is fully text-searchable.
    *   **Auto-Margin & Font Standardizer:** Modifies font sizes, line spacing, and margins to match specific High Court/District Court rules.
    *   **Smart Size Compressor:** Compresses large filing bundles to exactly under 20MB without losing OCR layer quality.

### B. Vernacular Translation Engine (Regional Court Orders to High Court Appeals)
*   **Problem:** Lower court records are in regional languages (Hindi, Marathi, Tamil, etc.), but appeal courts require English. Generic translators lose legal context.
*   **Feature Goal:** Legal-specific translation containing localized terminology mappings.
*   **Requirements:**
    *   Preserve document structure and exact paragraph page numbers.
    *   Accurately translate regional terms (e.g., "Panchnama", "Challan", "Khata", "Fard") into standardized English legal explanations instead of literal translations.

### C. Case Law Hierarchy Verifier (SCC/Manupatra Wrapper)
*   **Problem:** Generic LLMs hallucinate case citations or quote overruled judgments.
*   **Feature Goal:** Citation grounding validator.
*   **Requirements:**
    *   Cross-verify generated citations against live Indian judicial registries.
    *   Flag if a quoted judgment has been overruled or distinguished by a larger Supreme Court bench.

---

## 3. Litigator Operational Workflow Features

### A. Munshi (Clerk) Copilot & Mentioning Slip Generator
*   **Goal:** Streamline courtroom management and case coordination.
*   **Requirements:**
    *   **Automated Mentioning Slip Builder:** Generates standardized "Urgent Mentioning" letters containing case numbers, party names, and brief urgency reasons to present to the Bench clerk.
    *   **Dual-Index Sheet Alignment:** Generates paper-index print maps that align physical court folder paginations with digital PDF indexes.

### B. Daily Board (Cause List) Alert Tracker
*   **Goal:** Prevent missed case calls across multiple benches.
*   **Requirements:**
    *   Integrate directly with e-courts Cause Lists to scrape daily item numbers.
    *   Generate real-time priority dashboards showing case statuses across active rooms, flagging high-risk schedule conflicts for the lead advocate.

