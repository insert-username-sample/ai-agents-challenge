# IMPLEMENTATION PLAN 18: TAURI WINDOWS NATIVE CLIENT & SECURE SANDBOX (v0.0.0.1 ALPHA)

---

## 1. Objective & Native Desktop Distribution

This plan defines the distribution, client runtime environment, and operational sandbox constraints for the Clausely native Windows desktop client.

Legal operations are heavily bounded by data sovereignty, speed, and corporate security mandates. Practicing legal professionals cannot rely on unstable cloud-only web portals that expose sensitive materials to third-party outages. Clausely v1.5 packages the frontend UI, MCTS execution core, and local SQLite databases into a secure Windows desktop wrapper (Tauri) to run locally on i5/i7 client machines.

```
 [Tauri Windows wrapper (Rust)] ──> [Local SQLite & AES-GCM-256]
                  │
                  ▼
       [Local Python Sandbox] ──> [Quantized Gemma 4 AWQ/GGUF]
```

---

## 2. Desktop System Architecture & Sandbox Security

### 1. Tauri Host System Integrations
*   **Path**: `src-tauri/src/main.rs`
*   **System Core**: Rust-based Tauri backend executing web-views via Microsoft WebView2.
*   **Execution Gating**: Intercepts and isolates local file access, binding all data read/write commands to the secure workspace subfolder.

### 2. Desktop Environment Matrix

| System Module | Runtime Stack | Operational Constraint | Security Mitigation |
|---|---|---|---|
| **Local SQLite DB** | `sqlite3` via Rust SQLx | Stores active advocate telemetry signals locally. | Encrypted at rest using AES-GCM-256 keys. |
| **Local Python Core** | Python 3.11 embedded runtime | Executes deep strategist self-play MCTS loops. | Isolated in a virtual environment (`clausely-adk\.venv`). |
| **Local LLM Engine** | llama.cpp / Gemma C++ binding | Performs local semantic audits and fast token predictions. | Runs quantized Gemma 4 AWQ/GGUF models locally. |

### 3. Local Data Synchronization & Anonymization
*   Ensures that only highly aggregated, PII-scrubbed DPO training gradients are synchronized over HTTPS.
*   The raw legal files, case citations, and family lineage documents remain 100% localized on the host device's secure partition.

---

## 3. Deployment & Multi-Platform Verifications

*   Uses native MSI/EXE compilation chains built via GitHub Actions runner machines.
*   Enforces Code Signing certificates on all compiled binaries to prevent Windows Defender SmartScreen intervention warnings, ensuring a premium install experience for practicing attorneys.
