# Long-Horizon MCTS Stress Test Report

Generated: 2026-06-07T18:56:04.601387+00:00

---

## Kesavananda Bharati v. State of Kerala

### Simulation Metadata
- **Iterations**: 2212
- **Elapsed**: 433.5s
- **Exploration constant (c)**: 1.414
- **Lambda penalty**: 1000.0
- **Max tree depth**: 6
- **Grounding budget**: 30

### Tree Statistics
- **Total nodes created**: 6637
- **Pruned nodes**: 0
- **Active paths**: 4866
- **Max depth reached**: 3

### Grounding Verification
- **Total grounding calls**: 6636
- **Verified**: 9
- **Unverified**: 6627
- **Contradictions detected**: 0
- **Verification rate**: 0.1%

### Timeline Branching Entropy
- **H**: 0.0
- **Valid**: False
- **Interpretation**: INVALID: H=0 indicates static simulation. Re-run required.

### Success Probability: 27.9%

### Optimal Path
- **[D0] Litigation Root** (visits=2212, WR=0.279, P_assumption=0.00, grounded=0/0)
  - **[D1] Butterfly: Standing change to Petitioner-in-Person** (visits=2204, WR=0.279, P_assumption=0.00, grounded=1/1)
    - **[D2] Butterfly: Standing change to Advocate** (visits=2201, WR=0.278, P_assumption=0.00, grounded=1/1)
      - **[D3] Butterfly: Date shift (filing_date +365d)** (visits=0, WR=0.000, P_assumption=1.00, grounded=0/1)

### Grounding Audit Log (Sample)

| Agent | Node | Verified | P_assumption | Contradiction | Query (truncated) |
|-------|------|----------|-------------|---------------|-------------------|
| petitioner_agent | root-1-0 | False | 1.0 | False | Verify filing_date mutation: not_specified -> injected_delay |
| opponent_agent | root-1-1 | False | 1.0 | False | Verify jurisdiction mutation: IN-SC -> MH-HC |
| petitioner_agent | root-1-2 | False | 1.0 | False | Verify client_role mutation: not_specified -> Petitioner-in- |
| petitioner_agent | root-1-0-2-0 | False | 1.0 | False | Verify filing_date mutation: injected_delay_365_days -> shif |
| opponent_agent | root-1-0-2-1 | False | 1.0 | False | Verify jurisdiction mutation: IN-SC -> MH-HC |
| petitioner_agent | root-1-0-2-2 | True | 0.01 | False | Verify client_role mutation: not_specified -> Petitioner-in- |
| petitioner_agent | root-1-1-2-0 | False | 1.0 | False | Verify filing_date mutation: not_specified -> injected_delay |
| opponent_agent | root-1-1-2-1 | False | 1.0 | False | Verify jurisdiction mutation: MH-HC -> DL-HC |
| petitioner_agent | root-1-1-2-2 | True | 0.01 | False | Verify client_role mutation: not_specified -> Petitioner-in- |
| petitioner_agent | root-1-2-2-0 | True | 0.01 | False | Verify filing_date mutation: not_specified -> injected_delay |

---

## Navtej Singh Johar v. Union of India

### Simulation Metadata
- **Iterations**: 2218
- **Elapsed**: 403.42s
- **Exploration constant (c)**: 1.414
- **Lambda penalty**: 1000.0
- **Max tree depth**: 6
- **Grounding budget**: 30

### Tree Statistics
- **Total nodes created**: 6655
- **Pruned nodes**: 0
- **Active paths**: 4879
- **Max depth reached**: 3

### Grounding Verification
- **Total grounding calls**: 6654
- **Verified**: 8
- **Unverified**: 6646
- **Contradictions detected**: 0
- **Verification rate**: 0.1%

### Timeline Branching Entropy
- **H**: 0.0
- **Valid**: False
- **Interpretation**: INVALID: H=0 indicates static simulation. Re-run required.

### Success Probability: 27.85%

### Optimal Path
- **[D0] Litigation Root** (visits=2218, WR=0.278, P_assumption=0.00, grounded=0/0)
  - **[D1] Butterfly: Standing change to Petitioner-in-Person** (visits=2215, WR=0.278, P_assumption=0.00, grounded=1/1)
    - **[D2] Butterfly: Standing change to Advocate** (visits=2212, WR=0.278, P_assumption=0.00, grounded=1/1)
      - **[D3] Butterfly: Jurisdiction swap to MH-HC** (visits=0, WR=0.000, P_assumption=1.00, grounded=0/1)

### Grounding Audit Log (Sample)

