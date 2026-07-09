# Session Schema — CODEX_ENDPOINT v2

**Version:** 2.0
**Spec status:** Planned — target implementation module is `session_schema.py` (Pydantic models)

---

## 1. Session Model

### 1.1 Top-Level

```python
class Session(BaseModel):
    model_config = {"extra": "allow"}  # Forward-compatible: preserve unknown top-level fields

    schema_version: Literal["2.0"]
    session_id: str              # Pattern: ^[A-Za-z0-9_-]{8,64}$
    created_at: datetime
    updated_at: datetime
    title: str                   # 1-200 chars
    description: str             # 1-2000 chars
    workdir: str                 # Resolved absolute path
    artifacts_root: str          # Relative to CODEX_ENDPOINT, e.g. "tasks/<id>/artifacts"
    references_root: str | None = None  # Optional: directory for input/reference files
    status: SessionStatus        # Derived from state (see §4.6 in SPEC)
    state: SessionState          # creating | awaiting_codex | running_codex | awaiting_opencode | completed | error | cancelled
    turn: int                    # >= 0, always equals len(conversation) - 1
    revision: int                # >= 1, monotonically increasing
    current_holder: AgentName    # Derived display field from state
    needs_input: bool            # Derived display field from state
    last_bridge_run_id: str | None  # 8-char hex, matches bridge_{id}.json
    parent_session_id: str | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    conversation: list[ConversationEntry]
    error: ErrorInfo | None
    config: SessionConfig
```

### 1.2 Enums

```python
class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

class SessionState(str, Enum):
    CREATING = "creating"
    AWAITING_CODEX = "awaiting_codex"
    RUNNING_CODEX = "running_codex"
    AWAITING_OPENCODE = "awaiting_opencode"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

class AgentName(str, Enum):
    OPENCODE = "opencode"
    CODEX = "codex"

class EntryType(str, Enum):
    INSTRUCTION = "instruction"
    RESULT = "result"
    REVIEW = "review"
    REQUEST = "request"
```

### 1.3 Conversation Entry

```python
class ArtifactRef(BaseModel):
    path: str                    # Must resolve under artifacts_root or references_root
    hash: str | None = None      # "sha256:<hex>"
    mime: str | None = None      # MIME type hint

class ConversationEntry(BaseModel):
    model_config = {"extra": "allow"}  # Preserve unknown fields in entries too

    id: str                      # Stable unique ID (UUID 8-char)
    turn: int                    # Must equal index in conversation array
    from_: AgentName             # Serialized as "from"
    type: EntryType
    message: str                 # Full, untruncated
    artifacts: list[ArtifactRef] = []
    timestamp: datetime
    bridge_run_id: str | None = None
    metadata: dict = {}
```

### 1.4 Error Info

```python
class ErrorInfo(BaseModel):
    code: str                    # see SPEC §4.4 for codes
    message: str
    recoverable: bool
    bridge_log: str | None = None
    stderr_log: str | None = None
    timestamp: datetime
```

### 1.5 Config

```python
class SessionConfig(BaseModel):
    sandbox: str = "danger-full-access"
    timeout: int = 300
    ephemeral: bool = True
    cooldown: float = 2.0
```

---

## 2. State Machine Validation

### 2.1 Allowed Transitions

```
CREATING         → AWAITING_CODEX
AWAITING_CODEX   → RUNNING_CODEX
RUNNING_CODEX    → AWAITING_OPENCODE
RUNNING_CODEX    → ERROR              (Crash, timeout, protocol violation)
AWAITING_OPENCODE → AWAITING_CODEX   (OpenCode appends next instruction)
AWAITING_OPENCODE → COMPLETED
AWAITING_OPENCODE → CANCELLED
any              → CANCELLED          (Explicit cancel by OpenCode)
ERROR            → AWAITING_CODEX     (Retry from last valid OpenCode turn)
```

### 2.2 Validation Logic

