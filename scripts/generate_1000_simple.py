#!/usr/bin/env python3
import requests
import time
import sys

# 1000 diverse abstract art prompts
prompts = []
for i in range(1, 1001):
    prompts.append(
        f"abstract art pattern {i}: geometric forms with flowing colors and dynamic composition"
    )

url = "http://127.0.0.1:9000/mcp"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def generate_image(prompt, index):
    request = {
        "jsonrpc": "2.0",
        "id": index,
        "method": "tools/call",
        "params": {
            "name": "run_workflow",
            "arguments": {"workflow_id": "zai_small", "overrides": {"prompt": prompt}},
        },
    }

    try:
        response = requests.post(
            url, json=request, headers=headers, timeout=120, stream=True
        )
        response.raw.decode_content = True

        if response.status_code != 200:
            print(f"[{index}/1000] HTTP ERROR: {response.status_code}")
            return False

        # Read streaming response
        for line in response.iter_lines():
            line = line.decode("utf-8") if isinstance(line, bytes) else line
            if "event: message" in line:
                next_line = (
                    next(response.iter_lines()).decode("utf-8")
                    if isinstance(line, bytes)
                    else line
                )
                if next_line.startswith("data: "):
                    try:
                        data_str = next_line[6:]  # Remove 'data: ' prefix
                        data = json.loads(data_str)
                        if "result" in data:
                            result = data["result"]
                            if "content" in result and result["content"]:
                                content_text = result["content"][0].get("text", "")
                                if "asset_id" in content_text:
                                    print(f"[{index}/1000] SUCCESS")
                                    return True
                        elif "error" in data:
                            print(
                                f"[{index}/1000] ERROR: {data['error'].get('message', 'Unknown')}"
                            )
                            return False
                    except json.JSONDecodeError:
                        print(f"[{index}/1000] JSON ERROR: Could not parse response")
                        return False
    except Exception as e:
        print(f"[{index}/1000] EXCEPTION: {str(e)}")
        return False

    return False


def main():
    print("Starting generation of 1000 abstract art images...")
    print("This will take approximately 1.5-2 hours (~5 seconds per image)")
    print("=" * 60)

    success_count = 0
    fail_count = 0

    for i, prompt in enumerate(prompts, 1):
        success = generate_image(prompt, i)
        if success:
            success_count += 1
        else:
            fail_count += 1

        # Small delay between requests to avoid overwhelming the system
        time.sleep(0.5)

    print("=" * 60)
    print(f"Generation complete!")
    print(f"Success: {success_count}/1000")
    print(f"Failed: {fail_count}/1000")
    print(f"Total: {success_count + fail_count}/1000")


if __name__ == "__main__":
    main()
