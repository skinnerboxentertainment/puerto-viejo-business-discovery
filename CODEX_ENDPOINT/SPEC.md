# Bidirectional Agent Session Protocol — SPEC v2.0

**Date:** 2026-07-08
**System:** OpenCode (orchestrator) ↔ OpenAI Codex CLI (worker)
**Channel:** File-based session state + `codex exec` subprocess
**Goal:** Reliable ping-pong iteration so two agents can hand a task back and forth to completion without persistent servers, MCP, or daemons.

---

## 1. Problem

Current `codex_bridge.py` is **fire-and-forget**:

```
OpenCode ──spawns──> Codex exec ──exits──> OpenCode reads stdout
```

This works for one-shot tasks but breaks when:
- Codex produces a result and needs review before proceeding
- OpenCode needs to say "good, but change X" and re-engage Codex
- A complex creative pipeline requires multiple rounds of generation → critique → refine

**Requirement:** Both agents must pass work back and forth within a single logical session, surviving process restarts between turns. This must work on Windows without servers, daemons, or port allocation.

---

## 2. Architecture Decision

| Considered | Verdict |
|---|---|
| MCP server (`codex mcp-server`) | Rejected — experimental, unstable on Windows, one-directional |
| HTTP/WebSocket server | Rejected — adds daemon lifecycle, port conflicts, firewall issues |
| **File-based session state** | **Chosen** — zero daemons, survives restarts, trivially debuggable, works on any OS |

**Principle:** The session file IS the connection. Both agents read/write it. A state machine in the session file determines who holds the ball.

**Critical constraint:** File writes are NOT transactional. The protocol must enforce atomicity via temp-file-write + validate + rename pattern, revision checks, and lock files to prevent corruption and concurrent-write conflicts.

---

## 3. Directory Layout

```
openCodeEndpoint/CODEX_ENDPOINT/
├── SPEC.md                     ← This document
├── README.md                   ← Protocol summary + quickstart
├── session_schema.md           ← JSON Schema and Pydantic model docs
├── session_lib.py              ← Python module: atomic IO, locks, validation
├── session_schema.py           ← Python module: Pydantic models, state machine
├── session_orchestrator.py     ← OpenCode-side CLI for session lifecycle
├── codex_bridge.py             ← Thin wrapper spawning codex exec
├── sessions/                   ← Ping-pong state files (the ball)
│   ├── archive/                ← Completed sessions
│   ├── corrupt/                ← Unparseable session files for forensics
│   └── *.json
├── locks/                      ← Session lock files (pid-based, TTL)
├── inbox/                      ← OpenCode → Codex task requests
│   └── *.json
├── outbox/                     ← Codex → OpenCode task responses
│   └── *.json
├── requests/                   ← Long-form research/investigation briefs
│   └── *.md
├── responses/                  ← Final results and audit trail
│   ├── *.md
│   └── bridge_*.json
└── tasks/                      ← Work artifacts per session
    └── <session_id>/
        ├── artifacts/
        └── logs/
```

---

## 4. Session File Schema

File: `sessions/<session_id>.json`

### 4.1 Top-Level Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `schema_version` | string | yes | Schema version for migration support. Current: `"2.0"` |
| `session_id` | string | yes | UUID v4, 8-char short form `^[A-Za-z0-9_-]{8,64}$` |
| `created_at` | ISO-8601 | yes | Session creation timestamp |
| `updated_at` | ISO-8601 | yes | Last modification timestamp |
| `title` | string | yes | Human-readable session name |
| `description` | string | yes | High-level goal |
| `workdir` | string | yes | Project root path (resolved, absolute) |
| `artifacts_root` | string | yes | Canonical artifact directory: `tasks/<session_id>/artifacts/` |
| `references_root` | string | no | Canonical input references directory: `tasks/<session_id>/references/`. If set, referenced input files are copied here at session creation. Artifact paths resolving here are also allowlisted |
| `status` | string | yes | Derived from `state`. See §4.6 for consistency invariants |
| `state` | string | yes | Current protocol state (see §4.2). This is the single source of truth |
| `turn` | integer | yes | Monotonically increasing turn counter. Always equals `len(conversation) - 1` |
| `revision` | integer | yes | Monotonically increasing revision counter for compare-and-swap |
| `current_holder` | string | yes | **Derived display field.** Maps from `state`: see §4.7 for invariants. Must be kept consistent with `state` |
| `needs_input` | boolean | yes | **Derived display field.** Maps from `state`: see §4.7 for invariants. Must be kept consistent with `state` |
| `last_bridge_run_id` | string | no | Bridge run ID that last modified this session |
| `parent_session_id` | string | no | If this is a retry/recovery fork, the original session ID |
| `completed_at` | ISO-8601 | no | When the session reached terminal state |
| `cancelled_at` | ISO-8601 | no | When the session was cancelled |
| `conversation` | array | yes | Append-only log of turns (§4.3) |
| `error` | object | no | Structured error info (§4.4). Cleared on successful recovery |
| `config` | object | yes | Codex execution configuration (§4.5) |

