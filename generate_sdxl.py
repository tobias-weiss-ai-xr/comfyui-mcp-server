import requests, json, time

url = "http://127.0.0.1:9000/mcp"

request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "generate_image",
        "arguments": {
            "prompt": "abstract geometric art composition with intersecting geometric forms, bold color blocks, architectural abstraction, minimal lines, conceptual design",
            "model": "sd_xl_base_1.0.safetensors",
            "width": 1024,
            "height": 1024,
            "return_inline_preview": True,
        },
    },
}

print("Requesting abstract art image generation...")
print("Model: sd_xl_base_1.0.safetensors")
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

try:
    response = requests.post(url, json=request, headers=headers, timeout=180)
    print(f"Status Code: {response.status_code}")

    buffer = ""
    for chunk in response.iter_content(chunk_size=1024, decode_unicode=False):
        buffer += chunk.decode("utf-8", errors="ignore")

    print(f"Full response:\n{buffer[:3000]}")

    # Check for result
    if '"asset_url":"' in buffer:
        import re

        match = re.search(r'"asset_url":"([^"]+)"', buffer)
        if match:
            print(f"\n=== SUCCESS ===")
            print(f"Asset URL: {match.group(1)}")
            print("\nSuccessfully generated abstract art image!")

    if '"error":"' in buffer:
        import re

        error_match = re.search(r'"error":\s*"([^"]+)\s*"', buffer)
        if error_match:
            print(f"\n=== ERROR ===")
            print(f"Error: {error_match.group(1)}")

    time.sleep(5)

except Exception as e:
    print(f"Error: {e}")
