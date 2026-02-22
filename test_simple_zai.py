#!/usr/bin/env python3
import requests
import json

url = "http://127.0.0.1:9000/mcp"
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "run_workflow",
        "arguments": {
            "workflow_id": "zai_turbo",
            "overrides": {
                "prompt": "abstract geometric art with bold shapes",
                "width": 1024,
                "height": 1024,
            },
            "return_inline_preview": True,
        },
    },
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

response = requests.post(url, json=request, headers=headers, timeout=120, stream=True)
print(f"Status: {response.status_code}")

content = response.content.decode("utf-8")
for line in content.split("\n"):
    if line.strip():
        data = json.loads(line)
        if "result" in data:
            result = data["result"]
            print(f"Result: {json.dumps(result, indent=2)}")
