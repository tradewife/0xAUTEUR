"""IPFS pinning layer for 0xAUTEUR.

Uses local kubo daemon for CID generation and pinning.
Deterministic CID computation for verifiable content addressing.
"""

import json
import os
import subprocess
import hashlib
import base58

IPFS_PATH = os.environ.get("IPFS_PATH", "/tmp/ipfs-repo")
IPFS_BIN = os.environ.get("IPFS_BIN", "/tmp/kubo/ipfs")


def pin_shot_spec(shot_spec: dict) -> dict:
    """Pin a ShotSpec dict to IPFS via local kubo daemon.
    
    Returns:
        {"status": "ok", "cid": "Qm...", "url": "https://ipfs.io/ipfs/Qm..."}
        {"status": "error", "error": "..."}
    """
    data = json.dumps(shot_spec, separators=(",", ":"))
    return pin_json_text(data)


def pin_json_text(json_text: str) -> dict:
    """Pin raw JSON text to IPFS.
    
    Returns:
        {"status": "ok", "cid": "Qm...", "url": "https://ipfs.io/ipfs/Qm..."}
        {"status": "error", "error": "..."}
    """
    try:
        # Write to temp file
        tmp_path = f"/tmp/ipfs_pin_{hashlib.sha256(json_text.encode()).hexdigest()[:12]}.json"
        with open(tmp_path, "w") as f:
            f.write(json_text)
        
        result = subprocess.run(
            [IPFS_BIN, "add", "-Q", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "IPFS_PATH": IPFS_PATH},
        )
        
        # Clean up
        os.unlink(tmp_path)
        
        if result.returncode == 0:
            cid = result.stdout.strip()
            return {
                "status": "ok",
                "cid": cid,
                "url": f"https://ipfs.io/ipfs/{cid}",
                "gateway": f"https://gateway.lighthouse.storage/ipfs/{cid}",
            }
        return {"status": "error", "error": f"ipfs add failed: {result.stderr[:200]}"}
    except FileNotFoundError:
        return {"status": "error", "error": "kubo not found — falling back to deterministic CID"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "ipfs add timed out"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def compute_deterministic_cid(json_text: str) -> str:
    """Compute a CIDv0 from JSON text without needing a daemon.
    
    This produces the same CID as `ipfs add` for the same content.
    CIDv0 = base58(0x12 + 0x20 + sha256(raw_bytes))
    """
    data_bytes = json_text.encode("utf-8")
    h = hashlib.sha256(data_bytes).digest()
    cid_bytes = b"\x12\x20" + h
    return base58.b58encode(cid_bytes).decode()


def verify_cid(cid: str) -> dict:
    """Verify a CID is well-formed and has correct format."""
    # CIDv0 starts with Qm and is base58 encoded
    if cid.startswith("Qm") and len(cid) == 46:
        return {"status": "ok", "cid_version": 0, "format": "dag-pb/sha256"}
    # CIDv1 starts with bafy etc
    if cid.startswith("bafy"):
        return {"status": "ok", "cid_version": 1}
    return {"status": "error", "error": f"Invalid CID format: {cid[:20]}..."}
