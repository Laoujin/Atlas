---
title: "Task Design and Success Criteria for AI Coding Agent Cage Matches"
date: 2026-06-09
depth: standard
format: md
topic: "Task design and success criteria"
topic_raw: "Task design and success criteria"
issue: 208
tags: [ai-coding, benchmarking, evaluation, workshop, scoring, task-design, cage-match]
summary: "How to design tasks and score results when comparing AI coding agents head-to-head in a timed live-audience setting."
citations: 15
reading_time_min: 5
cover: cover.svg
cost_usd: 1.49
duration_sec: 562
model: "Sonnet 4.6"
---

> **Decision** Pick a **medium-scope feature implementation** (1–2 files, ~20 new lines, unfamiliar but realistic codebase) in a 30-minute time box. Score on 5 dimensions: correctness 40%, completeness 25%, code quality 15%, edge cases 10%, speed bonus 10%. Pre-lock the test file before the clock starts — the single biggest benchmark exploit is agents deleting tests to manufacture a pass. [[2]](https://benchmarkingagents.com/swe-bench/) Target a task where you expect 2–3 of 4 tools to partially succeed; all-pass or all-fail tasks tell you nothing. [[1]](https://arxiv.org/pdf/2604.00594)

## What makes a comparative task good

Three properties must hold simultaneously for a fair head-to-head:

**1. Appropriate difficulty — the 30–70% window.** Agent psychometrics research (applying classical test theory to AI evaluation) shows tasks where success rates fall in the middle range — neither near 0% nor near 100% — provide the most discriminative signal. [[1]](https://arxiv.org/pdf/2604.00594) Floor and ceiling tasks eliminate differentiation. The SWE-bench difficulty tiers map this to concrete scope metrics: [[3]](https://jatinganhotra.dev/blog/swe-agents/2025/04/15/swe-bench-verified-easy-medium-hard.html)

| Tier   | Time budget | Avg lines changed | Files modified | Multi-file % |
|--------|-------------|-------------------|----------------|--------------|
| Easy   | < 15 min    | 5                 | 1              | 3%           |
| Medium | 15–60 min   | ~20               | 1–2            | 30%          |
| Hard   | > 1 hour    | 56                | 2+             | 56%          |

For a 30–45 minute workshop slot, **medium** is the target tier: observable complexity without all-fail outcomes.

**2. Objective anchoring.** The gold-standard model is SWE-bench's dual criterion: a submission must achieve *fail-to-pass* (new failing tests now pass) AND *pass-to-pass* (existing green tests stay green). [[2]](https://benchmarkingagents.com/swe-bench/) No deletions allowed — lock `tests/` before the run. Objective anchoring means two judges watching the same run will agree on the score without negotiation.

**3. Real-world authenticity.** Benchmarks sourced from actual codebases outperform synthetic puzzles because they embed implicit context, naming conventions, and dependency graphs that agents must navigate — the same skills used daily. [[4]](https://runloop.ai/blog/understanding-llm-code-benchmarks-from-humaneval-to-swe-bench) Use a small open-source repo created or forked after the tools' training cutoffs to avoid contamination. HumanEval and MBPP are fully saturated by 2026 — all major tools score near ceiling and no longer discriminate. [[4]](https://runloop.ai/blog/understanding-llm-code-benchmarks-from-humaneval-to-swe-bench) [[13]](https://kili-technology.com/blog/ai-benchmarks-guide-the-top-evaluations-in-2026-and-why-theyre-not-enough)

## Task type comparison

| Task type                            | Observable? | Score objectively? | Discrimination risk         |
|--------------------------------------|-------------|--------------------|-----------------------------|
| Feature impl (endpoint + tests)      | ✓ High      | ✓ Test gate        | Low — ideal                 |
| Bug fix with failing tests           | ✗ Low       | ✓ Test gate        | Medium — progress invisible |
| Refactor + tests                     | ✓ Medium    | ✗ Subjective       | High — subjective success   |
| Algorithmic puzzle                   | ✗ Low       | ✓ Judge            | High — training saturation  |
| Full mini-app from scratch           | ✓ High      | ✗ Hard to grade    | High — inconsistent scope   |

**Recommended pattern:** add one new route to a small Express or Flask app; the repo has existing routes for reference, a `REQUIREMENTS.md` spec, and a locked `tests/` directory with at least 5 tests covering the happy path and 2 edge cases. [[5]](https://app.hackerearth.com/blog/crafting-hackathon-problem-statements) The existing routes give agents enough context to infer conventions without handing them the solution.

## Scoring rubric

Research on coding assessment rubrics recommends 4–6 dimensions, scored on a 1–4 scale, combining automated graders for objective criteria with LLM-as-judge for subjective ones. [[8]](https://www.shadecoder.com/topics/what-is-scoring-rubric-for-online-coding-assessment-a-practical-guide-for-2025) LLM judges agree with human reviewers ~85% of the time on structured rubrics — higher than inter-human agreement (~81%). [[11]](https://www.confident-ai.com/blog/why-llm-as-a-judge-is-the-best-llm-evaluation-method) Use a **static rubric** (fixed criteria applied identically to all agents) for fairness in a head-to-head; reliability improves when rubrics are explicit, criterion-separated, and calibrated. [[12]](https://medium.com/@adnanmasood/rubric-based-evals-llm-as-a-judge-methodologies-and-empirical-validation-in-domain-context-71936b989e80) [[15]](https://www.turingcollege.com/blog/evaluating-ai-agents-practical-guide)

| Dimension        | Weight | Grader       | 4-point anchor |
|------------------|--------|--------------|----------------|
| **Correctness**  | 40%    | Automated    | All tests pass / most / some / none |
| **Completeness** | 25%    | Automated    | All spec items / 3 of 4 / 2 of 4 / < half |
| **Code quality** | 15%    | LLM judge    | Clean + idiomatic / minor issues / poor names / unreadable |
| **Edge cases**   | 10%    | Automated    | Both handled / one / attempted / none |
| **Speed bonus**  | 10%    | Automated    | < 15 min / 15–25 / 25–35 / > 35 |

ProjDevBench validates a similar split: 80% Execution Score (verdict-level signals: compile error, runtime error, timeout, wrong answer) and 20% Code Review Score (rule-based + LLM). [[6]](https://arxiv.org/html/2602.01655v1) Displaying the Execution Score live during the run gives the audience a real-time scoreboard; add the Code Review Score afterward.

**Outcome over path.** Evaluate what agents produced, not the sequence of tool calls used to get there. Agents regularly find valid approaches eval designers didn't anticipate, so rigid step-checking penalises creativity unfairly. [[7]](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

## Partial credit and milestone scoring

Binary pass/fail discards meaningful signal — an agent that implements 3 of 4 endpoints is better than one that fails immediately. Two recent benchmark designs address this:

- **EvoClaw's Milestone Resolve Rate**: scores whether each ordered checkpoint was reached, plus a separate Score metric quantifying partial progress within each milestone. [[10]](https://arxiv.org/pdf/2603.13428)
- **SlopCodeBench**: structures tasks as ordered checkpoints pairing specs with test suites, exposing degradation patterns across the run. [[9]](https://arxiv.org/pdf/2603.24755)

For a live workshop: split the spec into 3 milestones (route defined → core tests pass → edge cases pass). Display milestone progress on screen. Audience sees which tools clear each gate in real time.

For non-deterministic comparison: **pass@1** scores the live single run; a post-event **pass@3** run (same task, three re-runs) separates fluky passes from reliably capable tools. [[7]](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

## Spec requirements

Spec misalignment is the single largest failure mode in end-to-end coding agent benchmarks — **41.86% of all failures** in ProjDevBench trace back to agents omitting critical business logic or misunderstanding requirements. [[6]](https://arxiv.org/html/2602.01655v1) A spec that passes the SMART test (Specific, Measurable, Achievable, Relevant, Time-bound) nearly eliminates this class of failure. [[5]](https://app.hackerearth.com/blog/crafting-hackathon-problem-statements) Required elements:

1. **User story** — "As an API consumer, I need `POST /items` to create a record and return 201."
2. **Explicit schema** — request body fields, response shape, HTTP status codes for each case.
3. **Quality standards** — e.g. "tests must pass, no `console.log` in production paths, follow existing error-handler pattern."
4. **Forbidden shortcuts** — "do not modify `tests/`, `package.json`, or `db/schema.sql`."
5. **Named edge cases** — at least 2 in the spec text; more in the locked test file.

## Anti-patterns

| Anti-pattern                      | Risk                                      | Mitigation                                              |
|-----------------------------------|-------------------------------------------|---------------------------------------------------------|
| Algorithmic puzzle                | Training data saturation; no progress visible | Use novel feature in post-cutoff repo               |
| Vague spec                        | 41% spec-misalignment failure rate        | 5 required spec elements above                          |
| Unlocked test file                | Agent deletes tests to fake a pass        | `chmod 444 tests/` before clock starts                  |
| Binary-only scoring               | Hides partial progress differences        | 5-dimension rubric + 3 milestone checkpoints            |
| Task too easy or too hard         | No discrimination signal                  | Target 30–70% expected solve rate                       |
| Scope drift (agent fixes extras)  | Complicates scoring, introduces regressions | Spec item 4: explicit forbidden-files list           |
| Network access during run         | Tools retrieve docs/solutions mid-task    | Air-gap or block outbound HTTP before start             |

Scope drift — agents completing the task and then unprompted fixing nearby code — is a documented failure pattern that complicates scoring and can introduce regressions. [[15]](https://www.turingcollege.com/blog/evaluating-ai-agents-practical-guide) The forbidden-files list in the spec double-loops with the locked test file.

## Environment parity

Any setup delta between agents becomes a tool-advantage, not a task-performance signal. Before the clock starts: [[14]](https://arxiv.org/pdf/2602.10975)

- All agents clone an **identical** repo snapshot (same commit SHA).
- Same language runtime and lockfile (`package-lock.json` / `poetry.lock` pinned).
- Same hardware (or same cloud tier) to eliminate latency/CPU asymmetry.
- Same model tier where the tool exposes a choice (e.g. all on the provider's "pro" plan).

FeatureBench research confirms that consistent environments are prerequisite for meaningful cross-agent comparisons on multi-file tasks. [[14]](https://arxiv.org/pdf/2602.10975)
