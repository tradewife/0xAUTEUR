# 0xAUTEUR

The onchain payment, identity, and minting layer that connects AUTEUR's cinematic MCP server to the Ethereum ecosystem.

## What it is

0xAUTEUR makes AUTEUR's validated ShotSpec output: payable, mintable, and agent-hireable.

AUTEUR validates creative decisions through sanitiser.py and produces ShotSpec — a verifiable data structure carrying every creative choice from intent to generation. 0xAUTEUR takes that output onchain.

## Contracts (Base Sepolia)

| Contract | Address | Description |
|----------|---------|-------------|
| **auteur** (0xAUTEUR) | `0x4473350125F66FC17988589A9a948514866bfdE3` | Payment + receipting. deposit(), spend(), getLog() |
| **auteuragent** (ERC-8183) | `0xc7cAF559a5cF8a3C85cA9acEE4A0010e666871B3` | Agentic commerce. createJob(), fundJob(), submitWork(), completeJob() |
| **0xAUTEUR Shot** (Rare Protocol ERC-721) | `0x24D258b4249051Dbfa06b1526Bf847062562f126` | Minted via Rare Protocol factory. NFTs with IPFS metadata |

### Explorer Links
- [0xAUTEUR.sol](https://sepolia.basescan.org/address/0x4473350125F66FC17988589A9a948514866bfdE3)
- [AuteurAgent.sol](https://sepolia.basescan.org/address/0xc7cAF559a5cF8a3C85cA9acEE4A0010e666871B3)
- [0xAUTEUR Shot NFT (Rare)](https://sepolia.basescan.org/address/0x24D258b4249051Dbfa06b1526Bf847062562f126)

## Deploy Transactions

| Action | TX Hash |
|--------|---------|
| Deploy 0xAUTEUR.sol | `0xb43b8a6333963d007f1eaa1afd37fe75f2512f2fec63501a4dcd0c6d9d158531` |
| Deposit 0.005 ETH | `0x7f4ce12ffe17e68c7cb4416b7149232bfafba107b151780cd9e9cd19eef819fa` |
| Deploy AuteurAgent (ERC-8183) | `0xd2f61da069c1fe8f14368731264807ca417d2d1f3767dfa29459d85b4087ca59` |
| Deploy ShotNFT (legacy, replaced by Rare) | `0x7178771e0d6b6aa57a049e358987f87f0f96fecd90c2deea216be2fe312f0c55` |
| **Rare Protocol: Deploy 0xAUTEUR Shot** | `0xabcb70f51642204176d79eb51c4fbf1064dc9bbd1f1f02548a69fc305b7cc9ce` |
| **Rare Protocol: Auction create** | `0xadc2100fa274949300ea422cc8baf9367cf748578d242e9cdc90d1f4f9bc56e8` |

## Rare Protocol Integration

All NFT mints and IPFS pinning go through the official Rare Protocol CLI (`@rareprotocol/rare-cli`). The CLI handles image upload, metadata generation, IPFS pinning to SuperRare's Filebase gateway, and onchain minting via the Rare factory contract.

### NFT Mint 1 — Beat 1 (Original Composition)

| Field | Value |
|-------|-------|
| Token ID | 1 |
| Name | 0xAUTEUR Shot #1 |
| Brief | A woman pressing her palm flat against cold glass, not looking at the man behind it. Warm amber key light. |
| Tension Level | 0.5 |
| Image CID | `QmNsWukwJCwDfYntuCA51qCxQAJU99JepopK9kg1FgXFGY` |
| Metadata CID | `QmNSGwVhRnbBuTuYpb7GxNvmZ3PkMJpMMwRwVH5f6Y7YdY` |
| Metadata URL | [superrare.myfilebase.com/ipfs/...](https://superrare.myfilebase.com/ipfs/QmNSGwVhRnbBuTuYpb7GxNvmZ3PkMJpMMwRwVH5f6Y7YdY) |
| Mint TX | `0x105b69a889b4cd732dad7971c3ac45c6956428b741c28ec17e8c58d4f99ce863` |
| SpendReceipt TX | `0x4274b1e2603e5d2b09220f65fe5fd7584c9b5eb0718b19230bbb15e0dc639579` |

### NFT Mint 2 — Beat 2 (Bid-Responsive Recomposition)

| Field | Value |
|-------|-------|
| Token ID | 2 |
| Name | 0xAUTEUR Shot #2 — Recomposed (Tension 0.65) |
| Brief | Bid-triggered recomposition. Tension rose from 0.50 to 0.65 after 2.5x reserve bid. |
| Tension Level | 0.65 (was 0.50, +0.15 from bid > 2x reserve) |
| Image CID | `QmThGsXnTNHrjfcwKWDF5xo1fn5BREPH9AX5vUWMXB2ghR` |
| Metadata CID | `QmUoh6f57Ssm8vHPhck4uZEp6epkxqKLLtUivm3dezapKL` |
| Metadata URL | [superrare.myfilebase.com/ipfs/...](https://superrare.myfilebase.com/ipfs/QmUoh6f57Ssm8vHPhck4uZEp6epkxqKLLtUivm3dezapKL) |
| Mint TX | `0xf5e702a253d4fc90e1792f1897bef4d65b44dc36b1dd4d32d784637c72b97c1d` |
| SpendReceipt TX | `0xcfd5c6a61a2ccda06e2c2088213acd982a8d7862cf818b284b8076b82d8cba08` |

### Auction

| Action | TX Hash |
|--------|---------|
| Auction created (token 1, 0.01 ETH reserve, 24h) | `0xadc2100fa274949300ea422cc8baf9367cf748578d242e9cdc90d1f4f9bc56e8` |
| Auction cancelled (nonce issue, recreated) | `0x2d03620dc1e883d5570491aa7b39de799979215f050900ebe8dedd74544ea7e2` |

## ERC-8183 Agent-to-Agent Flow

Complete lifecycle via the AuteurAgent contract:

| Step | TX Hash |
|------|---------|
| createJob (requestService) | `0xdf4bcc236ebffb93c5f59c41b6a21bc36ba63e66c5dda330ad87e3d00e89eb1a` |
| fundJob (0.0005 ETH escrow) | `0x2788e3e3b30fd403ed260a44dcb309808d345866c2d5f6d52d86f84181da7380` |
| submitWork (deliverable CID) | `0xb7ef7e0c1497402a9a74eadd7942397b3b289f7be3b667320942c79c47740c72` |
| completeJob (evaluator attestation) | `0x4356756a19fc0c71122b8ac304c241b22d1788479d237ef2239012f4a0c5f2e6` |

## Track Coverage

| Track | Component | Proof |
|-------|-----------|-------|
| **Base** | 0xAUTEUR.sol + spend() | SpendReceipt events with CID fields onchain |
| **SuperRare** | Rare Protocol ERC-721 + IPFS metadata | Mint TX + tokenURI with public gateway URLs |
| **Virtuals** | ERC-8183 AuteurAgent | createJob -> fundJob -> submitWork -> completeJob |
| **Open Track** | All of the above | Combined |

## Judge Verification

1. 0xAUTEUR.sol on Base Sepolia: [explorer](https://sepolia.basescan.org/address/0x4473350125F66FC17988589A9a948514866bfdE3)
2. SpendReceipt with CID: [TX 0x4274...9579](https://sepolia.basescan.org/tx/0x4274b1e2603e5d2b09220f65fe5fd7584c9b5eb0718b19230bbb15e0dc639579)
3. IPFS CID resolves to valid metadata: [QmNSGw...YdY](https://superrare.myfilebase.com/ipfs/QmNSGwVhRnbBuTuYpb7GxNvmZ3PkMJpMMwRwVH5f6Y7YdY)
4. Rare Protocol mint with image + metadata: [TX 0x105b...e863](https://sepolia.basescan.org/tx/0x105b69a889b4cd732dad7971c3ac45c6956428b741c28ec17e8c58d4f99ce863)
5. Bid-triggered recomposition: tension 0.50 -> 0.65, new mint [TX 0xf5e7...7c1d](https://sepolia.basescan.org/tx/0xf5e702a253d4fc90e1792f1897bef4d65b44dc36b1dd4d32d784637c72b97c1d)
6. ERC-8183 agent-to-agent: [createJob TX 0xdf4b...eb1a](https://sepolia.basescan.org/tx/0xdf4bcc236ebffb93c5f59c41b6a21bc36ba63e66c5dda330ad87e3d00e89eb1a)

## Architecture

```
Brief -> AUTEUR MCP -> ShotSpec -> Rare Protocol CLI -> IPFS Pin (Filebase) -> NFT Mint
                                                                      |
                                                          0xAUTEUR spend() -> SpendReceipt
                                                                      |
                                                    Bid listener -> tension adjustment -> recompose -> new mint
                                                                      |
                                                    ERC-8183: requestService -> fundJob -> submitWork -> completeJob
```

## Repo Structure

```
src/
  auteur.sol            # 0xAUTEUR - payment + receipting
  auteuragent.sol       # AuteurAgent - ERC-8183 agentic commerce
  shotnft.sol           # ShotNFT - legacy ERC-721 (replaced by Rare Protocol factory)
  ipfs.py               # IPFS pin layer (kubo daemon)
  mint.py               # NFT minting integration (legacy, now using Rare CLI)
  listener.py           # Bid-responsive recomposition
  mcp_bridge.py         # Full pipeline orchestrator
scripts/
  test_e2e.py           # End-to-end demo script (nonce-safe)
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
