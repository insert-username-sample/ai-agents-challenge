# Clausely Pitch Video Script & Storyboard (Version 2)

This document contains the word-for-word voiceover script and visual action storyboard for version 2 of the Clausely pitch demo video.

---

## 14-BEAT FLUID VIDEO STORYBOARD (Total: 93 Seconds)

| Time | Beat & Audio Narration (Voiceover) | Visual Action & Screen Recording |
| :--- | :--- | :--- |
| **0:00 - 0:05** | **BEAT 1: THE LIMITATION**<br>"Modern AI systems are becoming increasingly capable. But they still struggle with two fundamental problems: assumptions and hallucinations." | **[Visual]** Clean high-contrast dark-mode dashboard showing a legal document compilation failing. Faint red glow around the text: "COMPLIANCE FAILURE". |
| **0:05 - 0:09** | **BEAT 2: UNVERIFIED TRUTH**<br>"A response can appear correct, even when critical facts were never verified." | **[Visual]** Highlight text in a mock petition showing unverified dates and wrong demographics being generated automatically. |
| **0:09 - 0:13** | **BEAT 3: CLAUSELY MISSION**<br>"Clausely was built to challenge generated outputs before they become conclusions." | **[Visual]** The background glows indigo/cyan. Transition to the Clausely logo and subtitle fading in smoothly: "Zero-Hallucination Legal Compilation". |
| **0:13 - 0:21** | **BEAT 4: GOOGLE ADK FOUNDATION**<br>"Built on Google's Agent Development Kit, Clausely combines Gemini 3.5 Flash, Grounding with Google Search, and a coordinated swarm of specialized agents working together in real time." | **[Visual]** A sleek architecture visualization showing the **Swarm Harness Copilot** and a grid of 8 specialized agents: Petitioner, Opponent, Reviewer, Judge, Drafter, Verifier, Objector, Presenter. |
| **0:21 - 0:27** | **BEAT 5: PATH GENERATION**<br>"A user query enters the system. Instead of committing to a single answer, Clausely generates multiple possible reasoning paths." | **[Visual]** Interactive tree showing parallel reasoning branches splitting out from a single root node. |
| **0:27 - 0:34** | **BEAT 6: CONTINUOUS EVALUATION**<br>"Every path is continuously evaluated against grounded evidence. Facts, entities, dates, timelines, relationships, and citations are verified throughout the reasoning process, not just at the end." | **[Visual]** Active paths being evaluated. Pulse animations along the timeline tree showing live checks against retrieved RAG resources. |
| **0:34 - 0:45** | **BEAT 7: SWARM COLLABORATION**<br>"As grounded information enters the system, a swarm of specialized agents begins evaluating the generated paths. Some propose possibilities. Others search for weaknesses. Others verify evidence, challenge assumptions, and evaluate outcomes." | **[Visual]** Sibling nodes competing. Grid nodes lighting up sequentially as Petitioner, Opponent, Verifier, and Objector coordinate. |
| **0:45 - 0:54** | **BEAT 8: ALPHAPROOF NEXUS ALIGNMENT**<br>"During development, I noticed that my multi-agent verification approach closely aligned with the recently introduced AlphaProof Nexus framework. I subsequently adapted and refined parts of the system around those verification-driven principles." | **[Visual]** Highlight the Evolutionary Strategy Ratings display (Plackett-Luce Elo scale) showing strategy scores: `Strategy A: 1420 (+45)`, `Strategy B: 1050 (-45)`. |
| **0:54 - 1:00** | **BEAT 9: COMPETITION & PRESSURE TESTING**<br>"Rather than trusting the first response, Clausely continuously compares competing possibilities and pressure-tests them against available evidence." | **[Visual]** Parallel paths being actively scored. Standard LLM linear output compared against MCTS adversarial search paths. |
| **1:00 - 1:06** | **BEAT 10: ELIMINATING UNSUPPORTED PATHS**<br>"As new evidence arrives, unsupported paths are eliminated. Assumptions are challenged. Hallucinations are removed. Grounded paths continue forward." | **[Visual]** Incorrect paths turning red and fading out. The Constraint Pruning Gate marks vetoed branches with `UCT = -inf` in real time. |
| **1:06 - 1:13** | **BEAT 11: HUMAN-IN-THE-LOOP HALTING**<br>"When critical information is missing, Clausely does not guess. The system pauses, requests clarification, and resumes only when sufficient information is available." | **[Visual]** The dashboard fades and a glowing Human-in-the-Loop Gateway popup box appears: "UNIFIED GROUNDING VALIDATOR HALT — Fact Discrepancy Detected." |
| **1:13 - 1:22** | **BEAT 12: REAL-WORLD MISMATCH EXPOSED**<br>"In one real-world case, a generic model identified a petitioner as a daughter. Grounded evidence showed the judgment referred to a son. The unsupported path was eliminated, and the verified path remained." | **[Visual]** Zoom on the HITL Modal details: "Judgment WP 4769/2021 refers to: SON. Intake Form specifies: DAUGHTER." Highlight the primary action: `Confirm "SON"`. |
| **1:22 - 1:27** | **BEAT 13: THE RESULT**<br>"The result is a system designed not only to generate answers, but to verify them." | **[Visual]** SFE compiling the clean, fully-validated court document. pytest running in terminal: `314 passed in 47.21s`. |
| **1:27 - 1:33** | **BEAT 14: THE CONCLUSION**<br>"Clausely explores how coordinated AI agents can reduce hallucinations, challenge assumptions, and produce more reliable outcomes." | **[Visual]** Final clean dark screen fading in: "clausely-ai.web.app". |

---

## TECHNICAL PRODUCTION DIRECTIVES

1. **Fluid Visuals:** All elements exist in a single DOM viewport. Animations must use opacity and transform scales rather than display switches to prevent visual cuts.
2. **Typography:** Comfortaa fordisplay titles and Inter for text narratives to maintain modern corporate branding.
3. **No Emojis:** All texts and files must use ASCII markings only.
