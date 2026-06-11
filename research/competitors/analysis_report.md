# Competitor Analysis & Feature Mapping

This document lists the offerings, operational paradigms, and technical features of dominant legal tech platforms (JuriSphere, Jhana, NYAI, and Harvey AI) and details how Clausely integrates these functionalities on top of our custom validation engines.

---

## 1. Competitor Matrix & Offerings

### A. JuriSphere
*   **Target Segment:** Mid-size firms, corporate departments, and litigation counsel.
*   **Operating Paradigm:** Hybrid AI drafting paired with human attorney validation network to assure outcomes.
*   **Core Offerings:**
    *   *Real Estate:* Title review and automated transaction diligence.
    *   *M&A:* Due diligence entity matrices and contract reviews.
    *   *Litigation:* Timeline chronologies generated directly from briefs.
*   **Screenshot References:**
    *   **Real Estate Board:**
        ![JuriSphere Real Estate Interface](/g:/ai%20agents%20challenge/research/competitors/jurisphere_realestate.png)
    *   **Litigation Chronology Dashboard:**
        ![JuriSphere Litigation Interface](/g:/ai%20agents%20challenge/research/competitors/jurisphere_litigation.png)
    *   **In-House Counsel Suite:**
        ![JuriSphere In-House Interface](/g:/ai%20agents%20challenge/research/competitors/jurisphere_inhouse.png)
    *   **M&A Diligence View:**
        ![JuriSphere M&A Interface](/g:/ai%20agents%20challenge/research/competitors/jurisphere_mna.png)

### B. Jhana (jhana.ai)
*   **Target Segment:** Solo practitioners, litigation chambers, and junior associates.
*   **Operating Paradigm:** Self-service AI paralegal offering a direct free tier.
*   **Core Offerings:**
    *   *Paralegal Chat:* Fast case searches and legal argument formulation.
    *   *Document Intelligence Suit:* Bulk file indexing and legal summary extraction.
    *   *Steno:* Specialized dictation and typing tool for advocates.

### C. NYAI (nyai.ai)
*   **Target Segment:** Enterprise law firms and regulatory compliance teams.
*   **Operating Paradigm:** Private cloud/on-premises setups emphasizing security compliance.
*   **Core Offerings:**
    *   *Regulatory Intelligence:* Real-time tracking of statutory obligations.
    *   *Multi-lingual Processing:* Structured local language translation support (Hindi and Marathi).

### D. Harvey AI
*   **Target Segment:** Elite global enterprise law firms and consulting conglomerates.
*   **Operating Paradigm:** Highly secure, grounded model layers built on top of Azure infrastructure.
*   **Core Offerings:**
    *   *Vault:* Multi-file repository processing and conflict analysis.
    *   *Grounded UI:* Side-by-side contract redlining and citation verification.

---

## 2. Integrated Feature Map (Clausely Unified Chamber Suite)

To provide a complete law-firm workflow solution that goes beyond competitor offerings, Clausely combines their core capabilities with our deterministic compliance validation systems:

| Feature Class | Competitor Baseline | Clausely System (Integrated) |
| :--- | :--- | :--- |
| **Pleadings Drafting** | Jhana Chat / Harvey Assistant | **MCTS Swarm Engine:** Runs selection, expansion, and judicial evaluation trees to produce robust, stress-tested drafts. |
| **Chronology Generation** | JuriSphere Chronology Builder | **Timeline Matrix Ingestion:** Chronological graphing derived directly from court filings. |
| **Compliance Checking** | Limited formatting checks | **e-Filing Compliance Validator (System 6):** Validates A4 layout parameters, margins, justification, and 300MB/20MB file caps. |
| **Practice Billing** | Ignored by SaaS platforms | **GST RCM Billing Compiler (System 7):** Auto-calculates 10% Munshiana (clerkage) surcharges and toggles GST RCM notices. |
| **Urgent Listing** | Manual written filing | **Mentioning Slip Generator:** Automatically formats written slips matching vacation bench email rules. |
