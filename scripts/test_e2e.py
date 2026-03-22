#!/usr/bin/env python3
"""End-to-end demo script for 0xAUTEUR.

Runs the full pipeline:
  1. AUTEUR MCP: analyse_brief → propose_visual_language → plan_shots
  2. AUTEUR MCP: generate_video (enforcement gate → video URL)
  3. IPFS pin the video URL
  4. Mint NFT via Rare Protocol / direct cast
  5. spend() on 0xAUTEUR.sol
  6. Bid simulation → tension adjust → recompose → generate_video again
  7. ERC-8183 agent lifecycle

Usage:
  source .env && python3 scripts/test_e2e.py
  source .env && python3 scripts/test_e2e.py --video   # require real video gen
"""

import json
import os
import subprocess
import sys
import time
import hashlib
import asyncio

# ── Config ────────────────────────────────────────────────────────────────────

AUTEUR_CONTRACT = os.environ.get("AUTEUR_CONTRACT_ADDRESS", "0x4473350125F66FC17988589A9a948514866bfdE3")
AUTEURAGENT_CONTRACT = os.environ.get("AUTEURAGENT_CONTRACT_ADDRESS", "0xc7cAF559a5cF8a3C85cA9acEE4A0010e666871B3")
RARE_NFT_CONTRACT = os.environ.get("RARE_NFT_CONTRACT_ADDRESS", "0x24D258b4249051Dbfa06b1526Bf847062562f126")
RPC = "https://sepolia.base.org"
CAST = os.path.expanduser("~/.foundry/bin/cast")
IPFS_BIN = os.environ.get("IPFS_BIN", "/tmp/kubo/ipfs")
IPFS_PATH = os.environ.get("IPFS_PATH", "/tmp/ipfs-repo")
AUTEUR_BIN = os.path.expanduser("~/.local/bin/auteur")

BRIEF = "a woman pressing her palm flat against cold glass, not looking at the man behind it. Warm amber key light."
MODEL = "kling-3.0"

REQUIRE_VIDEO = "--video" in sys.argv

results = {}
nonce = None


# ── Helpers (nonce tracking, cast, ipfs) ─────────────────────────────────────

def get_nonce():
    pk = os.environ.get("DEPLOYER_PRIVATE_KEY", "")
    if not pk:
        return 0
    r = subprocess.run(
        [CAST, "nonce", "0xBAc0d61DE2B52Dbb7C6800210bf8A54388032109",
         "--rpc-url", RPC],
        capture_output=True, text=True, timeout=15,
    )
    try:
        return int(r.stdout.strip().split()[0])
    except (ValueError, IndexError):
        return 0


def next_nonce():
    global nonce
    if nonce is None:
        nonce = get_nonce()
    n = nonce
    nonce += 1
    return n


def cast_send(contract, sig, *args, value=""):
    global nonce
    args_str = " ".join(str(a) for a in args)
    value_str = f"--value {value}" if value else ""
    pk = os.environ.get("DEPLOYER_PRIVATE_KEY", "")
    n = next_nonce()
    cmd = f'{CAST} send {contract} "{sig}" {args_str} {value_str} --rpc-url {RPC} --private-key {pk} --nonce {n} --legacy'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    if result.returncode != 0 and "nonce too low" in result.stderr:
        nonce = get_nonce()
        n = next_nonce()
        cmd = cmd.replace(f"--nonce {n-1}", f"--nonce {n}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    return result


def cast_call(contract, sig, *args):
    args_str = " ".join(str(a) for a in args)
    cmd = f'{CAST} call {contract} "{sig}" {args_str} --rpc-url {RPC}'
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)


def ipfs_add(data_str):
    tmp = f"/tmp/ipfs_e2e_{hashlib.sha256(data_str.encode()).hexdigest()[:8]}.json"
    with open(tmp, "w") as f:
        f.write(data_str)
    result = subprocess.run(
        [IPFS_BIN, "add", "-Q", tmp],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, "IPFS_PATH": IPFS_PATH},
    )
    os.unlink(tmp)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def extract_tx_hash(output):
    for line in output.split("\n"):
        if "transactionHash" in line:
            parts = line.split()
            return parts[-1] if parts else None
    return None


# ── AUTEUR MCP Client ─────────────────────────────────────────────────────────

