Sub-questions — Evaluation rubrics and benchmarks for AI-assisted code review (2026)

1. What benchmarks/datasets exist to evaluate AI code reviewers, and what does the strongest independent evidence (peer-reviewed, large-PR studies) actually measure?
2. What do vendors (CodeRabbit, Greptile, Qodo, Cursor BugBot, Graphite/Diamond, Bito) claim in their own benchmarks, and how are those benchmarks constructed?
3. Which metrics are used (precision, recall, F1, false-positive/noise rate, bug-catch rate) and why does precision dominate for review tools — the skeptic's read on why vendor numbers are inflated or incomparable.
4. How is code-review quality scored qualitatively — human/LLM-as-judge rubrics, dimensions (correctness, actionability, usefulness), and rubric design.
5. Reliability of LLM-as-a-judge for code review: bias, self-preference, calibration; and adjacent code-task benchmarks (SWE-bench, RepoBench, BigCodeBench, CodeReviewBench) relevant as context.
6. Why benchmarking code review is hard (ground-truth labels, dataset contamination/leakage, reproducibility) and what a good evaluation would look like.
