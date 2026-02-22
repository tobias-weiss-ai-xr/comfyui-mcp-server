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
                "prompt": "abstract geometric art composition",
                "width": 1024,
                "height": 1024,
            },
            "return_inline_preview": True,
        },
    },
}

print("Sending request for zai_turbo workflow...")
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

try:
    response = requests.post(
        url, json=request, headers=headers, timeout=120, stream=True
    )
    print(f"Status Code: {response.status_code}")

    full_content = response.content.decode("utf-8")
    print(f"\nFull response (first 500 chars): {full_content[:500]}")

    # Look for image URL in the response
    if '"asset_url":"' in full_content:
        print("\n=== SUCCESS - ASSET URL FOUND ===")
        import re

        match = re.search(r'"asset_url":"([^"]+)"', full_content)
        if match:
            print(f"Asset URL: {match.group(1)}")

    # Also check for any errors
    if '"error":"' in full_content:
        print("\n=== ERROR DETECTED ===")
        import re

        error_match = re.search(r'"error":\s*"([^"]+)\s*"', full_content)
        if error_match:
            print(f"Error message: {error_match.group(1)}")

except Exception as e:
    print(f"Error: {e}")
