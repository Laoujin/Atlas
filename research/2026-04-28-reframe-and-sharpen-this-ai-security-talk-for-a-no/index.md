---
layout: expedition
title: "Reframing the AI & Security talk for a non-technical audience"
date: 2026-04-28
topic: "Reframe and sharpen the AI-Security-Talk for a non-technical audience: propose laymen-friendly titles, triage the existing deck, graft in concrete 2026 angles."
format: md
tags: [ai-security, talk-prep, laymen-audience, deepfakes, hallucinations]
summary: Keep "ProbLLMs: Why You Can't Trust the Robot", cut the developer-jargon half of the deck, and graft in four 2026 angles (voice-clone scams, kids + AI companions, AI-injected ads, deepfake nudes) that show up in actual public-concern polls.
cover: cover.svg
synthesis: true
children:
  - slug: title-candidates
    title: Title candidates
    depth: ceo
    status: success
    summary: Eight title candidates for the laymen reframing of the AI-Security-Talk, with a recommended pick and the patterns behind each.
    citations: 7
    reading_time_min: 2
  - slug: existing-deck-triage
    title: Existing deck triage
    depth: deep
    status: success
    summary: Slide-by-slide keep/trim/simplify/cut verdict on the AI-Security-Talk deck for a non-technical audience, plus the four laymen-relevant topics to graft in.
    citations: 77
    reading_time_min: 7
  - slug: ai-vs-llm-and-other-foundational-concepts
    title: AI vs LLM and other foundational concepts
    depth: standard
    status: success
    summary: A non-technical primer on the AI/ML/deep-learning/LLM stack and the surrounding jargon — built so the audience can follow an AI-security talk without losing the thread.
    citations: 17
    reading_time_min: 5
  - slug: scams-deepfakes-and-social-engineering-in-2026
    title: Scams, deepfakes, and social-engineering in 2026
    depth: deep
    status: success
    summary: Field guide to the 2026 AI scam landscape — named cases, dollar losses, attacker tooling, and the four defense layers that actually move the needle.
    citations: 99
    reading_time_min: 14
  - slug: data-harvesting-and-privacy
    title: Data harvesting and privacy
    depth: standard
    status: success
    summary: AI runs on harvested data. The legal wins are mostly piracy cases, not privacy ones; defaults still leak, and your every prompt is logged unless you turn it off.
    citations: 29
    reading_time_min: 6
  - slug: ads-manipulation-and-trust-erosion
    title: Ads, manipulation, and trust erosion
    depth: standard
    status: success
    summary: The ad-funded internet was already a manipulation engine; AI cheapens every step and accelerates a measurable decade-long collapse of trust.
    citations: 26
    reading_time_min: 5
  - slug: misinformation-hallucination-harms-and-election-me
    title: Misinformation, hallucination harms, and election/medical/legal risks
    depth: standard
    status: success
    summary: A talk-prep map of where LLM hallucinations and AI-generated misinformation have caused measurable harm — courts (sanctioned lawyers, 486+ cases), hospitals (Whisper inventing dialogue, 80% diagnostic misses), and elections (mostly cheap fakes, with sharp exceptions like Slovakia 2023 and the Arup $25M deepfake).
    citations: 20
    reading_time_min: 7
  - slug: presentation-craft-for-non-technical-audiences
    title: Presentation craft for non-technical audiences
    depth: ceo
    status: success
    summary: A CEO-depth playbook for explaining technical work — especially AI security — to audiences who don't share your jargon.
    citations: 7
    reading_time_min: 2
cost_usd: 28.69
duration_sec: 3632
citations: 282
reading_time_min: 48
---

