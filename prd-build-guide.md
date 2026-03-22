# — PRD

```markdown
# 0xAUTEUR — PRODUCT REQUIREMENTS DOCUMENT

## What it is
0xAUTEUR is the onchain payment, identity, and minting layer that
connects AUTEUR's cinematic MCP server to the Ethereum ecosystem.

AUTEUR already works. It validates creative decisions through
sanitiser.py and produces ShotSpec — a verifiable data structure
carrying every creative choice from intent to generation.

0xAUTEUR makes that output: payable, mintable, and agent-hireable.

## Core Components

### 1. 0xAUTEUR.sol (Base Sepolia)
Payment and receipting contract.
Functions:
- deposit(agentId, amount) — fund an agent's operating budget
- spend(agentId, taskId, amount, tokenId) — agent spends, emits receipt
- getLog(agentId) — returns full spend history
Events:
- SpendReceipt(agentId, taskId, amount, timestamp, tokenId)
Triggered by: sanitise_and_submit on every validated shot

### 2. IPFS Pin Layer
On every sanitise_and_submit pass:
- Serialize ShotSpec to JSON
- Pin to IPFS via Lighthouse SDK
- Return CID
- Pass CID into spend() as tokenId field
Tools: Lighthouse SDK (preferred) or web3.storage

### 3. Rare Protocol Mint
After IPFS pin succeeds:
- Mint ShotSpec as NFT via Rare Protocol on Base
- tokenURI = ipfs://{CID}
- Metadata: beat_position, tension_level, dp_blend, meisner_note,
  composition_id, timestamp
Returns: tokenId

### 4. Bid-Responsive Recomposition
Rare Protocol auction event listener:
- On bid event: read bid amount
- Map bid to tension_level adjustment:
  bid > 2x reserve → tension_level += 0.15 (more climactic)
  bid < reserve → tension_level -= 0.10 (more restrained)
- Regenerate next beat's ShotSpec with adjusted tension
- This makes auction dynamics literal compositional elements

### 5. ERC-8183 Agent Interface
Wraps AUTEUR as a hirable agent persona on Base.
Interface:
- capabilities() → ["film_composition", "shot_validation", "mint"]
- pricingModel() → per-shot USDC rate
- requestService(brief) → quote + sessionId
- executeService(sessionId) → ShotSpec + IPFS CID + mint tx + SpendReceipt
Enables: any ERC-8183 compatible agent to commission AUTEUR directly

## Track Coverage
| Track | Component | Proof |
|-------|-----------|-------|
| Base | 0xAUTEUR.sol + spend() | SpendReceipt tx hash |
| SuperRare | Rare Protocol mint + bid listener | Mint tx + tokenURI |
| Virtuals | ERC-8183 wrapper | Agent-to-agent tx |
| Open Track | All of the above | Combined |

## What is NOT in scope
- Audio tooling (human handles)
- Video rendering / Remotion (human handles demo)
- Submission copy (human handles with Perplexity)
- Demo video production (human handles)

## Success Criteria
A judge can:
1. Find 0xAUTEUR.sol on Base Sepolia explorer
2. See SpendReceipt events with real CID fields
3. Open the IPFS CID and find a valid ShotSpec JSON
4. Find the Rare Protocol mint with ShotSpec tokenURI
5. See one bid-triggered recomposition with different tension_level
6. Find the ERC-8183 contract and one agent-to-agent transaction
```


***

# 3— BUILD GUIDE

