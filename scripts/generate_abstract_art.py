#!/usr/bin/env python3
import requests
import json

url = "http://127.0.0.1:9000/mcp"

request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "generate_image",
        "arguments": {
            "prompt": "abstract geometric art composition with intersecting geometric forms, bold color blocks, architectural abstraction, minimal lines, conceptual design, ZAI style quality",
            "width": 1024,
            "height": 1024,
            "return_inline_preview": True,
        },
    },
}

print("Generating abstract art with standard workflow...")
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

try:
    response = requests.post(
        url, json=request, headers=headers, timeout=120, stream=True
    )
    print(f"Status Code: {response.status_code}")

    content = response.content.decode("utf-8")

    for line in content.split("\n"):
        if not line.strip():
            continue

        try:
            data = json.loads(line)

            if "result" in data:
                result = data["result"]

                if isinstance(result, dict):
                    # Check for asset_url
                    if "asset_url" in result:
                        print(f"\n=== SUCCESS ===")
                        print(f"Asset URL: {result['asset_url']}")
                        print(f"Asset ID: {result.get('asset_id', 'N/A')}")
                        print(f"Filename: {result.get('filename', 'N/A')}")
                        print(f"\nImage successfully generated!")
                        break

                    # Check for inline preview
                    if "content" in result:
                        for item in result["content"]:
                            if (
                                item.get("type") == "image"
                                and "inline_preview_base64" in item
                            ):
                                preview_size = len(item["inline_preview_base64"])
                                print(f"Inline preview size: {preview_size} bytes")
                                break

            elif "error" in data:
                error = data["error"]
                print(f"\n=== ERROR ===")
                print(f"Error: {error}")
                break

        except json.JSONDecodeError:
            continue

except Exception as e:
    print(f"Error: {e}")
