"""AUTEUR MCP ↔ 0xAUTEUR onchain bridge.

Orchestrates the full pipeline:
1. Receive creative brief
2. Call AUTEUR MCP: analyse_brief → propose_visual_language → plan_shots
3. Call AUTEUR MCP: generate_video (enforcement gate → video URL)
4. Pin video metadata to IPFS
5. Mint NFT via Rare Protocol
6. Call spend() on 0xAUTEUR.sol
7. Return all receipts, CIDs, video URLs, and tx hashes

Every generation passes through AUTEUR's enforcement gate.
NEVER call image/video APIs directly.
"""

import json
import os
import subprocess
import time
from web3 import Web3
from eth_account import Account

BASE_SEPOLIA_RPC = os.environ.get("BASE_SEPOLIA_RPC", "https://sepolia.base.org")
PRIVATE_KEY = os.environ.get("DEPLOYER_PRIVATE_KEY", "")
AUTEUR_WALLET = os.environ.get("DEPLOYER_ADDRESS", "")
AUTEUR_CONTRACT = os.environ.get("AUTEUR_CONTRACT_ADDRESS", "")
AUTEURAGENT_CONTRACT = os.environ.get("AUTEURAGENT_CONTRACT_ADDRESS", "")

AUTEUR_ABI = json.loads('''[
    {"inputs":[{"internalType":"address","name":"agentId","type":"address"}],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"address","name":"agentId","type":"address"},{"internalType":"string","name":"taskId","type":"string"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"string","name":"cid","type":"string"}],"name":"spend","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"address","name":"agentId","type":"address"}],"name":"getLog","outputs":[{"components":[{"internalType":"string","name":"taskId","type":"string"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"string","name":"cid","type":"string"}],"internalType":"struct auteur.Receipt[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"budgets","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"receiptCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
]''')

AUTEURAGENT_ABI = json.loads('''[
    {"inputs":[],"name":"getCapabilities","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"pricingModel","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"provider","type":"address"},{"internalType":"address","name":"evaluator","type":"address"},{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"}],"name":"createJob","outputs":[{"internalType":"uint256","name":"jobId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"jobId","type":"uint256"}],"name":"fundJob","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"bytes32","name":"deliverableHash","type":"bytes32"},{"internalType":"string","name":"deliverableCid","type":"string"}],"name":"submitWork","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"jobId","type":"uint256"},{"internalType":"bytes32","name":"attestationReason","type":"bytes32"}],"name":"completeJob","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"jobId","type":"uint256"}],"name":"getJob","outputs":[{"internalType":"address","name":"client","type":"address"},{"internalType":"address","name":"provider","type":"address"},{"internalType":"address","name":"evaluator","type":"address"},{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"uint8","name":"status","type":"uint8"},{"internalType":"bytes32","name":"deliverableHash","type":"bytes32"},{"internalType":"string","name":"deliverableCid","type":"string"}],"stateMutability":"view","type":"function"}
]''')


def get_w3():
    """Get a connected Web3 instance."""
    w3 = Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))
    if not w3.is_connected():
        raise ConnectionError("Cannot connect to Base Sepolia RPC")
    return w3


def call_spend(task_id: str, amount: int, cid: str) -> dict:
    """Call spend() on the 0xAUTEUR contract.
    
    Args:
        task_id: Unique task identifier
        amount: Amount to spend (in wei)
        cid: IPFS CID of the ShotSpec
        
    Returns:
        {"status": "ok", "tx_hash": "..."} or {"status": "error", "error": "..."}
    """
    if not PRIVATE_KEY or not AUTEUR_CONTRACT:
        return {"status": "error", "error": "Missing DEPLOYER_PRIVATE_KEY or AUTEUR_CONTRACT_ADDRESS"}
    
    w3 = get_w3()
    account = Account.from_key(PRIVATE_KEY)
    
    try:
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(AUTEUR_CONTRACT),
            abi=AUTEUR_ABI,
        )
        
        tx = contract.functions.spend(
            Web3.to_checksum_address(AUTEUR_WALLET),
            task_id,
            amount,
            cid,
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 500000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 84532,
        })
        
        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            return {"status": "ok", "tx_hash": tx_hash.hex(), "block": receipt.blockNumber}
        else:
            return {"status": "error", "error": f"TX reverted: {tx_hash.hex()}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_budget() -> dict:
    """Check current budget on the 0xAUTEUR contract."""
    if not AUTEUR_CONTRACT:
        return {"status": "error", "error": "Missing AUTEUR_CONTRACT_ADDRESS"}
    
    w3 = get_w3()
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(AUTEUR_CONTRACT),
        abi=AUTEUR_ABI,
    )
    
    budget = contract.functions.budgets(Web3.to_checksum_address(AUTEUR_WALLET)).call()
    return {"status": "ok", "budget_wei": budget, "budget_eth": Web3.from_wei(budget, "ether")}


