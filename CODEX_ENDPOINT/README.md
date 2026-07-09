# CODEX_ENDPOINT — IPC Hub

**Version:** 2.0
**Protocol:** One-shot (legacy) + Session-based bidirectional (v2)

This directory is the shared communication channel between **OpenCode** (orchestrator) and **OpenAI Codex CLI** (worker). Everything is file-based — no servers, no daemons, no MCP.

---

## Directory Layout

```
CODEX_ENDPOINT/
├── README.md              ← This file: protocol, conventions
├── SPEC.md                ← Full session protocol specification (v2)
├── session_schema.md      ← JSON Schema / Pydantic model documentation
├── session_lib.py         ← Python module: atomic IO, locks, validation
├── session_schema.py      ← Python module: Pydantic models, state machine
├── session_orchestrator.py← OpenCode-side CLI for session lifecycle
├── codex_bridge.py        ← Thin wrapper spawning codex exec
├── sessions/              ← Ping-pong state files (the ball)
│   ├── archive/           ← Completed sessions
│   ├── corrupt/           ← Unparseable session files (forensics)
│   └── *.json
├── locks/                 ← Session lock files (pid-based, TTL)
├── inbox/                 ← OpenCode → Codex task requests
│   └── *.json
├── outbox/                ← Codex → OpenCode task responses
│   └── *.json
├── requests/              ← Long-form research/investigation briefs
│   └── *.md
├── responses/             ← Codex outputs & bridge audit logs
│   ├── *.md
│   └── bridge_*.json
└── tasks/                 ← Work artifacts per session
    └── <session_id>/
        ├── artifacts/
        └── logs/
```

---

## Protocol v1 — One-Shot (fire and forget)

For simple, non-iterative tasks:

```powershell
python codex_bridge.py "Your task" --sandbox danger-full-access --json
```

1. OpenCode passes a task prompt to `codex_bridge.py`
2. Bridge spawns `codex exec`, captures stdout, strips Codex header
3. Codex executes, writes results to `responses/` or `tasks/`
4. Each call is logged as `responses/bridge_{uuid}.json`

---

## Protocol v2 — Session Bidirectional (ping-pong)

For iterative tasks requiring back-and-forth refinement between agents:

```powershell
# Create a session
python session_orchestrator.py create --title "My Task" --description "Do X"

# Run the next turn (appends your instruction, invokes Codex)
python session_orchestrator.py next --session-id <id> --message "Now change Y"

# Check status
python session_orchestrator.py status --session-id <id>

# Retry a failed turn
python session_orchestrator.py retry --session-id <id>
```

### How it works

1. **OpenCode creates** a session file in `sessions/<session_id>.json`
2. **OpenCode appends** the initial instruction, sets `state: awaiting_codex`
3. **Bridge acquires** a lock, spawns `codex exec --session <id>`
4. **Codex reads** the session, processes instruction, appends its turn, writes atomically
5. **Bridge validates** the update, releases lock
6. **OpenCode reviews**, appends next instruction, loops back to step 3
7. **Repeat** until `state: completed`

See `SPEC.md` for the full protocol specification.

---

## Key Principles

- **No daemons, no servers** — everything is file-based
- **Session files survive crashes** — inspectable, recoverable
- **Atomic writes** — temp file + validate + rename pattern prevents corruption
- **Lock-based concurrency** — pid-based lock files prevent concurrent writes
- **State machine** — `state` field (awaiting_codex, running_codex, awaiting_opencode, completed, error, cancelled) replaces ambiguous boolean flags
- **Append-only conversation log** — full audit trail per session
- **Codex is not trusted** — bridge validates every session update before accepting it

---

## Quick Start

```powershell
# One-shot task
python codex_bridge.py "List all files in this directory" --sandbox read-only

# Session-based task
python session_orchestrator.py create --title "Generate Art" --description "Create a dark fairy-tale pin-up"
python session_orchestrator.py next --session-id <id> --message "Use Wonder Carnival palette"
```