> **The single decision.** Keep the title **"ProbLLMs: Why You Can't Trust the Robot"** [[1]](https://github.com/itenium-be/AI-Security-Talk/blob/master/presentation/slides.md), cut the existing deck roughly in half, and graft in four laymen-relevant angles with strong 2026 evidence. Everything below explains why each move survives contact with what the audience actually fears.

## One thread runs through all eight angles

AI didn't invent any of these threats — it removed the friction. Phishing emails written by AI hit a 54% click rate vs 12% for human-written [[2]](https://www.paubox.com/blog/microsoft-ai-makes-phishing-4.5x-more-effective-and-far-more-profitable). Deloitte projects gen-AI fraud at $40B by 2027 [[3]](https://www.deloitte.com/us/en/insights/industry/financial-services/deepfake-banking-fraud-risk-on-the-rise.html). Engagement-ranked feeds were already a manipulation engine; AI just makes every step cheaper and more personalised, and trust in news has fallen 20 points in a decade as a result [[4]](https://www.pewresearch.org/short-reads/2025/10/29/how-americans-trust-in-information-from-news-organizations-and-social-media-sites-has-changed-over-time/). That single framing — *same threat, friction removed* — is the spine the laymen edition should hang on.

## What the audience polls actually fear, ranked

Public concern data lines up cleanly with three of the four grafts. Hallucinations top Pew at 66% concern [[5]](https://www.pewresearch.org/internet/2025/04/03/views-of-risks-opportunities-and-regulation-of-ai/); deepfakes/misinformation top YouGov [[6]](https://today.yougov.com/technology/articles/46058-majorities-americans-are-concerned-about-spread-ai). The FBI reports $893M in AI-fraud losses in 2025 with $352M of that against adults 60+ [[7]](https://scamwatchhq.com/fbi-893-million-ai-fraud-seniors-elderly-2026/) — voice-clone scams are the one AI risk laymen fear *personally*. NCMEC AI-CSAM reports jumped from 4,700 in 2023 to 440,000 in H1 2025 [[8]](https://www.usnews.com/news/us/articles/2025-12-22/the-rise-of-deepfake-cyberbullying-poses-a-growing-problem-for-schools), and the FTC opened a Sept-2025 inquiry into seven chatbot companies over kids and companion-AI harms [[9]](https://www.cnbc.com/2025/09/11/alphabet-meta-openai-x-ai-chatbot-ftc.html). By contrast, the existing deck's MCP/CVE/OWASP-LLM01 sections have no consumer surface [[10]](https://en.wikipedia.org/wiki/Model_Context_Protocol) and don't appear in any 2025 public-concern poll. Cut them.

## The contradictions worth flagging on stage

Two findings cut against the doom narrative — admit them, don't hide them. First: the 2024 "election deepfake apocalypse" mostly didn't land [[11]](https://knightcolumbia.org/blog/we-looked-at-78-election-deepfakes-political-misinformation-is-not-an-ai-problem); the damage was **targeted**, not viral — Slovakia 2023, the Biden NH robocall ($6M FCC fine [[12]](https://www.pbs.org/newshour/politics/ai-robocalls-impersonate-president-biden-in-an-apparent-attempt-to-suppress-votes-in-new-hampshire)), and the Arup $25M deepfake video call [[13]](https://www.cnn.com/2024/05/16/tech/arup-deepfake-scam-loss-hong-kong-intl-hnk). Second: the headline AI privacy fines have mostly been overturned (Italy's €15M against OpenAI was scrapped March 2026 [[14]](https://www.tradingview.com/news/reuters.com,2026:newsml_L8N4071DJ:0-italian-court-scraps-15-million-euro-privacy-watchdog-fine-on-chatgpt-maker-openai/)) — the wins are for *piracy* (Anthropic $1.5B [[15]](https://www.npr.org/2025/09/05/g-s1-87367/anthropic-authors-settlement-pirated-chatbot-training-material)), not privacy. So the practical advice for the audience is workflow-level, not "the law will protect you": don't paste secrets into chatbots, opt out where the toggle exists, assume "share" links are public [[16]](https://www.bitdefender.com/en-us/blog/hotforsecurity/your-shared-chatgpt-chats-may-be-publicly-searchable-heres-how-to-delete-them).

## The unified recommendation

Open with a humor anchor (DPD chatbot swearing at customer [[17]](https://time.com/6564726/ai-chatbot-dpd-curses-criticizes-company/)) → seat the "confident liar" mental model with hallucination stories (Mata v. Avianca [[18]](https://en.wikipedia.org/wiki/Mata_v._Avianca,_Inc.), Apple Intelligence's BBC summaries [[19]](https://daringfireball.net/2025/01/bbc_news_apple_intelligence_notification_summaries)) → escalate to deepfakes and voice clones with the Brightwell-mom and Arup cases → pivot from "AI fooling you" to "AI being fooled" with the resume-injection demo [[20]](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-agent-confused-deputy-prompt-injection/) → close with the four out-of-band defenses that actually work (family codeword, callback verification, dual-officer sign-off on video-call money instructions [[21]](https://www.ic3.gov/PSA/2025/PSA250515)). Six 10-minute attention chunks, ~24 slides total — every chunk one concrete story, not one taxonomy.

The open question the talk should leave hanging: when ChatGPT's $100M-run-rate ad business [[22]](https://www.windowscentral.com/artificial-intelligence/openai-is-slapping-ads-into-chatgpt-microsoft-copilot-is-obviously-next) becomes a $10B one, will any of these defenses still work — or does the "confident liar" become the most lucrative ad surface ever built?
