import json, subprocess

# Fix the session by cleaning artifacts
with open("CODEX_ENDPOINT/sessions/075f01a0.bak", encoding="utf-8") as f:
    raw = json.load(f)

for e in raw.get("conversation", []):
    e["artifacts"] = [{"path": a} if isinstance(a, str) else a for a in e.get("artifacts", [])]

raw["state"] = "awaiting_opencode"
raw["status"] = "active"
raw["error"] = None
raw["current_holder"] = "opencode"
raw["needs_input"] = True

with open("CODEX_ENDPOINT/sessions/075f01a0.json", "w", encoding="utf-8") as f:
    json.dump(raw, f, indent=2, ensure_ascii=False)

conv = raw.get("conversation", [])
if len(conv) > 1:
    print(conv[-1]["message"])
else:
    # Try to read from bridge log stdout
    with open("CODEX_ENDPOINT/responses/bridge_1d50ac8b.json", encoding="utf-8") as f:
        br = json.load(f)
    print("Bridge error:", br.get("error"))
    print("Bridge stdout:", br.get("stdout", "")[:500])