class AuteurMCP:
    """JSON-RPC client for the AUTEUR MCP server over stdio."""

    def __init__(self):
        self.proc = None
        self.request_id = 0

    def start(self):
        env = {**os.environ}
        # Ensure AUTEUR .env is loaded for KIE_API_KEY
        auteur_env_path = os.path.expanduser("~/AUTEUR/.env")
        if os.path.exists(auteur_env_path):
            with open(auteur_env_path) as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, _, v = line.partition("=")
                        if k in ("KIE_API_KEY", "FAL_KEY", "GEMINI_API_KEY",
                                 "BROWSER_USE_API_KEY", "BROWSER_USE_ENABLED"):
                            env[k] = v
        self.proc = subprocess.Popen(
            [AUTEUR_BIN, "serve", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        # Read the startup banner (server prints to stderr)
        time.sleep(1)

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=5)
            self.proc = None

    def _send(self, method: str, params: dict = None) -> dict:
        self.request_id += 1
        msg = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        if params:
            msg["params"] = params

        msg_str = json.dumps(msg)
        header = f"Content-Length: {len(msg_str)}\r\n\r\n"

        try:
            self.proc.stdin.write(header.encode())
            self.proc.stdin.write(msg_str.encode())
            self.proc.stdin.flush()

            # Read response
            response_header = b""
            while b"\r\n\r\n" not in response_header:
                chunk = self.proc.stdout.read(1)
                if not chunk:
                    break
                response_header += chunk

            if b"\r\n\r\n" not in response_header:
                return {"error": "No response header from MCP server"}

            header_str = response_header.decode()
            content_length = 0
            for line in header_str.split("\r\n"):
                if line.lower().startswith("content-length:"):
                    content_length = int(line.split(":")[1].strip())

            body = b""
            while len(body) < content_length:
                chunk = self.proc.stdout.read(content_length - len(body))
                if not chunk:
                    break
                body += chunk

            return json.loads(body.decode())
        except Exception as e:
            return {"error": str(e)}

    def call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        result = self._send("tools/call", {
            "name": tool_name,
            "arguments": arguments or {},
        })
        if "error" in result:
            return {"status": "error", "error": result["error"]}
        # MCP returns content as a list of text blocks
        content = result.get("result", {}).get("content", [])
        for block in content:
            if block.get("type") == "text":
                try:
                    return json.loads(block["text"])
                except json.JSONDecodeError:
                    return {"status": "ok", "raw": block["text"]}
        return {"status": "error", "error": "No text content in MCP response"}


def generate_shot_spec(brief, beat=1, tension=0.5):
    """Fallback: generate a demo ShotSpec locally (for when AUTEUR MCP is unavailable)."""
    shot_id = hashlib.sha256(f"{brief}_{beat}_{time.time()}".encode()).hexdigest()[:16]
    return {
        "shot_id": shot_id,
        "brief": brief,
        "beat_position": beat,
        "tension_level": round(tension, 2),
        "scene_description": brief,
        "dp_blend": "arri_logc_to_rec709",
        "meisner_note": f"Beat {beat}: emotional truth from brief",
        "composition_id": shot_id[:8],
        "timestamp": int(time.time()),
        "camera": {
            "movement": "static" if beat <= 3 else ("dolly_in" if tension > 0.6 else "handheld"),
            "angle": "eye_level" if beat <= 5 else ("low_angle" if tension > 0.7 else "high_angle"),
            "lens": "50mm" if tension < 0.5 else ("85mm" if tension > 0.7 else "35mm"),
        },
        "lighting": {
            "key_temp": "3200K" if tension > 0.6 else "5600K",
            "ratio": round(2.0 + tension * 6.0, 1),
            "motivation": "practical" if beat <= 4 else "dramatic",
        },
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    global nonce

    print("=" * 60)
    print("0xAUTEUR END-TO-END DEMO")
    print("=" * 60)

    mcp = AuteurMCP()
    mcp_available = False
    project_id = None

    # Try to start AUTEUR MCP
    print("\n[0/8] Starting AUTEUR MCP server...")
    try:
        mcp.start()
        mcp_available = True
        print("  AUTEUR MCP server started")
    except Exception as e:
        print(f"  WARNING: Could not start AUTEUR MCP: {e}")
        if REQUIRE_VIDEO:
            print("  FATAL: --video flag requires AUTEUR MCP. Exiting.")
            sys.exit(1)
        print("  Falling back to local ShotSpec generation.")

    # Step 1: Check budget
    print("\n[1/8] Checking budget...")
    r = cast_call(AUTEUR_CONTRACT, "budgets(address)(uint256)", "0xBAc0d61DE2B52Dbb7C6800210bf8A54388032109")
    budget = int(r.stdout.strip().split()[0]) if r.stdout.strip() else 0
    print(f"  Budget: {budget / 1e18} ETH")

    # Step 2: Create shot via AUTEUR MCP
    print("\n[2/8] Generating shot via AUTEUR MCP...")
    video_url = None

    if mcp_available:
        # 2a: analyse_brief
        r = mcp.call_tool("analyse_brief", {
            "logline": BRIEF,
            "description": BRIEF,
            "mood": "contemplative, tense",
        })
        print(f"  analyse_brief: {json.dumps(r, indent=2)[:200]}")
        project_id = r.get("project_id", "")

        if project_id:
            # 2b: propose_visual_language
            r = mcp.call_tool("propose_visual_language", {
                "project_id": project_id,
                "style_description": "warm amber key light, cold glass reflections, shallow depth of field",
                "aspect_ratio": "16:9",
            })
            print(f"  propose_visual_language: status={r.get('status', '?')}")

            # 2c: plan_shots
            r = mcp.call_tool("plan_shots", {
                "project_id": project_id,
                "scene_description": BRIEF,
                "pacing": "establishing_to_intimate",
            })
            print(f"  plan_shots: status={r.get('status', '?')}, scenes={r.get('scene_count', '?')}")

            # 2d: generate_video (THE enforcement gate)
            print(f"  Calling generate_video (model={MODEL})...")
            r = mcp.call_tool("generate_video", {
                "project_id": project_id,
                "scene_index": 0,
                "shot_index": 0,
                "model": MODEL,
            })

            if r.get("status") == "generated":
                video_url = r.get("video_url", "")
                print(f"  VIDEO URL: {video_url}")
                results["video_url_1"] = video_url
            else:
                print(f"  generate_video status: {r.get('status')}")
                if r.get("error"):
                    print(f"  Error: {r['error']}")
                if REQUIRE_VIDEO:
                    print("  FATAL: --video flag requires successful generation. Exiting.")
                    mcp.stop()
                    sys.exit(1)

    if not video_url and not mcp_available:
        shot = generate_shot_spec(BRIEF, beat=1, tension=0.5)
        print(f"  (fallback) Shot ID: {shot['shot_id']}, Tension: {shot['tension_level']}")
        results["shot_spec_1"] = shot
    elif video_url:
        # Build a ShotSpec from the generation result for downstream use
        shot = generate_shot_spec(BRIEF, beat=1, tension=0.5)
        shot["video_url"] = video_url
        results["shot_spec_1"] = shot
    else:
        # MCP was available but generation failed — use local fallback
        shot = generate_shot_spec(BRIEF, beat=1, tension=0.5)
        print(f"  (fallback) Shot ID: {shot['shot_id']}")
        results["shot_spec_1"] = shot

    # Step 3: IPFS Pin
    print("\n[3/8] Pinning to IPFS...")
    shot_json = json.dumps(shot, separators=(",", ":"))
    cid = ipfs_add(shot_json)
    if cid:
        print(f"  CID: {cid}")
        results["ipfs_cid_1"] = cid
        shot["ipfs_cid"] = cid
    else:
        print("  FAILED to pin")
        mcp.stop()
        return

    # Step 4: Spend receipt for beat 1
    print("\n[4/8] SpendReceipt for beat 1...")
    r = cast_send(AUTEUR_CONTRACT,
        "spend(address,string,uint256,string)",
        "0xBAc0d61DE2B52Dbb7C6800210bf8A54388032109",
        shot["shot_id"], "1000000000000000", cid)
    tx = extract_tx_hash(r.stdout)
    if tx:
        results["spend_tx_1"] = tx
        print(f"  Spend TX: {tx}")
    else:
        print(f"  FAILED: {r.stderr[:100]}")

    # Step 5: Bid simulation → recomposition
    print("\n[5/8] Bid simulation & recomposition...")
    old_tension = shot["tension_level"]
    bid_eth, reserve_eth = 0.025, 0.01
    ratio = bid_eth / reserve_eth
    new_tension = min(old_tension + 0.15, 1.0) if ratio > 2.0 else old_tension + 0.05
    print(f"  Bid: {bid_eth} ETH vs Reserve: {reserve_eth} ETH (ratio: {ratio}x)")
    print(f"  Tension: {old_tension} -> {new_tension}")

    # Try AUTEUR MCP recomposition if available
    video_url_2 = None
    if mcp_available and project_id:
        print(f"  Calling generate_video for recomposed beat (model={MODEL})...")
        r = mcp.call_tool("generate_video", {
            "project_id": project_id,
            "scene_index": 0,
            "shot_index": 1,
            "model": MODEL,
        })
        if r.get("status") == "generated":
            video_url_2 = r.get("video_url", "")
            print(f"  VIDEO URL: {video_url_2}")
            results["video_url_2"] = video_url_2

    recomposed = generate_shot_spec(BRIEF, beat=2, tension=new_tension)
    recomposed["recomposed"] = True
    recomposed["recomposition_reason"] = f"bid_at_{ratio}x_reserve"
    if video_url_2:
        recomposed["video_url"] = video_url_2
    results["shot_spec_2"] = recomposed

    shot_json_2 = json.dumps(recomposed, separators=(",", ":"))
    cid_2 = ipfs_add(shot_json_2)
    if cid_2:
        print(f"  Recomposed CID: {cid_2}")
        results["ipfs_cid_2"] = cid_2

    print("\n[5b/8] SpendReceipt for recomposed beat 2...")
    r = cast_send(AUTEUR_CONTRACT,
        "spend(address,string,uint256,string)",
        "0xBAc0d61DE2B52Dbb7C6800210bf8A54388032109",
        recomposed["shot_id"], "1000000000000000", cid_2)
    tx = extract_tx_hash(r.stdout)
    if tx:
        results["spend_tx_2"] = tx
        print(f"  Spend TX: {tx}")
    else:
        print(f"  FAILED: {r.stderr[:100]}")

    # Step 6: ERC-8183 agent interaction
    print("\n[6/8] ERC-8183 Agent interaction...")

    r = cast_call(AUTEURAGENT_CONTRACT, "getCapabilities()(string[])")
    print(f"  Capabilities: {r.stdout.strip()}")

    r = cast_call(AUTEURAGENT_CONTRACT, "pricingModel()(uint256)")
    price = int(r.stdout.strip().split()[0]) if r.stdout.strip() else 0
    print(f"  Price per shot: {price / 1e18} ETH")

    expiry = int(time.time()) + 86400

    r = cast_send(AUTEURAGENT_CONTRACT,
        "createJob(address,address,address,uint256,uint256)",
        "0xBAc0d61DE2B52Dbb7C6800210bf8A54388032109",
        "0xBAc0d61DE2B52Dbb7C6800210bf8A54388032109",
        "0x0000000000000000000000000000000000000000",
        "1000000000000000", str(expiry))
    tx = extract_tx_hash(r.stdout)
    if tx:
        results["erc8183_createjob_tx"] = tx
        print(f"  CreateJob TX: {tx}")

    r = cast_send(AUTEURAGENT_CONTRACT, "fundJob(uint256)", "0", value="0.001ether")
    tx = extract_tx_hash(r.stdout)
    if tx:
        results["erc8183_fundjob_tx"] = tx
        print(f"  FundJob TX: {tx}")

    deliverable_hash = hashlib.sha256((cid + cid_2).encode()).hexdigest()[:64]
    deliverable_hash = deliverable_hash.ljust(64, "0")

    r = cast_send(AUTEURAGENT_CONTRACT,
        "submitWork(uint256,bytes32,string)",
        "0", f"0x{deliverable_hash}", cid_2)
    tx = extract_tx_hash(r.stdout)
    if tx:
        results["erc8183_submit_tx"] = tx
        print(f"  SubmitWork TX: {tx}")

    reason = "0x" + hashlib.sha256(b"demo_complete").hexdigest()[:64]
    r = cast_send(AUTEURAGENT_CONTRACT,
        "completeJob(uint256,bytes32)", "0", reason)
    tx = extract_tx_hash(r.stdout)
    if tx:
        results["erc8183_complete_tx"] = tx
        print(f"  CompleteJob TX: {tx}")

    # Step 7: Provider status
    if mcp_available:
        print("\n[7/8] AUTEUR provider status...")
        r = mcp.call_tool("provider_status")
        print(f"  Providers: {json.dumps(r, indent=2)[:300]}")
        results["provider_status"] = r

    # Step 8: Summary
    print("\n[8/8] Summary")
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)

    pipeline_used = "AUTEUR MCP (generate_video)" if video_url else "Local ShotSpec (fallback)"
    print(f"  Pipeline: {pipeline_used}")
    if video_url:
        print(f"  Video 1: {video_url}")
    if video_url_2:
        print(f"  Video 2: {video_url_2}")
    print(f"  CIDs: {results.get('ipfs_cid_1', '?')}, {results.get('ipfs_cid_2', '?')}")
    print(f"  ERC-8183: createJob={results.get('erc8183_createjob_tx', 'N/A')[:20]}...")

    print("\n" + json.dumps(results, indent=2, default=str))

    with open("/home/kt/0xAUTEUR/demo_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to demo_results.json")

    # Cleanup
    mcp.stop()


if __name__ == "__main__":
    main()
