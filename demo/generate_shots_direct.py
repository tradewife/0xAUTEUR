#!/usr/bin/env python3
"""Direct KIE API calls for demo shot generation."""

import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv("/home/kt/AUTEUR/.env")

KIE_API_KEY = os.getenv("KIE_API_KEY")
if not KIE_API_KEY:
    print("ERROR: KIE_API_KEY not found")
    exit(1)

output_dir = Path("/home/kt/0xAUTEUR/demo/shots_new")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"✓ KIEAPI Key: {KIE_API_KEY[:10]}...{KIE_API_KEY[-4:]}")
print(f"✓ Output: {output_dir}\n")

# Cinematographic prompts for each shot
shots = [
    {
        "num": 1,
        "prompt": "Extreme close-up shot of a human hand holding a fountain pen, writing a single line of text on cream-colored paper, then the pen lifts slowly away. Shot on 16mm film with Super 16 sensor. Single window light from upper camera left creates soft shadow gradient across the page. Shallow depth of field at T1.4 with 100mm macro lens, only the pen tip and paper in focus. Medium grain structure, warm analog color science. Intimate and tactile composition. The hand moves deliberately, pauses, then releases. Emmanuel Lubezki naturalistic lighting style. 4 seconds.",
        "duration": 4
    },
    {
        "num": 2,
        "prompt": "Handheld documentary-style sequence: harsh fluorescent lights illuminating a subway car interior at night with a lone figure, cut to 3am desk scene with laptop glow casting cold blue light on an exhausted face, cut to extreme close-up of tired eyes staring at a blank white screen. Shot on Super 35mm digital sensor, native ISO 3200, prominent coarse grain. 35mm lens at T2.8. Unstable handheld framing, natural motivated lighting only. Unglamorous, gritty, real. Hard light quality. Rachel Morrison documentary realism aesthetic. Fast cutting rhythm. 6 seconds.",
        "duration": 6
    },
    {
        "num": 3,
        "prompt": "Split-screen composition, aspect ratio 16:9.  On the left half: computer terminal window displaying bright green monospace code text against pure black background, lines of JSON scrolling rapidly with MCP tool calls visible. On the right half: a dramatic cinematic shot materializing - a silhouetted human figure backlit by warm golden hour sunlight creating a halo effect, deep cinematic shadows. Full-frame sensor, 50mm lens at T2.0. Mixed lighting - technical precision on left, Roger Deakins warm naturalism on right. Fine grain. The contrast between code and cinema. Static locked composition. 8 seconds.",
        "duration": 8
    },
    {
        "num": 4,
        "prompt": "Three ultra-clean information design shots, each 1.3 seconds: First frame shows white Courier monospace text displaying an IPFS hash 'Qm...' centered on pure black background. Second frame shows a web browser displaying Base Sepolia block explorer with green verification checkmark and confirmed transaction status. Third frame shows terminal output with white text 'SpendReceipt' heading and glowing yellow CID field below. Full-frame sensor, 50mm at T5.6, absolutely  no grain, clinical sharpness. Ambient flat lighting. Pure informational aesthetic. Title card precision. 4 seconds total.",
        "duration": 4
    },
    {
        "num": 5,
        "prompt": "Side-by-side comparison shot, split vertically. Left side shows a medium close-up portrait with standard lighting and framing. Right side shows the EXACT same subject but recomposed: dramatically closer framing cutting off top of head, much darker with intense hard shadows from low angle, increased contrast and tension. Below right frame, white text displays new IPFS CID hash. Full-frame sensor, left at 85mm T2.8, right at 85mm T1.4. Medium grain. Left has soft light, right has hard directional light. Hoyte van Hoytema high-contrast drama. Dolly push-in movement. Visual proof of creative iteration. 4 seconds.",
        "duration": 4
    },
    {
        "num": 6,
        "prompt": "Pure black screen with clean white sans-serif typography. Text appears in staggered sequence: '0xauteur.com' fades in first at top third, then 'Pay per shot. USDC. x402.' appears in center, then 'No account. No session. No UI.' materializes below, finally 'AUTEUR' in larger bold letters at bottom. Helvetica Neue font family. Perfect center alignment. Zero grain, maximum contrast. Minimal confident typographic end card. Static locked  frame. Title card aesthetic. 4 seconds.",
        "duration": 4
    }
]

