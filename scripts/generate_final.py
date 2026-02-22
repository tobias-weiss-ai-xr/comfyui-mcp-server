#!/usr/bin/env python3
import requests
import json
import time

url = "http://127.0.0.1:9000/mcp"

request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "generate_image",
        "arguments": {
            "prompt": "abstract geometric art composition with intersecting geometric forms, bold color blocks, architectural abstraction, minimal lines, conceptual design",
            "width": 1024,
            "height": 1024,
            "return_inline_preview": True
        }
    }
}

print("Requesting image generation...")
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

try:
    response = requests.post(url, json=request, headers=headers, timeout=120, stream=True)
    print(f"Response status: {response.status_code}")
    
    buffer = ""
    for chunk in response.iter_content(chunk_size=1024, decode_unicode=False):
        buffer += chunk.decode('utf-8', errors='ignore')
        
        lines = buffer.split('\n')
        for line in lines:
            if not line.strip():
                continue
            
            try:
                data = json.loads(line)
                
                if 'result' in data:
                    result = data['result']
                    
                    if 'content' in result:
                        for item in result['content']:
                            if item.get('type') == 'image':
                                print(f"\n=== IMAGE GENERATED ===")
                                if 'inline_preview_base64' in item:
                                    preview = item['inline_preview_base64']
                                    print(f"Preview size: {len(preview)} bytes")
                                if 'asset_url' in item:
                                    print(f"Asset URL: {item['asset_url']}")
                                if 'asset_id' in item:
                                    print(f"Asset ID: {item['asset_id']}")
                                print("\nSuccessfully generated abstract art image!")
                                time.sleep(5)
                                exit(0)
                    
                    elif 'error' in result:
                        error = result['error']
                        print(f"\n=== ERROR ===")
                        print(f"Error: {error}")
                        exit(1)
                
                if lines:
                    buffer = '\n' + lines[-1]
                else:
                    buffer = '\n'
                
                if 'error' in str(buffer):
                    break
                    
    print("\nRequest sent. Waiting for generation...")
    time.sleep(10)
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)
