# IMPLEMENTATION PLAN 16: ZERO-KNOWLEDGE CLIENT-SIDE EVIDENCE ATTESTATION (v0.0.0.1 ALPHA)

---

## 1. Objective & Non-Disclosure Verification

This plan defines the cryptographic architecture governing the attestation of highly sensitive legal records.

In legal operations, proving the existence and validity of an official document (such as a vigilance inquiry report, lineage certificate, or non-disclosure agreement) is mandatory during early-stage filings. However, uploading these files to developer clouds or central LLM databases violates confidentiality and data privacy protections. 

This plan leverages Zero-Knowledge Proofs (ZKP) to prove document properties without exposing raw contents.

```
 [Raw Private Document] ──> [Local zk-SNARK Generator] ──> [ZK Proof (pi)] ──> [Central Sync]
                                                                                      │
                                                                                      ▼
                                                                           [On-Chain/Cloud Verify]
```

---

## 2. Cryptographic Attestation Architecture

### 1. Client-Side Proof Generation
*   **Path**: `packages/zk-attestation/prover.ts`
*   **Engine**: SnarkJS running locally in the client-side desktop environment.
*   **Methodology**:
    1.  The client uploads the sensitive legal PDF locally.
    2.  The prover computes a SHA-256 hash of the document: $H = \text{SHA256}(Doc)$.
    3.  Generates a zk-SNARK proof ($\pi$) validating specific assertions (e.g., "The document contains a valid stamp from the Nagpur Bench of the Bombay High Court and was signed in 2026") without revealing the text.

### 2. Verification Protocol

| Verification Claim | Public Inputs | Private Inputs | Verification Output |
|---|---|---|---|
| **Maternal Lineage Verification** | Verified genealogical root hash, signature threshold. | Full family names, identity numbers. | Proof of relationship depth and valid certificate authority signature. |
| **Vigilance Inquiry Attestation** | Status code, report date, issuing authority hash. | Raw investigative findings, PII. | Validates that no active adverse findings are recorded. |
| **Registry Stamp Authenticity** | Court signature key, registry serial stamp hash. | Raw filing metadata. | Confirms document has been officially logged in the court registry. |

### 3. Integration with Legal AST
*   If a proof is validated, the compiler updates the matching `LegalNodeType` state to `isGrounded = true`.
*   The raw document remains 100% encrypted inside the lawyer's local client sandbox, preserving attorney-client privilege.

---

## 3. Cryptographic Setup & Performance

*   Uses the Groth16 zk-SNARK protocol over the BN254 elliptic curve for ultra-fast proof generation ($< 2.5$ seconds) on standard on-device client CPUs.
*   The verification key is distributed statically with the Tauri desktop build, eliminating external network dependencies during validation.