def generate_video(prompt, duration, output_path):
    """Call KIE API to generate video with Kling 3.0"""
    
    print(f"  Calling KIE API (kling-3.0)...")
    print(f"  Prompt: {prompt[:80]}...")
    
    # KIE API endpoint - correct format from auteur/providers/kie.py
    url = "https://api.kie.ai/api/v1/jobs/createTask"
    
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Correct payload format for Kling 3.0
    payload = {
        "model": "kling-3.0/video",
        "input": {
            "prompt": prompt,
            "sound": False,
            "duration": str(duration),
            "aspect_ratio": "16:9",
            "mode": "pro",
            "multi_shots": False,
            "multi_prompt": []
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            
            # KIE returns {"code": 200, "data": {"taskId": "..."}}
            code = result.get("code")
            if code != 200:
                print(f"  ✗ API returned code {code}: {result.get('msg', 'Unknown error')}")
                return False
            
            data = result.get("data", {})
            task_id = data.get("taskId") or data.get("task_id")
            
            if task_id:
                print(f"  ✓ Generation started (task: {task_id[:16]}...)")
                return poll_task(task_id, output_path)
            else:
                print(f"  ✗ No task ID in response: {result}")
                return False
        else:
            print(f"  ✗ API error: {response.status_code}")
            print(f"    {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False

def poll_task(task_id, output_path, max_wait=600):
    """Poll KIE API for task completion"""
    print(f"  Polling task...")
    
    url = "https://api.kie.ai/api/v1/jobs/recordInfo"
    params = {"taskId": task_id}
    headers = {"Authorization": f"Bearer {KIE_API_KEY}"}
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                
                # KIE format: {"code": 200, "data": {"state": "SUCCESS", "resultJson": "..."}}
                if result.get("code") != 200:
                    print(f"  ✗ API error: {result.get('msg', 'Unknown')}")
                    return False
                
                data = result.get("data", {})
                state = data.get("state", "")
                
                if state != last_status:
                    print(f"  Status: {state}")
                    last_status = state
                
                # Check for success (case-insensitive)
                if state.lower() in ["success", "completed"]:
                    # Parse resultJson for video URL
                    result_json = data.get("resultJson", "{}")
                    try:
                        result_data = json.loads(result_json) if isinstance(result_json, str) else result_json
                        urls = result_data.get("resultUrls", [])
                        if urls and len(urls) > 0:
                            return download_video(urls[0], output_path)
                        else:
                            print(f"  ✗ No result URLs in response")
                            return False
                    except Exception as e:
                        print(f"  ✗ Failed to parse result: {e}")
                        return False
                        
                # Check for failure
                elif state.lower() in ["fail", "failed"]:
                    fail_msg = data.get("failMsg") or data.get("failCode") or "Unknown error"
                    print(f"  ✗ Task failed: {fail_msg}")
                    return False
                    
                # Still processing
                elif state.lower() in ["pending", "processing", "running"]:
                    time.sleep(15)  # Wait longer for video generation
                else:
                    print(f"  Unknown state: {state}, continuing to poll...")
                    time.sleep(15)
            else:
                print(f"  Poll HTTP error: {response.status_code}")
                time.sleep(15)
        except Exception as e:
            print(f"  Poll exception: {e}")
            time.sleep(15)
    
    elapsed = int(time.time() - start_time)
    print(f"  ✗ Timeout after {elapsed}s")
    return False

def download_video(url, output_path):
    """Download video from URL"""
    print(f"  Downloading from {url[:50]}...")
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  ✓ Downloaded {file_size:.1f} MB to {output_path.name}")
            return True
        else:
            print(f"  ✗ Download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Download exception: {e}")
        return False

# Generate each shot
print("="*60)
print("GENERATING DEMO SHOTS")
print("="*60)

results = []
for shot in shots:
    num = shot["num"]
    print(f"\nShot {num}/{len(shots)}")
    print("-" * 60)
    
    output_path = output_dir / f"shot_{num}.mp4"
    
    # Skip if already exists
    if output_path.exists():
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  ⊡ Already exists ({file_size:.1f} MB), skipping")
        results.append(True)
        continue
    
    success = generate_video(shot["prompt"], shot["duration"], output_path)
    results.append(success)
    
    if not success:
        print(f"  ⚠ Shot {num} failed, continuing...")
    
    # Brief pause between shots
    if num < len(shots):
        time.sleep(2)

print("\n" + "="*60)
print(f"COMPLETE: {sum(results)}/{len(results)} shots generated")
print("="*60)

if all(results):
    print("\n✓ All shots ready")
    print(f"\nNext: Assemble with voiceover using Remotion or ffmpeg")
    print(f"  Audio: /home/kt/0xAUTEUR/demo/voiceover.mp3")
    print(f"  Shots: {output_dir}/shot_*.mp4")
else:
    print("\n⚠ Some shots failed - manual intervention needed")
