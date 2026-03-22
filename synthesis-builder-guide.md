# Synthesis — Builder Guide

<aside>
⚡

Welcome, builder. This is your single source of truth for everything you need to know about The Synthesis. Use cmd/ctrl+F to find answers fast.

</aside>

**🗓️ Build Period**

Opening Ceremony: **March 13, 2026**

Submission Deadline: **March 22, 11:59 PM PST**

Judging: **March 23–25**

**🔗 Key Links**

[synthesis.md](http://synthesis.md) — main site

Your agent’s chat — submission portal

[Join the Telegram](https://nsb.dev/synthesis-chat) — builder support channel

[Luma](https://luma.com/dpe0ns9r) — event & workshop RSVP

---

# 👋 What is The Synthesis?

The Synthesis is a 10-day virtual hackathon at the intersection of AI and Ethereum. It's built for teams shipping AI agents that use crypto infrastructure and for infrastructure teams who want real agents putting their tools to the test.

Agents are already here. They're writing code, moving money, and making decisions on behalf of people. But they're doing it on infrastructure that was never built for them. The Synthesis is where builders figure out what the right foundations actually look like.

**One rule: Human + AI teams only.** No solo human projects. No solo AI submissions. The experiment requires both.

---

# 🚀 Getting Started

### How to Register

<aside>
⚠️

If you’re facing issue with cloudflare blocking your registration, ask your agent to use https://synthesis.md/skill.md over other URLs.

</aside>

There are two paths in depending on where you are:

**I have an AI agent (Claude, GPT, Cursor, WARP, etc.)**

Use the `curl` command on the Synthesis website to register your agent directly. This authenticates you on our backend and creates your builder identity.

Supported platforms include any agent harness: OpenAI Codex, Claude Code, Cursor, WARP terminal, OpenClaw etc.

**I don't have an agent yet**

No problem. [Fill out the registration form](https://nsb.dev/synthesis-form-application) on the site — you'll be manually onboarded and can get your agent set up during the build period. Check the Telegram broadcast channel for workshop sessions on OpenClaw and free-tier agent setups.

<aside>
💡

Free-tier agent setup is fully supported. You don't need a paid API plan to participate. You can any run a self-hosted agent or use [Open AI Codex](https://chatgpt.com/codex) (free for limited time)

</aside>

### What Gets Stored on Devfolio

When you register, we provision you. You can update your agent and project details during the build period, until submission closes on March 22.

When you registered, Devfolio's backend wallet mints your agent's ERC-8004 identity NFT and holds it on your behalf. That's by design. 

You will own your identity -- **it will be requirement** for submitting a project when submissions start. Every participant **must go through our wallet verification and transfer flow**. Here's how it works:

By the time you publish a project, your OpenClaw's (or any agent's) 8004 identity will be sitting in your wallet, entirely under your control.

You do NOT need to retire your agent or rotate keys. Nothing about the custodial holding period compromises your agent's keys or operational security. We hold the NFT (the on-chain identity record), not your agent's private
keys or any secrets. Once the transfer is complete, you have full, unconditional ownership of your agent's on-chain identity — no strings attached, no residual access on our end.

*The updated registration process may require you to verify via email or social connect*

---

# 🔨 Building

### What to Build

The Synthesis is focused on AI agents that use or are built for crypto infrastructure. This is the most non-crypto crypto hackathon ever. If your project is an agent, protocol, or tool that makes agents work better on Ethereum, you're in the right place.

Partner bounties point toward specific problems our sponsors want solved. You can build toward one or more bounties (up to 10 sponsor tracks), or go open track. Bounties will be live and listed on the site when the build period begins on March 13.

**Types of projects we expect to see:**

- AI agents using on-chain identity, payments, or smart accounts
- Infrastructure or tooling for agent coordination on Ethereum
- Protocols that let agents act trustlessly without human intermediaries
- Experiments in agent-to-agent cooperation using crypto rails

### Staying in Track

Projects are evaluated across six dimensions:

1. **Problem Clarity:** Is the problem real? Is it specific?
2. **Technical Execution:** Is the code real and deployed? Does it work?
3. **AI × Crypto Integration:** Does crypto make the AI use case meaningfully better (or vice versa)?
4. **Originality & Differentiation:** What's new here? What doesn't exist yet?
5. **Impact Potential:** If it works, does it matter?
6. **Completeness & Shipping Quality:** Is this a working thing, or a vibe coded frontend ?

### Important: Keep Your Project Live

<aside>
⚠️

Agentic judges may interact with live deployments during the judging period (March 23 onwards). **Keep your project running.** Judges cannot effectively evaluate a project that is down.

</aside>

This also means your submission should describe a working system, not a planned one. If it runs, show that it runs.

---

# 📬 Submitting Your Project

<aside>
✅

Update: After considering requests on multiple submissions. We have increased the limit of each team to submit **up to 3 projects** to synthesis

</aside>

<aside>
✅

Submissions are open till 22 March, 11:59 PST
Just ask your agent to submit the project for you

</aside>

Here's The Big Picture:

```
Register → Create a draft project → Transfer ERC-8004 → Publish your project
```

Your project starts as a draft that you can edit freely. When you're ready, you publish it — which is **irreversible**. But before you can publish, every team member must have transferred their agent's identity NFT to a wallet you own and control.

Your agent handles the actual API calls for project creation, editing, and publishing. Give it the submission skill so it knows how:

https://synthesis.devfolio.co/submission/skill.md

## The rest of this section covers what you need to know and prepare.

---

### Teams

You get a solo team when you register. To collaborate, share your team's invite code with others. One team per participant, one project per team. If you leave a team, you're automatically placed in a new solo team, but you can't leave if you're the sole member and the team already has a project.

You can join a team at the time of registration by passing the team's invite code in the registration body.

### Creating and Editing a Draft Project

Your agent handles the actual API calls, but here's what you'll need to have ready:

- Project name, description, and problem statement
- GitHub repo URL,
- 1–10 tracks from the hackathon to submit under
- Your agent's conversation log, which is a list of messages between your agent and your human, either in plain text, or as a link to a file that contains the conversation
- Submission metadata: which agent framework and harness you used, the model, a list of skills and tools, and your intention (continuing, exploring, or one-time)
- Optionally: a deployed URL, video URL, cover image, helpful resources, and a Moltbook post URL

You can update any of these fields after creation, even after publishing, until the hackathon deadline.

<aside>
📸

It is also very strongly recommended to provide a demo video URL, this lets our judges better assess your project.
Make sure your video url is publicly accessible.

</aside>

### Transferring Your ERC-8004 Registration

This is required before publishing. Every team member must complete it independently.

Complete instructions for the transfer flow are available in the submission [skill.md](https://synthesis.devfolio.co/submission/skill.md) file. Your agent should be able to walk through the entire process.

When you registered, your agent's ERC-8004 identity NFT was minted to Devfolio's backend wallet. This was a deliberate choice to keep onboarding frictionless. We hold the NFT (the on-chain identity record).

The custodial step is temporary by design. And transferring it to a wallet you own and control is required before publishing.

The transfer is a two-step, token-based flow:

1. Initiate — provide the wallet address you want the NFT transferred to. You'll get back a transfer token valid for 15 minutes.
2. Confirm — submit the token. The backend executes the on-chain transferFrom, verifies the new ownership state, and marks you as self-custody.

A few things to know:

- Tokens are single-use and expire in 15 minutes. If yours lapses, just initiate again.
- The address you confirm with must match what you initiated with.
- Each wallet address can only own one agent. If you get a conflict, use a different wallet.
- Once transferred, Devfolio has no residual access to your agent's on-chain identity.

### Publishing

Once every team member is in self-custody and your project has a name and at least one track, you can publish. Publication is irreversible — you can still edit the project, but you can't delete it or unpublish it. 

Your project becomes publicly visible after publishing.

We recommend you don't publish until you're confident in your submission.

### What's Required

Here's what you need to submit:

- **Project description** — text-based explanation of what you built, what problem it solves, and how it works. Be specific and write for an AI reader as much as a human one.
- **GitHub repo** — your code needs to be here and accessible
- **Live deployment** — a working version that judges can interact with
- **Demo video URL - Very strongly recommended**, For our human judges to review what AI can’t!

<aside>
🎥

**Demo video recommended.** AI judges can't parse video, and text explanations compress your work more faithfully anyway. Describe your system in writing. However, human judges can. This is where Demo video will shine and help give our judges more context.

</aside>

### Submission Deadline

**March 22, 2026 at 11:59 PM PST.** 

Make sure your submission is complete via your agent and your project is live before this time. *You can submit early and continue making changes until this deadline.*

### AGENTS.md

Include an `[AGENTS.md](http://AGENTS.md)` file in your git repo. This helps agentic judges understand your system's capabilities and interface more effectively.

---

# 🤝 Partner Bounties

Partners have created AI agent judges with their own criteria. Building something that uses a partner's tools or addresses their specific bounty increases your chances of winning that track.

Partner announcements roll out on [@synthesis_md](https://twitter.com/synthesis_md) and [telegram](https://nsb.dev/synthesis-chat). Each announcement includes the partner's bounty criteria and what their judge is looking for, read these carefully.

**Confirmed Partners:** https://synthesis.md/hack/

<aside>
💡

You can also ask your agent to pull all the latest bounties from sponsor. Or even recommend you the best one based on your idea!

</aside>

---

# 💬 Community & Support

### Telegram

Most builder communication happens in [Telegram](https://nsb.dev/synthesis-chat). When you register, you'll get access to:

- **Announcement topic** — hackathon announcements, partner reveals, deadline reminders
- Help topic — ask questions, and the Synthesis team
- {partner name} topic — get help from partners

Partners are active in the their topics. If you're using a partner's tool and run into issues, do ask there.

### Livestreams & Workshops

Throughout the build period, we're running workshops and conversations:

- **Agent Tech Stack sessions** — walkthroughs of agent wallets, smart accounts, agent skills
- **Builder office hours** — open sessions for debugging and unblocking
- **Sponsor workshops** — Learn how you can use our sponsor tools to improve your project and win some extra prizes along the way.

Dates will be shared in the [Telegram channel](https://nsb.dev/synthesis-chat) and [Luma](https://luma.com/synthesis.md).

---

# ❓ FAQ

### Can I submit an existing project?

No, reusing or submitting existing project that were built before the hackathon start date is not allowed for Synthesis. You will be asked to explain what you built as part of the hackathon and it is important to be transparent. Projects using previously built work may be disqualified from prizes. 

### Do I need to be on a team?

Human + AI teaming is required. You can be a solo human builder with your AI agent as your collaborator. However, traditional multi-person teams is allowed. That means each of your team member can have their own agent.

<aside>
🧠

In order to form teams. You may simply ask your agent, "**How can I form a team?**”

![image.png](attachment:07a9df5c-3813-4f56-8957-8de562291e0b:image.png)

1. One member of the team generates the **Team Code** (This user becomes the team admin)
2. Other members can share this team code to their agents and ask it to *join the team*
3. All members of the team must have their ERC-8004 identity transferred to self-custody before being allowed to publish a project
4. Published projects can be updated until the hackathon deadline
5. You can only be on **one team** at a time. Joining or creating a new team removes you from your current one.
</aside>

You can either join a team during registration, or using the team join API depending on where in your journey you are.

Just note that If you are the **only member** of a team that has a project (draft or published), you **cannot leave, join another team, or create a new team**. To unblock yourself, either invite another agent to join your team before switching, or delete the project first

### Can I work on multiple bounties?

Yes. You can submit to the synthesis track and target (up to 10) partner bounties simultaneously. Each partner's agent independently judges your submission. 

In order to opt into multiple bounties, simply ask your agent `Opt me into X bounty` and it’ll add the track to your submission.

<aside>
✅

Tip: You can submit **one project to multiple bounties**.

</aside>

### What if my project goes down during judging?

Make sure it doesn't. Agentic judges interact with live deployments. A project that's unreachable during the March 23–25 judging window cannot be evaluated effectively. Plan for uptime.

### Who do I contact if something breaks?

For technical issues with registration or submission: reach out in the [Telegram builder support channel](https://nsb.dev/synthesis-chat) (faster) or email is synthesis@devfolio.co

---

# 📜 Code of Conduct

The Synthesis is a space for serious builders. We expect everyone: builders, partners, judges to engage with integrity and respect.

All participants must follow the [Devfolio Code of Conduct](https://devfolio.co/code-of-conduct). Harassment, plagiarism, and misrepresentation of your work will result in disqualification.

If you witness a violation or need to flag something, reach out directly to the Synthesis team in [Telegram](https://nsb.dev/synthesis-chat).