```markdown
# 0xAUTEUR — BUILD GUIDE

## Prerequisites
- AUTEUR running locally: cd auteur && auteur serve --transport stdio
- Base Sepolia RPC + funded wallet (get testnet ETH from base-sepolia faucet)
- Lighthouse API key (lighthouse.storage — free tier)
- Rare Protocol testnet access
- Node 18+ and Python 3.11+

## Phase 1 — Deploy 0xAUTEUR.sol (target: 30 min)

Create: 0xauteur/contracts/0xAUTEUR.sol

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ZeroXAuteur {
    struct Receipt {
        string taskId;
        uint256 amount;
        uint256 timestamp;
        string cid;
    }

    mapping(address => uint256) public budgets;
    mapping(address => Receipt[]) public log;

    event SpendReceipt(
        address indexed agentId,
        string taskId,
        uint256 amount,
        uint256 timestamp,
        string cid
    );

    function deposit(address agentId) external payable {
        budgets[agentId] += msg.value;
    }

    function spend(
        address agentId,
        string calldata taskId,
        uint256 amount,
        string calldata cid
    ) external {
        require(budgets[agentId] >= amount, "Insufficient budget");
        budgets[agentId] -= amount;
        Receipt memory r = Receipt(taskId, amount, block.timestamp, cid);
        log[agentId].push(r);
        emit SpendReceipt(agentId, taskId, amount, block.timestamp, cid);
    }

    function getLog(address agentId) external view
        returns (Receipt[] memory) {
        return log[agentId];
    }
}

Deploy to Base Sepolia using Foundry or Hardhat.
Save: CONTRACT_ADDRESS to .env

## Phase 2 — IPFS Pin on Validation (target: 20 min)

In auteur/pipeline/shot.py (or wherever sanitise_and_submit is called),
add after successful validation:

import lighthouse from "@lighthouse-web3/sdk"  # or Python equivalent

async def pin_shot_spec(shot_spec: ShotSpec) -> str:
    data = shot_spec.model_dump_json()
    response = await lighthouse.uploadText(data, LIGHTHOUSE_API_KEY)
    return response.data.Hash  # returns CID

# After sanitise_and_submit passes:
cid = await pin_shot_spec(validated_shot)
receipt = await spend(AGENT_ID, shot.shot_id, SHOT_PRICE, cid)

## Phase 3 — Rare Protocol Mint (target: 45 min)

After IPFS pin returns CID:

async def mint_shot(cid: str, metadata: dict) -> str:
    token_uri = f"ipfs://{cid}"
    # Call Rare Protocol mint function on Base Sepolia
    # metadata: beat_position, tension_level, dp_blend, meisner_note
    tx = await rare_protocol.mint(
        to=AUTEUR_WALLET,
        tokenURI=token_uri,
        metadata=metadata
    )
    return tx.hash  # tokenId

## Phase 4 — Bid-Responsive Recomposition (target: 45 min)

Event listener on Rare Protocol auction contract:

async def on_bid(event):
    bid_amount = event.args.amount
    reserve = event.args.reservePrice
    composition_id = event.args.tokenId

    # Retrieve current ShotSpec for next beat
    current_shot = get_next_shot(composition_id)

    if bid_amount > reserve * 2:
        current_shot.tension_level = min(
            current_shot.tension_level + 0.15, 1.0
        )
    elif bid_amount < reserve:
        current_shot.tension_level = max(
            current_shot.tension_level - 0.10, 0.0
        )

    # Recompose next beat with adjusted tension
    recomposed = await director.recompose_beat(current_shot)
    new_cid = await pin_shot_spec(recomposed)
    await mint_shot(new_cid, recomposed.metadata())

## Phase 5 — ERC-8183 Agent Wrapper (target: 1 hr)

Create: 0xauteur/contracts/AUTEURAgent8183.sol

Implement ERC-8183 interface:
- capabilities(): return ["film_composition","shot_validation","mint"]
- pricingModel(): return per-shot USDC rate
- requestService(string brief): create session, return quote
- executeService(uint256 sessionId):
    1. Pass brief to AUTEUR MCP server
    2. Run full pipeline: analyse_brief → plan → sanitise_and_submit
    3. Pin to IPFS
    4. Mint via Rare Protocol
    5. Call spend() on 0xAUTEUR.sol
    6. Return: ShotSpec CID + mint tx + SpendReceipt

Deploy on Base Sepolia (same chain — no extra infra).

## Phase 6 — End-to-End Test (target: 30 min)

Run this sequence and save every tx hash and CID:

1. auteur serve --transport stdio
2. deposit(AGENT_WALLET, 0.01 ETH) → confirm budget
3. Send brief: "a woman pressing her palm flat against cold glass,
   not looking at the man behind it. Warm amber key light."
4. Pipeline runs: analyse → arc → sanitise_and_submit
5. IPFS pin fires → CID returned
6. Rare Protocol mint → tokenId returned
7. spend() fires → SpendReceipt event emitted with CID
8. Simulate bid at 2.5x reserve → tension_level adjusts → next
   beat recomposes → new CID → new mint
9. ERC-8183: external call to requestService + executeService
10. Save: contract address, all tx hashes, both CIDs

## Deliverables Checklist
- [ ] 0xAUTEUR.sol deployed + verified on Base Sepolia
- [ ] Contract address saved to README
- [ ] SpendReceipt event visible in Base explorer
- [ ] IPFS CID resolves to valid ShotSpec JSON on ipfs.io
- [ ] Rare Protocol mint tx with correct tokenURI
- [ ] Bid-triggered recomposition showing tension_level change
- [ ] ERC-8183 contract deployed on Base
- [ ] Agent-to-agent tx visible in Base explorer
- [ ] All addresses + tx hashes committed to 0xauteur repo README

## Repo Structure
0xauteur/
├── contracts/
│   ├── 0xAUTEUR.sol
│   └── AUTEURAgent8183.sol
├── scripts/
│   ├── deploy.js
│   └── test_e2e.py
├── src/
│   ├── ipfs.py          # Lighthouse pin wrapper
│   ├── mint.py          # Rare Protocol integration
│   ├── listener.py      # Bid event → recomposition
│   └── mcp_bridge.py    # AUTEUR MCP ↔ 0xAUTEUR bridge
└── README.md            # Contract addresses + tx hashes here
```