```python
ALLOWED_TRANSITIONS: dict[SessionState, set[SessionState]] = {
    SessionState.CREATING: {SessionState.AWAITING_CODEX},
    SessionState.AWAITING_CODEX: {SessionState.RUNNING_CODEX},
    SessionState.RUNNING_CODEX: {
        SessionState.AWAITING_OPENCODE,
        SessionState.ERROR,
        SessionState.CANCELLED,
    },
    SessionState.AWAITING_OPENCODE: {
        SessionState.AWAITING_CODEX,
        SessionState.COMPLETED,
        SessionState.CANCELLED,
    },
    SessionState.ERROR: {SessionState.AWAITING_CODEX, SessionState.CANCELLED},
    SessionState.COMPLETED: set(),
    SessionState.CANCELLED: set(),
}
```

---

## 3. Validation Rules

### 3.1 Session Integrity

- `session_id` matches `^[A-Za-z0-9_-]{8,64}$` and is not a Windows reserved name
- `revision` must be >= 1
- `turn` must be >= 0
- `updated_at` must be >= `created_at`
- `completed_at` must be set iff `status` is `completed`
- `artifacts_root` must resolve under `tasks/<session_id>/`

### 3.2 Conversation Integrity

- Entry `turn` must equal the entry's index in the conversation array (turn 0 = first entry, turn 1 = second, etc.)
- `session.turn` must equal `conversation[-1].turn`
- Entry `from_` must alternate between agents (no two consecutive entries from same agent)
- First entry must be from `opencode` with type `instruction`
- Entry `id` values must be unique
- `timestamp` must be monotonically increasing
- Prior entries must not change. Enforced by snapshotting all prior entries' canonical JSON before spawning Codex and comparing full JSON after the run. Any difference in any prior entry → protocol violation → `error`

### 3.3 Path Containment

- All artifact paths must resolve under `artifacts_root` (output artifacts) or `references_root` (input/reference files)
- `workdir` must be a valid absolute path or `.` (current directory)
- Artifact paths must not contain `..` segments after resolution
- At session creation, input reference files listed in the initial instruction are copied to `tasks/<session_id>/references/` and that directory becomes `references_root`

### 3.4 Post-Update Validation (Bridge)

After Codex writes back the session, the bridge validates:
1. `revision` increased by exactly 1
2. `conversation` length increased by exactly 1
3. New conversation entry `from_` is `codex`
4. New conversation entry `turn` equals previous `turn + 1`
5. Prior conversation entries unchanged (check by `id`)
6. `state` is `awaiting_opencode` (Codex must always return the ball to OpenCode — only OpenCode may set `completed`)
7. `updated_at` was updated
8. All artifact paths are contained

---

## 4. Lock Schema

```python
class LockInfo(BaseModel):
    session_id: str
    pid: int
    hostname: str
    acquired_at: datetime
    expires_at: datetime
    purpose: Literal["bridge_spawn", "opencode_edit"]
```

---

## 5. Migration

### From v1 (no schema_version) to v2

```python
def migrate_v1_to_v2(raw: dict) -> dict:
    raw["schema_version"] = "2.0"
    raw.setdefault("state", derive_state(raw))
    raw.setdefault("revision", 1)
    raw.setdefault("artifacts_root", f"tasks/{raw['session_id']}/artifacts")
    raw.setdefault("references_root", None)
    raw.setdefault("last_bridge_run_id", None)
    raw.setdefault("parent_session_id", None)
    raw.setdefault("completed_at", None)
    raw.setdefault("cancelled_at", None)
    raw.setdefault("error", None)
    # Derive display fields from state
    derive_display_fields(raw)
    # Derive status from state
    derive_status(raw)
    # Migrate conversation entries
    for i, entry in enumerate(raw.get("conversation", [])):
        entry.setdefault("id", f"e{i:04d}")
        entry.setdefault("bridge_run_id", None)
        # Wrap flat artifact strings in objects
        entry["artifacts"] = [
            {"path": a, "hash": None, "mime": None}
            if isinstance(a, str) else a
            for a in entry.get("artifacts", [])
        ]
    return raw
```
