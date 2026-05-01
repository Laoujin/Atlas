---
title: Data harvesting and privacy — what a non-technical audience needs to know
date: 2026-04-28
depth: standard
format: md
topic: "Data harvesting and privacy"
topic_raw: "Data harvesting and privacy"
issue: 23
tags: [ai, privacy, data, gdpr, security, llm]
summary: AI runs on harvested data. The legal wins are mostly piracy cases, not privacy ones; defaults still leak, and your every prompt is logged unless you turn it off.
citations: 29
reading_time_min: 6
cover: cover.svg
cost_usd: 1.99
duration_sec: 365
---

> **TL;DR** — Modern AI is built on three pipelines of harvested data: scraped public web, *your* chats and posts (on by default), and a $294B data-broker industry that now also feeds AI [[22]](https://www.mordorintelligence.com/industry-reports/data-broker-market). The legal news of 2025–26 is mixed: AI companies have paid out *billions* — but for **piracy** ([Anthropic](https://www.anthropic.com/), $1.5B [[10]](https://www.npr.org/2025/09/05/g-s1-87367/anthropic-authors-settlement-pirated-chatbot-training-material)) and **biometrics** ([Clearview](https://www.clearview.ai/), ~$51.75M equity [[12]](https://www.loevy.com/big-wins/judge-oks-loevys-innovative-51-75-million-settlement-in-clearview-ai-class-action-lawsuit/)), not for privacy. Europe's flagship privacy fine — Italy's €15M against [OpenAI](https://openai.com/) — was overturned in March 2026 [[4]](https://www.tradingview.com/news/reuters.com,2026:newsml_L8N4071DJ:0-italian-court-scraps-15-million-euro-privacy-watchdog-fine-on-chatgpt-maker-openai/). For the audience the practical message is workflow-level, not legal: **don't paste secrets into a chatbot, opt out where the toggle exists, and assume any "share" link can end up on Google** [[20]](https://www.bitdefender.com/en-us/blog/hotforsecurity/your-shared-chatgpt-chats-may-be-publicly-searchable-heres-how-to-delete-them).

## The three pipelines that feed AI

| Pipeline | What gets harvested | Who's affected | Real example |
|---|---|---|---|
| **Public-web scraping** | Anything reachable by a crawler — articles, forums, photos, code, even videos OpenAI/Google allegedly transcribed from YouTube [[2]](https://www.infosecurity-magazine.com/news-features/chatgpts-datascraping-scrutiny/) | Authors, photographers, anyone who ever posted online | Clearview AI: 60B+ facial images scraped from social media, Venmo, news sites [[13]](https://www.biometricupdate.com/202505/us-biometric-data-privacy-lawsuit-against-clearview-concludes-after-5-years/) |
| **First-party (your inputs)** | Prompts, uploads, voice notes, "memories"; ON by default on free ChatGPT [[27]](https://help.openai.com/en/articles/8983130-what-if-i-want-to-keep-my-history-on-but-disable-model-training); also LinkedIn profiles + posts since 3 Nov 2025 [[18]](https://www.helpnetsecurity.com/2025/09/18/linkedin-ai-data-privacy-policy/) | Every chatbot user, every active LinkedIn member | OmniGPT breach: 34M user messages + thousands of API keys leaked [[15]](https://cybernews.com/security/llm-hijacking-prompt-leaks-data-breaches/) |
| **Data brokers → AI** | Location, purchases, health proxies, app behavior, sold for training and inference | Anyone with a phone | FBI buys location histories on US citizens from brokers — no warrant needed [[29]](https://theconversation.com/us-government-ramps-up-mass-surveillance-with-help-of-ai-tech-data-brokers-and-your-apps-and-devices-277440) |

The data-broker market alone was **~$294B in 2025**, with ~5,000 brokers globally; California's 2025 disclosures revealed **33 brokers** admitting they sell US-resident data to entities in China, Russia, North Korea, or Iran (five include precise GPS) [[22]](https://www.mordorintelligence.com/industry-reports/data-broker-market) [[23]](https://epic.org/the-33-data-brokers-selling-us-data-to-foreign-actors-according-to-california/).

## What's gone wrong recently

Concrete incidents the audience may have heard about — useful as examples in the talk:

| Date | What happened | Why it matters for non-technical viewers |
|---|---|---|
| Mar 2023 | Samsung engineers pasted semiconductor source code, defect-detection algorithms, and meeting notes into ChatGPT — three leaks in 20 days, then a company-wide ban [[14]](https://www.darkreading.com/vulnerabilities-threats/samsung-engineers-sensitive-data-chatgpt-warnings-ai-use-workplace) | "Helping the AI" can equal "publishing to a third party" |
| Jul–Aug 2025 | ~4,500 shared ChatGPT chats showed up in Google; researchers found ~100K had been scraped. Names, resumes, kids' names, "emotionally sensitive disclosures" exposed [[20]](https://www.bitdefender.com/en-us/blog/hotforsecurity/your-shared-chatgpt-chats-may-be-publicly-searchable-heres-how-to-delete-them) | The "Share" button + an extra checkbox = public web page |
| Aug 2025 | OpenAI killed the discoverable-share feature; older links/cached copies still surface [[21]](https://fortune.com/2025/08/05/openai-google-search-chat-history/) | Once indexed, the genie doesn't fully go back in the bottle |
| Sep 2025 | Anthropic settled *Bartz et al. v. Anthropic* for $1.5B over 7M+ pirated books used to train Claude (~$3,000/book × 500K) [[10]](https://www.npr.org/2025/09/05/g-s1-87367/anthropic-authors-settlement-pirated-chatbot-training-material) | Even AI labs admit some of their training data was unlawfully obtained |
| 2025 | OmniGPT (chatbot aggregator) breach: 34M+ user messages + API keys leaked [[15]](https://cybernews.com/security/llm-hijacking-prompt-leaks-data-breaches/) | "It's just a chatbot" is wrong — every prompt is a server-side log |
| Nov 2025 | LinkedIn flips AI training ON by default for EU/EEA/Swiss/Canadian/HK users; opt-out is buried two settings deep, and pre-cutover posts are non-revocable [[18]](https://www.helpnetsecurity.com/2025/09/18/linkedin-ai-data-privacy-policy/) [[19]](https://www.malwarebytes.com/blog/news/2025/09/linkedin-will-use-your-data-to-train-its-ai-unless-you-opt-out-now) | Defaults matter; "consent" via inertia |
| Dec 2024 | Italy's Garante fines OpenAI **€15M** for training on personal web data without legal basis — the first GDPR enforcement action to bite a GenAI provider [[3]](https://thehackernews.com/2024/12/italy-fines-openai-15-million-for.html) | Privacy regulators have teeth in theory |
| Mar 2026 | Court of Rome **annuls** that same Italy fine — Europe's only successful GenAI-privacy enforcement now hangs in limbo [[4]](https://www.tradingview.com/news/reuters.com,2026:newsml_L8N4071DJ:0-italian-court-scraps-15-million-euro-privacy-watchdog-fine-on-chatgpt-maker-openai/) [[5]](https://www.crossborderdataforum.org/generative-ai-and-gdpr-enforcement-in-europe-a-lot-of-noise-one-fine-zero-survivors/) | EU privacy enforcement against AI is still mostly noise |

## Where the law sits in 2026

**The settled-ish parts.** The EU AI Act is in effect; from **2 Aug 2026** every general-purpose AI provider must publish a "sufficiently detailed summary" of their training data, using a mandatory European Commission template [[9]](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/european-commission-releases-mandatory-template-for-public-disclosure-of-ai-training-data). High-risk systems carry data-governance duties under Article 10 — quality, bias checks, full provenance records [[8]](https://artificialintelligenceact.eu/article/10/). Non-compliance: up to **€15M or 3% of global revenue** [[8]](https://artificialintelligenceact.eu/article/10/). California's **DROP** opt-out platform launched 1 Jan 2026; from 1 Aug 2026 brokers must scan it every 45 days and delete matched records [[24]](https://privacy.ca.gov/drop/personal-information-and-data-brokers/).

**The unsettled part.** Whether scraping public web data containing personal information is lawful under GDPR is still open. EU DPAs have converged on "**legitimate interest** with safeguards + opt-out" [[6]](https://www.skadden.com/insights/publications/2025/06/cnil-clarifies-gdpr-basis-for-ai-training); the proposed **Digital Omnibus** would codify that, though the Council may strip the provision [[7]](https://iapp.org/news/a/eu-digital-omnibus-amendments-to-gdpr-to-facilitate-ai-training-miss-the-mark). The Italy reversal removed the strongest enforcement precedent. Net: **Europe says you have rights; courts so far have not made AI labs pay for violating them.**

**The settled parts that aren't about privacy.** AI labs are paying out heavily — but for *copyright* (Bartz: training itself was fair use, but **how the data was acquired** wasn't [[11]](https://authorsguild.org/advocacy/artificial-intelligence/what-authors-need-to-know-about-the-anthropic-settlement/)) and *biometrics* (Clearview's BIPA settlement: 23% equity stake, ~$51.75M [[12]](https://www.loevy.com/big-wins/judge-oks-loevys-innovative-51-75-million-settlement-in-clearview-ai-class-action-lawsuit/)). Useful framing for the audience: **the lawsuits that stick aren't "you used my data" but "you stole my book" or "you scanned my face."**

## The technical wrinkle: models can leak training data

Worth one slide so the audience understands *why* harvesting is a privacy issue and not just a copyright one:

- Carlini et al. (2020) showed an outside attacker could coax GPT-2 into reciting **hundreds of verbatim training examples** — names, phone numbers, emails, code, even 128-bit UUIDs — using only the public API [[25]](https://arxiv.org/abs/2012.07805).
- In Nov 2025, "Retracing the Past" demonstrated **Confusion-Inducing Attacks** that still extract memorized data from production-aligned models by steering them into high-entropy states [[26]](https://arxiv.org/html/2511.05518).

→ If a piece of personal data is in the training set, a model can — under adversarial pressure — emit it. This is the empirical backbone of the GDPR claim.

## What the audience should actually do

The defaults are not on your side. Three concrete moves, in order of payoff:

1. **Don't paste secrets.** ⚠ 73.8% of workplace ChatGPT accounts are personal, not enterprise [[17]](https://www.cyberhaven.com/blog/shadow-ai-how-employees-are-leading-the-charge-in-ai-adoption-and-putting-company-data-at-risk); 47% of GenAI-using employees use personal accounts at work [[16]](https://www.infosecurity-magazine.com/news/personal-llm-accounts-drive-shadow/); shadow-AI-related breaches now cost **$4.63M on average — ~$670K more than baseline** [[28]](https://www.cybersecuritydive.com/news/shadow-ai-security-risks-netskope/808860/). Treat any chatbot prompt as if you'd posted it on a public forum.
2. **Opt out where the toggle exists.** ChatGPT: Settings → Data Controls → "Improve the model for everyone" → off [[27]](https://help.openai.com/en/articles/8983130-what-if-i-want-to-keep-my-history-on-but-disable-model-training). LinkedIn: Settings → Data Privacy → off (and accept that pre-3-Nov-2025 content is gone) [[19]](https://www.malwarebytes.com/blog/news/2025/09/linkedin-will-use-your-data-to-train-its-ai-unless-you-opt-out-now). Use **Temporary Chat** for one-shot questions you don't want logged.
3. **Be careful with "Share" links and browser AI extensions.** Sharable chat links are public web pages unless explicitly hidden — and have already leaked once at scale [[20]](https://www.bitdefender.com/en-us/blog/hotforsecurity/your-shared-chatgpt-chats-may-be-publicly-searchable-heres-how-to-delete-them). Browser extensions advertising "AI assistant" features have been caught **intercepting and reselling** chat content [[1]](https://futurism.com/artificial-intelligence/ai-chatbot-data-scraping).

## One-line takeaway for the talk

The harvest is the product. Privacy law has barely touched it; copyright and biometrics law have. Until that changes, the user-side defense is workflow hygiene and a handful of hidden opt-out toggles.
