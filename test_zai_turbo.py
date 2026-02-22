#!/usr/bin/env python3
"""Test script for zai_turbo workflow"""

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
                "prompt": "abstract geometric art composition with intersecting geometric forms, bold color blocks, architectural abstraction, minimal lines, conceptual design",
                "width": 1024,
                "height": 1024,
                "lora_name": "pixel_art_style_z_image_turbo.safetensors",
                "strength_model": 1.0,
                "lora_text": "",
            },
            "return_inline_preview": True,
        },
    },
}

print("Sending request to MCP server...")
print(f"Workflow ID: zai_turbo")

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

try:
    response = requests.post(
        url, json=request, headers=headers, timeout=120, stream=True
    )
    print(f"\nStatus Code: {response.status_code}")

    content = response.content.decode("utf-8")

    for line in content.split("\n"):
        if line.strip():
            try:
                data = json.loads(line)
                print(f"\nParsed: {json.dumps(data, indent=2)}")

                if "result" in data:
                    result = data["result"]
                    if isinstance(result, dict):
                        if "content" in result:
                            for item in result["content"]:
                                if item.get("type") == "text":
                                    print(f"  Text: {item.get('text', '')}")
                                if "asset_url" in result:
                                    print(f"\n=== SUCCESS ===")
                                    print(f"Asset URL: {result['asset_url']}")
                                    print(f"Asset ID: {result.get('asset_id', 'N/A')}")
                                    print(f"Filename: {result.get('filename', 'N/A')}")
                        elif "error" in result:
                            print(f"\n=== ERROR ===")
                            print(f"Error: {result['error']}")
            except json.JSONDecodeError:
                pass

except Exception as e:
    print(f"Error: {e}")
