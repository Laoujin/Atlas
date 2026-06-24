---
title: "Testing an authored Claude Code Skill before you ship it to a team"
date: 2026-06-24
depth: standard
format: md
topic: "How practitioners test an authored Claude Code Skill before shipping: verifying the description triggers (and doesn't over-trigger), snapshot/regression patterns for skill behavior, Skill-specific CI, and description-collision detection, with 2026 tooling flagged"
topic_raw: "How practitioners TEST AN AUTHORED CLAUDE CODE SKILL before shipping it to a team — (a) description field triggers when intended and does NOT misfire, (b) the skill body produces the right behavior once invoked. Cover trigger-matching harnesses, snapshot/regression patterns, CI specific to Skills, description-collision detection, and 2026 tooling."
tags: [claude-code, skills, testing, evals, ci, agent-extensions]
summary: "The two things to test are separable — does the description trigger, and does the body behave — and in 2026 the de-facto harness is Anthropic's skill-creator eval loop plus a with-skill/without-skill baseline; everything else is thin."
citations: 11
reading_time_min: 6
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 325
issue: 222
---

> **TL;DR.** Test two things *separately*: (a) does the `description` fire on the right prompts and stay quiet on the wrong ones, and (b) does the body produce the right behavior once loaded [[1]](https://code.claude.com/docs/en/skills). The 2026 de-facto harness is Anthropic's **skill-creator** eval loop (`evals/evals.json` → run with-skill vs without-skill → grade assertions → blind A/B), which got a dedicated **description-tuning** mode on **March 3 2026** that scores should-trigger/should-not-trigger prompts and rewrites the description to cut false positives *and* false negatives [[2]](https://agentskills.io/skill-creation/evaluating-skills)[[3]](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills). For repeatable CI, the most concrete pattern is MLflow's headless-Claude-Code-plus-judges harness [[4]](https://mlflow.org/blog/evaluating-skills-mlflow/). Honest state of the art: trigger-matching is still ~50% reliable on autonomous activation, collision detection is manual, and a purpose-built "skill linter in CI" is mostly vaporware. Nobody has a clean push-button answer yet.

## The core split: trigger vs. behavior

Anthropic's own docs state the trap directly: *"Seeing a skill trigger tells you Claude found it, not that it did what you intended. To know a skill is working, measure two things separately: whether Claude invokes it on the prompts it should, and whether the output matches what you expect when it does."* [[1]](https://code.claude.com/docs/en/skills) Both are checked by the *same* primitive — a **baseline comparison**: run realistic prompts in a fresh session with the skill available and again with it disabled, then diff [[1]](https://code.claude.com/docs/en/skills). A fresh session is load-bearing — leftover authoring context masks gaps in the written instructions [[1]](https://code.claude.com/docs/en/skills).

## (a) Testing that the description triggers — and doesn't over-trigger

The `description` field *is* the trigger; Claude fuzzy-matches against it to decide whether to load the skill, so a vague description silently never fires [[6]](https://mcp.directory/blog/why-your-claude-skill-isnt-activating-2026-fixes). Autonomous activation is unreliable by default — practitioners report *"roughly a 50% success rate"* because Claude prioritises task completion over checking available tools [[5]](https://dev.to/lizechengnet/why-claude-code-skills-dont-trigger-and-how-to-fix-them-in-2026-o7h).

**skill-creator's description-tuning mode** is the only purpose-built trigger harness in 2026. It *"generates should-trigger and should-not-trigger prompts, measures the hit rate, and proposes description edits when the skill activates on the wrong requests"* [[1]](https://code.claude.com/docs/en/skills). The March 2026 upgrade frames this as a false-positive/false-negative classifier: it *"analyzes your current description against sample prompts and suggests edits that cut both false positives and false negatives"*; Anthropic ran it across their document-creation skills and *"saw improved triggering on 5 out of 6 public skills"* [[3]](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills). The wrapping tooling is branded the "Skill Description Improver" / grader / blind-comparator / analyzer set [[10]](https://www.whytryai.com/p/how-to-test-claude-skills).

Manual/diagnostic checks that catch trigger failures before ship:

| Symptom | Check / fix | Source |
|------------------------------|---------------------------------------------------------------------------------------------------|--------|
| Doesn't fire when expected   | Description missing keywords users would actually type; verify via `What skills are available?`    | [[1]][d] |
| Fires too often (over-trigger) | Make description more specific; or set `disable-model-invocation: true` for manual-only skills    | [[1]][d] |
| Silently truncated           | `/doctor` shows how many descriptions are shortened/dropped; budget is ~1% of context window      | [[1]][d] |
| Malformed YAML / multi-line desc | Skill loads with empty metadata → no `description` to match; run `--debug`; keep description single-line | [[1]][d][[7]][p] |
| Budget overflow with many skills | Raise `SLASH_COMMAND_TOOL_CHAR_BUDGET` / `skillListingBudgetFraction`; combined desc capped at 1,536 chars | [[5]][l][[1]][d] |

[d]: https://code.claude.com/docs/en/skills
[p]: https://perevillega.com/posts/2026-04-01-claude-code-skills-2-what-changed-what-works-what-to-watch-out-for/
[l]: https://dev.to/lizechengnet/why-claude-code-skills-dont-trigger-and-how-to-fix-them-in-2026-o7h

**Pre-write the trigger evals.** The practitioner consensus is to write the test cases *before* the SKILL.md body — *"write three test cases for your skill before writing the SKILL.md body"* (a positive, a negative, an edge case) so triggering has a measurable baseline [[5]](https://dev.to/lizechengnet/why-claude-code-skills-dont-trigger-and-how-to-fix-them-in-2026-o7h).

## (b) Testing the body behaves — snapshot & regression

This is the `evals/evals.json` loop, formalised in the Agent Skills open standard [[2]](https://agentskills.io/skill-creation/evaluating-skills). A test case is `{prompt, expected_output, files, assertions}`; the runner executes each prompt twice (with-skill / without-skill) in isolated subagent contexts, writing `grading.json` (per-assertion PASS/FAIL + evidence), `timing.json` (tokens, duration), and an aggregated `benchmark.json` with a `delta` block — *what the skill costs (time, tokens) vs. what it buys (pass-rate lift)* [[2]](https://agentskills.io/skill-creation/evaluating-skills).

```json
// evals/evals.json — the one file you author by hand
{ "skill_name": "csv-analyzer",
  "evals": [{
    "id": 1,
    "prompt": "find the top 3 months by revenue in data/sales_2025.csv and make a bar chart",
    "expected_output": "A bar chart of the top 3 months by revenue, labeled axes.",
    "files": ["evals/files/sales_2025.csv"],
    "assertions": ["The chart shows exactly 3 months", "Both axes are labeled"] }]}
```

**Snapshot / regression patterns that actually map to Skills:**

- **Versioned baseline (the snapshot).** Before editing, `cp -r <skill> <workspace>/skill-snapshot/` and run the new version against the snapshot as baseline — `old_skill/` vs the edit — instead of against no-skill [[2]](https://agentskills.io/skill-creation/evaluating-skills). This is the closest thing to a behavioral snapshot test.
- **Blind A/B version comparison.** skill-creator runs a *blind* comparison between two skill versions — the judge scores holistic quality without knowing which is which, *"so you can confirm an edit is an improvement before committing it"* and avoid confirmation bias [[1]](https://code.claude.com/docs/en/skills)[[2]](https://agentskills.io/skill-creation/evaluating-skills).
- **Iteration directories.** Each pass writes to `iteration-N/`, so regressions are diffable across runs; flaky evals show up as high `stddev` in the benchmark → signal of an ambiguous instruction, not just model noise [[2]](https://agentskills.io/skill-creation/evaluating-skills).
- **Rule-based assertions over LLM judgment for mechanical checks** (valid JSON, row counts, file exists) — *"scripts are more reliable than LLM judgment for mechanical checks and reusable across iterations"* [[2]](https://agentskills.io/skill-creation/evaluating-skills).

## Skill-specific CI

There is no first-party "test-this-skill" GitHub Action yet. The two real patterns:

**MLflow's headless harness** is the most concrete CI-shaped approach: a YAML config (`project_dir`, `skills`, `prompt`, `judges`, `timeout`) drives `mlflow autolog claude` to trace every tool call, then LLM + rule-based judges grade the trace; a refinement loop feeds failing judge rationales back to `claude -p "...Fix SKILL.md."` [[4]](https://mlflow.org/blog/evaluating-skills-mlflow/). Crucially for regression: *multiple test configs cover the same skill so "a fix that addresses one failing test config must not cause another to regress"* — overfit protection [[4]](https://mlflow.org/blog/evaluating-skills-mlflow/). This runs anywhere a shell runs (`claude -p` headless), which is the generic CI hook [[11]](https://github.com/anthropics/claude-code-action).

**Static linting in CI** is where the hype outruns reality. A dev.to post describes a `pulser` zero-dependency CLI / GitHub Action that lints skill frontmatter (YAML parse, required fields, description-quality score, broken cross-refs) and fails the PR on exit code 1 [[9]](https://dev.to/thestack_ai/testing-claude-code-skills-in-ci-pulser-eval-github-action-3na9). ⚠ **Flag:** I could not verify `pulser` exists — no `pulserin/pulser` repo and no `pulser` npm package resolve as of 2026-06-24. Treat it as unverified/aspirational, not a tool you can adopt.

## Detecting description collisions between skills

No tooling does this automatically — it's manual and behavioral. The failure mode: *"if two skills have overlapping descriptions you can get the wrong one… the choice is non-deterministic enough to be a debugging nightmare"* [[6]](https://mcp.directory/blog/why-your-claude-skill-isnt-activating-2026-fixes). Detection and mitigation in practice:

- Run skill-creator's should-trigger/should-not-trigger set with *both* skills installed and watch which one fires — a should-not-trigger hit on skill B for skill A's prompt *is* the collision signal [[3]](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills).
- Add explicit disambiguation lines — *"use this for X, not Y"* / *"Do not use for X"* — after observed misfires; narrow each skill's domain [[6]](https://mcp.directory/blog/why-your-claude-skill-isnt-activating-2026-fixes).
- Keep the active set small. Practitioner heuristic: *"5–8 active skills per project"*; beyond that, descriptions truncate and collisions multiply, and `/doctor` shows what's being dropped [[7]](https://perevillega.com/posts/2026-04-01-claude-code-skills-2-what-changed-what-works-what-to-watch-out-for/)[[1]](https://code.claude.com/docs/en/skills).
- For workflows that *must* fire, bypass the trigger lottery entirely: a `UserPromptSubmit` hook emitting an explicit `Use Skill(name)` is deterministic where description matching is ~50% [[5]](https://dev.to/lizechengnet/why-claude-code-skills-dont-trigger-and-how-to-fix-them-in-2026-o7h).

## Where to get the harness

| Tool | What it gives you | Stars |
|------|------------------------------------------------------------|-------|
| [skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) (install: `/plugin install skill-creator@claude-plugins-official`) [[8]](https://github.com/anthropics/claude-plugins-official) | Eval loop, description tuning, blind A/B, benchmark | ⭐ 31k |
| [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | Reference skill-creator source + skill examples [[2]](https://agentskills.io/skill-creation/evaluating-skills) | ⭐ 155k |
| [MLflow skill harness](https://mlflow.org/blog/evaluating-skills-mlflow/) | Trace-based CI judges + auto-refine loop [[4]](https://mlflow.org/blog/evaluating-skills-mlflow/) | n/a |

## Talk thesis, answered

*"How do you know the skill you authored actually works before you push it to your team?"* — In 2026 the honest answer: run a **with-skill/without-skill baseline** on a handful of real prompts in a *fresh* session, let **skill-creator** tune the description against should/should-not-trigger sets, snapshot the prior version for a blind A/B before each edit, and wire `claude -p` evals into CI if you want regression gates. But say the quiet part out loud in the talk: autonomous triggering is still a coin-flip-ish ~50% [[5]](https://dev.to/lizechengnet/why-claude-code-skills-dont-trigger-and-how-to-fix-them-in-2026-o7h), collision detection is eyeballing, and a real CI-native skill linter doesn't exist yet [[9]](https://dev.to/thestack_ai/testing-claude-code-skills-in-ci-pulser-eval-github-action-3na9). The maturity gap *is* the story.
