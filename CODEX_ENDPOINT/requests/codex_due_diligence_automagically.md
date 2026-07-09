# Codex Due Diligence: AutoMagically / automagically-refactored

**Scope Reviewed**

I inspected both local repos:

- [AutoMagically](C:/Users/oscar/AI%20WORKBENCH/devChorus/AutoMagically)
- [automagically-refactored](C:/Users/oscar/AI%20WORKBENCH/devChorus/automagically-refactored)

Key files reviewed included `AGENTS.md`, `opencode.json`, `package.json`, `README.md`, selected agents, rules, director gates, workflow catalog, `/auto-build`, genre templates, custom skills, `src/main.ts`, `src/core/*`, and `packages/narrative-core/src/*`.

I also attempted `npm test` and `npm run build` in both repos. Both failed before execution because dependencies are not installed: `vitest` and `tsc` are not available in `node_modules/.bin`.

**High-Level Verdict**

The repos are much more mature as an AI-process template than as a game framework.

The agent/workflow layer is extensive, intentional, and often thoughtfully written. The actual runtime game engine is tiny. In the original repo, the runtime is essentially PixiJS initialization plus narrative-core. In the refactored repo, there is a small scaffold: `SceneManager`, `InputManager`, `GameLoop`, config loader, graph registry, audio manager, RNG, and a welcome screen.

That mismatch is the central architectural fact: perceived complexity is high because the process layer is huge; actual executable complexity is low because most systems are prompts, policies, and generation instructions rather than implemented framework code.

---

**Architecture Critique**

What is well designed:

- Clear separation between process, source code, assets, design docs, tests, and production state.
- The layer rule `core <- gameplay <- ui/rendering/audio/tools` is directionally right.
- The refactored `src/core` surface is appropriately small for a browser game starter.
- `InputManager` centralization is a good call. Scenes should not register arbitrary DOM listeners.
- Stack-based `SceneManager` is pragmatic for small PixiJS games.
- The “plain state, render sync” rule is excellent. It directly improves testability and save/load.
- Genre templates are useful. They turn vague game requests into constrained starter shapes.
- Seeded RNG and fake clocks are the right primitives for deterministic game tests.
- The narrative-core package is independent enough to be reusable. Zod schemas, graph analysis, and the VM boundary are sensible.

What is over-engineered:

- 36 agents, 81 commands, 13 rules, 34 installed skills, director gates, workflow catalogs, session state, architecture manifests, and graph topology are far more structure than most one-person browser games need.
- The director-gate system resembles enterprise process for projects that may only need prototype velocity.
- The graph integration is conceptually interesting but too mandatory. Requiring every gameplay system to register `NarrativeDocumentV2` topology is heavy for arcade/platformer systems.
- The narrative document schema is broad: content, topology, environment, presentation, runtime, editor, audio, plugins. For most generated browser games, only a small subset matters.
- `/auto-build` promises complete generation, retries, graph registration, tests, asset manifests, audio, config validation, and build summaries. That is a lot of behavioral contract in markdown without a real orchestrator implementation.

What is missing:

- A real generation engine. `/auto-build` is a command spec, not an executable compiler/generator.
- A stable internal project model/schema for game specs. The auto-build process describes fields in prose but does not define a typed intermediate representation.
- True validation of generated files before write. The command says “dry-run parse all generated TypeScript,” but there is no implemented static validator.
- Runtime integration in the fork is incomplete. `main.ts` shows a welcome screen, but does not wire `InputManager`, `SceneManager`, `GameLoop`, `BootScene`, graph API, or asset manifest flow.
- Config loading is typed but not validated. It fetches JSON and casts to `GameplayConfig`.
- `GraphRegistry` returns a `Record<string, unknown>` with `_systems`, not a properly merged `NarrativeDocumentV2`.
- No Playwright dependency despite `/auto-build` specifying browser tests.
- No actual generated game examples in the stripped fork to prove the pipeline works end to end.
- No formal compatibility tests for PixiJS v8 APIs beyond prompt instructions.

---

**Agent System Critique**

The agent design is strong as a role taxonomy, weak as a default operating model.

The best parts:

- Directors have clear authority boundaries: creative, technical, production.
- The collaboration protocol is explicit: question, options, decision, draft, approval.
- The selected agents I read are mostly high-quality prompts. `creative-director`, `technical-director`, and `producer` give useful decision frameworks rather than vague persona text.
- Specialist boundaries are generally good. `pixijs-specialist` is narrow; `gameplay-programmer` is implementation-focused and correctly pushes ambiguity back to design/architecture.
- Gate verdict formatting is machine-readable, which is good.

