---
title: "Evaluation Rubrics and Benchmarks for AI Code Review: What Holds Up (2026)"
date: 2026-06-09
depth: deep
format: md
topic: "Evaluation rubrics and benchmarks"
topic_raw: "Evaluation rubrics and benchmarks"
issue: 203
tags: [code-review, benchmarks, evaluation, llm, software-engineering]
summary: "Independent benchmarks put the best AI reviewer at F1≈19% while vendors claim 50–82%; this maps the benchmarks, rubrics, metrics, and the contamination and methodology gaps that explain the gulf."
cover: cover.svg
citations: 50
reading_time_min: 11
cost_usd: 5.96
duration_sec: 681
model: "Opus 4.8"
---

> **TL;DR** — There are two parallel universes of evidence. In the **independent** one, the largest peer-reviewed test of AI code *review* (1,000 manually verified PRs) puts the best system at **F1 ≈ 19.4%** [[2]](https://arxiv.org/html/2509.01494v1), and an in-the-wild study of 3,109 PRs found 12 of 13 review agents emit **<60% signal** [[9]](https://arxiv.org/html/2604.03196v1). In the **vendor** one, every tool publishes a benchmark it wins — Greptile claims 82%, CodeRabbit/Qodo/CodeAnt cluster at 51–60% F1 — on datasets they each designed [[11]](https://www.greptile.com/benchmarks)[[20]](https://deepsource.com/blog/ai-code-review-benchmarks). The gap is not lying; it's **methodology**: tiny self-curated gold sets, LLM-injected synthetic bugs, incompatible "caught" definitions, and benchmark contamination. **For evaluating a tool yourself, ignore the headline percentages.** What transfers: measure **precision/false-positive rate** on *your* recent PRs (acceptance rate is the honest proxy), use a reference-free rubric like **CRScore**'s conciseness/comprehensiveness/relevance, and treat any number from a benchmark the vendor built as marketing, not measurement.

This is the evaluation slice of the 2026 AI-code-review survey — the companion pieces cover [agentic workflows](../agentic-code-review-workflows/), the [commercial market map](../market-map-commercial-vendors-and-platforms/), and the [open-source ecosystem](../open-source-tools-agents-and-research-ecosystem/). Here the question is narrower and harder: **how do you actually know if an AI reviewer is any good?**

## The headline numbers don't reconcile

| Source | Best system | Score | Dataset | Who built it |
|--------------------------------|-----------------------|---------------|----------------------------------------|--------------|
| SWRBench (peer-reviewed)       | PR-Review + Gemini-2.5-Pro | **F1 19.38%** | 1,000 verified PRs, 12 OSS Python repos | Independent [[2]](https://arxiv.org/html/2509.01494v1) |
| AIDev in-the-wild (peer-reviewed) | best of 13 agents   | **<60% signal** (Copilot 19.79%) | 3,109 real PRs                | Independent [[9]](https://arxiv.org/html/2604.03196v1) |
| Greptile benchmark             | Greptile              | 82% catch rate | 50 bug-fix PRs, 5 repos                 | Greptile [[11]](https://www.greptile.com/benchmarks) |
| Martian / CodeRabbit           | CodeRabbit            | F1 51.2%      | ~300k real PRs (online method)          | Martian (vendor-promoted) [[12]](https://www.coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark) |
| Qodo benchmark                 | Qodo 2.0              | F1 60.1%      | 100 PRs / 580 LLM-injected issues       | Qodo [[16]](https://www.qodo.ai/blog/introducing-qodo-2-0-agentic-code-review/) |
| Propel benchmark               | Propel                | F-score 64%   | proprietary                             | Propel [[21]](https://www.propelcode.ai/benchmarks) |

A 4× spread between the independent floor and the vendor ceiling. The rest of this piece explains why — and what you can trust.

## The independent benchmark landscape

The academic side has converged on a handful of named artifacts. None of them flatter the tools.

| Benchmark | Year | What it measures | Size | Headline finding |
|-----------|------|------------------|------|------------------|
| [SWRBench](https://arxiv.org/abs/2509.01494) | 2025 | Bug detection on real PRs, P/R/F1 | 1,000 PRs (500 buggy / 500 clean), 12 repos | Best F1 **19.38%**; most tools 4.9–19% [[1]](https://arxiv.org/abs/2509.01494)[[2]](https://arxiv.org/html/2509.01494v1) |
| [CRScore](https://aclanthology.org/2025.naacl-long.457/) | 2025 (NAACL) | Reference-free comment quality | 2.9k human-scored reviews | Spearman **0.54** with humans; BLEU fails [[3]](https://aclanthology.org/2025.naacl-long.457/)[[4]](https://arxiv.org/html/2409.19801v2) |
| [CodeReviewer / CodeReview](https://arxiv.org/pdf/2203.09095) | 2022 (Microsoft) | Comment generation (BLEU) | 7.9M PRs, 9 languages | BLEU stays **<10** — task is hard [[5]](https://arxiv.org/pdf/2203.09095) |
| [CodeReviewQA](https://arxiv.org/pdf/2503.16167) | 2025 | Reasoning via MCQA (dodges generation noise) | 900 curated cases | Decomposes into recognition/localization/solution [[6]](https://arxiv.org/pdf/2503.16167) |
| [CodeFuse-CR-Bench](https://arxiv.org/pdf/2509.14856) | 2025 | Comprehensiveness-aware, PR-level | Python repos | End-to-end, LLM-as-judge scored [[10]](https://arxiv.org/pdf/2509.14856) |

Three things stand out. **First, the scores are low** — F1 in the teens is the state of the art on rigorously labeled data, and a simple trick (aggregating multiple independent reviews) lifts F1 by up to **43.67%** relative, which tells you single-pass systems leave a lot on the table [[1]](https://arxiv.org/abs/2509.01494). **Second, the metric matters more than the model**: CRScore shows reference-based metrics like BLEU are actively misleading for review, because a perfectly valid comment that doesn't n-gram-match the one human reference can score as low as **0.0458** [[4]](https://arxiv.org/html/2409.19801v2). **Third, even the ground truth is dirty** — a 2025 data-quality audit found only **64% of CodeReviewer comments are valid**, the other ~36% being noise the models are graded against [[8]](https://arxiv.org/html/2502.02757). A 2026 survey of 99 code-review-benchmark papers (2015–2025) reaches the same verdict: benchmarks and metrics remain immature, and treating human PR comments as gold is the core weakness [[7]](https://arxiv.org/html/2602.13377v1).

## Vendor benchmarks: everyone wins their own

> "Every AI code review vendor benchmarks itself, and wins." — DeepSource [[20]](https://deepsource.com/blog/ai-code-review-benchmarks)

That is not a cheap shot; it is structurally true. Each vendor designs the dataset, picks the repos, defines "caught," and runs the eval. The numbers are internally coherent and mutually incomparable.

| Vendor | Claimed metric | Dataset & method | "Caught" / TP definition |
|--------|----------------|------------------|--------------------------|
| [Greptile](https://www.greptile.com/benchmarks) | 82% catch rate (vs Bugbot 58, Copilot 54, CodeRabbit 44, Graphite 6) | 50 real bug-fix PRs (10 per language, 5 langs) | Line-level comment that explains impact [[11]](https://www.greptile.com/benchmarks) |
| [CodeRabbit](https://www.coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark) | F1 51.2%, recall 53.5% (#1) | Martian Bench, ~300k real PRs | "Online": dev edits code after the comment [[12]](https://www.coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark) |
| [CodeAnt](https://www.codeant.ai/blogs/ai-code-review-benchmark-results-from-200-000-real-pull-requests) | F1 51.7% (#3 of 17) | Martian Bench, 200k+ PRs + 50-PR offline gold | Dev acts on comment + offline gold set [[13]](https://www.codeant.ai/blogs/ai-code-review-benchmark-results-from-200-000-real-pull-requests) |
| [Qodo](https://www.qodo.ai/blog/introducing-qodo-2-0-agentic-code-review/) | Qodo 2.0 F1 60.1%, recall 56.7% | 100 PRs / 580 issues, 7 repos | Correct description **and** correct file/line [[15]](https://www.qodo.ai/blog/how-we-built-a-real-world-benchmark-for-ai-code-review/)[[16]](https://www.qodo.ai/blog/introducing-qodo-2-0-agentic-code-review/) |
| [Cursor BugBot](https://cursor.com/blog/building-bugbot) | "Resolution rate" 52%→70%+ | BugBench, human-annotated real diffs | Author fixes the flagged bug by merge [[14]](https://cursor.com/blog/building-bugbot) |
| [Bito](https://bito.ai/blog/benchmarking-the-best-ai-code-review-tool/) | 69.5% coverage (CodeRabbit 65.8%) | 65-issue truth set, 5 langs | Issue from truth set detected [[17]](https://bito.ai/blog/benchmarking-the-best-ai-code-review-tool/) |
| [Korbit](https://www.korbit.ai/post/why-precision-matters-most-in-ai-code-review-tools-2) | precision-first (no headline %) | counter-positioning | Suppress low-value comments [[19]](https://www.korbit.ai/post/why-precision-matters-most-in-ai-code-review-tools-2) |

The methodological tells:

- **Tiny synthetic gold sets.** Qodo injects bugs with an LLM by "corrupting the diff while preserving functionality," then an LLM judges the hits [[15]](https://www.qodo.ai/blog/how-we-built-a-real-world-benchmark-for-ai-code-review/). Greptile's set is 50 PRs reduced to one planted bug each [[11]](https://www.greptile.com/benchmarks). Construct validity — does catching a seeded bug predict real-world usefulness? — is rarely argued.
- **The "online" method is the most honest, and still gameable.** Martian counts a comment as a true positive when the developer actually edits the code in response [[13]](https://www.codeant.ai/blogs/ai-code-review-benchmark-results-from-200-000-real-pull-requests) — a real behavioral signal, not a synthetic label. But the dataset and harness are still vendor-controlled, and developers edit code for reasons unrelated to the comment.
- **Cross-vendor numbers move violently.** Greptile self-reports 82%; in Propel's independent board Greptile lands at a 45% F-score, behind Propel (64%) and Cursor BugBot (49%) [[21]](https://www.propelcode.ai/benchmarks). Same tool, ~half the number, different referee.
- **Definitions don't align.** "Catch rate" (Greptile, recall-like), "F1" (Martian-benchmarked vendors), "resolution rate" (Cursor), and "coverage" (Bito) are four different quantities. Stacking them in one ranking is a category error.

There's even a strategic split: recall-led vendors (Qodo, CodeRabbit) advertise *finding more*, while Korbit and the deprecated Graphite Diamond optimized for **precision** and low false positives — Diamond ranked last for raw detection, then got deprecated and folded into Cursor's BugBot after acquisition in Dec 2025 [[18]](https://graphite.com/blog/series-b-diamond-launch)[[19]](https://www.korbit.ai/post/why-precision-matters-most-in-ai-code-review-tools-2).

## Metrics: why precision beats recall for reviewers

The classification quartet — precision, recall, F1, false-positive rate — applies, but for a *reviewer* the asymmetry is severe. Recall failures are invisible (a missed bug looks like a clean PR); precision failures are loud (every false flag costs a human's attention). The dynamics:

- **Typical false-positive rates run 5–15%**, with well-tuned tools at 5–8% [[22]](https://graphite.com/guides/ai-code-review-false-positives). That sounds fine until you multiply by PR volume.
- **Noise compounds into "dismiss all."** A high-FPR reviewer degrades trust through skepticism → pattern-recognition → blanket dismissal, after which true positives die alongside the false ones — at 15% FPR, roughly 13 of every 15 "critical" weekly flags are wrong, and engineers learn to ignore the channel [[25]](https://www.codeant.ai/blogs/ai-code-review-false-positives).
- **Developers already distrust the tools.** 46% actively distrust AI accuracy and 66% cite "almost right, but not quite" as their top frustration — which is why most serious vendors now design precision-first [[23]](https://www.augmentcode.com/guides/deep-code-review-recall-vs-precision). Practitioners on HN report only a small fraction of CodeRabbit/Codacy comments are useful, and that bots send juniors into rabbit holes on non-issues while real bugs slip through [[24]](https://news.ycombinator.com/item?id=42451968).

**The honest in-house metric is acceptance / resolved rate** — did the comment cause a code change — which is exactly Microsoft's 2015 operational definition of a *useful* review comment [[26]](https://www.microsoft.com/en-us/research/publication/characteristics-of-useful-code-reviews-an-empirical-study-at-microsoft/) and the "online" signal Martian later industrialized [[13]](https://www.codeant.ai/blogs/ai-code-review-benchmark-results-from-200-000-real-pull-requests). The 2026 CR-Bench formalizes the tradeoff with a **signal-to-noise ratio** as a proxy for developer trust, precisely because high recall with excess output causes fatigue and abandonment [[45]](https://arxiv.org/html/2603.11078v1). The lesson: a single F1 number hides the only thing that matters operationally — what fraction of what the bot says is worth reading.

## Rubrics: scoring quality when there's no single right answer

Free-text review comments are one-to-many — many valid reviews exist for one diff — so n-gram metrics break and you need a **rubric**. The field has converged on a small, recurring set of dimensions:

| Rubric / tradition | Dimensions | Scale / signal | Reliability |
|--------------------|-----------|----------------|-------------|
| [CRScore](https://arxiv.org/html/2409.19801v2) (NAACL 2025) | **Conciseness** (precision), **comprehensiveness** (recall), **relevance** (their harmonic mean) | grounded in detected code claims/smells; 5-pt Likert in human layer | Krippendorff α ≈ 0.85–0.89; 0.54 Spearman vs humans [[3]](https://aclanthology.org/2025.naacl-long.457/)[[4]](https://arxiv.org/html/2409.19801v2) |
| [CodeFuse-CR-Bench](https://arxiv.org/pdf/2509.14856) | correctness, completeness, relevance vs reference | LLM-as-judge | comprehensiveness-aware [[10]](https://arxiv.org/pdf/2509.14856) |
| [Microsoft usefulness](https://www.microsoft.com/en-us/research/publication/characteristics-of-useful-code-reviews-an-empirical-study-at-microsoft/) | useful ⇔ triggers a nearby code change | behavioral, binary | ~⅓ of 1.5M comments non-useful [[26]](https://www.microsoft.com/en-us/research/publication/characteristics-of-useful-code-reviews-an-empirical-study-at-microsoft/) |
| ["Hold On!"](https://arxiv.org/html/2501.06738) (2025) | Code / Text / Voice / Jargon features predicting usefulness | classifier (F1/AUC/MCC) | >1 in 3 comments lack utility [[27]](https://arxiv.org/html/2501.06738) |

For **designing your own rubric**, the consensus guidance is concrete: write behavioral level-definitions instead of vague labels, make dimensions independently scorable, use a 5–7-point Likert — or **Best-Worst Scaling**, which is measurably more reliable: across 64k+ annotations BWS hit split-half reliability ρ=0.98 vs 0.95 for rating scales (p<.001) and reached the same reliability with ~30% of the labeling effort [[48]](https://arxiv.org/pdf/1712.01765), a gain replicated outside NLP [[49]](https://cognitiveresearchjournal.springeropen.com/articles/10.1186/s41235-019-0183-2). Validate with the agreement coefficient that fits your design — **Krippendorff's alpha** (handles missing data, any number of raters, nominal/ordinal/interval), since Cohen's kappa is limited to two annotators and Fleiss' to equal-rating designs; critically, high agreement confirms *consistency, not construct validity* — annotators can agree on the wrong thing [[50]](https://arxiv.org/html/2603.06865)[[28]](https://snorkel.ai/blog/data-quality-and-rubrics-how-to-build-trust-in-your-models/). Golden-dataset practice promotes "silver" synthetic examples to "gold" via evaluator agreement and calibrates annotators in pilot rounds before full annotation [[29]](https://www.getmaxim.ai/articles/building-a-golden-dataset-for-ai-evaluation-a-step-by-step-guide/). Newer LLM-as-judge frameworks treat rubrics as the bridge between human policy language and machine-checkable rewards, even applying Item Response Theory to retire criteria that are too ambiguous to score reliably [[30]](https://medium.com/@adnanmasood/rubric-based-evals-llm-as-a-judge-methodologies-and-empirical-validation-in-domain-context-71936b989e80).

## The meta-problem: can an LLM judge a code review?

Almost every modern benchmark (SWRBench, CodeFuse-CR-Bench, CRScore) uses an LLM as the judge, so the eval is only as trustworthy as that judge. The evidence is "conditionally yes":

- **Strong judges match human agreement in aggregate** — GPT-4-class judges hit **>80% agreement** with human preferences, the same level humans reach with each other [[31]](https://arxiv.org/abs/2306.05685). SWRBench reports ~90% judge-human agreement on its labels [[2]](https://arxiv.org/html/2509.01494v1).
- **But the biases are real and code-relevant.** Position, verbosity, and self-enhancement biases all appear [[31]](https://arxiv.org/abs/2306.05685); self-preference is mechanistically a **perplexity/familiarity** effect — judges over-reward fluent, low-perplexity text regardless of who wrote it [[32]](https://arxiv.org/abs/2410.21819). In **pairwise code judging, swapping response order can shift accuracy by >10%**, and agreement with human subject-matter experts drops to **60–68%** in expert domains [[33]](https://neurotechnus.com/2025/09/21/llm-as-a-judge-bias-reliability/).
- **Debiasing helps but isn't free.** A 2026 systematic study of 9 strategies across 5 judges found gains of **+7.2 to +11.2 points**, but the best strategy is model-dependent [[34]](https://arxiv.org/html/2604.23178). Practical mitigations: reference-guided grading where a correct answer exists, human spot-check calibration on your domain, meta-judging over debate setups, and a judge from a **different provider** than the generator [[35]](https://www.adaline.ai/blog/llm-as-a-judge-reliability-bias).

For code review specifically, the order-sensitivity and expert-domain drop are the ones to fear: review quality is exactly an expert-domain pairwise judgment.

## Why benchmarking review is genuinely hard

Four reinforcing problems, all documented:

1. **Ground truth is noisy.** Human PR comments — the default gold labels — are artifacts of a social process: clarification questions, style nits, and back-and-forth whose wording doesn't map cleanly to any underlying defect [[46]](https://arxiv.org/html/2604.24525v1). There is no "CVE for code quality"; credible labels need expert annotators who agree, which almost no benchmark has [[20]](https://deepsource.com/blog/ai-code-review-benchmarks).
2. **Contamination inflates everything.** Public PRs leak into training. On SWE-bench, models identify the buggy file from the **issue text alone (no repo access) up to 76%** of the time, collapsing below 53% on out-of-distribution repos, with **11.7–31.6% verbatim solution memorization** — recall, not reasoning [[42]](https://arxiv.org/html/2506.12286v4). OpenAI's own audit of 138 o3 failures found 59.4% were test-harness flaws and **32.67% of "successes" leaked the solution** from the issue [[43]](https://www.mindstudio.ai/blog/swe-rebench-benchmark-decontaminated-tests-model-inflation).
3. **Reproducibility is near-zero.** Of 85 LLM-centric ICSE/ASE 2024 papers, only **18 shared artifacts, 5 were executable, and none fully reproduced** [[44]](https://arxiv.org/abs/2510.25506). Vendor benchmarks are self-run and rarely re-runnable by outsiders [[20]](https://deepsource.com/blog/ai-code-review-benchmarks).
4. **Construct validity is weak.** A systematic review of SE benchmarks found **nearly every one** had a construct-validity weakness — the score doesn't support the claim being made about real capability [[47]](https://arxiv.org/html/2503.05860v2). Catching a seeded bug ≠ being a useful reviewer.

## Adjacent benchmarks (useful context, wrong target)

The famous coding leaderboards measure **generation and repair**, not review. They're the de-facto yardsticks for "is this model good at code," so they leak into AI-reviewer marketing — treat them as background, not evidence about review quality.

| Benchmark | Measures | Scale / note |
|-----------|----------|--------------|
| [SWE-bench Verified](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified) | Resolving real GitHub issues | 500 human-validated issues (68.3% of original filtered out) [[37]](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified); June 2026 leaderboard led by Claude Mythos Preview 93.9%, Opus 4.8 88.6% [[36]](https://llm-stats.com/benchmarks/swe-bench-verified) |
| SWE-bench Pro | Contamination-resistant variant | 80%+ Verified models drop to **46–57%** on Pro [[38]](https://www.codeant.ai/blogs/swe-bench-scores) |
| [LiveCodeBench](https://livecodebench.github.io/leaderboard.html) | Contest problems, date-stamped | Contamination-free by construction (post-cutoff problems only) [[39]](https://livecodebench.github.io/leaderboard.html) |
| [BigCodeBench](https://bigcode-bench.github.io/) | Practical tasks, library use | 1,140 tasks, calibrated Pass@1 [[40]](https://bigcode-bench.github.io/) |
| [RepoBench](https://arxiv.org/abs/2306.03091) | Repo-level completion | Retrieval + completion + pipeline, Python/Java [[41]](https://arxiv.org/abs/2306.03091) |

The SWE-bench Verified → Pro drop (93%→~50% for the same model class) is the single clearest demonstration of how much benchmark contamination matters [[38]](https://www.codeant.ai/blogs/swe-bench-scores) — and it's a direct warning for anyone reading a code-review benchmark built on public PRs.

## What a credible evaluation looks like

Synthesizing the independent work, a trustworthy AI-reviewer evaluation has these properties:

- **Fresh, time-split data.** Use PRs that post-date the model's training cutoff (the SWE-rebench approach) so you're measuring reasoning, not memorization [[43]](https://www.mindstudio.ai/blog/swe-rebench-benchmark-decontaminated-tests-model-inflation).
- **A shared, versioned, re-runnable harness** anyone can download and reproduce — the opposite of the current self-run vendor norm [[44]](https://arxiv.org/abs/2510.25506).
- **Blind human adjudication** of a sample, with a defined rubric (CRScore-style dimensions) and reported inter-rater agreement [[3]](https://aclanthology.org/2025.naacl-long.457/).
- **Signal-to-noise / acceptance as the headline**, not raw recall — because trust, not coverage, is what determines whether the tool survives contact with a team [[45]](https://arxiv.org/html/2603.11078v1)[[26]](https://www.microsoft.com/en-us/research/publication/characteristics-of-useful-code-reviews-an-empirical-study-at-microsoft/).
- **Reported on your own repos.** The only benchmark that fully transfers is your last 50 merged PRs, with you adjudicating whether each AI comment would have helped. Every external number is a prior, not a result.

**Bottom line:** the rubrics (CRScore's conciseness/comprehensiveness/relevance, usefulness-as-code-change) and the metric discipline (precision-first, acceptance-rate, signal-to-noise) are mature enough to use today. The *benchmarks* are not — independent ones say the tools are weak, vendor ones say they're strong, and the truth is unknowable from headline numbers because nearly every dataset is self-built, synthetic, or contaminated. Evaluate on your own recent PRs and trust behavior over percentages.
