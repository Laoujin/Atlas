---
title: "Live Workshop Logistics and Team Setup for an AI Coding Cage Match"
date: 2026-06-09
depth: standard
format: md
topic: "Live workshop logistics and team setup"
topic_raw: "Live workshop logistics and team setup"
issue: 208
tags: [workshop, logistics, team-setup, ai-coding, live-event, hackathon, wifi, scoring]
summary: "Run-of-show, room and network guide, and per-tool pre-event checklist for hosting a live 4-way AI coding tool competition with real-time audience scoring."
citations: 15
reading_time_min: 5
cover: cover.svg
cost_usd: 1.43
duration_sec: 556
model: "Sonnet 4.6"
---

> **TL;DR** Assign one tool per team of 3–5 people at least 48 h before the event — don't let participants self-select on the day. [[12]](https://eventornado.com/blog/how-to-form-a-winning-team-for-hackathons) Pre-provision all subscriptions and authenticate all accounts the week before; credit-based tools (Copilot, Windsurf) can exhaust allocation mid-session. [[2]](https://www.cosmicjs.com/blog/claude-code-vs-github-copilot-vs-cursor-which-ai-coding-agent-should-you-use-2026) Budget 5 Mbps per device with a VLAN per team, use Slido for live Q&A and voting, and run a tight 30-min build → demo → score sequence. [[7]](https://www.slicewifi.com/blog/hackathons) [[5]](https://www.classpoint.io/blog/slido-vs-mentimeter-vs-classpoint)

## Team formation

