# IMPLEMENTATION PLAN 11: ON-DEVICE LOCAL MODEL DEPLOYMENT (v0.0.0.1 ALPHA)

---

## 1. Objective & Hardware Constraints

This plan formalizes the optimization and local compilation parameters for deploying **Gemma 4 E2B/E4B** and **MiniCPM-3** on local client machines (on-device tier).

```
 [Natural Language] ──> [Local llama.cpp / MLC Engine] ──> [Local Inference]
                                                                  │
                                                                  ▼
                                                      [Dynamic UI Spec Generation]
```

On-device inference is critical to support the **v1.5 persistent input field** and dynamic UI compiler pipeline with sub-second intent classification latencies, bypassing expensive network REST roundtrips.

---

## 2. Model Quantization & Compilation Spec

We optimize models using the **MLC-LLM** or **llama.cpp** compilation backends:

### 1. Model Selection
*   **Gemma 4 E2B** (Google's highly optimized 2-billion parameter model for intent classification).
*   **Gemma 4 E4B** or **MiniCPM-3-4B** (for local UI specification generation and draft editing).

### 2. Quantization Format
*   **4-bit AWQ (Activation-aware Weight Quantization)**:
    *   *Purpose*: Restricts memory footprint to under 2.5 GB of RAM, allowing high-speed local CPU execution without requiring dedicated NVIDIA GPUs on lawyer client laptops.
*   **Format**: `q4_k_m` or `q5_k_m` GGUF templates.

### 3. Execution Engine
*   Compiled directly as a dynamic library (`.dll` for Windows clients) embedded within the Clausely desktop workspace client, exposing a clean C++ API.

---

## 3. Offline Performance Targets

- **Intent Classification**: Latency $\le 150\text{ms}$ (on standard Intel i5/i7 laptops).
- **UI Spec Compilation**: Speed $\ge 35\text{ tokens/second}$ under local AWQ quantization.
- **Maximum Memory Limit**: $\le 3.0\text{ GB}$ active resident set size (RSS).