---

# this looks great just to clarify the agent will use the demo using 0xAUTEUR (connecting to AUTEUR MCP) and Remotion I will sort out the audio.

Perfect clarification. So the demo pipeline is:

**Hermes** → calls **AUTEUR MCP** (via 0xAUTEUR) → generates validated ShotSpecs → **Remotion** renders the visual composition → **you** lay the audio on top.

Three small updates to lock this in across all documents:

***

## Updates to Build Guide — Phase 6 (End-to-End Test)

Replace the test brief section with:

```markdown
## Phase 6 — Demo Run (target: 30 min)

The demo IS the end-to-end test. Run this sequence:

1. auteur serve --transport stdio          ← AUTEUR MCP live
2. deposit(AGENT_WALLET, 0.01 ETH)         ← fund 0xAUTEUR.sol
3. Send brief to AUTEUR via 0xAUTEUR ERC-8183 interface
4. Pipeline: analyse_brief → 9-beat arc → sanitise_and_submit
5. Each validated ShotSpec:
   → IPFS pin → CID
   → Rare Protocol mint → tokenId
   → spend() → SpendReceipt emitted
6. Pass each validated ShotSpec to Remotion
   → Remotion renders composition per beat
   → Output: visual sequence of all 9 beats
7. Bid simulation → tension_level adjusts → recompose beat 7 (climax)
   → Remotion re-renders beat 7 with new composition
8. Save all outputs: renders + tx hashes + CIDs

Human adds audio layer to Remotion output.
Human produces final demo video.
Agent does NOT touch audio or final video assembly.
```


***

## One line to add to Mission Brief under STEP 4

```markdown
## STEP 4 — DEMO VIDEO (human handles)
The demo uses: 0xAUTEUR (onchain layer) → AUTEUR MCP (creative layer)
→ Remotion (visual render). Output is a visual sequence.
Human adds audio and assembles final video.
Agent role: run the pipeline, save Remotion renders, report file paths.
Do NOT produce audio. Do NOT assemble final video.
```


***

## One line to add to PRD under What is NOT in scope

```markdown
- Audio tooling (human handles)
- Final video assembly (human handles)
- Remotion setup (apollo/skills/remotion handles render calls only)
  Agent passes ShotSpec → Remotion → saves render output → stops there
```


***

That's the complete picture:[^30_1]


| Layer | Who |
| :-- | :-- |
| Onchain receipts + minting | Hermes via 0xAUTEUR |
| Cinematic validation + ShotSpec | Hermes via AUTEUR MCP |
| Visual render | Hermes via Remotion |
| Audio | You |
| Final cut + demo video | You |

Clean separation, no ambiguity. Hermes knows exactly where its job ends. 🎬

<div align="center">⁂</div>

[^30_1]: https://www.remotion.dev/docs/ai/skills

## Generation Stack (current)

AUTEUR MCP is the only valid generation path.
- Server: ~/AUTEUR, run with `auteur serve --transport stdio`
- Tool for single shot: quick_compose (model="kling-3.0")
- Tool for full pipeline: sanitise_and_submit (model="kling-3.0")
- Output: video URL (not image URL)
- That URL → IPFS pin → ShotNFT tokenURI

## Payment Layer (Base Services track)
- x402 gates quick_compose and sanitise_and_submit
- Price: $0.01 / $0.05 USDC on Base Sepolia (eip155:84532)

## What is DONE (do not rebuild)
- auteur.sol, auteuragent.sol (ERC-8183), ShotNFT deployed on Base Sepolia
- Rare Protocol CLI integrated — Beat 1 + Beat 2 minted
- IPFS pinned to SuperRare Filebase, all CIDs resolve HTTP 200
- Nonce tracking fixed, 6 sequential TXs clean
- ERC-8183 job lifecycle: 4 TXs onchain

## What is NOT done yet
- AUTEUR MCP not installed — install first
- Video generation not wired — wire second
- x402 not implemented — wire third
- 0xauteur repo is empty — push after video works

