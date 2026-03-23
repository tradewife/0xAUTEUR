# 0xAUTEUR

The onchain payment, identity, and minting layer that connects AUTEUR's cinematic MCP server to the Ethereum ecosystem.

## What it is

0xAUTEUR makes AUTEUR's validated ShotSpec output: payable, mintable, and agent-hireable.

AUTEUR validates creative decisions through its enforcement gate (`sanitise_and_submit`) and produces `ShotSpec` — a verifiable data structure carrying every creative choice from intent to generation. 0xAUTEUR takes that output onchain.

## Codebase

| Language | Files | Code | Comment |
|----------|-------|------|---------|
| Solidity | 5 | 283 | 12 |
| Python | 5 | 738 | 226 |
| Markdown | 5 | — | 617 |
| **Total** | **18** | **1074** | **858** |

## Contracts (Base Sepolia)

| Contract | Address | Description |
|----------|---------|-------------|
| **auteur** (0xAUTEUR) | `0x4473350125F66FC17988589A9a948514866bfdE3` | Payment + receipting. `deposit()`, `spend()`, `getLog()` |
| **auteuragent** (ERC-8183) | `0xc7cAF559a5cF8a3C85cA9acEE4A0010e666871B3` | Agentic commerce. `createJob()`, `fundJob()`, `submitWork()`, `completeJob()` |
| **0xAUTEUR Shot** (Rare Protocol ERC-721) | `0x24D258b4249051Dbfa06b1526Bf847062562f126` | Minted via Rare Protocol CLI with IPFS metadata |
| **RareProtocolMock** | `0xA530eb2F308BC6D7810eF73d8103ff9123630Cb4` | Standalone mock for testing (deployed, not factory) |
| **Rare Auction** | `0x1f0c946f0ee87acb268d50ede6c9b4d010af65d2` | Auction contract for bid-responsive recomposition |

### Explorer Links