### 4.2 State Machine

The session state is controlled by a single `state` field — this is the **single source of truth**.
`current_holder` and `needs_input` are derived display fields.

Valid transitions:

```
                    ┌─────────────┐
                    │  creating    │  (transient — session being initialized)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
              ┌────▶│ awaiting_   │◀──── OpenCode creates session,
              │     │ codex       │       appends initial instruction
              │     └──────┬──────┘
              │            │
              │     ┌──────▼──────┐
              │     │ running_    │  (transient — bridge has spawned codex exec)
              │     │ codex       │       lock held by bridge
              │     └──────┬──────┘
              │            │
              │     ┌──────▼──────────┐
              │     │ awaiting_       │◀──── Codex appended its turn,
              │     │ opencode        │       ball is with OpenCode
              │     └──────┬──────────┘
              │            │
              │     ┌──────▼──────┐
              │     │ awaiting_   │  OpenCode reviewed and appended
              └─────┤ codex       │  → loop back
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼─────┐ ┌───▼────┐ ┌────▼─────┐
       │ completed   │ │ error  │ │ cancelled │
       └────────────┘ └────────┘ └──────────┘
```

**State descriptions:**

| State | Meaning | Who acts | Codex spawnable? |
|---|---|---|---|
| `creating` | Session being initialized by OpenCode | OpenCode | No |
| `awaiting_codex` | OpenCode has appended a turn; Codex should process it | Codex | Yes |
| `running_codex` | Bridge has spawned codex exec; waiting for completion. Lock held | Codex (spawned) | No (already running) |
| `awaiting_opencode` | Codex has produced output; OpenCode should review | OpenCode | No |
| `completed` | Task is done | Neither | No |
| `error` | Something went wrong; may be recoverable | OpenCode | No |
| `cancelled` | Explicit cancellation | Either | No |

**Allowed state transitions (enforced by validator):**

- `creating` → `awaiting_codex` (session initialized with instruction)
- `awaiting_codex` → `running_codex` (bridge spawns Codex)
- `running_codex` → `awaiting_opencode` (Codex completed; wants review)
- `running_codex` → `error` (Codex crashed, timeout, or protocol violation)
- `running_codex` → `cancelled` (bridge timeout forced cancel)
- `awaiting_opencode` → `awaiting_codex` (OpenCode appends next instruction)
- `awaiting_opencode` → `completed` (OpenCode satisfied — only OpenCode can mark completion)
- `awaiting_opencode` → `cancelled` (OpenCode cancels)
- `any` → `cancelled` (explicit cancel by OpenCode)
- `error` → `awaiting_codex` (retry from last valid OpenCode instruction — see §13)

### 4.3 Conversation Entry Schema

```jsonc
{
  "id": "string",                   // Stable unique ID per entry (UUID v4, 8-char)
  "turn": 0,                        // Strictly increasing, always equals conversation index
  "from": "opencode",               // "opencode" | "codex"
  "type": "instruction",            // "instruction" | "result" | "review" | "request"
  "message": "string",              // Full message content (no truncation)
  "artifacts": [                    // Paths to files produced this turn
    {
      "path": "tasks/<id>/artifacts/file.png",
      "hash": "sha256:...",         // Optional content hash
      "mime": "image/png"           // Optional MIME type
    }
  ],
  "timestamp": "ISO-8601",
  "bridge_run_id": "string",        // Optional: bridge_*.json id that produced this
  "metadata": {}
}
```

