---
title: Presentation craft for non-technical audiences
date: 2026-04-28
depth: ceo
format: md
topic: "Presentation craft for non-technical audiences"
topic_raw: "Presentation craft for non-technical audiences"
issue: 23
tags: [presentation, communication, public-speaking, ai-security, executive]
summary: A CEO-depth playbook for explaining technical work — especially AI security — to audiences who don't share your jargon.
citations: 7
reading_time_min: 2
cover: cover.svg
cost_usd: 0.73
duration_sec: 83
---

> **TL;DR.** Open with the bottom line, not the build-up. Frame every technical claim as a business consequence (revenue, cost, risk, reputation), use one analogy per concept, and repeat the core message ~7 times. For an AI security talk specifically: map threats onto risk categories the audience already owns (data protection, third-party, compliance, reputation) and translate findings into dollars + a decision the audience must make [[1]](https://lsaglobal.com/4-proven-ways-to-present-technical-ideas-to-non-technical-audiences/) [[5]](https://www.roguewaive.com/presenting-ai-risk-to-the-board/).

## The five moves that matter most

| Move | What it looks like | Why it works |
|---|---|---|
| **Lead with BLUF** | First 2–3 sentences carry situation, complication, and your recommendation [[2]](https://en.wikipedia.org/wiki/BLUF_(communication)) | Executives are problem-solvers; they decide whether to keep listening in ~30 seconds [[1]](https://lsaglobal.com/4-proven-ways-to-present-technical-ideas-to-non-technical-audiences/) |
| **Audience is the hero, you're the mentor** | Use Duarte's *Sparkline*: toggle between "what is" and "what could be," ending on a call to action [[3]](https://www.duarte.com/resources/talks/the-secret-structure-of-great-talks/) | Empathy frames the talk around their stakes, not your work |
| **One analogy per concept, no jargon** | "Prompt injection is SQL injection for English" — anchor every term in something they already know [[4]](https://online.stanford.edu/10-tips-communicating-technical-ideas-non-technical-people) | Buzzwords and acronyms make non-technical audiences tune out fast [[1]](https://lsaglobal.com/4-proven-ways-to-present-technical-ideas-to-non-technical-audiences/) |
| **10-7 rule** | Identify the most essential 10% of the message, repeat it ~7 times across the talk [[1]](https://lsaglobal.com/4-proven-ways-to-present-technical-ideas-to-non-technical-audiences/) | Recall is driven by repetition, not novelty |
| **One idea per slide, visual over text** | ≤3–4 short bullets, replace bullets with a diagram when systems are involved [[1]](https://lsaglobal.com/4-proven-ways-to-present-technical-ideas-to-non-technical-audiences/) [[3]](https://www.duarte.com/resources/talks/the-secret-structure-of-great-talks/) | Slides are scaffolding, not the script |

## AI-security-specific reframing

A non-technical audience doesn't need the threat model. They need:

- **Translation into money.** "We found 47 unauthorized AI tools" lands as noise; "$8.4M in exposure via 47 AI tools touching customer PII" lands as a decision [[5]](https://www.roguewaive.com/presenting-ai-risk-to-the-board/).
- **Mapping to risk categories they already own.** Data protection, third-party/vendor risk, compliance, and reputation — AI rarely needs a new bucket [[5]](https://www.roguewaive.com/presenting-ai-risk-to-the-board/) [[6]](https://hbr.org/2026/04/ai-is-reshaping-cyber-risk-boards-need-to-manage-the-threat).
- **Practical risks before exotic ones.** Employees pasting customer data into public LLMs beats data-poisoning and model theft as your opener — it's what's happening this week [[5]](https://www.roguewaive.com/presenting-ai-risk-to-the-board/).
- **Take a position.** Boards want to know what you recommend, not a balanced survey of options [[5]](https://www.roguewaive.com/presenting-ai-risk-to-the-board/) [[7]](https://www.gartner.com/en/articles/ai-presentation).

## The pre-flight checklist

1. Can a stranger state your one-line recommendation after slide 1? If no, rewrite the opener.
2. Does every technical term have an analogy or a concrete example within 10 seconds of first use? [[4]](https://online.stanford.edu/10-tips-communicating-technical-ideas-non-technical-people)
3. Does every claim end in "so what?" — a cost, risk, or decision?
4. Have you cut the slide that's there because it took you a long time to make? (Sunk-cost slides are the most common reason talks bloat.)
5. Watch faces in the first three minutes — confused → slow down; nodding → advance [[1]](https://lsaglobal.com/4-proven-ways-to-present-technical-ideas-to-non-technical-audiences/).
