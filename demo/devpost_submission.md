Clausely is a legal compilation engine built on Google ADK for India's 1.7 million advocates.

THE PROBLEM
Courts reject 8-15% of Indian legal filings for preventable formatting errors — wrong margins, wrong fonts, missing clauses. Generalist AI makes this worse: it hallucinates facts and generates documents that look right but fail at registry.

THE APPROACH
Clausely treats law as a compilation task, not a generation task.

Natural language intent -> Legal AST -> SFE formatting -> Court-accepted document.

THE ARCHITECTURE (Google ADK)
- 8-Agent MCTS Swarm: Petitioner, Opponent, Reviewer, Judge, Drafter, Verifier, Objector, Presenter running adversarial litigation simulation
- Symbolic Formatting Engine: Deterministic layout compiler enforcing exact court margin/font rules — not suggested, enforced
- Human-in-the-Loop Gateway: System halts when facts are ambiguous rather than hallucinating
- Swarm Harness Copilot: Stateful coordinator routing context across all agents

WHAT MAKES THIS DIFFERENT
In the Vidya Khobrekar caste certificate case (Nagpur Bench), every generalist LLM we tested drafted the petition for a "daughter" based on case summaries. The actual judgment says "son". Clausely's Verifier Agent caught the demographic mismatch and triggered the HITL gateway before a single word was compiled.

This is not a chatbot. It's a compiler with a conscience.

TECHNICAL PROOF
314 automated verification tests. Live deployment at https://clausely-ai.web.app.
Built on Google ADK + Gemini 3.5 Flash + Firebase.

THE VISION
Phase 1: Drafter + Acceptor (court-correct documents)
Phase 2: Strategist (adversarial litigation simulation)
Phase 3: Autonomous law firm OS (80% AI, 20% human oversight)

Clausely is legal infrastructure. Not a legal chatbot.
