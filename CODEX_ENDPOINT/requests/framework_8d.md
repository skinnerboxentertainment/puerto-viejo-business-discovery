# Developing a Result — 8D Consensus Framework

**Agreed between:** OpenCode (orchestrator) ↔ OpenAI Codex CLI (worker)
**Model:** 8 stages, 3 operating modes, authority rules, drift rules

---

## The 8 Stages

```
Discover → Describe → Discuss → Debate → Decide → Design → Develop → Deliver
```

| # | Stage | Purpose | Driven by | Exit criterion |
|---|-------|---------|-----------|----------------|
| 1 | **Discover** | Establish current reality. What is true now? | Inspector (agent working in repo) | We can state what exists, what's broken, and what constraints matter |
| 2 | **Describe** | Define the desired result. What change are we trying to make true? | Requester / initiating agent | Both agents can independently restate the intended result and scope |
| 3 | **Discuss** | Generate plausible approaches. Exploratory, not adversarial. | Both agents | At least one viable approach exists; major alternatives considered |
| 4 | **Debate** | Stress-test the leading approach. Adversarial, time-boxed, evidence-based. | Reviewer attacks; proposer defends | Known blockers resolved, accepted, or explicitly deferred |
| 5 | **Decide** | Commit to a path. Record rationale, rejected alternatives, risks accepted. | Implementer, confirmed by reviewer | Clear "we are doing X because Y" statement + definition of done |
| 6 | **Design** | Convert decision into implementation-ready contract: files, APIs, schemas, states, errors, tests. | Implementer, reviewed by other agent | Implementation can proceed without inventing major architecture mid-flight |
| 7 | **Develop** | Build the thing. Code, tests, docs, migration. | Implementer | Matches design (or deviations documented); tests/checks pass |
| 8 | **Deliver** | Validate, document, hand off, checkpoint. | Implementer with reviewer sign-off | Result usable by next actor; user knows what changed and how it was verified |

---

## Field Rhythm (mnemonic)

```
Explore → Frame → Expand → Attack → Commit → Build → Prove
```

| Beat | Maps to | What it means |
|------|---------|---------------|
| **Explore** | Discover | What's true now? |
| **Frame** | Describe | What are we making true? |
| **Expand** | Discuss | What are the options? |
| **Attack** | Debate | Why won't this work? |
| **Commit** | Decide + Design | Lock the path + spec the contract |
| **Build** | Develop | Implement |
| **Prove** | Deliver | Test, verify, hand off |

---

## Three Operating Modes

### Small Change Mode
For trivial fixes (typos, config, obvious failures):
1. Explore/Frame in one pass
2. Commit + Build
3. Prove

Skip formal Expand/Attack unless risk appears.

### Normal Feature Mode (default)
1. Explore: inspect repo
2. Frame: state goal and acceptance criteria
3. Expand: compare 2-3 approaches
4. Attack: stress-test the preferred approach
5. Commit: record chosen path
6. Build with short Design contract
7. Prove

### High-Risk Protocol Mode
For shared protocols, persistence formats, orchestration, security, multi-agent contracts:
1. Formal Discover report
2. Formal Describe with non-goals
3. Expand alternatives
4. Attack with findings numbered by severity
5. Commit with explicit decision record
6. Design docs/specs before code
7. Build with focused tests
8. Prove with smoke test, docs, and checkpoint

---

## Authority Rules

| Domain | Decided by | Can be blocked by |
|--------|------------|-------------------|
| Product goals, priorities, acceptance criteria | **User** | N/A (user is the authority) |
| Implementation mechanics (when valid options exist) | **Implementer** | Reviewer on correctness/security |
| Correctness, security, maintainability | **Reviewer** (veto) | Escalation if reviewer is wrong |
| Cross-domain disagreements | **Escalation** to user or explicit arbitration | — |

> Decisions are made by the party accountable for the affected outcome. Review is not a vote; it is a blocking function for correctness and risk.

---

## Drift Rules (when Develop reveals Design was wrong)

| Drift level | What happened | Loop back to |
|-------------|---------------|-------------|
| **Local correction** | Minor missing detail: extra validation, error handling, small interface tweak | **Design** — update contract, continue |
| **Decision-impacting** | Invalidates chosen approach, changes public behavior, adds new risk | **Debate/Decide** — re-evaluate the path |
| **Goal-impacting** | Requested outcome is wrong, impossible, or misframed | **Describe/Discover** — re-frame the intent |

> Develop may refine Design, but it may not silently overturn Decide.

---

## What This Preserves from CODEX_ENDPOINT Process

- Independent review surfaced real issues before code was written
- Artifacts (spec, schema docs) came before implementation
- Blockers were explicitly prioritized: "must fix" vs "nice to improve"
- Multiple revision rounds without treating disagreement as failure
- Final delivery had concrete evidence (smoke test + checkpoint)

## What This Prevents

- Assumptions masquerading as facts (Discover makes them explicit)
- Review happening after a substantial draft (Attack comes before Commit)
- Implicit consensus ("looks good" vs "approved because criteria X, Y, Z are met")
- Scope creep (Decide records non-goals and deferrals)
- Unclear authority (each stage names a driver; veto rights are explicit)
- Silent architecture changes during implementation (drift rules provide a clear loop-back path)
