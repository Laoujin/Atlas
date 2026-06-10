---
title: "User Story and Acceptance Criteria Authoring"
date: 2026-06-09
depth: standard
format: md
topic: "User story and acceptance criteria authoring"
topic_raw: "User story and acceptance criteria authoring"
issue: 204
tags: [agile, user-stories, acceptance-criteria, product-management, scrum, bdd]
summary: "Practical guide to writing user stories and acceptance criteria: formats, INVEST quality checks, splitting patterns, Three Amigos, Definition of Ready, and anti-patterns to avoid."
citations: 14
reading_time_min: 5
cover: cover.svg
cost_usd: 1.03
duration_sec: 403
model: "Sonnet 4.6"
---

> **TL;DR** Write stories as `As a [persona], I want [goal], so that [benefit]` [[1]](https://agileforall.com/new-to-agile-invest-in-good-user-stories/). Validate with INVEST before sprint commit [[2]](https://blog.logrocket.com/product-management/writing-meaningful-user-stories-invest-principle/). Write 3–5 acceptance criteria — **bullet checklist** for simple flows, **Given/When/Then** for conditional logic [[3]](https://www.altexsoft.com/blog/acceptance-criteria-purposes-formats-and-best-practices/). If a story needs more than 6 criteria, split it first [[4]](https://www.prodpad.com/blog/acceptance-criteria-examples/).

## The User Story Format

```
As a [role / persona], I want [goal], so that [benefit].
```

The "so that" clause is the most skipped part and the most important: it forces you to verify the goal actually delivers value rather than just describing a feature [[1]](https://agileforall.com/new-to-agile-invest-in-good-user-stories/).

| Weak                          | Strong                                                                                                            |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| "User can reset password"     | "As a returning user, I want to reset my password via email, so that I can regain access without calling support." |
| "Add CSV export"              | "As a site admin, I want to export user data as CSV, so that I can share it with analytics without a database dump." |
| "Build the dashboard"         | "As a manager, I want to see team velocity on a dashboard, so that I can identify blockers before end of sprint." |

## INVEST: Quality Checklist Before Sprint

Introduced by Bill Wake [[1]](https://agileforall.com/new-to-agile-invest-in-good-user-stories/). Run this check before pulling a story into sprint planning [[14]](https://scrum-master.org/en/creating-the-perfect-user-story-with-invest-criteria/):

| Criterion       | Question to ask                                           | Common failure                                        |
| --------------- | --------------------------------------------------------- | ----------------------------------------------------- |
| **I**ndependent | Can it ship without another story being live first?       | Story A blocks Story B — forces sequential scheduling |
| **N**egotiable  | Are the details still open for conversation?              | Story treated as a fixed spec, team rubber-stamps it  |
| **V**aluable    | Does completing it deliver something a user cares about?  | "Set up DB schema" as a user-facing story             |
| **E**stimatable | Does the team know enough to size it?                     | Too vague, or too large to estimate confidently       |
| **S**mall       | Completable within one sprint?                            | "Build the user profile system" (an epic in disguise) |
| **T**estable    | Can someone write a failing test for this?                | "The UI should feel intuitive"                        |

[[2]](https://blog.logrocket.com/product-management/writing-meaningful-user-stories-invest-principle/)

## Acceptance Criteria Formats

Three formats — pick by complexity [[3]](https://www.altexsoft.com/blog/acceptance-criteria-purposes-formats-and-best-practices/) [[6]](https://medium.com/agile-true-north/the-3-templates-that-make-writing-acceptance-criteria-actually-easy-fe219a5bcad3):

| Format           | Best for                                                   | Skip when                                         |
| ---------------- | ---------------------------------------------------------- | ------------------------------------------------- |
| Bullet checklist | Simple CRUD, clear happy path, team shares the context     | Multiple conditional branches exist               |
| Given/When/Then  | Complex business logic, BDD/automation, multi-path flows   | Overkill for a single-outcome field validation    |
| Rules-based      | Business constraints, integration boundaries, compliance   | Scenarios flow naturally as GWT                   |

### Bullet checklist — password reset [[6]](https://medium.com/agile-true-north/the-3-templates-that-make-writing-acceptance-criteria-actually-easy-fe219a5bcad3)

- Reset link emailed within 2 minutes of request
- Link expires after 24 hours
- New password: ≥8 characters, ≥1 uppercase letter, ≥1 digit
- User is automatically logged in after successful reset
- Confirmation message shown: "Your password has been updated"

### Given/When/Then — discount code [[5]](https://www.parallelhq.com/blog/given-when-then-acceptance-criteria)

- **Scenario A:** Given a valid "SAVE20" code and a $100 cart, When applied, Then a $20 discount is labelled in the order summary
- **Scenario B:** Given an invalid code, When applied, Then an error is displayed and the cart total is unchanged
- **Scenario C:** Given an expired code, When applied, Then "Code expired" message shown, no discount applied

Quantify outcomes — "loads in < 200 ms" beats "loads quickly" [[5]](https://www.parallelhq.com/blog/given-when-then-acceptance-criteria). One criterion = one condition: no AND/OR inside a single line.

### Rules-based — payment failures [[4]](https://www.prodpad.com/blog/acceptance-criteria-examples/)

- If a payment fails → alert the billing team immediately
- If three consecutive failures occur → lock the account and notify the user
- If a fraud flag is set → route to manual review, block automated retry

## Acceptance Criteria Quality Rules

1. **3–5 per story.** More than 6 → the story is an epic; split it [[4]](https://www.prodpad.com/blog/acceptance-criteria-examples/).
2. **Measurable.** "< 2 seconds" not "fast". "Yes/No" testable [[11]](https://testomat.io/blog/clear-acceptance-criteria-for-user-stories-bdd-way/).
3. **One criterion, one condition.** No AND/OR conjunctions.
4. **Cover the edge cases.** Empty state, error state, permission boundaries.
5. **Include non-functionals.** Performance, security, accessibility — don't assume they're implied.
6. **Written before development starts** — not as an afterthought once QA asks for test cases [[12]](https://www.zenhub.com/blog-posts/acceptance-criteria-what-it-is-and-best-practices).

## Story Splitting Patterns

When INVEST.Small fails, use one of these nine patterns [[7]](https://www.humanizingwork.com/the-humanizing-work-guide-to-splitting-user-stories/):

| Pattern              | When to apply                                 | Example                                                      |
| -------------------- | --------------------------------------------- | ------------------------------------------------------------ |
| Workflow steps       | Story spans a sequential process              | "Publish article" → draft / review / approve / publish       |
| CRUD operations      | Story covers multiple actions on one entity   | "Manage account" → create / edit / delete                    |
| Business rule paths  | Different rule branches in one story          | Flexible-date search → by range / by weekend / by ±N days    |
| Data variations      | Multiple input types need different handling  | File upload → PDF first, then images, then XLSX              |
| Happy path first     | Edge cases dominate the complexity            | Basic login → then 2FA → then lockout/brute-force            |
| User roles           | Different access levels need different UX     | Dashboard → admin view first, then manager, then employee    |
| Interface / platform | Multiple delivery channels                    | Notifications → web first, then mobile push                  |
| Defer performance    | Speed is optional for v1                      | "Search works" → "search < 1 s" next sprint                  |
| Spike                | Unknown implementation approach               | "Investigate payment gateway options" (time-boxed story)     |

[[8]](https://skillifysolutions.com/blogs/agile/story-splitting/) Meta-pattern: find the core complexity → identify its variations → reduce to one slice → build the rest incrementally.

## The Three Amigos

Pre-sprint ritual: **Business (PO) + Developer + Tester** review each story together before it enters a sprint. Goal: surface misunderstandings when a conversation is cheap [[9]](https://agilealliance.org/glossary/three-amigos/). Recommended duration: 30–45 min, scheduled before refinement and estimation sessions.

Each perspective adds something the others miss:

- **PO:** Is this story delivering the right value? Does the acceptance criteria match actual user intent?
- **Dev:** Is this technically feasible? What constraints might change the design?
- **Tester:** Can I write tests for this? What scenarios are missing from the acceptance criteria?

## Definition of Ready

A story is ready to pull into a sprint when it passes all of [[10]](https://www.atlassian.com/agile/project-management/definition-of-ready):

- [ ] Written in the agreed user story format
- [ ] Acceptance criteria defined, measurable, and agreed by the whole team
- [ ] INVEST-compliant: no blocking dependencies, fits within one sprint
- [ ] UI/UX designs attached (if UI-facing)
- [ ] External dependencies (APIs, third-party services, data sources) identified
- [ ] Estimated (story points or T-shirt size)
- [ ] No open questions that would block development once the sprint starts

## Common Anti-Patterns

| Anti-pattern          | Problem                                           | Fix                                                        |
| --------------------- | ------------------------------------------------- | ---------------------------------------------------------- |
| System as actor       | "The API should validate the email format"        | "As a user, I want inline email validation feedback"       |
| Epic-as-story         | "Build the entire checkout flow"                  | Split by workflow steps into 4–6 stories                   |
| Vague AC              | "Should feel intuitive" / "should be accessible"  | Replace with a measurable, yes/no-testable outcome         |
| AND-heavy AC          | "User can search, filter, and sort results"       | One criterion per capability                               |
| Missing "so that"     | "As a user, I want a dashboard"                   | Add the benefit — it reveals whether the story is correct  |
| AC as implementation  | "Back-end should use Redis for session caching"   | Describe observable behavior, not the chosen solution      |
| Too many AC           | 10+ criteria on a single story                    | Story is an epic; split it before estimating               |

[[13]](https://medium.com/@carmineingaldi/user-stories-writing-antipatterns-9e9e1ff710b9) [[2]](https://blog.logrocket.com/product-management/writing-meaningful-user-stories-invest-principle/)
