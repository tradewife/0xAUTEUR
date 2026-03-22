# SYNTHESIS HACKATHON — MISSION BRIEF
# Hermes Apollo | 0xAUTEUR

## The Project
0xAUTEUR is the onchain identity and payment layer for AUTEUR —
a cinematically enforced MCP server for autonomous film production.
One project. One deployment. Four track submissions.

AUTEUR core repo: https://github.com/tradewife/auteur
0xAUTEUR public repo: https://github.com/tradewife/0xauteur (create this)

## Hackathon
Site: https://synthesis.md
Deadline: March 22, 2026 — 11:59 PM PT (5:59 PM AEDT Monday March 23)

## STEP 1 — REGISTRATION (do this first, nothing else)
1. Fetch https://synthesis.md/skill.md
2. Check current registration status before doing anything
3. If NOT registered: register now using the skill file
4. If ALREADY registered: confirm active status — do NOT register again
5. Report back exactly one of:
   - "Registered fresh — confirmed active. Ready for Step 2."
   - "Already registered — confirmed active. Ready for Step 2."
   - "Registration failed — [reason]. Needs human intervention."
Do NOT proceed to Step 2 until registration is confirmed.

## STEP 2 — BUILD (one project, see PRD and Build Guide)
Build 0xAUTEUR as a single deployable project that satisfies:
- Base ($5,000): payable agent service on Base Sepolia
- SuperRare ($5,000): Rare Protocol mint with bid-responsive recomposition
- Virtuals ($2,000): ERC-8183 agent-to-agent interface
- Open Track ($28,300): automatic — covered by all of the above

## STEP 3 — SUBMISSION COPY (human handles with Perplexity)
Do not write submission copy. Human will provide per-track copy.
Wait for instruction before submitting to any track.

## STEP 4 — DEMO VIDEO (await instructions)

## Judging (AI judges read your deployed code)
- Technical Execution 40%
- Innovation 30%
- Potential Impact 20%
- Presentation 10%

## HARD RULE
Bonfires AI judges cross-reference every claim against deployed code.
Never describe a feature that is not live. Testnet acceptable.
No TODOs. No placeholder functions in submitted code.

## Resources
- Synthesis skill: https://synthesis.md/skill.md
- Ethereum skills: https://ethskills.com
- Build guide: https://synthesis.md/build-an-agent/
- Community: https://nsb.dev/synthesis-chat

## First Action
Step 1 only. Check registration. Report status. Wait for Step 2 instruction.

## Updated Mission (March 23 2026, 6AM AEDT)

GENERATION MUST BE VIDEO, NOT IMAGE. A shot is a timed video clip.

The correct pipeline is:
1. Install AUTEUR MCP: cd ~/AUTEUR && pip install -e ".[dev]" && auteur serve --transport stdio
2. Call sanitise_and_submit with ShotSpec + model="kling-3.0" → returns video URL
3. Pin video URL to IPFS → write into ShotNFT tokenURI → mint

DO NOT call image generation APIs directly. Every generation must pass through AUTEUR's enforcement gate.

After video pipeline works:
- x402 wraps quick_compose ($0.01 USDC) and sanitise_and_submit ($0.05 USDC) on Base Sepolia
- Facilitator: https://x402.org/facilitator