- [0xAUTEUR.sol](https://sepolia.basescan.org/address/0x4473350125F66FC17988589A9a948514866bfdE3)
- [AuteurAgent.sol](https://sepolia.basescan.org/address/0xc7cAF559a5cF8a3C85cA9acEE4A0010e666871B3)
- [0xAUTEUR Shot NFT (Rare)](https://sepolia.basescan.org/address/0x24D258b4249051Dbfa06b1526Bf847062562f126)
- [RareProtocolMock](https://sepolia.basescan.org/address/0xA530eb2F308BC6D7810eF73d8103ff9123630Cb4)
- [Rare Auction](https://sepolia.basescan.org/address/0x1f0c946f0ee87acb268d50ede6c9b4d010af65d2)

## Deploy Transactions

| Action | TX Hash |
|--------|---------|
| Deploy 0xAUTEUR.sol | `0xb43b8a6333963d007f1eaa1afd37fe75f2512f2fec63501a4dcd0c6d9d158531` |
| Deposit 0.005 ETH | `0x7f4ce12ffe17e68c7cb4416b7149232bfafba107b151780cd9e9cd19eef819fa` |
| Deploy AuteurAgent (ERC-8183) | `0xd2f61da069c1fe8f14368731264807ca417d2d1f3767dfa29459d85b4087ca59` |
| Deploy ShotNFT (legacy, replaced by Rare) | `0x7178771e0d6b6aa57a049e358987f87f0f96fecd90c2deea216be2fe312f0c55` |
| Rare Protocol: Deploy 0xAUTEUR Shot | `0xabcb70f51642204176d79eb51c4fbf1064dc9bbd1f1f02548a69fc305b7cc9ce` |
| Rare Protocol: Auction create | `0xadc2100fa274949300ea422cc8baf9367cf748578d242e9cdc90d1f4f9bc56e8` |
| Deploy RareProtocolMock | `0x...` (TX hash from `edfc4ab`) |
| Synthesis Registration | `0xba9f8cc02c561d19d875e31bdb2a0d790f5aecf8466a20e245cece0996344ed1` |

## x402 Payment Flow

AUTEUR MCP enforces HTTP 402 payment on every request when `X402_ENABLED=true`. 0xAUTEUR.sol is the settlement layer.

```
Client discovers (402 response with amount, asset, chain, address)
         |
Client signs EIP-712 Payment proof (or personal_sign fallback)
         |
Client retries with X-Payment header (base64 JSON)
         |
Server verifies: chain, asset, recipient, amount, expiry, nonce, signature
         |
After generation → spend() on auteur.sol → SpendReceipt event onchain
```

Payment verification: `auteur/x402_verify.py` in the AUTEUR repo.
Onchain settlement: `auteur/x402_settle.py` calls `spend(address agentId, string taskId, uint256 amount, string cid)`.

## Rare Protocol Integration

All NFT mints and IPFS pinning go through the official Rare Protocol CLI (`@rareprotocol/rare-cli`). The CLI handles image upload, metadata generation, IPFS pinning to SuperRare's Filebase gateway, and onchain minting via the Rare factory contract.

The ShotNFT (`0x24D258...f126`) is registered with Rare Protocol via `rare import erc721` on Base Sepolia. On Base Sepolia, only `wallet+search+status+import+mint` are supported (no factory deploy — collections are deployed separately via Foundry and imported).

Verified mint via CLI: TX `0xcd926b9a989042ef4bcba11b32e86a20f30f6db313e6988506b8248c72d83456` (Token ID #3).

### Minted NFTs

**NFT #1 — Beat 1 (Original Composition)**

| Field | Value |
|-------|-------|
| Token ID | 1 |
| Brief | A woman pressing her palm flat against cold glass, not looking at the man behind it |
| Tension | 0.5 |
| Image CID | `QmNsWukwJCwDfYntuCA51qCxQAJU99JepopK9kg1FgXFGY` |
| Metadata CID | `QmNSGwVhRnbBuTuYpb7GxNvmZ3PkMJpMMwRwVH5f6Y7YdY` |
| Mint TX | `0x105b69a889b4cd732dad7971c3ac45c6956428b741c28ec17e8c58d4f99ce863` |
| SpendReceipt TX | `0x4274b1e2603e5d2b09220f65fe5fd7584c9b5eb0718b19230bbb15e0dc639579` |

**NFT #2 — Beat 2 (Bid-Responsive Recomposition)**

| Field | Value |
|-------|-------|
| Token ID | 2 |
| Brief | Bid-triggered recomposition. Tension 0.50 → 0.65 after 2.5x reserve bid |
| Tension | 0.65 |
| Image CID | `QmThGsXnTNHrjfcwKWDF5xo1fn5BREPH9AX5vUWMXB2ghR` |
| Metadata CID | `QmUoh6f57Ssm8vHPhck4uZEp6epkxqKLLtUivm3dezapKL` |
| Mint TX | `0xf5e702a253d4fc90e1792f1897bef4d65b44dc36b1dd4d32d784637c72b97c1d` |
| SpendReceipt TX | `0xcfd5c6a61a2ccda06e2c2088213acd982a8d7862cf818b284b8076b82d8cba08` |

## ERC-8183 Agent-to-Agent Flow

Complete lifecycle via the AuteurAgent contract:

| Step | TX Hash |
|------|---------|
| createJob (requestService) | `0xdf4bcc236ebffb93c5f59c41b6a21bc36ba63e66c5dda330ad87e3d00e89eb1a` |
| fundJob (0.0005 ETH escrow) | `0x2788e3e3b30fd403ed260a44dcb309808d345866c2d5f6d52d86f84181da7380` |
| submitWork (deliverable CID) | `0xb7ef7e0c1497402a9a74eadd7942397b3b289f7be3b667320942c79c47740c72` |
| completeJob (evaluator attestation) | `0x4356756a19fc0c71122b8ac304c241b22d1788479d237ef2239012f4a0c5f2e6` |

## Synthesis Hackathon Track Coverage

| Track | Component | Proof |
|-------|-----------|-------|
| **Base** | 0xAUTEUR.sol + `spend()` | SpendReceipt events with CID fields onchain |
| **SuperRare** | Rare Protocol ERC-721 + IPFS metadata | Mint TX + tokenURI with public gateway URLs |
| **Virtuals** | ERC-8183 AuteurAgent | createJob → fundJob → submitWork → completeJob |
| **Open Track** | All of the above | Combined |

## Judge Verification

1. 0xAUTEUR.sol on Base Sepolia: [explorer](https://sepolia.basescan.org/address/0x4473350125F66FC17988589A9a948514866bfdE3)
2. SpendReceipt with CID: [TX 0x4274...9579](https://sepolia.basescan.org/tx/0x4274b1e2603e5d2b09220f65fe5fd7584c9b5eb0718b19230bbb15e0dc639579)
3. IPFS CID resolves to valid metadata: [QmNSGw...YdY](https://superrare.myfilebase.com/ipfs/QmNSGwVhRnbBuTuYpb7GxNvmZ3PkMJpMMwRwVH5f6Y7YdY)
4. Rare Protocol mint with image + metadata: [TX 0x105b...e863](https://sepolia.basescan.org/tx/0x105b69a889b4cd732dad7971c3ac45c6956428b741c28ec17e8c58d4f99ce863)
5. Bid-triggered recomposition: tension 0.50 → 0.65, new mint [TX 0xf5e7...7c1d](https://sepolia.basescan.org/tx/0xf5e702a253d4fc90e1792f1897bef4d65b44dc36b1dd4d32d784637c72b97c1d)
6. ERC-8183 agent-to-agent: [createJob TX 0xdf4b...eb1a](https://sepolia.basescan.org/tx/0xdf4bcc236ebffb93c5f59c41b6a21bc36ba63e66c5dda330ad87e3d00e89eb1a)

## AUTEUR MCP Server (Railway)

The AUTEUR MCP server is publicly deployed and reachable for any MCP-compatible client:

- **Endpoint**: `https://auteur-mcp-production.up.railway.app/mcp`
- **Transport**: Streamable HTTP
- **Railway Project**: `auteur-mcp` (107fcd42)

### KIE Model Configuration

| Role | Model | Env Var |
|------|-------|---------|
| Main Image | Nano Banana 2 | `KIE_IMAGE_MODEL_MAIN` |
| Main Video | Kling 3.0 | `KIE_VIDEO_MODEL_MAIN` |
| Judge Image | Qwen Image 2.0 | `KIE_IMAGE_MODEL_JUDGE` |
| Judge Video | Seedance 1.5 Pro | `KIE_VIDEO_MODEL_JUDGE` |

## Architecture

```
Brief → AUTEUR MCP (Railway) → ShotSpec → sanitise_and_submit → PromptComposer → Provider
                                              │                              │
                                         validation                     video URL / image
                                              │                              │
                                    x402 settle ──→ spend()                   │
                                              │                         Rare CLI mint
                                         SpendReceipt onchain            │
                                              │                      IPFS pin (Filebase)
                                              │                              │
                                              └──→ ERC-721 NFT on Base Sepolia

                                    Bid listener → tension adjustment → recompose → new mint
                                    ERC-8183: requestService → fundJob → submitWork → completeJob
```

## Repo Structure

```
src/
  auteur.sol            # 0xAUTEUR — payment + receipting (86 LOC)
  auteuragent.sol       # AuteurAgent — ERC-8183 agentic commerce (233 LOC)
  shotnft.sol           # ShotNFT — legacy ERC-721, replaced by Rare Protocol (36 LOC)
  RareProtocolMock.sol  # Standalone mock for testing (44 LOC)
  ipfs.py               # IPFS pin layer (kubo daemon)
  mint.py               # NFT minting integration (legacy, now using Rare CLI)
  listener.py           # Bid-responsive recomposition
  mcp_bridge.py         # Full pipeline orchestrator
script/
  DeployMock.s.sol      # Foundry deploy script for RareProtocolMock
scripts/
  test_e2e.py           # End-to-end demo script (nonce-safe)
docs/
  prd-build-guide.md    # Product requirements document
  mission-brief.md      # Synthesis hackathon mission brief
  synthesis-builder-guide.md  # Synthesis builder guide reference
foundry.toml            # Foundry config (Base Sepolia RPC)
remappings.txt          # OpenZeppelin + forge-std
```

## Quick Start

```bash
# Install Rare Protocol CLI
npm install -g @rareprotocol/rare-cli

# Configure
rare configure --chain base-sepolia --private-key $PK --rpc-url https://sepolia.base.org

# Mint via Rare Protocol (handles IPFS natively)
rare mint --contract 0x24D258b4249051Dbfa06b1526Bf847062562f126 \
  --image shot.png --name "My Shot" --description "..." \
  --attribute "Tension Level=0.7" --chain base-sepolia

# Create auction
rare auction create --contract <addr> --token-id 1 --starting-price 0.01 --duration 86400

# Run E2E demo
source .env && python3 scripts/test_e2e.py
```

## License

MIT
