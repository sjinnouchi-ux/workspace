import json
import os

# Step2: ~/.claude.json にSearch Console MCP追記
path = os.path.expanduser("~/.claude.json")

with open(path, "r") as f:
    config = json.load(f)

if "mcpServers" not in config:
    config["mcpServers"] = {}

config["mcpServers"]["gsc"] = {
    "command": "npx",
    "args": ["-y", "google-searchconsole-mcp"]
}

with open(path, "w") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✅ ~/.claude.json にSearch Console MCP追記完了")
print(json.dumps(config.get("mcpServers", {}), indent=2, ensure_ascii=False))
