---
title: "Where AI hallucinations are actually hurting people: legal, medical, electoral"
date: 2026-04-28
depth: standard
format: md
topic: "Misinformation, hallucination harms, and election/medical/legal risks"
topic_raw: "Misinformation, hallucination harms, and election/medical/legal risks"
issue: 23
tags: [ai-safety, hallucinations, misinformation, deepfakes, legal, medical, elections]
summary: A talk-prep map of where LLM hallucinations and AI-generated misinformation have caused measurable harm — courts (sanctioned lawyers, 486+ cases), hospitals (Whisper inventing dialogue, 80% diagnostic misses), and elections (mostly cheap fakes, with sharp exceptions like Slovakia 2023 and the Arup $25M deepfake).
citations: 20
reading_time_min: 7
cover: cover.svg
cost_usd: 2.19
duration_sec: 380
---

> **TL;DR for the talk.** Three rooms, three different shapes of harm.
> **Legal:** quietly catastrophic — 486+ court cases globally where lawyers filed AI-fabricated citations [[3]](https://www.damiencharlotin.com/hallucinations/), with sanctions climbing from $5,000 to $10,000+ [[4]](https://en.wikipedia.org/wiki/Mata_v._Avianca,_Inc.) [[5]](https://calmatters.org/economy/technology/2025/09/chatgpt-lawyer-fine-ai-regulation/) and the rate of new filings going from "a few a month" to "a few a day" inside 2025 [[6]](https://cronkitenews.azpbs.org/2025/10/28/lawyers-ai-hallucinations-chatgpt/).
> **Medical:** quiet, structural, harder to count — Whisper invents dialogue in ~1% of clinical audio segments [[8]](https://arxiv.org/abs/2402.08021) while being deployed to 30,000+ clinicians [[9]](https://fortune.com/2024/10/26/openai-transcription-tool-whisper-hallucination-rate-ai-tools-hospitals-patients-doctors/), and frontier chatbots fail differential diagnosis from initial symptoms >80% of the time [[10]](https://www.massgeneralbrigham.org/en/about/newsroom/press-releases/ai-chatbot-lacks-clinical-reasoning).
> **Electoral:** loud but smaller than feared — the 2024 "deepfake apocalypse" didn't land [[12]](https://knightcolumbia.org/blog/we-looked-at-78-election-deepfakes-political-misinformation-is-not-an-ai-problem) [[19]](https://ash.harvard.edu/articles/the-apocalypse-that-wasnt-ai-was-everywhere-in-2024s-elections-but-deepfakes-and-misinformation-were-only-part-of-the-picture/), but specific incidents (Slovakia 2023 [[13]](https://misinforeview.hks.harvard.edu/article/beyond-the-deepfake-hype-ai-democracy-and-the-slovak-case/), Grok's ballot-deadline lies [[14]](https://www.axios.com/2024/08/05/elon-musk-grok-2024-election-ballot-misinformation), the Arup $25M video-call scam [[15]](https://www.cnn.com/2024/05/16/tech/arup-deepfake-scam-loss-hong-kong-intl-hnk)) show the real damage is targeted, not viral.

## How often do frontier models hallucinate?

The base rate matters because every other section sits on top of it. On Vectara's grounded-summarisation leaderboard (Apr 2026), even the best frontier models still produce factually unsupported sentences when summarising a document they were given [[17]](https://github.com/vectara/hallucination-leaderboard) ⭐ 3.2k:

| Model | Hallucination rate (summary task) |
|---|---|
| Gemini-2.5-flash-lite | 3.3% |
| GPT-4.1 | 5.6% |
| Grok-3 | 5.8% |
| Claude Opus 4.5 | 10.9% |
| o3-Pro (reasoning) | 23.3% |

All [[17]](https://github.com/vectara/hallucination-leaderboard) ⭐ 3.2k. Two things to flag for a non-technical audience: (1) these are rates *with the source document in the prompt* — open-ended Q&A is worse; (2) the new "reasoning" models do not improve on this — several get worse [[17]](https://github.com/vectara/hallucination-leaderboard) ⭐ 3.2k.

Domain-specific benchmarks are harsher. Stanford RegLab and HAI found legal hallucination rates of **69%–88%** on verifiable federal-court questions across general-purpose models, and ≥75% on case-holding queries [[1]](https://hai.stanford.edu/news/ai-trial-legal-models-hallucinate-1-out-6-or-more-benchmarking-queries). Even the legal-industry tools that explicitly market "no hallucinations" failed: Lexis+ AI got facts wrong **>17%** of the time, Westlaw AI-Assisted Research **>34%** [[2]](https://reglab.stanford.edu/publications/hallucination-free-assessing-the-reliability-of-leading-ai-legal-research-tools/).

## Legal — fabricated case law in real filings

This is the cleanest harm story because each incident leaves a public docket. The Charlotin "AI Hallucination Cases" database has logged **486+ rulings** worldwide where a court found that a party relied on AI-fabricated content, 324 in U.S. courts [[3]](https://www.damiencharlotin.com/hallucinations/). The submission rate accelerated through 2025 — researcher Robert Freund went from "a few cases a month" to "a few cases a day" [[6]](https://cronkitenews.azpbs.org/2025/10/28/lawyers-ai-hallucinations-chatgpt/).

| Case | Year | What was fake | Sanction |
|---|---|---|---|
| *Mata v. Avianca* (S.D.N.Y.) [[4]](https://en.wikipedia.org/wiki/Mata_v._Avianca,_Inc.) | 2023 | Multiple fictitious airline-injury precedents with invented internal quotations | $5,000 fine; attorneys ordered to mail apology letters to the real judges named as authors of the fake opinions |
| Anonymised California appeal [[5]](https://calmatters.org/economy/technology/2025/09/chatgpt-lawyer-fine-ai-regulation/) | 2025 | 21 of 23 case quotations fabricated | $10,000 fine — largest California sanction for AI fabrications to date |
| *Moffatt v. Air Canada* (BC tribunal) [[7]](https://www.americanbar.org/groups/business_law/resources/business-law-today/2024-february/bc-tribunal-confirms-companies-remain-liable-information-provided-ai-chatbot/) | 2024 | Air Canada's customer-service chatbot invented a bereavement-fare refund policy | Airline held liable for negligent misrepresentation; ordered to honour the fake policy and pay damages |

The pattern in the data is striking: **90% of sanctioned filings come from solo or small firms; 56% are plaintiff-side; ~50% of identified tools are some version of ChatGPT** [[20]](https://cyberlaw.stanford.edu/blog/2025/10/whos-submitting-ai-tainted-filings-in-court/). Big-firm associates have research databases and review pipelines; pro-se litigants and overworked solo practitioners do not — and they are the ones being caught.

→ **Talk hook:** *Moffatt v. Air Canada* is the cleanest one-slide story. A grieving customer, a polite chatbot inventing a policy that doesn't exist, and a tribunal saying: yes, the airline owns its bot's lies. It dispenses with the "the AI did it" defence in 30 seconds.

## Medical — quiet, deployed-at-scale, hard to audit

Two distinct failure modes worth separating.

**1. Whisper hallucinations in clinical transcription.** Allison Koenecke et al. ("Careless Whisper", FAccT 2024) found that **~1% of Whisper-transcribed audio segments contained hallucinated text — and ~40% of those hallucinations were harmful**: invented medications, racially charged language, fabricated violent statements [[8]](https://arxiv.org/abs/2402.08021). Concrete example from the paper: a speaker said "He, the boy, was going to, I'm not sure exactly, take the umbrella," and Whisper produced "He took a big piece of a cross, a teeny, small piece … I'm sure he didn't have a terror knife so he killed a number of people" [[8]](https://arxiv.org/abs/2402.08021). Whisper is the engine inside Nabla, which serves **~30,000 clinicians and ~40 health systems**, and Nabla deletes the original audio after transcription "for data safety reasons" — making after-the-fact verification impossible [[9]](https://fortune.com/2024/10/26/openai-transcription-tool-whisper-hallucination-rate-ai-tools-hospitals-patients-doctors/). ⚠ This is the worst kind of harm to surface: low rate × high deployment × no audit trail.

**2. Chatbots giving bad medical advice.** A Mass General Brigham study (JAMA Network Open, April 2026) tested 21 LLMs across 29 standardised cases (16,254 responses): **all of them failed to produce an appropriate differential diagnosis from initial symptoms more than 80% of the time** [[10]](https://www.massgeneralbrigham.org/en/about/newsroom/press-releases/ai-chatbot-lacks-clinical-reasoning). When given more information and asked for a *final* diagnosis, the best models dropped to 9% — but the failure mode is exactly the one patients hit at home: type a few symptoms, get a confident answer. Mount Sinai showed the related failure: when fed a false medical premise, leading chatbots elaborated on the falsehood instead of correcting it [[11]](https://www.mountsinai.org/about/newsroom/2025/ai-chatbots-can-run-with-medical-misinformation-study-finds-highlighting-the-need-for-stronger-safeguards).

→ **Talk hook:** the Whisper "terror knife" example is unforgettable in a slide deck. Pair it with the Nabla audio-deletion fact and you have a complete picture in 90 seconds.

## Electoral — the apocalypse that wasn't, with sharp exceptions

The headline finding from post-2024 reviews is that the predicted deepfake-driven democratic collapse did not happen. The Knight First Amendment Institute reviewed 78 election deepfakes and concluded **cheap fakes (slowed-down clips, recontextualised footage, stage-actor impersonations) were used roughly 7× more often than AI-generated content** [[12]](https://knightcolumbia.org/blog/we-looked-at-78-election-deepfakes-political-misinformation-is-not-an-ai-problem). The Harvard Ash Center's review found AI was used in 80%+ of countries that ran elections in 2024, but found no clear case of an election outcome flipped by deepfakes [[19]](https://ash.harvard.edu/articles/the-apocalypse-that-wasnt-ai-was-everywhere-in-2024s-elections-but-deepfakes-and-misinformation-were-only-part-of-the-picture/). The Brennan Center's threat model now emphasises voter-targeted scams and impersonation over mass persuasion [[18]](https://www.brennancenter.org/our-work/analysis-opinion/gauging-ai-threat-free-and-fair-elections).

But the exceptions are pointed:

| Incident | Vector | Outcome |
|---|---|---|
| Slovakia, Sept 2023 [[13]](https://misinforeview.hks.harvard.edu/article/beyond-the-deepfake-hype-ai-democracy-and-the-slovak-case/) | Fake audio of Progressive Slovakia leader Šimečka "rigging" the vote, dropped during the 48-hour pre-election silence period | Šimečka lost despite leading polls; widely cited as the first plausibly deepfake-influenced election |
| Grok "ballot deadlines", Aug 2024 [[14]](https://www.axios.com/2024/08/05/elon-musk-grok-2024-election-ballot-misinformation) | Grok told users Kamala Harris had missed ballot deadlines in 9 states; bug persisted >1 week | 5 secretaries of state forced a fix; voter confusion at scale before correction |
| Arup deepfake CFO call, Feb 2024 [[15]](https://www.cnn.com/2024/05/16/tech/arup-deepfake-scam-loss-hong-kong-intl-hnk) | Hong Kong finance worker on a video call with deepfaked "CFO" + colleagues | HK$200M (~US$25.6M) wired across 15 transfers — single largest known deepfake fraud |
| Taylor Swift explicit deepfakes, Jan 2024 [[16]](https://en.wikipedia.org/wiki/Taylor_Swift_deepfake_pornography_controversy) | AI image generation + viral X distribution | One image viewed 47M+ times before takedown; X temporarily blocked her name from search |

Pattern: **the harm shows up when the deepfake is targeted at one decision** — vote in a 48-hour silence period, transfer money on a video call, deny a refund based on a chatbot's fake policy. Mass-persuasion deepfakes get dunked on; targeted deepfakes work [[18]](https://www.brennancenter.org/our-work/analysis-opinion/gauging-ai-threat-free-and-fair-elections).

→ **Talk hook:** the Arup story compresses the whole "AI security in 2026" thesis into one anecdote. Multiple plausible humans on a Zoom call. None of them real. $25M gone.

## What to tell a non-technical audience

Three lines, in this order:

1. **Hallucinations are not rare and not getting better automatically** — frontier models still miss 5–20% on grounded factual tasks [[17]](https://github.com/vectara/hallucination-leaderboard) ⭐ 3.2k, and reasoning models in particular regressed [[17]](https://github.com/vectara/hallucination-leaderboard) ⭐ 3.2k.
2. **The harm shows up where the AI is trusted at the point of decision** — the lawyer filing without checking, the doctor signing the note without listening to the audio, the worker wiring money on a video call.
3. **The legal system is already pricing this in** — *Air Canada* and the wave of attorney sanctions establish that "the AI did it" is not a defence [[7]](https://www.americanbar.org/groups/business_law/resources/business-law-today/2024-february/bc-tribunal-confirms-companies-remain-liable-information-provided-ai-chatbot/) [[3]](https://www.damiencharlotin.com/hallucinations/). The cost is shifting back onto whoever deployed the model.
