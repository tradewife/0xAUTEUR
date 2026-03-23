# 0xAUTEUR — Agent Guide

## What this is

0xAUTEUR is the onchain payment, identity, and minting layer for AUTEUR,
a cinematographically enforced MCP server for autonomous film production.

This repo contains Solidity contracts, pipeline scripts, and the bridge
between AUTEUR's MCP server and onchain infrastructure.

## Architecture

```
Brief → AUTEUR MCP (sanitise_and_submit) → PromptComposer → Provider
                                                    │                 │
                                               validation          video/image URL
                                                    │                 │
                                          x402 settle → spend()     │
                                                    │           Rare CLI mint
                                          SpendReceipt onchain       │
                                                    │           IPFS pin (Filebase)
                                                    └──→ ERC-721 NFT (Base Sepolia)

                                   Bid listener → tension adjustment → recompose → new mint
                                   ERC-8183: requestService → fundJob → submitWork → completeJob
```

## AUTEUR MCP Server

Location: `~/AUTEUR`
Railway endpoint: `https://auteur-mcp-production.up.railway.app/mcp`
Start local: `cd ~/AUTEUR && auteur serve --transport stdio`

Key MCP tools:
- `analyse_brief(logline, description, mood)` → create project
- `propose_visual_language(project_id, style_description)` → lock look (call ONCE)
- `plan_music_video(project_id)` → 9-beat dramatic arc with tension curve
- `generate_hero_shots(project_id)` → character portraits with AuteurLayer enrichment
- `sanitise_and_submit(project_id, scene_index, shot_index, model)` → **THE enforcement gate** — validates + generates, returns prompt + result
- `quick_compose(description, style_description, model)` → one-shot no-project path
- `provider_status()` → check which providers are available
- `get_project(project_id)` → current project state

**NEVER call image/video generation APIs directly.** All generation must
pass through AUTEUR's `sanitise_and_submit` tool (or `quick_compose` for standalone shots).

Video model: `kling-3.0` (via KIE provider, requires `KIE_API_KEY`).
Image model: `nano-banana-2` (via KIE provider).

## Contracts (Base Sepolia)

| Contract | Address | Description |
|----------|---------|-------------|
| auteur (payment) | `0x4473350125F66FC17988589A9a948514866bfdE3` | `deposit()`, `spend()`, `getLog()` |
| auteuragent (ERC-8183) | `0xc7cAF559a5cF8a3C85cA9acEE4A0010e666871B3` | `createJob()`, `fundJob()`, `submitWork()`, `completeJob()` |
| 0xAUTEUR Shot (Rare) | `0x24D258b4249051Dbfa06b1526Bf847062562f126` | ERC-721 via Rare Protocol |
| RareProtocolMock | `0xA530eb2F308BC6D7810eF73d8103ff9123630Cb4` | Standalone test mock |

Deployer: `0xBAc0d61DE2B52Dbb7C6800210bf8A54388032109`
RPC: `https://sepolia.base.org`

## x402 Payment Flow

When `X402_ENABLED=true`, AUTEUR MCP returns HTTP 402 with payment requirements.
Client signs EIP-712 `Payment(amount, asset, recipient, nonce, expiry)` typed data
(or `personal_sign` fallback), retries with `X-Payment` header (base64 JSON).
Server verifies in `auteur/x402_verify.py`, settles via `auteur/x402_settle.py`
calling `spend()` on auteur.sol (selector `0x0eff02ca`).

## Rare Protocol Integration

NFT minting uses the official `rare` CLI (npm global). The ShotNFT is registered
via `rare import erc721` on Base Sepolia. On Base Sepolia, only
`wallet+search+status+import+mint` are supported — no factory deploy.

```bash
# Import an existing ERC-721
rare import erc721 --contract 0x24D258b... --chain base-sepolia

# Mint
rare mint --contract 0x24D258b... --token-uri <metadata-uri> --chain base-sepolia

# Create auction
rare auction create --contract 0x24D258b... --token-id 1 --starting-price 0.01 --duration 86400
```

Verified mint: TX `0xcd926b9a...` (Token ID #3).

## Tools

- Foundry: `~/.foundry/bin/forge` (v1.5.1) — compile, test, deploy Solidity
- Rare CLI: `rare` (npm global) — NFT import, mint, auction
- IPFS: `/tmp/kubo/ipfs` (repo: `/tmp/ipfs-repo`)
- AUTEUR CLI: `auteur` (at `~/.local/bin/auteur`)
- Railway CLI: `railway` — deploy MCP server

## Environment

Copy `.env` and set:
- `DEPLOYER_PRIVATE_KEY` — wallet key for signing TXs
- `KIE_API_KEY` — for Kling/Nano Banana generation via KIE provider
- `BASE_SEPOLIA_RPC` — RPC endpoint (default: `https://sepolia.base.org`)

## Repo Structure

```
src/
  auteur.sol            # Payment + receipting (86 LOC)
  auteuragent.sol       # ERC-8183 agentic commerce (233 LOC)
  shotnft.sol           # Legacy ERC-721, replaced by Rare Protocol (36 LOC)
  RareProtocolMock.sol  # Standalone mock for testing (44 LOC)
  ipfs.py               # IPFS pin layer
  mint.py               # Legacy minting (now using Rare CLI)
  listener.py           # Bid-responsive recomposition
  mcp_bridge.py         # Full pipeline orchestrator
script/
  DeployMock.s.sol      # Foundry deploy script
scripts/
  test_e2e.py           # End-to-end demo script
foundry.toml            # Foundry config (Base Sepolia)
remappings.txt          # OpenZeppelin + forge-std
```

## Running the E2E Demo

```bash
cd ~/0xAUTEUR
source .env
python3 scripts/test_e2e.py
```

With `--video` flag to require real video generation via AUTEUR MCP.