def get_capabilities() -> dict:
    """Query ERC-8183 agent capabilities."""
    if not AUTEURAGENT_CONTRACT:
        return {"status": "error", "error": "Missing AUTEURAGENT_CONTRACT_ADDRESS"}
    
    w3 = get_w3()
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(AUTEURAGENT_CONTRACT),
        abi=AUTEURAGENT_ABI,
    )
    
    caps = contract.functions.getCapabilities().call()
    price = contract.functions.pricingModel().call()
    return {
        "status": "ok",
        "capabilities": caps,
        "price_per_shot_wei": price,
        "price_per_shot_eth": str(Web3.from_wei(price, "ether")),
    }


class AuteurMCPClient:
    """JSON-RPC client for the AUTEUR MCP server over stdio."""

    def __init__(self):
        self.proc = None
        self.request_id = 0

    def start(self):
        env = {**os.environ}
        auteur_env_path = os.path.expanduser("~/AUTEUR/.env")
        if os.path.exists(auteur_env_path):
            with open(auteur_env_path) as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, _, v = line.partition("=")
                        if k in ("KIE_API_KEY", "FAL_KEY", "GEMINI_API_KEY"):
                            env[k] = v
        auteur_bin = os.path.expanduser("~/.local/bin/auteur")
        self.proc = subprocess.Popen(
            [auteur_bin, "serve", "--transport", "stdio"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=env,
        )
        time.sleep(1)

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=5)
            self.proc = None

    def _send(self, method, params=None):
        self.request_id += 1
        msg = {"jsonrpc": "2.0", "id": self.request_id, "method": method}
        if params:
            msg["params"] = params
        msg_str = json.dumps(msg)
        header = f"Content-Length: {len(msg_str)}\r\n\r\n"
        try:
            self.proc.stdin.write(header.encode())
            self.proc.stdin.write(msg_str.encode())
            self.proc.stdin.flush()
            rh = b""
            while b"\r\n\r\n" not in rh:
                c = self.proc.stdout.read(1)
                if not c:
                    break
                rh += c
            cl = 0
            for line in rh.decode().split("\r\n"):
                if line.lower().startswith("content-length:"):
                    cl = int(line.split(":")[1].strip())
            body = b""
            while len(body) < cl:
                c = self.proc.stdout.read(cl - len(body))
                if not c:
                    break
                body += c
            return json.loads(body.decode())
        except Exception as e:
            return {"error": str(e)}

    def call_tool(self, tool_name, arguments=None):
        result = self._send("tools/call", {"name": tool_name, "arguments": arguments or {}})
        if "error" in result:
            return {"status": "error", "error": result["error"]}
        content = result.get("result", {}).get("content", [])
        for block in content:
            if block.get("type") == "text":
                try:
                    return json.loads(block["text"])
                except json.JSONDecodeError:
                    return {"status": "ok", "raw": block["text"]}
        return {"status": "error", "error": "No text content in MCP response"}


