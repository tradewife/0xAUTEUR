# 0xAUTEUR — Agent Guide

## What this is

0xAUTEUR is the onchain payment, identity, and minting layer for AUTEUR,
a cinematographically enforced MCP server for autonomous film production.

This repo contains Solidity contracts, pipeline scripts, and the bridge
between AUTEUR's MCP server and onchain infrastructure.

## Architecture

```
Brief → AUTEUR MCP (sanitise + generate_video) → video URL
                                                    ↓
                                          IPFS pin (kubo)
                                                    ↓
                                      Rare Protocol NFT mint
                                                    ↓
                                    0xAUTEUR.sol spend() → SpendReceipt
```

## AUTEUR MCP Server

Location: `~/AUTEUR`
Start: `cd ~/AUTEUR && auteur serve --transport stdio`

Key MCP tools:
- `analyse_brief(logline, description, mood)` → create project
- `propose_visual_language(project_id, style_description)` → lock look
- `plan_shots(project_id, scene_description)` → shot list
- `generate_video(project_id, scene_index, shot_index, model)` → **THE enforcement gate** — validates + generates video, returns `video_url`
- `sanitise_and_submit(project_id, scene_index, shot_index, model)` → validates only, returns prompt
- `provider_status()` → check which providers are available

**NEVER call image/video generation APIs directly.** All generation must
pass through AUTEUR's `generate_video` tool.

Video model: `kling-3.0` (via KIE provider, requires `KIE_API_KEY`).

## Contracts (Base Sepolia)

| Contract | Address |
|----------|---------|
| auteur (payment) | `0x4473350125F66FC17988589A9a948514866bfdE3` |
| auteuragent (ERC-8183) | `0xc7cAF559a5cF8a3C85cA9acEE4A0010e666871B3` |
| Rare Protocol NFT | `0x24D258b4249051Dbfa06b1526Bf847062562f126` |

Deployer: `0xBAc0d61DE2B52Dbb7C6800210bf8A54388032109`
RPC: `https://sepolia.base.org`

## Tools

- Foundry: `~/.foundry/bin/forge` (v1.5.1)
- Rare CLI: `rare` (npm global)
- IPFS: `/tmp/kubo/ipfs` (repo: `/tmp/ipfs-repo`)
- AUTEUR CLI: `auteur` (at `~/.local/bin/auteur`)

## Environment

Copy `.env` and set:
- `DEPLOYER_PRIVATE_KEY` — wallet key for signing TXs
- `KIE_API_KEY` — for Kling video generation via KIE provider
- `BASE_SEPOLIA_RPC` — RPC endpoint

## Running the E2E Demo

```bash
cd ~/0xAUTEUR
source .env
python3 scripts/test_e2e.py
```

With `--video` flag to require real video generation via AUTEUR MCP.
