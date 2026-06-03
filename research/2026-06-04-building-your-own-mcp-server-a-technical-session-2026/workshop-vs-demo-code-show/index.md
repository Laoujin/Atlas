---
title: "Workshop vs Demo for a 2–3h MCP-Server Session: A Decision Framework + Two Timeboxed Agendas"
date: 2026-06-04
depth: standard
format: md
topic: "Workshop vs demo/code-show for a 2–3h MCP-server session — a decision framework plus TWO concrete timeboxed agendas: (a) a hands-on workshop where attendees build along, and (b) a shorter live-code demo where they watch. Cover prerequisites & attendee environment setup, pacing, the build-a-working-MCP-server-live arc, and what tends to fail live with hands-on coding workshops and how to de-risk it (pre-baked checkpoints, fallback branches). Give a clear recommendation for a mixed Java/.NET room with a 2–3h budget."
topic_raw: "Workshop vs demo/code-show"
tags: [mcp, workshop, live-coding, conference, facilitation, typescript-sdk]
summary: "When to make a 2–3h MCP-server session hands-on vs watch-only, with two timeboxed agendas and a de-risking checklist for live coding."
citations: 18
reading_time_min: 9
---

> **Decision.** For a mixed Java/.NET room with a 2–3h budget building their first MCP server on an unfamiliar TypeScript SDK, run a **demo-led hybrid, not a pure build-along**: you drive a live demo and reach two or three short "now you try it" checkpoints where attendees clone a pinned starter branch and add one tool each. A pure build-along burns ~40% of the budget on environment setup [[8]](https://github.com/autodesk-platform-services/devcon-mcp-workshop-prerequisites) and strands the slowest attendee; a pure demo leaves no retention [[1]](https://www.fielddrive.com/blog/best-workshop-ideas-next-event). The hybrid keeps the hands on the keyboard without the room falling apart. Both full agendas below.

## The decision: which format for which room

The choice is not "workshop good, demo bad." It is a function of three variables: **stack familiarity, room size, and budget**. Hands-on workshops retain more than passive sessions [[1]](https://www.fielddrive.com/blog/best-workshop-ideas-next-event) — but only when setup doesn't eat the clock and nobody gets stranded.

| If your room is… | …and budget is… | Run | Why |
|---|---|---|---|
| Fluent in the stack (Node/TS daily) | 2–3h | **Full build-along** | Setup is cheap; the value is in their own keyboard [[1]](https://www.fielddrive.com/blog/best-workshop-ideas-next-event) |
| New to the stack (Java/.NET → TS SDK) | 2–3h | **Demo-led hybrid** ⭐ recommended | TS toolchain is the unfamiliar part; you absorb the setup risk, they still build at checkpoints |
| Mixed / unknown | < 90 min | **Pure live-code demo** | No time to recover from a single broken `npm install` across 30 laptops |
| Any | Pre-event async support available | Lean more hands-on | A "setup the night before" gate removes the biggest failure source [[8]](https://github.com/autodesk-platform-services/devcon-mcp-workshop-prerequisites) |

The deciding fact for a **Java/.NET room**: they are expert developers, so the *concepts* (tools, resources, transports, schema validation) land fast. What they don't have is muscle memory for the Node/TS toolchain — `npm`/`npx`, `tsconfig`, ESM vs CJS, `zod`. That mismatch is exactly where a build-along stalls, and exactly what a demo-led hybrid routes around.

### The cost of each format, in minutes

A real 2026 MCP workshop (Autodesk DevCon) gates attendees on Node 18+, VS Code, a GitHub/Copilot account, *and* pre-created API credentials — a multi-step setup attendees are told to complete before arrival [[8]](https://github.com/autodesk-platform-services/devcon-mcp-workshop-prerequisites). Even with that, allow 20–40 min of in-room setup reconciliation for a build-along. Microsoft's MCP Dev Days deliberately scoped its "Vibe Code your first MCP server" build slot to **under 30 minutes** by leaning on Copilot scaffolding rather than hand-typing [[10]](https://developer.microsoft.com/en-us/reactor/events/26140/). Duke's Innovation Co-Lab packs "build your first MCP server" into a **2-hour** interactive session [[9]](https://colab.duke.edu/event/building-mcp-servers-03-23-2026/) — proof the arc fits the budget, but only with tight scoping.

## The "build a working MCP server live" arc

Both agendas share the same backbone, derived from the official TypeScript build path. Each stage is a **natural git checkpoint** — a branch you can fast-forward to if the previous stage breaks (see de-risking below).

| Stage | What happens | Checkpoint branch |
|---|---|---|
| 0. Scaffold | `npm init`, install `@modelcontextprotocol/sdk` + `zod` [[12]](https://github.com/modelcontextprotocol/typescript-sdk), `tsconfig` | `00-scaffold` |
| 1. First tool | Define one tool with a Zod input schema (e.g. `get_forecast`) [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | `01-one-tool` |
| 2. Transport | Wire `StdioServerTransport`, `server.connect()` [[15]](https://dev.to/jangwook_kim_e31e7291ad98/build-an-mcp-server-with-typescript-2026-tutorial-1ipk) | `02-stdio` |
| 3. Inspect | Launch MCP Inspector, call the tool, read the Server-output panel [[13]](https://github.com/modelcontextprotocol/inspector) | `03-inspector` |
| 4. Host | Register the server in Claude Desktop / VS Code, invoke from chat [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | `04-host` |
| 5. Second tool | Add a tool that calls a real API → the "aha" payoff [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | `05-two-tools` |

MCP servers expose three capability types — **tools, resources, prompts** [[11]](https://modelcontextprotocol.io/docs/develop/build-server) — but a first live build should focus on **tools only**. Resources and prompts are a slide, not a coding stage, in a 2–3h budget.

**One non-obvious live trap, baked into stage 3:** a stdio server must *never* log to stdout — that stream is the protocol channel. Log to stderr via `console.error`; MCP Inspector renders it in a dedicated "Server output" panel that is your best live-debug surface [[14]](https://www.stainless.com/mcp/mcp-inspector-testing-and-debugging-mcp-servers/). Demo this deliberately; it's the bug every attendee will hit afterward.

---

## Agenda A — Hands-on workshop (attendees build along)

**Total: 3h with a break. Assumes a setup gate completed before arrival and ≥1 helper/TA per ~12 attendees.**

| Time | Segment | Outcome |
|---|---|---|
| 0:00–0:10 | Welcome + MCP in one diagram (tools/resources/prompts) [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | Shared mental model; no 101 framing |
| 0:10–0:30 | **Live setup reconciliation** — `node --version` pre-flight [[8]](https://github.com/autodesk-platform-services/devcon-mcp-workshop-prerequisites), clone starter, `npm ci` [[16]](https://dev.to/vasughanta09/solving-dependency-hell-a-developers-guide-to-managing-package-conflicts-in-2026-o2o) | Every laptop runs `00-scaffold` green |
| 0:30–0:55 | Build stage 1 together: first tool + Zod schema [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | Each attendee has a compiling tool |
| 0:55–1:05 | **Checkpoint + break** — anyone behind resets to `01-one-tool` [[5]](http://blog.gilliard.lol/2018/10/25/live-coding-tips.html) | Room re-synced |
| 1:05–1:30 | Stage 2–3: stdio transport, launch Inspector, call the tool [[13]](https://github.com/modelcontextprotocol/inspector) | Tool callable in Inspector at :6274 |
| 1:30–1:40 | Debug clinic: the stdout-vs-stderr trap [[14]](https://www.stainless.com/mcp/mcp-inspector-testing-and-debugging-mcp-servers/) | Attendees can read the Server-output panel |
| 1:40–2:10 | Stage 4: register in Claude Desktop / VS Code, invoke from chat [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | Working server in a real host |
| 2:10–2:20 | **Checkpoint** — reset stragglers to `04-host` | Room re-synced |
| 2:20–2:45 | Stage 5: add a real-API tool — the payoff [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | Two-tool server doing something useful |
| 2:45–3:00 | Wrap: resources/prompts as next steps, Q&A | Clear path beyond the room |

**Engagement rhythm:** something changes on every attendee's screen at least every ~10–12 min [[2]](https://www.streamalive.com/blog/how-to-host-training-workshops-that-maximize-roi-and-interaction); the break lands at the natural energy dip [[3]](https://www.parallelhq.com/blog/how-to-facilitate-workshop). Two re-sync checkpoints are the load-bearing mechanism — they cap how far behind anyone can fall.

## Agenda B — Live-code demo (attendees watch)

**Total: ~75–90 min, no break needed. One presenter, optional driver/narrator pair. Attendees watch; the repo is shared so they can replay later.**

| Time | Segment | Outcome |
|---|---|---|
| 0:00–0:08 | MCP in one diagram; what "good" looks like at the end [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | Audience knows the destination |
| 0:08–0:20 | Scaffold live from `00-scaffold`: SDK + Zod, why TS SDK is Tier-1 [[12]](https://github.com/modelcontextprotocol/typescript-sdk) | First tool defined on screen |
| 0:20–0:35 | Wire stdio transport; launch MCP Inspector, call the tool [[13]](https://github.com/modelcontextprotocol/inspector) | Tool responds in Inspector |
| 0:35–0:45 | The stdout-vs-stderr trap, shown by triggering and fixing it [[14]](https://www.stainless.com/mcp/mcp-inspector-testing-and-debugging-mcp-servers/) | The #1 future bug pre-empted |
| 0:45–1:00 | Register in Claude Desktop / VS Code; invoke from chat [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | Server working in a real host |
| 1:00–1:15 | Add a real-API second tool — the payoff [[11]](https://modelcontextprotocol.io/docs/develop/build-server) | End-to-end working server |
| 1:15–1:30 | Resources/prompts tour, repo handout, Q&A | Audience can rebuild solo |

A watch-only demo is the right call under ~90 min or when the room's stack is unknown — there is no time to recover from one broken install across many laptops, and passive demo + a take-home repo still gets people building afterward.

---

## What fails live in hands-on workshops — and how to de-risk it

Most live-workshop failures are not coding failures; they are **environment and pacing failures**. Ranked by how often they sink a session:

| Failure | Why it happens | De-risk |
|---|---|---|
| **Setup eats the clock** | 30 laptops, mismatched Node, proxies, OS quirks | Mandatory pre-event setup gate — laptop with node/npm/git/editor installed beforehand [[18]](https://www.kcdc.info/workshops/2021) — plus a `node --version` pre-flight [[8]](https://github.com/autodesk-platform-services/devcon-mcp-workshop-prerequisites); ship a starter repo, run `npm ci` (lock-file pinned) not `npm install` [[16]](https://dev.to/vasughanta09/solving-dependency-hell-a-developers-guide-to-managing-package-conflicts-in-2026-o2o) |
| **One attendee falls behind, derails the room** | Build-along has no built-in catch-up | Per-stage **checkpoint branches**; reset stragglers with `git reset --hard && git clean -fdx` [[6]](https://christoph-rumpel.com/2021/7/12-tips-for-better-live-coding) to the last green stage [[5]](http://blog.gilliard.lol/2018/10/25/live-coding-tips.html) |
| **Conference Wi-Fi dies mid-`npm install`** | Shared, throttled, hostile network | Pre-bake `node_modules` into the starter repo / vendor a cache; never depend on connectivity for the critical path [[5]](http://blog.gilliard.lol/2018/10/25/live-coding-tips.html) |
| **Hallucinated / wrong dependency** | AI-assisted scaffolding invents packages | Pin exact versions in the starter `package.json`; don't run AI-suggested `npm install` live [[17]](https://vocal.media/futurism/8-ai-code-generation-mistakes-devs-must-fix-to-win-2026) |
| **Typos under pressure** | Nerves + projector + 30 people watching | Don't hand-type boilerplate — paste prepared chunks [[6]](https://christoph-rumpel.com/2021/7/12-tips-for-better-live-coding), or script keystrokes with a tool like Demo Time [[7]](https://demotime.show/) |
| **Catastrophic break, no recovery** | Something just doesn't work on stage | Keep a **backup screen-recording** of a clean run; narrate what *should* happen and move to the next branch [[5]](http://blog.gilliard.lol/2018/10/25/live-coding-tips.html) |
| **Projector unreadable** | Low contrast, small font, line-wrap | Large font, high contrast (black-on-white beats themed terminals), test from the back of the room [[5]](http://blog.gilliard.lol/2018/10/25/live-coding-tips.html) |

### The four-part safety net

1. **Pre-baked checkpoints.** One git branch per stage (`00`…`05`). Any attendee, or you, can jump to the last-known-good state in seconds [[5]](http://blog.gilliard.lol/2018/10/25/live-coding-tips.html).
2. **Pinned starter repo.** `node_modules` cached or lock-file pinned, exact versions, `npm ci` [[16]](https://dev.to/vasughanta09/solving-dependency-hell-a-developers-guide-to-managing-package-conflicts-in-2026-o2o) — this removes the single largest failure source.
3. **Co-facilitation.** "Four eyes see more than two" [[4]](https://www.sessionlab.com/state-of-facilitation/2026-report/) — a co-presenter or TAs (≥1 per ~12) unblock individuals while the driver keeps the room moving. This is what makes a build-along survivable at all.
4. **Backup recording + fallback narration.** When all else fails, switch to the recorded clean run and keep the energy up [[5]](http://blog.gilliard.lol/2018/10/25/live-coding-tips.html).

## Bottom line for the Java/.NET room

Run **Agenda A's structure but with Agenda B's risk posture**: you drive the build live, and attendees join at the two checkpoints rather than typing every line. They are expert developers — the MCP concepts land in minutes — so spend the budget on the unfamiliar TS toolchain and on getting a *working* server into a real host, not on babysitting `npm install` across the room. Gate setup before the session, pin the starter repo, keep a recorded fallback, and put a TA in the room. That combination delivers the retention of hands-on [[1]](https://www.fielddrive.com/blog/best-workshop-ideas-next-event) without the failure surface that makes pure build-alongs collapse.
