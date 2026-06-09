---
title: "Metrics Beyond Accuracy"
date: 2026-06-09
depth: ceo
format: md
topic: "Metrics beyond accuracy"
topic_raw: "Metrics beyond accuracy"
issue: 206
tags: [evaluation, metrics, machine-learning, classification]
summary: "Accuracy hides failures on imbalanced data and across subpopulations. Match your metric to your use case: Precision/Recall for trade-offs, F1 for imbalance, PR-AUC for rare positives, and task-specific metrics for AI agents."
citations: 7
reading_time_min: 2
cost_usd: 0.16
duration_sec: 62
model: "Haiku 4.5"
---

> **TL;DR:** Accuracy is dangerous for imbalanced data and masks failures on subpopulations. For classification, use Precision if false positives are costly, Recall if false negatives are critical, F1 when classes are imbalanced, and PR-AUC instead of ROC-AUC for rare positive cases. For AI agents, measure Task Completion Rate, Recovery Rate, and Cost per Task alongside accuracy. Always choose metrics based on the business cost of errors, not aggregated performance.

## Why Accuracy Fails

A fraud detection model that predicts "legitimate" on 99.9% of transactions can hit 99.9% accuracy while catching zero fraud [[1]](https://machinelearningmastery.com/beyond-accuracy-5-metrics-that-actually-matter-for-ai-agents/). Accuracy rewards majority-class predictions and hides catastrophic failures on the subset that matters. Worse, [[2]](https://news.mit.edu/2026/why-its-critical-to-move-beyond-overly-aggregated-machine-learning-metrics-0120) models with the highest average accuracy can be the worst performers in new settings—the "best" model on your test set may be the worst on 6–75% of real-world data when deployment contexts differ.

## Classification: Precision vs Recall vs F1

**Precision** answers "of everything I labeled positive, how many were right?" Use it when false positives are expensive: spam filtering, ad approval, or screening tests with high follow-up cost.

**Recall** answers "of all the actual positives, how many did I find?" Use it when missing cases is catastrophic: disease diagnosis, fraud detection, or safety-critical systems.

**F1 Score** is the harmonic mean of precision and recall. [[3]](https://machinelearningmastery.com/roc-auc-vs-precision-recall-for-imbalanced-data/) Use F1 for imbalanced datasets where both false positives and false negatives matter, or when you need a balanced assessment of minority-class behavior.

## ROC-AUC vs PR-AUC

ROC-AUC is popular but can be "overly optimistic" on imbalanced data [[3]](https://machinelearningmastery.com/roc-auc-vs-precision-recall-for-imbalanced-data/). On a fraud dataset with <1% positive cases, one model showed ROC-AUC of 0.957 but PR-AUC of only 0.708. [[4]](https://www.openlayer.com/blog/post/f1-score-precision-recall-balance) PR-AUC focuses on the minority class and reveals true performance on rare events. For imbalanced or high-stakes binary classification (disease, fraud, anomaly), reach for PR-AUC.

## Beyond Classification: Metrics for AI Agents

Accuracy doesn't capture how agents actually fail. [[1]](https://machinelearningmastery.com/beyond-accuracy-5-metrics-that-actually-matter-for-ai-agents/) Five critical metrics:

- **Task Completion Rate:** % of tasks completed without human intervention. Reveals end-to-end reliability.
- **Tool Selection Accuracy:** Does the agent pick the right API or function? Critical in finance and high-stakes domains.
- **Recovery Rate:** How often does the agent detect errors and replan? Essential for systems that interact with external tools.
- **Autonomy Score:** Ratio of independent actions to human interventions. Context-dependent—low autonomy may be correct in healthcare.
- **Cost per Successful Task:** Computational or economic cost to complete one task. Prevents hidden cost escalation at scale.

## The Rule

[[5]](https://www.analyticsvidhya.com/blog/2019/08/11-important-model-evaluation-error-metrics/) Match your metric to the business cost of each error type, not to convention. Imbalanced data → F1 or PR-AUC. Trade-offs between error types → Precision or Recall. Agent systems → Completion, recovery, cost. Subpopulation failures → Disaggregate and measure performance per group, not in aggregate.
