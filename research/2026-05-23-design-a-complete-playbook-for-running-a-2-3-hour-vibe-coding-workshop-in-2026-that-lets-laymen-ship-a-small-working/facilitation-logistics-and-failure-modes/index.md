---
title: "Facilitation logistics and failure modes for a 2-3 hour vibe coding workshop"
date: 2026-05-23
depth: ceo
format: md
topic: "Facilitation logistics and failure modes"
topic_raw: "Facilitation logistics and failure modes"
issue: 56
tags: [facilitation, workshops, vibe-coding, logistics, failure-modes]
summary: "The pre-flight checklist, room/tool fallbacks, and the failure modes that actually sink 2-3 hour vibe coding workshops."
citations: 7
reading_time_min: 2
cover: cover.svg
cost_usd: 0.85
duration_sec: 144
---

> **Decision.** Spend 30 min on pre-flight (accounts, wifi, billing) before participants arrive — the workshop dies on logistics, not pedagogy. Plan for one AI provider going down: have a second IDE/key ready. Cut scope ruthlessly; one shipped tiny app beats a half-built ambitious one [[1]](https://medium.com/design-bootcamp/top-7-most-common-mistakes-done-by-workshop-facilitators-a5e7588de262)[[2]](https://voltagecontrol.com/articles/the-pitfalls-of-poor-facilitation-common-mistakes-and-how-to-avoid-them/).

## Pre-flight checklist (do before doors open)

| Item                      | Why it matters                                                                                                                          |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Test wifi from a laptop   | Venue wifi often blocks new MACs or rate-limits — discover it now, not at minute 5 [[3]](https://hep-fcc.github.io/fcc-tutorials/master/software-basics/prerequisites.html) |
| Pre-create accounts list  | Email, GitHub, Cursor/Claude, Vercel sign-ups eat 20+ min of live time [[4]](https://vibecodingworkshops.com/)                          |
| Top up API credits        | Anthropic free-tier is 5 req/min, paid is per-org — assume one shared key will rate-limit [[5]](https://platform.claude.com/docs/en/api/rate-limits) |
| Have a backup model       | If Claude is down, Cursor's GPT/Gemini fallback keeps the room shipping                                                                 |
| Print the agenda          | Visible on the wall — sets stage and pace, the single biggest workshop hygiene win [[1]](https://medium.com/design-bootcamp/top-7-most-common-mistakes-done-by-workshop-facilitators-a5e7588de262) |

## Failure modes ranked by frequency

| Mode                                     | Trigger                                              | Mitigation                                                                                                                       |
| ---------------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Setup eats the session**               | Sign-ups, installs, wifi onboarding done live        | Send pre-work email 48h ahead with accounts to create and a 5-line "if you only do one thing" install [[3]](https://hep-fcc.github.io/fcc-tutorials/master/software-basics/prerequisites.html) |
| **Overloaded agenda**                    | Facilitator wants to cover everything                | One outcome only: a deployed URL. Cut the rest [[1]](https://medium.com/design-bootcamp/top-7-most-common-mistakes-done-by-workshop-facilitators-a5e7588de262) |
| **Lecture creep**                        | Facilitator dominates the room                       | Hard rule: < 25% of clock is facilitator talking; the rest is hands on keyboards [[2]](https://voltagecontrol.com/articles/the-pitfalls-of-poor-facilitation-common-mistakes-and-how-to-avoid-them/) |
| **AI provider down / rate-limited**      | Shared key, Cursor outage, Anthropic 529s            | Second provider configured in-IDE; tell participants to switch model dropdown, not call support [[5]](https://platform.claude.com/docs/en/api/rate-limits) |
| **One stuck participant blocks the room**| Facilitator drops into 1:1 debugging                 | Co-facilitator handles individual blockers; lead keeps cohort moving                                                             |
| **Fizzle ending, no artefact**           | Out of time before deploy                            | Build in deploy-by minute T-30; demo round is non-negotiable [[6]](https://about.stormz.me/en/blog/article/five-common-mistakes-when-preparing-collaborative-workshop/) |
| **No follow-up → no retention**          | 43.5% of facilitators report no post-session contact | Send recap email same day with URL list, next-step prompt, and "ship one more thing this week" challenge [[7]](https://www.sessionlab.com/state-of-facilitation/2026-report/) |

## Timing skeleton (150 min)

| Block             | Min    | Notes                                                              |
| ----------------- | ------ | ------------------------------------------------------------------ |
| Welcome + agenda  | 0–10   | Show the final artefact you'll all ship; set the bar [[1]](https://medium.com/design-bootcamp/top-7-most-common-mistakes-done-by-workshop-facilitators-a5e7588de262) |
| Tool tour + prompt| 10–30  | One live build by the facilitator, narrated                        |
| Build block 1     | 30–80  | Cohort builds; co-facilitator floats                               |
| Break             | 80–90  | Non-negotiable — skip it and engagement collapses [[1]](https://medium.com/design-bootcamp/top-7-most-common-mistakes-done-by-workshop-facilitators-a5e7588de262) |
| Build block 2     | 90–120 | Deploy starts here, not at the end                                 |
| Demo round        | 120–145| Each person shares URL; 90 sec each                                |
| Wrap + follow-up  | 145–150| Recap email going out today; one homework prompt [[7]](https://www.sessionlab.com/state-of-facilitation/2026-report/) |

## The two rules that prevent most of the above

1. **Pre-work is not optional.** If participants arrive without accounts, you are running a 30-min IT helpdesk, not a workshop [[3]](https://hep-fcc.github.io/fcc-tutorials/master/software-basics/prerequisites.html).
2. **One artefact, deployed.** The whole session is reverse-engineered from "everyone has a live URL by minute 145." Anything that doesn't serve that goal gets cut [[6]](https://about.stormz.me/en/blog/article/five-common-mistakes-when-preparing-collaborative-workshop/).