**Invariants (enforced by validator):**
- `turn` must equal the entry's index in the conversation array (no gaps, no duplicates)
- `session.turn` must equal `conversation[-1].turn` (last entry's turn is the session turn)
- `from` must be a valid agent name
- `type` must be a valid entry type
- Prior entries are append-only: never modified, deleted, or reordered. Enforced by snapshotting prior entries' canonical JSON before the Codex spawn and comparing after the run
- `artifacts` paths may resolve under two roots: (a) `artifacts_root` for output artifacts, or (b) `references_root` for input/reference files. Paths outside both roots are rejected

### 4.4 Error Object

```jsonc
{
  "code": "codex_timeout",
  "message": "Codex exec timed out after 300s",
  "recoverable": true,
  "bridge_log": "bridge_a1b2c3d4.json",
  "stderr_log": "tasks/<id>/logs/codex_stderr.txt",
  "timestamp": "ISO-8601"
}
```

Error codes: `codex_timeout`, `codex_crash`, `codex_protocol_violation`, `session_corrupt`, `bridge_error`, `lock_failed`, `invalid_transition`

### 4.5 Config Object

```jsonc
{
  "sandbox": "danger-full-access",   // Sandbox level
  "timeout": 300,                    // Codex exec timeout in seconds
  "ephemeral": true,                 // Use --ephemeral flag
  "cooldown": 2.0                    // Seconds to wait between codex exec invocations
}
```

### 4.6 Status/State Consistency Invariants

`status` is derived from `state`. The following mapping is enforced:

| State | status | Notes |
|---|---|---|
| `creating` | `active` | Transient, session being set up |
| `awaiting_codex` | `active` | Waiting for Codex to process |
| `running_codex` | `active` | Codex exec in flight |
| `awaiting_opencode` | `active` | Waiting for OpenCode review |
| `completed` | `completed` | Terminal |
| `error` | `error` | Terminal (recoverable via retry) |
| `cancelled` | `cancelled` | Terminal |

The validator MUST reject any combination that violates this mapping.

### 4.7 Derived Display Field Invariants

`current_holder` and `needs_input` are derived display fields kept for compatibility.
Their values MUST be consistent with `state`:

| state | current_holder | needs_input |
|---|---|---|
| `creating` | `opencode` | `false` |
| `awaiting_codex` | `codex` | `false` |
| `running_codex` | `codex` | `false` |
| `awaiting_opencode` | `opencode` | `true` |
| `completed` | `opencode` | `false` |
| `error` | `opencode` | `false` |
| `cancelled` | `opencode` | `false` |

These fields SHOULD be auto-computed from `state` in the schema validator.
The validator MUST reject any combination that violates this mapping.

---

## 5. Atomic Write Protocol

Session file writes are NOT safe as simple overwrites. The following sequence MUST be used:

### 5.1 Write Sequence

1. Read current session and verify `revision`
2. **Copy** current session to `sessions/<id>.json.bak.<revision>` as a snapshot
3. Write updated JSON to `sessions/<id>.json.tmp.<pid>`
4. Flush and fsync the temp file
5. Validate the temp file by reading and parsing it
6. Atomically replace: `os.replace(temp_path, target_path)`
7. Prune old backups (keep last 5)
8. Optionally fsync the directory (platform-dependent)

**Note:** Step 2 copies before any destructive operation. The canonical path
(`sessions/<id>.json`) is never absent — it is either the old valid file (before
step 6) or the new valid file (after step 6). Readers can always find a valid
session at the canonical path.

### 5.2 Read with Automatic Recovery

On `JSONDecodeError` during read:
1. Log parse error details to a bridge log
2. Copy corrupt file to `sessions/corrupt/<id>.<timestamp>.json`
3. Restore latest valid `.bak` if present
4. If no valid `.bak`, create a minimal error session file pointing to the corrupt copy
5. Set session `state` to `error` with `error.code: "session_corrupt"`

### 5.3 Revision-Based Compare-and-Swap

Every read must capture the current `revision`. Every write must check that the
file's `revision` has not changed since read. If it has, the write is stale and
must be retried (re-read, merge, increment revision, retry).

---

## 6. Lock Protocol

### 6.1 Lock File Location

Locks live in `locks/<session_id>.lock` as JSON files:

```jsonc
{
  "session_id": "a1b2c3d4",
  "pid": 12345,
  "hostname": "DESKTOP-ABC",
  "acquired_at": "ISO-8601",
  "expires_at": "ISO-8601",
  "purpose": "bridge_spawn | opencode_edit"
}
```

### 6.2 Lock Acquisition

1. Check if lock exists and is not expired
2. If expired (>30s stale), break lock and acquire
3. Write lock file atomically (same temp+rename pattern)
4. On failure, retry with exponential backoff (100ms, 200ms, 400ms, max 3s)
5. Release on completion: delete lock file

### 6.3 Stale Lock Detection

A lock is stale if `expires_at` is in the past. The stale threshold is 30 seconds
past `expires_at`. The lock's purpose field helps diagnose stale locks.

### 6.4 Lock TTL for Long Codex Runs

The lock TTL must cover the full Codex exec timeout. When setting the lock in
the bridge preflight, `expires_at` is set to `now + config.timeout + 60s` (grace
period). This prevents long-running Codex invocations from being falsely detected
as stale.

### 6.5 Lock Ownership and Codex Write Authorization

The bridge acquires the lock and holds it for the entire Codex exec lifecycle.
The spawned Codex process writes the session file under this lock — it does NOT
acquire its own lock. Instead, the bridge validates the write after completion.

The session `last_bridge_run_id` serves as the authorization token: any valid
post-run session update must have `last_bridge_run_id` matching the current
bridge run. This prevents a stale or concurrent Codex from writing a session
it wasn't authorized for.

### 6.6 Lock Renewal

If a Codex exec runs longer than expected, the bridge MAY renew the lock by
updating `expires_at` in the lock file every 60 seconds while the subprocess
is still alive. This is optional — setting TTL to `timeout + 60s` at acquisition
is sufficient for most cases.

---

## 7. Protocol Flow

### 7.1 Normal Ping-Pong

```
Turn  State              Action
────  ─────              ──────
  0   creating           OpenCode creates session.json with initial instruction
      awaiting_codex     OpenCode sets state=awaiting_codex, revision=1
                         Bridge acquires lock, sets state=running_codex
                         Bridge spawns codex exec --session <id>

  1   awaiting_opencode  Codex reads session, processes instruction
                         Codex appends turn, sets state=awaiting_opencode
                         Codex writes atomically, increments revision
                         Bridge validates post-state, releases lock
                         OpenCode reads session, reviews result

  2   awaiting_codex     OpenCode appends review+instruction
                         OpenCode sets state=awaiting_codex
                         Bridge acquires lock, sets state=running_codex
                         Bridge spawns codex exec again
                         ...repeat until completion

  N   completed          OpenCode satisfied, sets state=completed
                         Session archived to sessions/archive/
```

### 7.2 Completion

Only OpenCode can set `state: "completed"`. Codex must always return
`state: "awaiting_opencode"` with its result, even for the final turn.
OpenCode reviews the final result and marks completion.

**Rationale:** The orchestrator is the authority on whether a task is truly
done. Codex returning "completed" preemptively could close a session with
results the user hasn't reviewed.

On completion:
- OpenCode sets `state: "completed"`, `status: "completed"`
- Session moved to `sessions/archive/<id>.json`
- Lock file cleaned up
- Task artifacts MAY be archived or cleaned up

### 7.3 Cancellation

Either agent may set `state: "cancelled"`. The bridge should also set
`cancelled_at`.

### 7.4 Error Recovery

On unexpected exit, timeout, or protocol violation:
- Set `state: "error"` with structured `error` object
- Set `recoverable: true` if a retry from last valid OpenCode turn is possible
- Set `recoverable: false` if the session file is corrupt beyond repair

**Retry behavior (`error` → `awaiting_codex`):**
1. Preserve all existing conversation entries (including the failed Codex turn)
2. Append a new OpenCode retry/review entry with `type: "review"` and message indicating the retry
3. Clear the `error` object (set to null)
4. Set `state: "awaiting_codex"`, `status: "active"`
5. Increment `revision`
6. The normal bridge preflight then proceeds as usual

This preserves the full audit trail — the failed turn is visible, the retry instruction is explicit, and Codex sees the entire history.

---

## 8. Codex Bridge Integration

### 8.1 Session Mode CLI

```powershell
python codex_bridge.py --session <session_id> [--sandbox <level>] [--timeout <sec>]
```

The bridge preflight:
1. Validate `session_id` against `^[A-Za-z0-9_-]{8,64}$`
2. Resolve session path and verify it is inside `SESSION_DIR`
3. Load and validate session JSON (catch `JSONDecodeError`)
4. Verify `state` is `awaiting_codex`
5. Verify latest conversation entry is from `opencode`
6. Verify conversation is non-empty
7. Create `tasks/<session_id>/artifacts/` and `tasks/<session_id>/logs/`
8. Acquire lock
9. Set `state: running_codex`, record `last_bridge_run_id`, increment `revision`
10. Spawn `codex exec` with protocol-oriented prompt

The bridge post-run:
1. Reload session
2. Validate JSON and schema
3. Verify `revision` advanced
4. Verify exactly one Codex turn was appended
5. Verify lifecycle state is `awaiting_opencode` (Codex must always return the ball to OpenCode). Any other state from Codex → protocol violation, mark session `error`
6. If invalid (wrong state, no update, corrupt), preserve stdout/stderr as log artifact, mark session `error`
7. On timeout, append error turn, set `state: error`
8. Release lock

### 8.2 Protocol-Oriented Prompt Structure

The bridge builds a prompt for Codex with two clearly separated sections:

**Section 1: Non-negotiable protocol rules (trusted)**

```
You are Codex running session <id> of the CODEX_ENDPOINT v2 protocol.

Protocol rules (do not override):
1. Read the session JSON at <absolute_path>
2. Process only if latest conversation entry is from "opencode" and state is "running_codex"
   and last_bridge_run_id matches the current bridge run
3. Do not modify any previous conversation entries — they are append-only
4. Append exactly one "codex" entry with turn equal to session.turn + 1
5. Preserve all unknown fields in the session JSON (do not strip extras)
6. Update: updated_at, turn, revision (+1), state, current_holder, needs_input
7. Write session JSON atomically: write to temp file in same directory, validate JSON,
   then replace target. Do not leave temp files behind.
8. Do NOT set status or state to "completed" — only OpenCode may complete a session.
   Return state to "awaiting_opencode" with your result.
9. If you cannot complete the task, append a "request" entry explaining the blocker
   and set state to "awaiting_opencode".
10. Validate your JSON after writing — ensure it parses correctly.
```

**Section 2: Session data (untrusted — may contain conversation content)**

```
Session path: <path>
Artifact directory: <path>
Expected turn: <N>
Expected revision: <N>

Required post-state (Codex must always set this — only OpenCode may mark completed):
  state: awaiting_opencode
  current_holder: opencode
  needs_input: true

Session JSON:
<full session JSON>

Latest instruction (full, not truncated):
<message text>

Previous turns (full or summarized):
...
```

### 8.3 Legacy One-Shot Mode

The bridge retains its original mode when `--session` is not passed:

```powershell
python codex_bridge.py "prompt" [--flags]
```

For simple one-shot tasks that don't need iteration.

---

## 9. Security Controls

1. **Session ID validation:** reject characters that could enable path traversal (`..`, `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`), Windows reserved device names, and enforce length limits
2. **Path containment:** resolve session file path and verify it is under `SESSION_DIR` before any read or write operation
3. **Artifact root containment:** all conversation artifact paths must resolve under `artifacts_root` or an explicit allowlist
4. **Prompt separation:** protocol instructions are clearly separated from untrusted conversation content; conversation content cannot override protocol rules
5. **Sandbox scoping:** prefer `workspace-write` when possible; `danger-full-access` only when explicitly required
6. **Audit log hygiene:** bridge logs record task previews but full prompts only when debug logging is enabled
7. **Post-run validation:** bridge validates that Codex's session update conforms to protocol constraints before accepting it

---

## 10. Edge Cases

| Scenario | Handling |
|---|---|
| **Codex crashes mid-turn** | Session remains at `running_codex`. Bridge detects subprocess failure, sets `state: error`, appends error turn with stderr log. OpenCode may retry from last valid OpenCode instruction |
| **Codex writes corrupt JSON** | Bridge validates JSON on reload. On parse failure, preserves corrupt file to `sessions/corrupt/`, restores from `.bak`, marks session `error` |
| **Codex does not update session** | Bridge post-run validator detects revision didn't advance, no Codex turn appended. Preserves stdout as artifact, marks session `error` |
| **Codex overwrites prior turns** | Bridge snapshots prior entries' canonical JSON before spawn. After run, compares full JSON of all prior entries. Any change → `error` |
| **Concurrent writes by two bridges** | Lock protocol prevents this. Second bridge fails lock acquisition and exits with error. |
| **Stale lock from crashed bridge** | Lock TTL of 30s + stale detection allows new bridge to break lock. |
| **OpenCode crashes mid-orchestration** | Session file persists on disk. Manual inspection and recovery possible via `session_orchestrator.py recover` |
| **OneDrive file locking** | Add retry with backoff (3 attempts, 200ms delay) for read/write operations. Temp files on same volume as target |
| **Windows reserved names** | Reject session IDs and artifact filenames matching `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9` |
| **Long paths (>260 chars)** | Use `\\?\` prefix on Windows or keep session artifact paths under the limit. `artifacts_root` uses short relative paths |
| **Large conversations** | Summarize prior turns for context; include latest instruction in full. Cap total conversation entries at 100 for prompt size |
| **Session with empty conversation** | Bridge preflight rejects before spawning Codex |
| **Timeout** | Bridge kills subprocess, appends error turn, sets `state: error`, records `error.code: codex_timeout` |

---

## 11. Orchestrator Responsibilities

`session_orchestrator.py` manages the OpenCode side of the protocol:

| Command | Description |
|---|---|
| `create` | Creates session with initial OpenCode instruction and valid state |
| `next` | Appends OpenCode review/instruction, invokes bridge, waits for completion |
| `run` | Full loop: next → review → next → ... until completed |
| `status` | Prints concise state and latest conversation entry |
| `show` | Full session dump |
| `cancel` | Sets state to cancelled |
| `retry` | Retries failed Codex turn from last valid OpenCode instruction |
| `recover` | Restores from backup or marks corrupt sessions |
| `archive` | Moves completed sessions to archive |
| `list` | Lists all sessions with status filter |

---

## 12. Schema Validation

The `session_schema.py` module provides:

- Pydantic models for all session entities
- `validate(session: dict) -> Session` — parse and validate
- `validate_transition(before: Session, after: Session) -> bool` — state machine enforcement
- `validate_conversation(entries: list) -> bool` — append-only, monotonic turn check
- `validate_paths(session: Session) -> bool` — path containment checks
- `migrate(session: dict, target_version: str) -> dict` — schema migration

---

## 13. Implementation Order (Revised)

1. **Create `session_lib.py`** — atomic write helper, lock management, path validation
2. **Create `session_schema.py`** — Pydantic models, state machine, validation
3. **Migrate `sessions/2d0cc98d.json`** — either add initial instruction or mark as test fixture
4. **Update `codex_bridge.py`** — hardened preflight, protocol-oriented prompt, post-run validation
5. **Create `session_orchestrator.py`** — OpenCode-side CLI for session lifecycle
6. **Test with fake Codex executables** — simulate success, no-update, corrupt write, timeout, stale revision
7. **Live test with real Codex** — single round-trip, multi-turn ping-pong, error recovery
8. **Update `README.md`** — document the implementation
9. **Edge case hardening** — Windows path tests, concurrency tests, recovery tests

---

## 14. Example Session File (End State)

```json
{
  "schema_version": "2.0",
  "session_id": "a1b2c3d4",
  "created_at": "2026-07-08T11:00:00Z",
  "updated_at": "2026-07-08T11:15:00Z",
  "title": "Dark Fairy-Tale Glamour Image Generation",
  "description": "Apply style guide to Alice composition and generate image",
  "workdir": "C:\\Users\\oscar\\OneDrive\\Documents\\Zenescope Pin Up Art",
  "artifacts_root": "tasks/a1b2c3d4/artifacts",
  "status": "completed",
  "state": "completed",
  "turn": 2,
  "revision": 4,
  "current_holder": "opencode",
  "needs_input": false,
  "last_bridge_run_id": "d5bf2d54",
  "completed_at": "2026-07-08T11:15:00Z",
  "conversation": [
    {
      "id": "inst001",
      "turn": 0,
      "from": "opencode",
      "type": "instruction",
      "message": "Read the style guide and composition. Apply the style guide to the Alice composition. Generate an image.",
      "artifacts": [
        {"path": "dark-fairy-tale-glamour-style-guide.md", "mime": "text/markdown"},
        {"path": "areYouMadAtMe.md", "mime": "text/markdown"}
      ],
      "timestamp": "2026-07-08T11:00:00Z",
      "bridge_run_id": null
    },
    {
      "id": "res001",
      "turn": 1,
      "from": "codex",
      "type": "result",
      "message": "Generated image using Wonder Carnival palette. Alice replaced with Crimson Card Trickster, Cat replaced with Velvet Moon Imp.",
      "artifacts": [
        {"path": "tasks/a1b2c3d4/artifacts/generated.png", "mime": "image/png"}
      ],
      "timestamp": "2026-07-08T11:15:00Z",
      "metadata": {
        "model": "gpt-image-2",
        "size": "1024x1536"
      },
      "bridge_run_id": "d5bf2d54"
    }
  ],
  "config": {
    "sandbox": "danger-full-access",
    "timeout": 300,
    "ephemeral": true,
    "cooldown": 2.0
  }
}
```

---

*End of SPEC v2.0*
