import subprocess, json
result = subprocess.run(["gh", "api", "repos/skinnerboxentertainment/mekatelyu/pages/builds", "--paginate"], capture_output=True, text=True)
data = json.loads(result.stdout)
for b in data[:5]:
    print(f"Status: {b['status']}")
    print(f"  Created: {b['created_at'][:19]}")
    err = b.get("error", {})
    if err:
        print(f"  Error: {err.get('message', '')}")
    print()