**4 teams, 3–5 people each.** Pairs produce bottlenecks; groups of 4–5 allow a driver/navigator/observer split without paralysis. [[6]](https://devblogs.microsoft.com/visualstudio/vslive-microsoft-ai-hackathon-2026-send-your-team-home-with-working-code/)

**Assign tools pre-event.** Left to self-select, participants cluster on the tool they already know — which defeats the comparison — or fight over the "best" tool. Send tool assignments with confirmation emails at least 48 h before. [[13]](https://blogs.reskilll.com/how-to-organize-a-hackathon-in-2026-the-complete-step-by-step-guide/) Two strategies:

| Strategy | When to use |
|---|---|
| Random assignment | Blind evaluation; any bias in results is chance, not skill |
| Skill-matched assignment | Fair race; pair experienced devs with harder-to-use tools to equalise |

**Roles within each team:**

| Role | Count | Job |
|---|---|---|
| Driver | 1 | Uses the tool; types all code |
| Navigator | 1–2 | Reads requirements; directs the driver |
| Observer | 1–2 | Notes prompts tried, dead-ends, speed; reports to judge |

**Cluster teams, don't mix rows.** [[1]](https://angelhack.com/blog/hackathon-best-practices/) Separate clusters prevent accidental prompt cross-contamination and make tech support routing easy.

## Room and display setup

Two screens beat one. A **presenter display** shows the facilitator's scoring dashboard and countdown timer; an **audience display** mirrors the active team's IDE/terminal. [[4]](https://carpentries.github.io/instructor-training/17-live.html)

Key settings: [[4]](https://carpentries.github.io/instructor-training/17-live.html)
- Font ≥ 18 pt in IDE and terminal; bump to 22 pt if the room is deeper than 8 m
- Black text on white background outperforms white-on-dark when projector lumens are limited; dark themes are fine with ≥ 3,500 lm
- Clear all notifications (OS alerts, Slack, email) on every presenting machine before the clock starts
- Carry HDMI + USB-C adaptors for every team, plus 2 spare sets

Each team cluster needs a 4-outlet surge-protected power strip. If the building shares circuits, request a dedicated 20 A circuit per cluster from the venue.

## Network infrastructure

| Metric | Recommended |
|---|---|
| Bandwidth per device | 5 Mbps [[7]](https://www.slicewifi.com/blog/hackathons) |
| Devices per participant | 1.5× headcount [[8]](https://www.ticketfairy.com/blog/event-wi-fi-networking-in-2026-building-a-reliable-infrastructure-for-seamless-connectivity) |
| Users per radio | ≤ 30 [[8]](https://www.ticketfairy.com/blog/event-wi-fi-networking-in-2026-building-a-reliable-infrastructure-for-seamless-connectivity) |
| Network segmentation | VLAN per team [[15]](https://www.spotipo.com/post/optimize-wifi-networks-for-events) |
| Standard | Wi-Fi 6 / 6E preferred |

For 20 participants: 30 devices × 5 Mbps × 1.4 headroom = **210 Mbps** minimum on tap. [[1]](https://angelhack.com/blog/hackathon-best-practices/)

**VLAN per team.** One team's agentic loop shouldn't starve the others. If the venue can't provision VLANs, bring a managed switch (TP-Link Omada or similar) and create SSIDs per team. [[15]](https://www.spotipo.com/post/optimize-wifi-networks-for-events)

**Failsafe.** One charged mobile hotspot per team in a sealed envelope, opened only if venue WiFi fails. Brief participants upfront so there's no panic scramble.

## Per-tool pre-event checklist

Run this in the **week before** the event — not the morning of. [[13]](https://blogs.reskilll.com/how-to-organize-a-hackathon-in-2026-the-complete-step-by-step-guide/) [[1]](https://angelhack.com/blog/hackathon-best-practices/)

**Claude Code** [[3]](https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/)
- Anthropic Claude Pro ($17–20/mo); install via `npm install -g @anthropic-ai/claude-code`; authenticate once per machine
- Available as VS Code / JetBrains extension or terminal-native CLI
- ⚠ Heavy agentic sessions can hit the 5-hour usage reset window — avoid rehearsals on the same morning

**Cursor** [[3]](https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/)
- Download from cursor.com; Cursor Pro ($20/mo) required for Composer 2 multi-file editing
- Supports Claude, GPT-5.5, Gemini 3.1 Pro — decide which model to demo before the event
- ⚠ Free-tier trials expire unpredictably; use paid seats

**GitHub Copilot** [[2]](https://www.cosmicjs.com/blog/claude-code-vs-github-copilot-vs-cursor-which-ai-coding-agent-should-you-use-2026) [[3]](https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/)
- Pro ($10/mo) via GitHub settings, or Business ($19/seat) for org-wide rollout
- Extension for VS Code, JetBrains, Neovim, Xcode — confirm participant IDE before the day
- ⚠ **June 1, 2026:** billing switched to usage-based credits (1,500/mo on Pro); agentic loops drain allocation fast — verify credit balance 24 h before

**Windsurf / Devin Desktop** [[3]](https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/)
- Rebranded to **Devin Desktop** on June 2, 2026 (cognition.ai); existing Windsurf accounts carry over
- Windsurf Pro was $20/mo → Devin Desktop Teams $40/user/mo; download new installer under Devin branding
- ⚠ Docs still say "Windsurf" in many places — same product, new name; brief participants

**Kiro** [[3]](https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/)
- Download from kiro.dev (AWS-backed); Pro ($20/mo) = 1,000 credits
- Spec-driven workflow: provide a `SPECS.md` alongside the requirements doc to reduce cold-start confusion
- CLI available (Windows 11+, April 2026); macOS/Linux via desktop app

## Audience engagement

For a 20–100 person developer audience, **Slido** edges out Mentimeter on Q&A management: the upvoting module lets technical questions surface naturally. [[5]](https://www.classpoint.io/blog/slido-vs-mentimeter-vs-classpoint)

| Tool                                            | Best for                              | Cost (100 participants)        |
|-------------------------------------------------|---------------------------------------|-------------------------------|
| [Slido](https://www.slido.com)                  | Q&A upvoting, post-demo polls         | ~$17.50/mo, 200 participant cap |
| [Mentimeter](https://www.mentimeter.com)        | Live leaderboard (competition mode)   | €13/mo; free tier limits to 50/mo |
| [ClassPoint](https://www.classpoint.io)         | PowerPoint-integrated quiz + timer    | ~$8/mo, up to 200              |

Run two audience interactions: (a) a **quick vote** immediately after each team's demo ("did this tool actually solve the problem?"), and (b) a **ranked-choice poll** after all four demos for the overall winner. Display the join code before each interaction — don't assume people noted it from slide 1.

## Roles on the day

| Role | Count | Key responsibility |
|---|---|---|
| Facilitator | 1 | Clock, transitions, energy |
| Judge / scorer | 2–3 | Applies rubric; resolves ties [[9]](https://angelhack.com/blog/hackathon-platform-2026-guide/) |
| Tech support | 1 per 2 teams | Auth failures, IDE crashes, WiFi escalation |
| Demo operator | 1 | Runs the test suite on the projector during scoring |

Judges must see the scoring rubric and calibrate against a sample output **before** the event starts. Publish criteria at least 24 h in advance — participants build toward what they are evaluated on. [[9]](https://angelhack.com/blog/hackathon-platform-2026-guide/) For scoring infrastructure, HackerEarth integrates coding assessments directly into competition workflows; Devpost is simpler for smaller events. [[14]](https://www.hackerearth.com/blog/hackathon-platforms)

## Run-of-show

| Clock | Action |
|---|---|
| T−60 min | Accounts verified, repo cloned, all tests passing on each machine |
| T−30 min | Teams seated, Slido join code on screen, WiFi per-team SSID confirmed |
| T−10 min | Facilitator reads task spec aloud; questions answered; timer visible |
| **0:00** | **BUILD starts** (all 4 teams simultaneously) |
| +15:00 | Facilitator check-in: "any tool crashed?" — surface blockers early |
| **+30:00** | **BUILD stops**; `git commit` or screenshot to lock state |
| +32:00 | Team 1 demo: 3-min walkthrough → demo operator runs test suite on projector |
| +45:00 | Teams 2–4 in sequence (~13 min per team) |
| +57:00 | Judge scores finalised; Slido overall-winner poll opens |
| +65:00 | Results announced + structured debrief |

## Pre-flight checklist

- [ ] All tool subscriptions paid and active; credit/token balance confirmed 24 h before [[2]](https://www.cosmicjs.com/blog/claude-code-vs-github-copilot-vs-cursor-which-ai-coding-agent-should-you-use-2026)
- [ ] Repo cloned and dependencies installed on every participant machine
- [ ] All pre-existing tests passing before the clock starts (baseline locked)
- [ ] VLAN or dedicated SSID per team configured and tested [[15]](https://www.spotipo.com/post/optimize-wifi-networks-for-events)
- [ ] HDMI + USB-C adaptors for each team; 2 spare sets for presenter display [[4]](https://carpentries.github.io/instructor-training/17-live.html)
- [ ] Slido/Mentimeter event created; join code tested from a non-presenter device
- [ ] Scoring spreadsheet or platform pre-loaded with rubric [[9]](https://angelhack.com/blog/hackathon-platform-2026-guide/) [[14]](https://www.hackerearth.com/blog/hackathon-platforms)
- [ ] Printed requirements doc (1 per team) as offline fallback [[1]](https://angelhack.com/blog/hackathon-best-practices/)
- [ ] Mobile hotspot per team, charged and ready in sealed envelopes
- [ ] Power strips (4-outlet, surge-protected) at each team cluster [[1]](https://angelhack.com/blog/hackathon-best-practices/)
- [ ] All OS/app notifications cleared on presenting machines [[4]](https://carpentries.github.io/instructor-training/17-live.html)
- [ ] Judges calibrated on sample output; scoring rubric published to participants