The problems:

- 36 agents is too many for default use. It creates routing overhead and prompt overlap.
- Several roles are premature for most projects: `community-manager`, `live-ops-designer`, `localization-lead`, `analytics-engineer`, `security-engineer`, and `network-programmer` are valid domains but should be optional modules, not always-present core.
- The lead/specialist distinction is often artificial in an AI workflow. `lead-programmer`, `engine-programmer`, `gameplay-programmer`, `tools-programmer`, `pixijs-specialist`, and `technical-director` can overlap heavily.
- “Agents never act autonomously” conflicts with `/auto-build`, which explicitly bypasses normal protocol and writes during verification.
- The process assumes the assistant can consistently spawn the right subagents and preserve shared context. In practice, the file-backed state model is needed because conversation memory is unreliable, but the docs do not fully solve context handoff fidelity.
- The system has many commands that appear to be thin prompt wrappers. Discoverability suffers.

My recommendation: keep the role model, but collapse the default roster.

Default clean-room roster should be closer to:

- `studio-director` or `product-director`: vision, scope, final tradeoffs.
- `technical-architect`: architecture, boundaries, libraries, performance.
- `producer`: workflow, milestones, task slicing.
- `gameplay-engineer`: mechanics and tests.
- `rendering-ui-engineer`: PixiJS, scenes, UI, assets.
- `qa-reviewer`: tests, verification, regression risks.

Then add optional packs: audio, narrative, live ops, localization, networking, accessibility, analytics.

---

**Auto-Build Pipeline Critique**

The approach is directionally solid: ingest spec, resolve missing fields, match a constrained template, generate files, verify, summarize. That is the right shape.

The strongest ideas:

- Genre-pattern fallback is pragmatic.
- “Always produce something runnable” is useful for prototyping.
- A typed config file for tunables is right.
- Deterministic tests and seeded RNG should be built in from the start.
- One batched question for unknowns is better than a long interview.
- Verification with `tsc` and `vitest` before final approval is correct.

Major failure modes:

1. It is markdown-as-orchestrator.
The command describes behavior but does not implement parsing, generation, retries, cleanup, or a transactional write model.

2. It writes before final approval.
Phase 4 says write files to disk for verification. Phase 5 then asks whether to write. That is contradictory unless there is a temp workspace or rollback transaction.

3. No typed spec IR.
Without a schema like `ResolvedGameSpec`, generation will drift. Agents will infer fields inconsistently across runs.

4. No template compiler.
Genre patterns are prose. That helps the LLM, but it is not deterministic. A clean rebuild should use structured templates plus editable codegen.

5. Verification scope is incomplete.
`tsc` and `vitest` catch syntax and unit failures, not whether the canvas is nonblank, input works, assets load, or the game loop runs.

6. Generated graph registration is too heavy.
Making every system declare `NarrativeDocumentV2` will inflate code and create low-value boilerplate unless graph data becomes a first-class product feature.

7. Retry loops can mask bad architecture.
“Fix all errors and retry up to 3 times” is useful, but without preserving cause analysis, it can produce patchy code.

8. Defaulting unknowns may build the wrong game.
Applying genre defaults is useful, but the summary must clearly mark inferred decisions and make them easy to revise.

---

**Code Quality**

TypeScript practices:

- `strict: true` is good.
- `moduleResolution: bundler` is appropriate for Vite.
- Root `tsconfig` excludes tests and tools, so `npm run build` will not typecheck tests. That is common, but it means `vitest` must be part of verification.
- The narrative types derive from Zod schemas, which is good.
- Some typing is loose:
- `GraphRegistry.register(systemId, doc: Record<string, unknown>)`
- `GraphRegistry.exportJSON(): Record<string, unknown>`
- Config JSON is cast, not validated.
- Narrative condition comparisons cast unknowns to numbers without type checks.
- `packages/narrative-core/package.json` points `main` and `types` to `.ts` source. This can work inside a Vite workspace, but it is not a clean package boundary for publication or external use.

Test coverage:

- Original has narrative-core tests only.
- Refactored adds `InputManager` and `SceneManager` tests.
- There are no actual gameplay-system tests yet because there is no generated game.
- Tests depend on `design/game-graph.json`, so narrative-core tests are not pure unit tests. They are fixture/integration tests.
- The test rules are stronger than the implemented test suite.

