---
title: "Midjourney v6 Prompt Craft: A Field Guide"
date: 2026-06-09
depth: deep
format: md
topic: "Midjourney v6 prompt craft"
topic_raw: "Midjourney v6 prompt craft"
issue: 210
tags: [midjourney, prompt-engineering, ai-image, generative-ai, diffusion-models]
cover: cover.svg
summary: "How to prompt Midjourney v6: drop the v5 keyword soup, write natural-language scenes, and use weights, references and parameters deliberately."
citations: 40
reading_time_min: 8
cost_usd: 4.10
duration_sec: 480
model: "Opus 4.8"
---

> **TL;DR** — v6 broke v5's habits: stop stacking junk keywords ("8k, octane render, trending on artstation") and **describe one coherent scene in plain language** [[1]](https://venturebeat.com/ai/midjourney-v6-is-here-with-in-image-text-and-completely-overhauled-prompting)[[2]](https://aituts.com/midjourney-v6/). Front-load the subject, keep prompts ~50–150 words, and reach for parameters (`--stylize`, `--chaos`, `--style raw`) and references (`::` weights, `--sref`, `--cref`) only when the words alone can't get there [[8]](https://www.imagetoprompt.dev/blog/midjourney-prompt-guide-2026/)[[15]](https://docs.midjourney.com/hc/en-us/articles/32658968492557-Multi-Prompts-Weights). ⚠ v6 is a **legacy model** in 2026 (default has moved through v7 to v8 [[40]](https://freeacademy.ai/blog/midjourney-vs-dalle-vs-stable-diffusion-vs-flux-comparison-2026)), but its core craft — describe what you *do* want, concisely — still transfers [[34]](https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version)[[36]](https://godofprompt.ai/blog/midjourney-2025-v7-timeline-and-video-features/).

## What actually changed in v6

Midjourney's own v6 announcement was blunt: prompting is "significantly different than V5," users must "relearn" it, and the model is "MUCH more sensitive" to wording while being far better at understanding explicit descriptions [[1]](https://venturebeat.com/ai/midjourney-v6-is-here-with-in-image-text-and-completely-overhauled-prompting). The practical effect is a paradigm shift from comma-separated keyword salad toward **natural language** — write a full descriptive sentence, the way you'd brief a photographer on a scene [[5]](https://medium.com/design-bootcamp/midjourney-v-6-is-arriving-with-a-different-image-prompting-focus-on-natural-language-094d5a51858e).

Three concrete consequences:

- **Junk tokens stopped helping.** Camera and quality boilerplate ("8k, best quality, Canon EOS R5") can be stripped with nothing lost, because v6 understands prompts well enough not to need them [[2]](https://aituts.com/midjourney-v6/)[[9]](https://blog.mlq.ai/getting-started-with-midjourney-v6/).
- **Longer, coherent prompts hold up.** v6 takes long, conversational prompts and fulfills nearly every element — a marked upgrade over v5.2's comprehension [[3]](https://goldpenguin.org/blog/midjourney-v6-reviewed/). In token-retention testing it held all prompt elements through seven diffusion steps before dropping any, one step further than v5.2 [[4]](https://midlibrary.io/midguide/midjourney-v6-in-depth-review-part-2-prompting).
- **Literalness levers appeared.** Text inside `"double quotes"` is rendered as a literal instruction, and `--style raw` produces a more literal, less auto-beautified result — recommended when you need legible lettering [[6]](https://www.imaginepro.ai/blog/2025/7/master-midjourney-word-art-prompts).

## Anatomy of a v6 prompt

Midjourney's docs frame a prompt around seven considerations — **subject, medium, environment, lighting, color, mood, composition** — and stress that short, simple prompts usually generate the best images (brevity buys variety, length buys control) [[7]](https://docs.midjourney.com/hc/en-us/articles/32023408776205-Prompt-Basics). A widely-shared working order:

```
[subject] · [style/medium] · [lighting] · [color palette] · [composition] · [mood] --ar [ratio] --style raw
```

[[8]](https://www.imagetoprompt.dev/blog/midjourney-prompt-guide-2026/) A parallel six-part recipe runs style → subject → setting → composition → lighting → details [[10]](https://midjourneyv6.org/midjourney-v6-prompt-structure/).

Three rules that matter more than the exact template:

| Lever | Guidance | Source |
|------------------|------------------------------------------------------------------------------|--------|
| **Front-loading** | Attention is distributed across the prompt; earlier terms carry more visual weight, so lead with the most important element | [[8]][0] |
| **Length**        | ~50–150 words is the sweet spot — enough to specify, short enough to retain  | [[8]][0] |
| **Specificity**   | "a dragon" → generic; qualified subject (scales, pose, environment) → distinctive. v6 rewards explicit physical/contextual/emotional detail | [[9]][1] |

[0]: https://www.imagetoprompt.dev/blog/midjourney-prompt-guide-2026/
[1]: https://blog.mlq.ai/getting-started-with-midjourney-v6/

One nuance: word order's effect is muted when a strong artist reference anchors the aesthetic, but becomes decisive for weak or undefined styles [[8]](https://www.imagetoprompt.dev/blog/midjourney-prompt-guide-2026/).

## Parameters that move the needle

Parameters do two jobs: steer the model's aesthetic latitude, and shape output geometry. Ranges and defaults below are from the official docs.

| Parameter | Range (default) | What it does | Source |
|------------------|-----------------------|-------------------------------------------------------------------------------|--------|
| `--stylize` `-s` | 0–1000 (**100**)      | Master "artistic freedom" slider. Low = tracks prompt literally; high = MJ adds flair that can drift | [[11]][s] |
| `--chaos` `-c`   | 0–100 (**0**)         | "Variety" — how different the four grid images are; high diverges from prompt  | [[12]][c] |
| `--weird` `-w`   | 0–3000 (**0**)        | Experimental/unconventional aesthetics; ⚠ not fully compatible with seeds      | [[13]][w] |
| `--style raw`    | on/off                | Disables MJ's auto-styling "auto-pilot" → more photo-real, tighter control (v5.1+) | [[14]][r] |
| `--quality` `-q` | .25 / .5 / 1 (**1**)  | GPU time → detail; affects only the initial four, not variations/upscales       | [[16]][L][[19]][q] |
| `--ar`           | any (**1:1**)         | Aspect ratio; goes at prompt end, no space before the dashes                    | [[20]][p] |
| `--seed`         | 0–4294967295 (random) | Reproducibility/testing; ⚠ seed-locking unreliable in Turbo mode                | [[17]][sd] |
| `--tile`         | on/off                | One seamless tile for patterns; ⚠ upscaling breaks the repeat                   | [[18]][t] |

[s]: https://docs.midjourney.com/hc/en-us/articles/32196176868109-Stylize
[c]: https://docs.midjourney.com/hc/en-us/articles/32099348346765-Chaos-Variety
[w]: https://docs.midjourney.com/hc/en-us/articles/32390120435085-Weird
[r]: https://docs.midjourney.com/hc/en-us/articles/32634113811853-Raw
[L]: https://docs.midjourney.com/hc/en-us/articles/33329788681101-Legacy-Features
[q]: https://docs.midjourney.com/hc/en-us/articles/32176522101773-Quality
[p]: https://docs.midjourney.com/hc/en-us/articles/32859204029709-Parameter-List
[sd]: https://docs.midjourney.com/hc/en-us/articles/32604356340877-Seeds
[t]: https://docs.midjourney.com/hc/en-us/articles/32197978340109-Tile

⚠ **High `--stylize` washes out fidelity.** At `--s 750` Midjourney takes creative liberty and may ignore some specified details to polish the image — so if v6 is "disobeying" your prompt, lower the stylize before adding more words [[31]](https://midlibrary.io/midguide/midjourney-v6-in-depth-review-part-3-parameters).

## References and weights

The double-colon `::` syntax is the foundation of fine control. `concept:: number` weights a concept relative to others — `space::2 ship` makes "space" twice as influential as "ship". No space before `::`, one space after [[15]](https://docs.midjourney.com/hc/en-us/articles/32658968492557-Multi-Prompts-Weights). v6 accepts decimal weights for fine tuning [[21]](https://aituts.com/midjourney-prompt-weights/).

**Negation is just a negative weight.** `--no X` is exactly shorthand for `X::-0.5` [[15]](https://docs.midjourney.com/hc/en-us/articles/32658968492557-Multi-Prompts-Weights). Weights are relative (`wood::1 teapot::-1` ≡ `wood::10 teapot::-10`), but the **sum of all weights must stay positive** or Midjourney errors [[21]](https://aituts.com/midjourney-prompt-weights/).

| Reference | Syntax / range | Effect | Source |
|--------------------|----------------------------------|------------------------------------------------------------------------|--------|
| Image prompt       | `--iw 0–3` (**1**)               | Weight of an input image vs the text; v6 ceiling is higher than older 0–2 | [[22]][iw] |
| Style reference    | `--sref <url\|code\|random>` + `--sw 0–1000` (**100**) | Transfers an aesthetic. `--sw 0` cancels it; sweet spot ~65–175 | [[23]][sr][[24]][sc] |
| Character reference | `--cref <url>` + `--cw 0–100` (**100**) | Consistent character. `--cw 100` carries face+hair+clothes; `--cw 0` = face only (swap outfit) | [[25]][cr] |

[iw]: https://www.aiarty.com/midjourney-guide/midjourney-image-weight.htm
[sr]: https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference
[sc]: https://midlibrary.io/midguide/deep-dive-into-midjourney-sref-codes
[cr]: https://updates.midjourney.com/character-refs/

`--sref random` resolves to a reusable numeric code shown in the prompt after generation — a free way to discover and lock aesthetics [[24]](https://midlibrary.io/midguide/deep-dive-into-midjourney-sref-codes). `--cref` is precision-limited: it won't reproduce exact dimples, freckles or t-shirt logos, and is **not** designed for real people or photos [[25]](https://updates.midjourney.com/character-refs/).

## What backfires (the skeptic's section)

The single biggest failure mode is carrying v5 habits into v6 [[26]](https://journeyaiart.com/blog-Mastering-Midjourney-v6-A-Deep-Dive-into-the-New-Version-25318).

- **Keyword stacking averages to mush.** Pile on five-plus style modifiers and they blend into a muddy average rather than compounding — exactly why "highly detailed, 8k, octane render, trending on artstation" lost its punch [[29]](https://prompt-architects.com/blog/40-why-midjourney-prompts-dont-work). Vague quality boilerplate ("award-winning," "photorealistic," "4k/8k") dilutes the prompt [[9]](https://blog.mlq.ai/getting-started-with-midjourney-v6/).
- **Long prompts silently drop tokens.** The longer the prompt, the more likely Midjourney assigns weight `0.00` to important keywords — especially late ones — and ignores them [[30]](https://promptomania.com/models/midjourney/midjourney-v6). v6 begins omitting detail past a token threshold; fusing words with underscores into a single token (`stained_glass`) raises per-token weight [[33]](https://medium.com/@alexcarltully/how-i-use-underscores-to-get-more-out-of-my-midjourney-prompts-1972f69d9306).
- **Diagnose with `/shorten`.** It scores every token 0–1 and strikes through near-zero words, making your dead filler visible [[32]](https://aituts.com/midjourney-shorten/).
- **Negation in the positive prompt backfires.** Writing "without hats" forces the model to parse a negation and can emphasize the very thing you wanted gone; the dedicated `--no hat` removes it reliably [[27]](https://docs.midjourney.com/hc/en-us/articles/32173351982093-No)[[28]](https://www.whytryai.com/p/midjourney-negative-prompt).

The consistent, official-aligned rule: **describe what you DO want, concisely** — not what to avoid.

## Where v6 sits in 2026

v6's lineage moved fast: v6.1 became default on **July 30 2024**, and v7 (released April 3 2025) took over as default on **June 17 2025** [[34]](https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version); by early 2026 Midjourney had shipped **v8** on a rewritten engine with native 2K output [[40]](https://freeacademy.ai/blog/midjourney-vs-dalle-vs-stable-diffusion-vs-flux-comparison-2026). v6 is still selectable via `--v 6`, but it's two-plus generations behind.

For craft, the **trajectory matters more than the version number**. Midjourney's own v7 note warns it's "an entirely new model" that "may require different styles of prompting" and is "much smarter with text prompts" [[35]](https://updates.midjourney.com/v7-alpha/). v7 improved prompt understanding ~35%, so **simpler prompts now beat** the parameter-heavy scaffolding v6 rewarded [[36]](https://godofprompt.ai/blog/midjourney-2025-v7-timeline-and-video-features/)[[37]](https://evolink.ai/blog/midjourney-v7-review-2026). The direction of travel — less prompt-engineering, more plain description — is the same lesson v6 first taught.

### How the prompting philosophies compare

| Model | Prompting style | Adherence | Source |
|-------------------|------------------------------------------------|--------------------------------------------|--------|
| **Midjourney v6** | Terse aesthetic phrases + parameters/refs      | Aesthetic-first; may ignore literal specs  | [[38]][cmp][[39]][pxz] |
| **DALL-E 3**      | Verbose natural-language sentences (ChatGPT rewrites) | High, conversational                  | [[38]][cmp] |
| **Flux**          | Photographic / camera terminology              | Precise — follows instructions literally    | [[38]][cmp][[39]][pxz] |
| **Stable Diffusion XL/3** | Weighted `(parentheses)` keywords + negative-prompt field | Keyword-control driven           | [[38]][cmp] |

[cmp]: https://www.imagetoprompt.dev/blog/stable-diffusion-vs-midjourney-vs-dalle3/
[pxz]: https://pxz.ai/blog/midjourney-vs-stable-diffusion-vs-flux

Flux's strict instruction-following is the cleanest contrast to Midjourney's looser, taste-driven interpretation — ask Midjourney for three people and you may get five [[39]](https://pxz.ai/blog/midjourney-vs-stable-diffusion-vs-flux). If you need exact counts, positions or text, that gap is the reason to reach for a rival; if you want a striking image fast, it's Midjourney's whole appeal.
