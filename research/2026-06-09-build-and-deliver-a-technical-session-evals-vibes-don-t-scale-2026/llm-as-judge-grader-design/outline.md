What is LLM-as-judge and what grading paradigms exist (pointwise/direct scoring, pairwise comparison, reference-based/reference-free), and when do you use each?
How do you design the grader prompt and rubric: binary vs Likert scales, decomposing criteria, requiring rationale/chain-of-thought, few-shot anchoring, structured output, and additive scoring?
What are the known biases and failure modes of LLM judges (position, verbosity/length, self-preference/self-enhancement, sycophancy, prompt-sensitivity) and how do you mitigate them?
How do you validate and calibrate a judge against human labels: agreement metrics (Cohen's/kappa, TPR, precision/recall), the "evaluate the evaluator" loop, and aligning the judge to your preferences?
What tooling, frameworks, and judge-model choices exist (Braintrust autoevals, G-Eval/DeepEval, Ragas, LangSmith, Phoenix, OpenAI evals, promptfoo), and which model should grade?
What's the skeptic's counter-reading and the advanced state of the art: do LLM judges actually correlate with humans, jury/panel-of-judges ensembles, and fine-tuned judge models (Prometheus, JudgeLM)?
