---
title: "Workshop Exercises & Scaffolding for AI-Assisted TDD"
date: 2026-06-03
depth: standard
format: md
topic: "Workshop exercises & scaffolding"
topic_raw: "Workshop exercises & scaffolding"
issue: 182
tags: [workshop, tdd, ai-testing, exercises, scaffolding, copilot, kata]
summary: "Curated exercises, katas, and scaffolding patterns for a hands-on AI-assisted TDD mini-workshop targeting expert developers."
citations: 22
reading_time_min: 6
cover: cover.svg
cost_usd: 1.46
duration_sec: 620
model: "Sonnet 4.6"
---

> **TL;DR** — Run 2–3 exercises, not ten. Expert developers disengage from trivially simple katas; start with a warm-up that calibrates the room (15 min), then move immediately to a realistic problem. The dominant scaffolding pattern: **failing tests pre-written, participants implement with AI** — this enforces TDD discipline without debating whether to write tests first. Use a Dev Container to eliminate environment setup as a time sink. [[1]](https://www.theregister.com/2026/02/20/from_agile_to_ai_anniversary/) [[2]](https://github.com/eficode/copilot-tdd-exercise)

## Technical Scaffolding

The biggest practical decision is eliminating environment friction before any coding starts. [Centric Consulting's 10-lab workshop](https://github.com/centricconsulting/ai-coding-workshop) ⭐ 6 [[5]](https://github.com/centricconsulting/ai-coding-workshop) solves this with a Dev Container participants open in one click — no local toolchain required. Key components of a production-ready workshop scaffold:

- **Dev Container / GitHub Codespaces** — one config, everyone runs the same runtime + AI extension. Centric offers a choice of .NET, Spring Boot, or bilingual containers [[5]](https://github.com/centricconsulting/ai-coding-workshop).
- **`.github/copilot-instructions.md` or `.cursor/rules`** — encode TDD rules ("write the failing test first; never implement without a red test") so the AI tool itself enforces the discipline [[18]](https://helpercode.com/2026/03/16/kiro-for-test-driven-development-tdd/).
- **Skeleton repo with failing tests pre-written** — participants clone a repo where tests exist but implementation stubs are empty, then make them pass with their AI tool [[2]](https://github.com/eficode/copilot-tdd-exercise).
- **Reference solution on a separate branch** — unblocks stuck participants without spoiling the exercise for everyone else [[5]](https://github.com/centricconsulting/ai-coding-workshop).
- **`prompts/` folder** — participants log each AI prompt chronologically as they work, making debrief discussions on prompt quality concrete rather than hypothetical [[4]](https://github.com/xpepper/goose-game-ai-driven).
- **CI on every push** — instant green/red signal via GitHub Actions; removes the facilitator as a validation bottleneck [[2]](https://github.com/eficode/copilot-tdd-exercise).

[Caltech's one-day format](https://ctme.caltech.edu/ai-assisted-software-development-custom.html) [[6]](https://ctme.caltech.edu/ai-assisted-software-development-custom.html) adds reusable checklists and an "LLM-in-the-loop" operating pattern participants take home. Provide both a reference impl branch *and* a take-home checklist; the checklist is what sticks.

## Exercise Catalog

For a 90-minute or half-day session, pick **one warm-up + one main exercise**. The table below spans the full range:

| Exercise                    | Type                  | Duration  | Difficulty  | Key learning                         |
|-----------------------------|-----------------------|-----------|-------------|--------------------------------------|
| [String Calculator][e-sc]   | Greenfield TDD        | 15–20 min | Warm-up     | Incremental test growth; calibration |
| [Tetris skeleton][e-tet]    | Greenfield AI TDD     | 45–60 min | Medium      | Failing-tests-first with AI          |
| [Goose Game][e-gg]          | Greenfield AI TDD     | 45–60 min | Medium      | Prompt engineering + RGR loop        |
| [Gilded Rose][e-gr]         | Legacy refactoring    | 40–60 min | Medium-High | Characterization tests with AI       |
| [Trip Service][e-ts]        | Dependency breaking   | 45–60 min | High        | Seam isolation before adding tests   |
| EXACT mini-project          | Full EXACT workflow   | 60–90 min | Expert      | Example Mapping → AI-TDD synthesis   |

[e-sc]:  https://osherove.com/tdd-kata-1
[e-tet]: https://github.com/eficode/copilot-tdd-exercise
[e-gg]:  https://github.com/xpepper/goose-game-ai-driven
[e-gr]:  https://understandlegacycode.com/blog/5-coding-exercises-to-practice-refactoring-legacy-code/
[e-ts]:  https://understandlegacycode.com/blog/5-coding-exercises-to-practice-refactoring-legacy-code/

**String Calculator** [[16]](https://osherove.com/tdd-kata-1): Roy Osherove's canonical warm-up. Starts with `add("") == 0`, incrementally adds comma delimiters, newlines, custom delimiters, and negatives. For an expert audience, run it *twice*: once without AI (baseline), once with AI (measure delta). The comparison lands more convincingly than any slide. See also [garora/TDD-Katas](https://github.com/garora/TDD-Katas) ⭐ 735 [[22]](https://github.com/garora/TDD-Katas) for a broader multi-language kata collection.

**Skeleton katas** [[2]](https://github.com/eficode/copilot-tdd-exercise) [[4]](https://github.com/xpepper/goose-game-ai-driven): both pre-write the full test suite; participants use their AI tool to make tests pass. [Eficode's Tetris](https://github.com/eficode/copilot-tdd-exercise) ⭐ 0 phases tests across board initialization, movement mechanics, line clearing, and scoring. [Goose Game](https://github.com/xpepper/goose-game-ai-driven) ⭐ 3 (Kotlin) adds a `prompts/` log that becomes debrief material on where AI needed disambiguation [[4]](https://github.com/xpepper/goose-game-ai-driven).

**Legacy katas** [[9]](https://understandlegacycode.com/blog/5-coding-exercises-to-practice-refactoring-legacy-code/): The [Gilded Rose](https://understandlegacycode.com/blog/5-coding-exercises-to-practice-refactoring-legacy-code/) is the entry point — pure nested conditionals, no external dependencies, so participants focus on writing characterization tests before touching any logic. Trip Service escalates: participants must break HTTP/DB dependencies to get code under test, a problem AI alone cannot reliably solve without human seam design. [Bourgau's dojo progression](https://philippe.bourgau.net/a-coding-dojo-exercises-plan-towards-refactoring-legacy-code/) [[8]](https://philippe.bourgau.net/a-coding-dojo-exercises-plan-towards-refactoring-legacy-code/) maps the full 4-stage path from FizzBuzz to Ugly Trivia if you want to run a multi-session track.

## Frameworks: TDAID and EXACT

Two frameworks add structure that's worth teaching explicitly alongside the exercises.

**TDAID (Test-Driven AI Development)** [[3]](https://www.awesome-testing.com/2025/10/test-driven-ai-development-tdaid) extends the classic loop with a **Plan** phase before Red and a **Validate** phase after Refactor. Plan: AI generates a structured implementation roadmap. Validate: human reviews the diff to ensure the agent didn't "cheat" by writing tests that confirm broken behavior [[1]](https://www.theregister.com/2026/02/20/from_agile_to_ai_anniversary/) [[21]](https://www.devclass.com/development/2026/02/21/should-there-be-a-new-manifesto-for-ai-development/4091612). Exercise shape for TDAID: write the plan as a comment block, let AI drive Red → Green → Refactor, then human-review the git diff before moving to the next increment.

**EXACT Coding** [[12]](https://www.codecentric.de/en/knowledge-hub/blog/exact-coding-with-ai) (Example-guided AI-Collaborative Test-driven Coding) prepends an **Example Mapping** session to the first test: team clarifies story, rules, examples, and open questions in a short structured conversation. Three autonomy levels let participants choose their control posture:

| Level | AI runs until...               | Recommended for              |
|-------|--------------------------------|------------------------------|
| A     | End of feature                 | Experienced AI users, speed  |
| B     | End of each RGR cycle          | Default; balanced control    |
| C     | End of each phase              | Learning mode; max oversight |

[e-exact]: https://www.codecentric.de/en/knowledge-hub/blog/exact-coding-with-ai

Level B is the default for workshop use — frequent enough to stay engaged, coarse enough that AI assistance feels meaningful [[12]](https://www.codecentric.de/en/knowledge-hub/blog/exact-coding-with-ai). The [GitHub Copilot Workshop](https://customer-workshops.github.io/copilot-workshop/index.html) [[15]](https://customer-workshops.github.io/copilot-workshop/index.html) structures a similar three-path progression (IDE features → pro/agents → CLI/SDK) that maps well onto beginner-to-expert cohorts.

For AI-specific techniques inside an exercise, [Automattic's pattern](https://github.com/readme/guides/github-copilot-automattic) [[11]](https://github.com/readme/guides/github-copilot-automattic) is worth demonstrating: after writing one test, ask the AI to "triangulate examples" — it generates additional edge-case assertions from existing code structure, eliminating manual boilerplate. Similarly, GitHub's `/tests` slash command [[10]](https://github.blog/ai-and-ml/github-copilot/github-for-beginners-test-driven-development-tdd-with-github-copilot/) lets participants describe requirements in natural language and get AI-generated test scaffolding back in one step.

## Anti-pattern Demo: Vibe Coding vs. TDD

Reserve 10–15 minutes for a live demonstration of the failure mode. Start a feature without tests, use AI to "just implement it," add a second feature, observe the architecture degrade. Without tests, AI coding agents never spontaneously suggest refactoring, producing monolithic, tightly coupled code where each new feature takes longer than the last [[20]](https://www.softwareseni.com/understanding-anti-patterns-and-quality-degradation-in-ai-generated-code/). The fix isn't discipline — it's tests: they enforce interface stability, make hallucinated code fail immediately, and prevent the "refactoring avoidance" anti-pattern [[14]](https://medium.com/@rupeshit/tdd-in-the-age-of-vibe-coding-pairing-red-green-refactor-with-ai-65af8ed32ae8). Show the vibe-coded diff alongside the TDD diff; expert developers will internalize the point without further argument.

Planning-first also helps: creating a mini-PRD or `SPEC.md` before prompting [[13]](https://beyond.addy.ie/) shifts AI from free-wheeling code generator to constrained implementation engine — a pattern that pairs naturally with EXACT's Example Mapping step.

## Expert Audience Considerations

- **Skip TDD theory.** They know what red-green-refactor is. Spend that time on what *changes* with AI in the loop: the Validate phase, autonomy levels, prompt engineering.
- **Use real-world complexity.** [Codely's approach](https://codely.com/en/ai-workshop) [[7]](https://codely.com/en/ai-workshop) of working on existing codebases (not greenfield toys) is more relevant and more engaging for senior developers.
- **Pair strategically.** Pair architects (who own test strategy and system design) with devs who drive agent prompts and the RGR cycle [[19]](https://completeaitraining.com/news/agile-turns-25-tdd-proves-crucial-for-ai-coding-as-security/). Knowledge transfer surfaces naturally without making it the explicit goal.
- **Leave autonomy open.** Let participants choose their AI tool's EXACT autonomy level rather than mandating one [[12]](https://www.codecentric.de/en/knowledge-hub/blog/exact-coding-with-ai). Comparing Level A vs Level C choices in debrief is itself a rich discussion.
- **Debrief the prompts, not the code.** The most valuable expert discussion is about prompt quality: what context the AI needed, where it hallucinated, where it outperformed. The `prompts/` log pattern [[4]](https://github.com/xpepper/goose-game-ai-driven) makes this concrete.

For open-source curricula to adapt, see [GitHub Copilot Bootcamp](https://dev.to/pwd9000/github-copilot-bootcamp-a-free-4-week-training-curriculum-to-master-ai-powered-development-h5b) [[17]](https://dev.to/pwd9000/github-copilot-bootcamp-a-free-4-week-training-curriculum-to-master-ai-powered-development-h5b) (4-week open curriculum with labs and weekly reflections) and [Caltech CTME's format](https://ctme.caltech.edu/ai-assisted-software-development-custom.html) [[6]](https://ctme.caltech.edu/ai-assisted-software-development-custom.html) (6–8 hour intensive with enterprise customization).