Error handling:

- Narrative engine throws for invalid transition, which is reasonable.
- Event bus logs on every publish. That is noisy for runtime and tests.
- Config loader swallows fetch errors and falls back silently. Good for startup resilience, weak for diagnosis.
- Audio skill has good failure guidance, but actual enforcement is thin.
- Graph registry does not validate documents despite depending on a Zod schema package.

---

**Actual vs Perceived Complexity**

Actual executable complexity:

- Original: very low. Pixi app init, narrative-core package, audio pipeline tool, MCP tool.
- Refactored: low-to-moderate. Small core scaffolding, audio manager, graph registry, tests, genre templates.

Perceived complexity:

- Very high. The process layer reads like a full studio operating system.

The biggest simplification opportunity is to treat this as three separable products:

1. Game runtime starter.
2. AI workflow/agent pack.
3. Auto-build generator.

Right now those are interleaved. A clean-room rebuild should make each independently understandable and testable.

---

**Top 5 Problems A Re-Architecture Must Solve**

1. **Markdown contracts are pretending to be executable systems.**
`/auto-build`, gates, validation, graph export, and retry behavior need real code or a much smaller stated contract.

2. **The default process is too heavy.**
36 agents and 81 commands create cognitive overhead before a user has a playable game.

3. **No typed generation pipeline.**
There is no canonical `GameSpec -> ResolvedSpec -> Plan -> FileSet -> VerificationResult` model.

4. **Runtime and process are misaligned.**
The docs promise scene stacks, asset manifests, graph APIs, Playwright smoke tests, audio lifecycle, config validation, and generated gameplay. The current runtime only partially implements those.

5. **Graph/narrative integration is mandatory before it has proven value.**
Narrative-core is useful, but requiring all gameplay systems to register topology risks boilerplate and fragile generated code.

---

**Top 5 Things To Preserve**

1. **Plain TypeScript state separated from PixiJS display objects.**
This is the best technical rule in the project.

2. **Small scene lifecycle contract.**
`enter()`, `update(dt)`, `exit()` with a stack manager is right for this domain.

3. **Spec-to-template auto-build concept.**
Ingesting a short idea or design doc and producing a runnable starter is the highest-value feature.

4. **Verification-driven generation.**
`tsc`, tests, and ideally browser smoke checks should be non-negotiable.

5. **Role-based critique, but not the full roster.**
Director/architect/producer/QA viewpoints are useful. Preserve the decision frameworks, collapse the agent count.

---

**Clean-Room Re-Architecture Direction**

Build a small, real kernel first.

Core packages:

- `@automagically/runtime`
- Pixi app bootstrap
- scene manager
- input manager
- game loop
- asset loader wrapper
- audio interface
- config loader with Zod validation

- `@automagically/spec`
- Zod schemas for `GameSpec`, `ResolvedGameSpec`, `GenrePattern`, `GeneratedFile`, `BuildPlan`
- migration/versioning for specs

- `@automagically/generator`
- deterministic template loading
- genre pattern resolution
- file generation into a temp workspace
- transactional write/apply
- verification pipeline

- `@automagically/narrative-core`
- keep, but make optional
- use for narrative games, quest graphs, state-machine visualization, and graph viewer exports
- do not require every gameplay system to depend on it

- `@automagically/agent-pack`
- reduced default agent set
- optional role packs
- commands generated from a smaller workflow catalog

Suggested `/auto-build` architecture:

1. Parse input into `RawSpec`.
2. Normalize into `ResolvedGameSpec` using explicit defaults.
3. Produce a `BuildPlan`.
4. Generate into `.automagically/tmp/build-[id]`.
5. Run:
- `npm run typecheck`
- `npm test`
- browser smoke test if Playwright is installed
6. Present diff/summary.
7. Apply transactionally to repo.
8. Write `docs/build-summary-[date].md`.

Suggested default command set:

- `/start`
- `/auto-build`
- `/iterate`
- `/design-review`
- `/architecture-review`
- `/test`
- `/ship-check`

Everything else should be discoverable as optional advanced workflows, not front-loaded.

The clean-room goal should not be “a full AI game studio.” It should be: **a reliable browser-game generator and iteration loop with enough expert review to prevent bad defaults.** The studio metaphor can remain as UX, but the architecture should be a typed generator plus a small runtime, not a large prompt hierarchy.