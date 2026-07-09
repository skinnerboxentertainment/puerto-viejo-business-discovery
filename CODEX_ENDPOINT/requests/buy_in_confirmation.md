# Codex Buy-In Confirmation

**Date:** 2026-07-08
**Reviewer:** OpenAI Codex CLI
**Documents reviewed:**

- `CODEX_ENDPOINT/SPEC.md` — Bidirectional Agent Session Protocol v2.0
- `CODEX_ENDPOINT/README.md` — IPC Hub v2 summary
- `CODEX_ENDPOINT/session_schema.md` — Session Schema v2

## Decision

I reviewed all three documents. I do **not** approve implementation as-is yet.

The architecture is sound and the v2 direction is a substantial improvement over the earlier fire-and-forget bridge, but there are several spec/schema contradictions that need to be resolved before implementation. These are mostly documentation-level fixes, but if left unresolved they will produce incompatible implementations.

## Required Changes Before Implementation

1. **Resolve the `awaiting_codex` vs `running_codex` prompt contradiction.**
   - `SPEC.md` says bridge preflight changes the session from `awaiting_codex` to `running_codex` before spawning Codex.
   - The trusted prompt rules then tell Codex to process only if the session state is `awaiting_codex`.
   - Required fix: Codex must either be instructed to accept `running_codex` as its expected input state, or the bridge must not transition to `running_codex` until after Codex has read the session. I recommend keeping the bridge transition and changing the prompt rule to: process only if latest entry is from `opencode`, state is `running_codex`, and `last_bridge_run_id` matches the current bridge run.

2. **Define whether `current_holder` and `needs_input` are derived compatibility fields or remove them.**
   - The change summary says the ambiguous `current_holder + needs_input` model was replaced by a single state enum.
   - `SPEC.md` and `session_schema.md` still require both fields.
   - Required fix: either remove them from required schema, or explicitly mark them as derived display/legacy fields with invariant mappings from `state`. If kept, validators must reject combinations inconsistent with `state`.

3. **Add explicit `status` and `state` consistency invariants.**
   - The docs define both fields but do not fully specify allowed combinations.
   - Required fix: define mappings such as `state in {creating, awaiting_codex, running_codex, awaiting_opencode} => status=active`, `state=completed => status=completed`, `state=cancelled => status=cancelled`, and `state=error => status=error`.

4. **Clarify who is allowed to mark `completed`.**
   - `SPEC.md` says "A session ends when one agent sets state: completed" and the prompt permits Codex to set `completed`.
   - The same section also says OpenCode is the final arbiter and should mark completion.
   - Required fix: choose one rule. I recommend Codex should normally return `awaiting_opencode` with a result/recommendation, and only OpenCode should transition to `completed`. If Codex-initiated completion is allowed, define exactly when and how OpenCode confirms or archives it.

5. **Fix artifact path rules for input/reference artifacts.**
   - The schema says all artifact paths must resolve under `artifacts_root` or an explicit allowlist.
   - The example session lists initial artifacts like `dark-fairy-tale-glamour-style-guide.md` outside `tasks/<id>/artifacts`.
   - Required fix: define an explicit `input_artifacts`/`references` mechanism, allowlist rules, or require all referenced files to be copied into `artifacts_root`.

6. **Tighten the atomic backup protocol.**
   - The current write sequence renames the current session file to `.bak.<revision>` before replacing the target with the temp file. That creates a window where the canonical session path is absent.
   - Required fix: prefer copying the current valid file to backup first, then `os.replace(temp, target)`, then prune backups. If renaming is retained, document the missing-target window and how readers handle it.

7. **Clarify lock ownership and Codex write permissions.**
   - Bridge acquires the lock and holds it while Codex runs, while Codex is also instructed to write the session file.
   - Required fix: state explicitly that the spawned Codex process writes under the bridge-owned lock and must not acquire its own lock, or require Codex to acquire/revalidate the same lock token. Include a `lock_token` or `bridge_run_id` check if the lock is meant to authorize the write.

8. **Fix lock TTL semantics for long Codex runs.**
   - Lock TTL is 30 seconds, but Codex timeout defaults to 300 seconds.
   - Required fix: define lock renewal/heartbeat while Codex is running, or make `running_codex` locks expire after at least `timeout + grace`. Otherwise a legitimate long run can be considered stale and broken by another process.

9. **Specify append-only validation by content hash, not only entry id.**
   - `session_schema.md` says prior entries unchanged "check by id", which is not sufficient; an entry can keep the same id and mutate content.
   - Required fix: bridge must snapshot prior entries before spawn and compare full canonical JSON for all prior entries after run.

10. **Resolve conversation turn semantics.**
    - `SPEC.md` says entry turns must be unique and strictly increasing.
    - `session_schema.md` says no gaps.
    - Required fix: decide whether gaps are invalid. I recommend requiring `entry.turn == index` and `session.turn == last_entry.turn` for simplicity.

11. **Correct the schema document implementation status.**
    - `session_schema.md` says "Spec status: Implemented in session_schema.py", but the reviewed directory does not contain `session_schema.py`.
    - Required fix: change this to planned/target implementation until the module exists.

12. **Define unknown-field preservation scope.**
    - The prompt tells Codex to preserve unknown fields, but Pydantic defaults often drop extras unless configured.
    - Required fix: specify `extra="allow"` for forward-compatible models, or remove the preservation requirement and make schema strict. I recommend allowing top-level and metadata extension fields only where explicitly intended.

13. **Make recovery from `error` precise.**
    - `ERROR -> AWAITING_CODEX` is allowed, but it is not specified whether the error turn is removed, superseded, or followed by a new OpenCode retry instruction.
    - Required fix: define retry behavior: preserve error turns, append a new OpenCode retry/review entry, clear `error`, set `status=active`, set `state=awaiting_codex`, increment revision.

14. **Decide whether `running_codex -> awaiting_codex` is actually valid.**
    - This transition is described as "Codex completed but set same state — continue", but post-run validation also requires exactly one Codex turn appended.
    - Required fix: define the use case. If it means Codex is requesting immediate re-entry without OpenCode review, that weakens the ping-pong ownership model and can create loops. I recommend removing this transition unless there is a concrete requirement.

## Buy-In Status

Conditional buy-in: I agree with the file-based session-state architecture, the state-machine approach, atomic write requirement, lock-file approach, schema-versioned migration path, and post-run validation model.

Green light is withheld until the required changes above are reconciled in the three foundational documents. After those updates, implementation can proceed against the revised spec.