| Agent | Node | Verified | P_assumption | Contradiction | Query (truncated) |
|-------|------|----------|-------------|---------------|-------------------|
| petitioner_agent | root-1-0 | False | 1.0 | False | Verify filing_date mutation: not_specified -> injected_delay |
| opponent_agent | root-1-1 | False | 1.0 | False | Verify jurisdiction mutation: IN-SC -> MH-HC |
| petitioner_agent | root-1-2 | True | 0.01 | False | Verify client_role mutation: not_specified -> Petitioner-in- |
| petitioner_agent | root-1-0-2-0 | False | 1.0 | False | Verify filing_date mutation: injected_delay_365_days -> shif |
| opponent_agent | root-1-0-2-1 | False | 1.0 | False | Verify jurisdiction mutation: IN-SC -> MH-HC |
| petitioner_agent | root-1-0-2-2 | False | 1.0 | False | Verify client_role mutation: not_specified -> Petitioner-in- |
| petitioner_agent | root-1-1-2-0 | False | 1.0 | False | Verify filing_date mutation: not_specified -> injected_delay |
| opponent_agent | root-1-1-2-1 | False | 1.0 | False | Verify jurisdiction mutation: MH-HC -> DL-HC |
| petitioner_agent | root-1-1-2-2 | True | 0.01 | False | Verify client_role mutation: not_specified -> Petitioner-in- |
| petitioner_agent | root-1-2-2-0 | False | 1.0 | False | Verify filing_date mutation: not_specified -> injected_delay |

---

## Shreya Singhal v. Union of India

### Simulation Metadata
- **Iterations**: 1812
- **Elapsed**: 420.77s
- **Exploration constant (c)**: 1.414
- **Lambda penalty**: 1000.0
- **Max tree depth**: 6
- **Grounding budget**: 30

### Tree Statistics
- **Total nodes created**: 4357
- **Pruned nodes**: 0
- **Active paths**: 25
- **Max depth reached**: 4

### Grounding Verification
- **Total grounding calls**: 4356
- **Verified**: 9
- **Unverified**: 4347
- **Contradictions detected**: 0
- **Verification rate**: 0.2%

### Timeline Branching Entropy
- **H**: 0.0
- **Valid**: False
- **Interpretation**: INVALID: H=0 indicates static simulation. Re-run required.

### Success Probability: 32.64%

### Optimal Path
- **[D0] Litigation Root** (visits=1812, WR=0.326, P_assumption=0.00, grounded=0/0)
  - **[D1] Butterfly: Standing change to Petitioner-in-Person** (visits=1809, WR=0.326, P_assumption=0.00, grounded=1/1)
    - **[D2] Butterfly: Standing change to Advocate** (visits=1806, WR=0.326, P_assumption=0.00, grounded=1/1)
      - **[D3] Butterfly: Standing change to Petitioner-in-Person** (visits=1803, WR=0.326, P_assumption=0.00, grounded=1/1)
        - **[D4] Butterfly: Standing change to Advocate** (visits=1800, WR=0.326, P_assumption=0.00, grounded=1/1)

### Grounding Audit Log (Sample)

| Agent | Node | Verified | P_assumption | Contradiction | Query (truncated) |
|-------|------|----------|-------------|---------------|-------------------|
| petitioner_agent | root-1-0 | False | 1.0 | False | Verify filing_date mutation: not_specified -> injected_delay |
| opponent_agent | root-1-1 | False | 1.0 | False | Verify jurisdiction mutation: IN-SC -> MH-HC |
| petitioner_agent | root-1-2 | True | 0.01 | False | Verify client_role mutation: not_specified -> Petitioner-in- |
| petitioner_agent | root-1-0-2-0 | False | 1.0 | False | Verify filing_date mutation: injected_delay_365_days -> shif |
| opponent_agent | root-1-0-2-1 | False | 1.0 | False | Verify jurisdiction mutation: IN-SC -> MH-HC |
| petitioner_agent | root-1-0-2-2 | True | 0.01 | False | Verify client_role mutation: not_specified -> Petitioner-in- |
| petitioner_agent | root-1-1-2-0 | False | 1.0 | False | Verify filing_date mutation: not_specified -> injected_delay |
| opponent_agent | root-1-1-2-1 | False | 1.0 | False | Verify jurisdiction mutation: MH-HC -> DL-HC |
| petitioner_agent | root-1-1-2-2 | False | 1.0 | False | Verify client_role mutation: not_specified -> Petitioner-in- |
| petitioner_agent | root-1-2-2-0 | False | 1.0 | False | Verify filing_date mutation: not_specified -> injected_delay |

---