def run_full_pipeline(brief: str, nft_address: str = "", model: str = "kling-3.0") -> dict:
    """Run the complete 0xAUTEUR pipeline via AUTEUR MCP.

    1. analyse_brief → propose_visual_language → plan_shots (AUTEUR MCP)
    2. generate_video (AUTEUR MCP enforcement gate → video URL)
    3. Pin metadata to IPFS
    4. Mint NFT (if nft_address provided)
    5. Call spend() on 0xAUTEUR.sol

    Falls back to local ShotSpec if AUTEUR MCP is unavailable.
    """
    mcp = AuteurMCPClient()
    try:
        mcp.start()
    except Exception as e:
        print(f"[bridge] WARNING: AUTEUR MCP unavailable: {e}")

    project_id = None
    video_url = None

    if mcp.proc and mcp.proc.poll() is None:
        # Step 1: analyse_brief
        r = mcp.call_tool("analyse_brief", {
            "logline": brief, "description": brief, "mood": "cinematic",
        })
        project_id = r.get("project_id", "")
        print(f"[bridge] analyse_brief: project_id={project_id}")

        if project_id:
            # Step 2: propose_visual_language
            mcp.call_tool("propose_visual_language", {
                "project_id": project_id,
                "style_description": "cinematic, warm amber key light",
                "aspect_ratio": "16:9",
            })

            # Step 3: plan_shots
            mcp.call_tool("plan_shots", {
                "project_id": project_id,
                "scene_description": brief,
                "pacing": "establishing_to_intimate",
            })

            # Step 4: generate_video (THE enforcement gate)
            r = mcp.call_tool("generate_video", {
                "project_id": project_id,
                "scene_index": 0, "shot_index": 0,
                "model": model,
            })
            if r.get("status") == "generated":
                video_url = r.get("video_url", "")
                print(f"[bridge] generate_video: {video_url[:80]}...")

        mcp.stop()

    # Build ShotSpec with video URL
    shot_spec = _generate_demo_shot_spec(brief)
    if video_url:
        shot_spec["video_url"] = video_url

    # IPFS pin
    from ipfs import pin_shot_spec
    ipfs_result = pin_shot_spec(shot_spec)
    print(f"[bridge] IPFS: {ipfs_result['status']}")
    if ipfs_result["status"] != "ok":
        return {"status": "error", "step": "ipfs", "error": ipfs_result["error"]}
    cid = ipfs_result["cid"]
    shot_spec["ipfs_cid"] = cid

    # NFT mint (optional)
    mint_result = {"status": "skipped"}
    if nft_address:
        from mint import mint_shot_nft
        mint_result = mint_shot_nft(cid, shot_spec, nft_address)
        print(f"[bridge] Mint: {mint_result['status']}")

    # spend()
    spend_result = call_spend(
        task_id=shot_spec["shot_id"],
        amount=Web3.to_wei(0.001, "ether"),
        cid=cid,
    )
    print(f"[bridge] Spend: {spend_result['status']}")

    return {
        "status": "ok" if spend_result["status"] == "ok" else "partial",
        "project_id": project_id,
        "video_url": video_url,
        "shot_spec": shot_spec,
        "ipfs": ipfs_result,
        "mint": mint_result,
        "spend": spend_result,
    }


def _generate_demo_shot_spec(brief: str, beat_position: int = 1, tension: float = 0.5) -> dict:
    """Generate a demo ShotSpec (fallback when AUTEUR MCP is unavailable)."""
    import hashlib
    shot_id = hashlib.sha256(f"{brief}_{beat_position}_{time.time()}".encode()).hexdigest()[:16]
    return {
        "shot_id": shot_id,
        "brief": brief,
        "beat_position": beat_position,
        "tension_level": round(tension, 2),
        "scene_description": brief,
        "dp_blend": "arri_logc_to_rec709",
        "meisner_note": f"Beat {beat_position}: emotional truth from brief",
        "composition_id": shot_id[:8],
        "timestamp": int(time.time()),
        "camera": {
            "movement": "static" if beat_position <= 3 else ("dolly_in" if tension > 0.6 else "handheld"),
            "angle": "eye_level" if beat_position <= 5 else "low_angle" if tension > 0.7 else "high_angle",
            "lens": "35mm" if tension < 0.5 else ("50mm" if tension < 0.8 else "85mm"),
        },
        "lighting": {
            "key_temp": "3200K" if tension > 0.6 else "5600K",
            "ratio": round(2.0 + tension * 6.0, 1),
            "motivation": "practical" if beat_position <= 4 else "dramatic",
        },
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mcp_bridge.py '<creative brief>' [nft_address] [model]")
        sys.exit(1)

    brief = sys.argv[1]
    nft_addr = sys.argv[2] if len(sys.argv) > 2 else ""
    model = sys.argv[3] if len(sys.argv) > 3 else "kling-3.0"

    result = run_full_pipeline(brief, nft_addr, model)
    print(json.dumps(result, indent=2, default=str))
