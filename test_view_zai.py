#!/usr/bin/env python3
"""Test script to view ZAI-generated image"""

import requests
import json
import base64

url = "http://127.0.0.1:9000/mcp"

# Get asset info first to get the asset_id
request1 = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "list_assets",
        "arguments": {
            "limit": 5
        }
    }
}

print("Step 1: List assets to find ZAI image...")
try:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    response = requests.post(url, json=request1, headers=headers, timeout=60)
    print(f"Status: {response.status_code}")
    
    content = response.content.decode('utf-8')
    for line in content.split('\n'):
        if line.strip():
            try:
                data = json.loads(line)
                if 'result' in data:
                    result = data['result']
                    assets = result.get('assets', [])
                    zai_assets = [a for a in assets if 'ComfyUI_0059' in a.get('filename', '') or 'ComfyUI_00590' in a.get('filename', '') or 'ComfyUI_00591' in a.get('filename', '')]
                    
                    print(f"\nFound {len(zai_assets)} ZAI image(s)")
                    for asset in zai_assets:
                        print(f"  - Asset ID: {asset.get('asset_id', 'N/A')}")
                        print(f"    Filename: {asset.get('filename', 'N/A')}")
                        print(f"    URL: {asset.get('asset_url', 'N/A')}")
                        print(f"    Created: {asset.get('created_at', 'N/A')}")
                    
                    # Use the first ZAI asset for viewing
                    if zai_assets:
                        asset_id = zai_assets[0]['asset_id']
                        print(f"\nStep 2: View image with asset_id: {asset_id}")
                        
                        view_request = {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/call",
                            "params": {
                                "name": "view_image",
                                "arguments": {
                                    "asset_id": asset_id
                                }
                            }
                        }
                        
                        view_response = requests.post(url, json=view_request, headers=headers, timeout=60)
                        print(f"Status: {view_response.status_code}")
                        
                        view_content = view_response.content.decode('utf-8')
                        for vline in view_content.split('\n'):
                            if vline.strip():
                                try:
                                    vdata = json.loads(vline)
                                    if 'result' in vdata:
                                        vresult = vdata['result']
                                        if 'content' in vresult:
                                            for item in vresult['content']:
                                                if item.get('type') == 'image':
                                                    print(f"\n=== IMAGE FOUND ===")
                                                    if 'inline_preview_base64' in item:
                                                        preview = item['inline_preview_base64']
                                                        if len(preview) > 0:
                                                            print(f"Inline preview: {len(preview)} bytes (webp format)")
                                                            # Decode to verify it's valid
                                                            try:
                                                                image_data = base64.b64decode(preview)
                                                                print(f"Decoded image size: {len(image_data)} bytes")
                                                                print("\nImage successfully generated with ZAI workflow!")
                                                                break
                                                            except Exception as e:
                                                                print(f"Preview decode error: {e}")
                                break
                                except json.JSONDecodeError:
                                    pass
                        break
            except json.JSONDecodeError:
                pass
except Exception as e:
    print(f"Error: {e}")
