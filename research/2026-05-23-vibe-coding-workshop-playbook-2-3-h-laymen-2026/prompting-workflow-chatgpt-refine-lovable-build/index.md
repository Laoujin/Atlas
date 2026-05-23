---
title: "Prompting workflow: ChatGPT-refine → Lovable-build"
date: 2026-05-23
depth: standard
format: md
topic: "Prompting workflow: ChatGPT-refine → Lovable-build"
topic_raw: "Prompting workflow: ChatGPT-refine → Lovable-build"
issue: 56
tags: [lovable, chatgpt, vibe-coding, workshop, prompting]
summary: "A two-step workshop recipe — plan a structured PRD in ChatGPT (free, no credits burned), then paste it once into Lovable's Agent mode to seed the build."
citations: 17
reading_time_min: 7
cover: cover.svg
cost_usd: 2.01
duration_sec: 370
---

> **Decision.** For a 2–3 hour workshop with laymen: refine the idea into a structured PRD in ChatGPT (free, no Lovable credits burned [[1]](https://docs.lovable.dev/tips-tricks/chatgpt-app)), then hand off to Lovable's Agent mode for the build. If every attendee already has a Lovable account, skip ChatGPT and use Lovable's built-in **Chat Mode** for the same conversation — it's purpose-built to precede a build [[5]](https://lovable.dev/blog/chat-mode-and-questions). The ChatGPT step earns its keep when (a) attendees know ChatGPT but not Lovable, or (b) you want one tool for ideation across the cohort before anyone signs into Lovable.

## Why two tools instead of one

Lovable used to jump straight from the first prompt into code. That's still the default behaviour [[5]](https://lovable.dev/blog/chat-mode-and-questions), and for a beginner it's the worst possible default: a vague one-liner produces a vague app, and the fix consumes credits. Three reasons to plan elsewhere first:

1. **Credits are scarce on free.** Lovable's free tier gives 5 daily credits, capped at 30/month [[7]](https://docs.lovable.dev/introduction/plans-and-credits). A 20-person workshop has ~600 monthly credits to share. Every iteration costs 0.5–2 credits — a styling tweak ~0.5, a landing page ~2, adding auth ~1.2 [[10]](https://www.banani.co/blog/lovable-pricing-and-credits). Planning in chat is free; debugging a half-baked first build isn't.
2. **The handoff is built in.** The official ChatGPT app for Lovable lets you `@Lovable` inside a ChatGPT conversation; the prompt and the surrounding context become the initial build, and no credits are charged until the build actually fires [[1]](https://docs.lovable.dev/tips-tricks/chatgpt-app)[[2]](https://lovable.dev/chatgpt-app).
3. **ChatGPT is the familiar UX.** Most laymen already have a free ChatGPT account. Starting in a tool they know, then crossing into a new one once, is a softer learning curve than two unknowns at once.

## Step 1 — Refine in ChatGPT (≈ 30 minutes)

The goal of this step is **one structured paste** that you'll hand to Lovable. The handoff is one-way: Lovable's docs explicitly note that once you've seeded the project, "you need to open Lovable to continue editing" [[1]](https://docs.lovable.dev/tips-tricks/chatgpt-app). So the first paste matters more than any later one.

Lovable's own docs prescribe a four-question planning frame [[3]](https://docs.lovable.dev/prompting/prompting-one):

- **What is this?** One sentence.
- **Who is it for?** Target user.
- **Why will they use it?** Core value.
- **What's the one key action?** Primary CTA.

Have attendees answer those four in plain language, then ask ChatGPT to expand them into a PRD-style prompt. A working meta-prompt:

```
You are helping me brief Lovable.dev to build a small web app.
Here is my idea: <one paragraph from the attendee>.
Produce a single prompt that includes:
- Project overview (one sentence)
- Target audience
- 2–4 key pages with the components on each
- Design direction: pick 2 buzzwords from {minimal, expressive,
  cinematic, playful, premium, developer-focused}
- Empty / loading / error states for the main data view
- Mobile-first responsive note
Keep it under 250 words. End with: "Ask me any clarifying
questions before you start."
```

Two of those instructions are not decorative:

- The **design buzzwords** are an officially documented Lovable lever — terms like *minimal*, *expressive*, *cinematic*, *playful*, *premium*, *developer-focused* are interpreted as parameters that shift typography, spacing, shadow, radius, and palette [[3]](https://docs.lovable.dev/prompting/prompting-one)[[14]](https://aiagentskit.com/blog/lovable-prompting-guide/). Layman picks two; ChatGPT does the rest.
- The **clarifying-questions tail** is the single highest-yield trick in Lovable's docs: "Ask me any questions you need in order to fully understand what I want from this feature and how I envision it" [[3]](https://docs.lovable.dev/prompting/prompting-one). It surfaces the assumptions the AI would otherwise just guess at, and it works in both ChatGPT and Lovable.

If you don't want to write your own meta-prompt, there's a public **Lovable PRD Generator** Custom GPT that does this packaging for you [[15]](https://chatgpt.com/g/g-67e1e85fbeac8191a69b95c6d5c42ef6-lovable-prd-generator).

A canonical example of the kind of prompt this step should produce, from one widely-cited prompt library [[11]](https://www.buildwithlovable.xyz/blog/15-lovable-prompt-examples-that-actually-work-in-2026):

> Build a one-page site for a budgeting app targeted at Gen Z freelancers. The main CTA should be "Start Saving Smarter." Focus on a bold, expressive aesthetic with large text and punchy colors.

That's three sentences with all four planning answers folded in. It's the *floor*, not the ceiling.

## Step 2 — Build in Lovable (≈ 60 minutes)

Two routes from ChatGPT to a running app:

| Route                          | Friction                       | When to use                                  | Cost                                                       |
| ------------------------------ | ------------------------------ | -------------------------------------------- | ---------------------------------------------------------- |
| `@Lovable` tag inside ChatGPT  | One auth grant, one tag        | Attendees already in ChatGPT                 | No credits until build fires [[1]](https://docs.lovable.dev/tips-tricks/chatgpt-app) |
| Copy/paste into Lovable's "new project" box | Two windows, one paste | Attendees prefer staying inside Lovable      | Same                                                       |

Either way, the first paste lands in Lovable's **Agent mode** (also called Build mode), which is the execution mode that actually writes files [[6]](https://docs.lovable.dev/features/modes). For workshop iteration after the seed, two patterns matter:

- **Build by component, not by page.** The official docs are emphatic: "build by component, not full pages at once," and "use real content instead of placeholder text" [[3]](https://docs.lovable.dev/prompting/prompting-one). Asking for "the whole landing page redone" burns 2+ credits and tends to regress unrelated parts; asking for "the hero CTA, change copy to X, keep everything else" costs ~0.5 [[10]](https://www.banani.co/blog/lovable-pricing-and-credits).
- **Use the edit template.** Lovable's docs supply a literal pattern: *"Change [specific element] to [new specification]. Keep [what stays the same]."* [[3]](https://docs.lovable.dev/prompting/prompting-one). Drilling this template into attendees prevents the most expensive class of mistake.

For deeper changes mid-build, switch into **Chat Mode** before re-entering Agent mode. Chat Mode is conversational and doesn't touch code — it's "having a planning session with a technical co-founder before diving into development" [[5]](https://lovable.dev/blog/chat-mode-and-questions). The docs frame this cleanly: "Plan mode is for decision-making. Agent mode is for execution" [[6]](https://docs.lovable.dev/features/modes).

## Failure modes to teach explicitly

Workshop time is short. These are the failure modes worth naming out loud before attendees hit them:

- **Fix-one-break-ten.** The most-reported Reddit complaint about Lovable-class tools: "AI is still just soooooo stupid and it will fix one thing but destroy 10 other things in your code" [[9]](https://www.morphllm.com/reddit-vibe-coding). The countermeasure is the edit-template above and the next bullet.
- **Three-strike rule.** Lovable's own prompting guidance: "Three targeted correction prompts with no improvement is the signal to stop iterating and reassess the approach entirely" [[12]](https://www.lowcode.agency/blog/lovable-prompting-guide). For laymen the rule is more aggressive — **two failed corrections, then revert and re-prompt from scratch with more context.**
- **Vague prompts produce vague apps.** "A vague prompt leads to assumptions, and assumptions lead to apps that miss the mark" [[5]](https://lovable.dev/blog/chat-mode-and-questions). This is why the ChatGPT step exists.
- **Security blind spots.** Independent assessment found 170 of 1,645 Lovable-built apps had vulnerabilities exposing personal data [[9]](https://www.morphllm.com/reddit-vibe-coding). For a workshop this means: **don't have attendees connect Supabase auth to real PII**. Use seed data only.
- **Lorem ipsum trap.** Lovable's docs warn against placeholder text because it cascades — the AI builds layouts around the placeholders rather than the real content [[3]](https://docs.lovable.dev/prompting/prompting-one). Make attendees write three real product names, three real testimonial sentences, three real menu items before they paste.

## Workshop logistics that follow from the workflow

- **Timebox.** ~30 min refine in ChatGPT, ~60 min build in Lovable, ~30 min polish & deploy, ~30 min show-and-tell. The "first app in 1–2 hours" expectation is the published norm for beginner vibe-coding tutorials [[17]](https://www.coursera.org/learn/vibe-coding-with-lovable-from-idea-to-app), and Lovable's own format expects results in minutes once the seed prompt lands [[2]](https://lovable.dev/chatgpt-app).
- **Credit accounting.** 30 monthly free credits ÷ ~15 typical iterations per attendee ≈ 2 credits each, which is the budget for one page + four small edits. Tell attendees that explicitly so they spend deliberately. The May 2026 University of Ljubljana / AI4DH workshop runs a five-hour version of this same shape for humanities researchers, no programming required [[13]](https://ai4dh.eu/2026/04/20/vibe-coding-workshop-for-humanities-and-social-sciences/).
- **Curate examples.** Hand attendees 3–5 example PRDs (a landing page, a CRUD app, an internal tool, a portfolio). The [`cporter202/lovable-for-beginners`](https://github.com/cporter202/lovable-for-beginners) ⭐ 530 (May 2026) repo is a usable starting point [[16]](https://github.com/cporter202/lovable-for-beginners). The [Lovable Prompting Bible](https://lovable.dev/blog/2025-01-16-lovable-prompting-handbook) is the canonical longer-form reference if any attendee wants depth after the workshop [[4]](https://lovable.dev/blog/2025-01-16-lovable-prompting-handbook).
- **Have a "scaffolding designer" sit with you.** For attendees who want their PRD reviewed before the Lovable paste, a senior helper applying Lovable's "lightweight PRD" naming discipline — clear, stable labels for panels/buttons/cards because "small label changes can ripple through file paths" [[8]](https://medium.com/design-bootcamp/from-prompt-to-prototype-get-the-most-out-of-lovable-3eedb5c8e756) — saves a lot of mid-build pain.

## The single rule to drill

> Plan the *whole thing* in chat. Build *one component at a time* in code.

Every other tip in this artifact is a corollary. The two-tool workflow makes the rule concrete: chat happens in ChatGPT (free), code happens in Lovable (credits) — and that physical separation is what stops attendees from collapsing planning and building into a single underspecified prompt.
