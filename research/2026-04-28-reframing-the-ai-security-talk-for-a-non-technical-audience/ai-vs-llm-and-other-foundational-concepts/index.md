---
title: "AI vs LLM and other foundational concepts"
date: 2026-04-28
depth: standard
format: md
topic: "AI vs LLM and other foundational concepts"
topic_raw: "AI vs LLM and other foundational concepts"
issue: 23
tags: [ai, llm, foundations, glossary, primer, security]
summary: A non-technical primer on the AI/ML/deep-learning/LLM stack and the surrounding jargon — built so the audience can follow an AI-security talk without losing the thread.
citations: 17
reading_time_min: 5
cover: cover.svg
cost_usd: 2.05
duration_sec: 312
---

> **TL;DR.** "AI" is the umbrella; **LLMs** are one specific flavour of it. The hierarchy is **AI ⊃ Machine Learning ⊃ Deep Learning ⊃ LLMs**[[2]](https://www.ibm.com/think/topics/ai-vs-machine-learning-vs-deep-learning-vs-neural-networks). When people today say "AI", they almost always mean an LLM — a transformer-based neural network trained to predict the next token of text[[3]](https://en.wikipedia.org/wiki/Large_language_model)[[4]](https://aws.amazon.com/what-is/large-language-model/). Everything else on the slide deck (foundation model, RAG, agent, hallucination, prompt injection) is either a property of that LLM, a way of plugging it into something, or a way it goes wrong.

## The hierarchy in one picture

Each layer is a strict subset of the one above it[[2]](https://www.ibm.com/think/topics/ai-vs-machine-learning-vs-deep-learning-vs-neural-networks).

| Layer | What it means | Canonical example |
|---|---|---|
| **AI** | A machine-based system that makes predictions, recommendations, or decisions for human-defined goals[[1]](https://csrc.nist.gov/glossary/term/artificial_intelligence). Includes hand-coded rule engines, chess engines, recommendation systems, anything "smart". | A thermostat that learns your schedule. |
| **Machine Learning (ML)** | A subset of AI in which the system learns patterns from data instead of being explicitly programmed[[2]](https://www.ibm.com/think/topics/ai-vs-machine-learning-vs-deep-learning-vs-neural-networks). | Spam filter, credit-scoring model. |
| **Deep Learning** | A subset of ML that uses many-layered artificial neural networks to learn complex patterns at scale[[2]](https://www.ibm.com/think/topics/ai-vs-machine-learning-vs-deep-learning-vs-neural-networks). | Image recognition, speech-to-text. |
| **LLM** | A specific kind of deep-learning model — a neural network trained on huge text corpora to generate language[[3]](https://en.wikipedia.org/wiki/Large_language_model). | ChatGPT, Claude, Gemini. |

Practically: when a journalist or a vendor pitch deck says "AI", in 2026 they almost always mean **LLM**. The umbrella word is doing the heavy lifting because it sounds bigger than what's actually under the hood.

## How an LLM actually works (one paragraph)

An LLM is **autocomplete at industrial scale**. You feed it a sequence of tokens (roughly: word fragments), and it outputs a probability distribution over what the next token should be, then samples one, then repeats[[5]](https://developers.google.com/machine-learning/crash-course/llm/transformers). The model learned that distribution by being shown trillions of tokens during **pretraining** and being scored on whether it predicted the next one correctly[[17]](https://magazine.sebastianraschka.com/p/llm-training-rlhf-and-its-alternatives). The architecture that made this practical is the **transformer**, introduced in 2017; its **self-attention** mechanism lets the model weigh how much every other token in the input should influence the current prediction, regardless of distance[[3]](https://en.wikipedia.org/wiki/Large_language_model). That's it. There is no internal database of facts, no reasoning engine — just a very large statistical guess about what word comes next.

Why this matters for a security audience: the model has no notion of "true" or "false", "safe" or "unsafe", "instruction" or "data". Those are properties we *project* onto it. Most LLM security failures come from that gap.

## Glossary — the words that will keep coming up

| Term | Plain-English definition | Why it shows up in security talks |
|---|---|---|
| **Token** | The smallest unit of text an LLM processes — usually a word fragment of ~3-4 characters[[15]](https://blog.mlq.ai/tokens-context-window-llms/). 100 English words ≈ 150 tokens. | Pricing, rate limits, and **context window** are all measured in tokens. |
| **Parameters** | The numerical weights inside the neural network learned during training — modern LLMs have billions to trillions of them[[3]](https://en.wikipedia.org/wiki/Large_language_model). | "70B model" = 70 billion parameters. Bigger ≠ smarter, but it's the headline number. |
| **Context window** | The amount of text (in tokens) the model can hold in working memory at once[[15]](https://blog.mlq.ai/tokens-context-window-llms/). In 2026 this ranges from ~128K (DeepSeek, Mistral) up to 10M tokens (Llama 4 Scout)[[16]](https://devtk.ai/en/blog/llm-context-window-explained/). | Anything outside the window is invisible — including security policies the developer pasted at the top, once the conversation runs long. |
| **Foundation model** | A large model trained on broad data that can be adapted to many downstream tasks[[6]](https://en.wikipedia.org/wiki/Foundation_model). Term coined by Stanford CRFM in 2021[[7]](https://crfm.stanford.edu/). | LLMs are foundation models. The same base model gets resold under dozens of product names. |
| **Generative AI** | A model that produces *new* content (text, images, code) by learning the joint distribution of its training data[[8]](https://www.datacamp.com/blog/generative-vs-discriminative-models). Contrasts with **discriminative AI**, which only classifies. | "GenAI" = the category that includes LLMs, image models, code models, etc. |
| **Pretraining** | The first training phase: feed the model trillions of tokens of raw web text and have it predict the next token[[17]](https://magazine.sebastianraschka.com/p/llm-training-rlhf-and-its-alternatives). | This is where the model absorbs the open internet — including unvetted, contradictory, and adversarial content. |
| **Fine-tuning** | A shorter second training phase on a curated dataset, to specialise the model for a task or domain[[17]](https://magazine.sebastianraschka.com/p/llm-training-rlhf-and-its-alternatives). | Custom company assistants are usually fine-tunes of a foundation model. |
| **RLHF** | Reinforcement Learning from Human Feedback. Humans rank pairs of model outputs; a reward model learns from those rankings; the LLM is then nudged toward the preferred behaviour[[14]](https://huggingface.co/blog/rlhf). | This is what makes a base model "helpful, harmless, honest" rather than just an autocomplete. It's also where guardrails live — and where they leak. |
| **RAG** | Retrieval-Augmented Generation. Before the model answers, the system searches a knowledge base, pastes the relevant chunks into the prompt, and *then* asks the model[[9]](https://aws.amazon.com/what-is/retrieval-augmented-generation/). | The dominant 2026 enterprise pattern. The retrieved text is treated as instructions by the model — which is why **indirect prompt injection** is a problem (see below). |
| **Agent / agentic AI** | An LLM hooked up to tools (browser, terminal, APIs) and a goal, allowed to plan and act autonomously across multiple steps[[10]](https://en.wikipedia.org/wiki/AI_agent). | The blast radius of a security failure goes from "wrong answer" to "wrong action taken on your behalf". |
| **Hallucination** | A response that contains false or misleading information presented as fact[[11]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)). The model isn't lying; it's confidently completing a sequence. | Recent research argues this is partly **incentive-driven**: training/eval procedures reward confident guessing over admitting uncertainty[[12]](https://arxiv.org/abs/2509.04664). |
| **Prompt injection** | An attacker crafts input that overrides the developer's intended instructions to the model[[13]](https://genai.owasp.org/llmrisk/llm01-prompt-injection/). | Ranked **#1** on the OWASP Top 10 for LLM Applications 2025[[13]](https://genai.owasp.org/llmrisk/llm01-prompt-injection/). |

## The three concepts that matter most for an AI-security audience

These earn their own callout because they're where almost every published incident lives.

**1. There is no instruction/data boundary.** Everything the model sees — system prompt, user message, retrieved RAG document, tool output, image with text in it — is concatenated into one big string of tokens. The model decides what to "follow" based on patterns it learned during pretraining and RLHF[[14]](https://huggingface.co/blog/rlhf), not based on a privileged channel. This is why **indirect prompt injection** works: an attacker plants instructions in a document, an email, or a webpage; your RAG pipeline retrieves it; the model executes those instructions[[13]](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

**2. Hallucination is a feature of the architecture, not a bug to patch.** The model is a probability distribution over next tokens — it has no source of ground truth and no calibrated sense of "I don't know"[[11]](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)). Worse, common evaluation setups *reward* it for guessing[[12]](https://arxiv.org/abs/2509.04664). RAG[[9]](https://aws.amazon.com/what-is/retrieval-augmented-generation/) reduces this by grounding answers in retrieved documents, but does not eliminate it.

**3. "Agent" changes the threat model.** A chat assistant that hallucinates wastes a user's afternoon. An **agent**[[10]](https://en.wikipedia.org/wiki/AI_agent) that hallucinates can send the email, run the SQL query, or wire the money. The same prompt-injection bug becomes a remote-code-execution-equivalent the moment the LLM has tool access — because you are letting an attacker-controlled string steer real-world actions through your authenticated session.

## What to skip

A non-technical talk does **not** need to dwell on:

- Transformer mathematics (attention, Q/K/V matrices) — the "autocomplete" intuition above is enough.
- Differences between GPT, Llama, Claude, Gemini at the architecture level — they are far more alike than different.
- AGI / sentience debates — orthogonal to security and a guaranteed time-sink in Q&A.
- Generative-vs-discriminative as a deep concept[[8]](https://www.datacamp.com/blog/generative-vs-discriminative-models) — useful as a label, not as a slide.

The audience needs to walk out able to read a vendor pitch and a news headline without being snowed. Eleven defined terms, one diagram, three security framings — that's the whole job.
