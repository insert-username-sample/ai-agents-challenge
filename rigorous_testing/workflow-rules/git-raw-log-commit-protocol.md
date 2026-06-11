# Git and Raw Conversation Commit Protocol

This protocol is mandatory for Clausely development work.

## Non-Negotiables

1. A git repository must exist before feature, harness, audit, or workflow changes continue.
2. Every coherent change set must end with a git commit.
3. Every commit that changes source, tests, plans, workflow rules, findings, or vision docs must also include the current raw conversation log artifact when one is available in `rigorous_testing/raw_conversation_log*.jsonl`.
4. Raw conversation logs must not be summarized, redacted, or rewritten to make results look cleaner.
5. If the live raw transcript source cannot be copied, the commit message or companion audit note must explicitly say that the raw log source was unavailable.
6. Do not commit `.env`, virtual environments, `node_modules`, generated caches, downloaded model archives, or bulky dataset binaries unless the user explicitly requests a data snapshot commit.
7. Do not use invented agent names in commit messages, docs, tests, or reports. The canonical strategist agents are exactly: `petitioner_agent`, `opponent_agent`, `reviewer_agent`, `verifier_agent`, `objector_agent`, `presenter_agent`, `judge_agent`.

## Change Set Boundary

A coherent change set is one of:

- a harness/rules update,
- a simulation engine update,
- a UI feature update,
- a test/report update,
- a raw audit sync,
- a documentation or plan correction,
- a repository hygiene change.

Each boundary requires:

1. inspect `git status --short`;
2. add only intentional files;
3. ensure `rigorous_testing/raw_conversation_log*.jsonl` is tracked when available;
4. commit with a clear message;
5. verify the repository is clean or explain remaining uncommitted work.

## Failure Handling

If a commit cannot be made because git identity is missing, configure a repository-local identity and retry. If git itself is unavailable, halt development and report that the audit trail cannot be guaranteed.
