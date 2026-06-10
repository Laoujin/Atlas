---
layout: expedition
title: "Diffusion Models: From Noise to Image — and Into Midjourney v6"
date: 2026-06-09
topic: "Live explainer + Midjourney craft guide: diffusion models from noise to image, with real prompt-engineering takeaways (2026)."
format: md
tags: [diffusion-models, midjourney, prompt-engineering, generative-ai, deep-learning]
summary: "Complete technical journey from Gaussian noise schedules through score networks and CLIP conditioning to production Midjourney v6 craft — with a post-mortem on why hands failed and how the same architectural fixes inform smarter prompting."
cover: cover.svg
synthesis: true
children:
  - slug: forward-diffusion-and-noise-schedules
    title: "Forward diffusion and noise schedules"
    depth: standard
    status: success
    summary: "How the forward diffusion process works mathematically, and how the choice of noise schedule — linear, cosine, EDM σ, or Laplace — shapes training quality, resolution behaviour, and what not to get wrong."
    citations: 16
    reading_time_min: 6
  - slug: reverse-denoising-architectures-and-the-score-network
    title: "Reverse denoising: architectures and the score network"
    depth: deep
    status: success
    summary: "How the denoiser that drives reverse diffusion is really a score network, and how its backbone evolved from U-Net to the transformers behind FLUX, SD3 and Sora."
    citations: 52
    reading_time_min: 9
  - slug: text-conditioning-via-clip-and-beyond
    title: "Text conditioning via CLIP (and beyond)"
    depth: standard
    status: success
    summary: "How CLIP's shared text/image embedding space powers diffusion model conditioning—and why modern models now stack T5-XXL, dual CLIPs, and even LLMs on top."
    citations: 20
    reading_time_min: 6
  - slug: why-hands-broke-and-what-fixed-it
    title: "Why hands broke — and what fixed it"
    depth: standard
    status: success
    summary: "A technical post-mortem on why diffusion models generated malformed hands for years — sparse training data, CLIP counting blindness, VAE resolution limits, U-Net locality, and mode-interpolation — plus the layered fixes that pushed success rates from ~30% to ~90% by 2025."
    citations: 21
    reading_time_min: 7
  - slug: midjourney-v6-prompt-craft
    title: "Midjourney v6 prompt craft"
    depth: deep
    status: success
    summary: "How to prompt Midjourney v6: drop the v5 keyword soup, write natural-language scenes, and use weights, references and parameters deliberately."
    citations: 40
    reading_time_min: 8
  - slug: latent-space-and-vae
    title: "Latent space and VAE"
    depth: ceo
    status: success
    summary: "VAEs encode data as probability distributions in latent space, enabling smooth interpolation and generative capabilities beyond standard autoencoders."
    citations: 5
    reading_time_min: 2
  - slug: controlnet-and-structural-conditioning
    title: "ControlNet and structural conditioning"
    depth: ceo
    status: success
    summary: "ControlNet adds spatial control to image generation by training a parallel network branch to inject structural guidance without disrupting the base model."
    citations: 4
    reading_time_min: 2
cost_usd: 14.18
duration_sec: 3030
citations: 158
reading_time_min: 40
issue: 210
model: "Sonnet 4.6"
---

The deepest unifying thread across this expedition is a single mathematical object: the **score function** — the gradient of the log data density `∇ log p(x)`. Forward diffusion destroys information by following a noise schedule; reverse diffusion reconstructs by following the score back toward data. Every network architecture surveyed (U-Net, DiT, MMDiT, FLUX) is just a different box for computing this gradient. Every training objective — ε-prediction, x₀-prediction, v-prediction, rectified flow — is a reparametrization of the same score, [[1]](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/) and Karras et al.'s EDM framework makes the equivalence explicit via preconditioning coefficients. [[2]](https://arxiv.org/abs/2206.00364) When you increase Midjourney's `--stylize` or a diffusers `guidance_scale`, you are literally amplifying the conditional score relative to the unconditional one — CFG is `ε̂ = ε(x,∅) + w·(ε(x,text) − ε(x,∅))`, steering the gradient trajectory in latent space.

**Architecture and anatomy are causally linked.** The hands post-mortem and the architecture survey are really the same story told from different angles. U-Net's convolutional locality meant fingers were processed without global palm context — the network learned fingers as local textures, not as a kinematically constrained structure. [[3]](https://zsky.ai/blog/flux-vs-sdxl-comparison) DiT and MMDiT replace this with full-sequence self-attention: every finger token attends to every palm token in every layer. [[4]](https://www.wpeebles.com/DiT) FLUX.1's 12B-parameter MMDiT achieved "correct finger count in the vast majority of generations" not from anatomical training but from the architectural side-effect that global attention enforces global consistency. [[5]](https://www.ikomia.ai/blog/best-ai-diffusion-models-comparison-guide) The scaling law DiT demonstrated — more compute → lower FID monotonically — is the same reason FLUX outperforms SDXL on anatomy at matched prompt complexity.

**The text encoder stack is the hidden variable behind prompt strategy.** CLIP's 77-token hard limit and visual-contrastive training bias made keyword-front-loading rational in SD 1.x: token 78 onward was invisible, so packing the most important terms early was load-bearing engineering, not stylistic preference. [[6]](https://arxiv.org/abs/2103.00020) Imagen's demonstration that a frozen T5-XXL outperforms CLIP on compositional prompts [[7]](https://imagen.research.google/paper.pdf) — and SD3/FLUX's stacking of dual CLIPs with T5 — is what legitimises Midjourney v6's "write a natural scene description" instruction. The model has deep language understanding of grammar, syntax, and spatial relations available once T5 is in the stack; the keyword-soup habit actively fights against it by fragmenting coherent grammatical structure into a bag of tokens. By 2026 HiDream-I1 uses a full Llama-3.1-8B encoder [[8]](https://arxiv.org/abs/2505.22705) — at that point prompt writing and LLM prompting converge completely.

**Resolution and the VAE interact in ways the surface-level pipeline hides.** The VAE's 8× spatial compression means a full-frame hand at 512px collapses to 5–8 latent pixels per finger — the decoder is asked to reconstruct detail it never saw encoded. [[9]](https://www.makeuseof.com/ai-image-generators-hands-issue/) SDXL's move to 1024px native resolution was not cosmetic; it tripled the effective latent resolution for fine anatomy. ControlNet's depth-map injection acts as a third bypass: it supplies the spatial constraints the latent bottleneck loses, explicitly conditioning the score network on 3D structure rather than asking it to infer depth from pixel patterns alone. The open question is whether higher-resolution VAEs (SD3 uses a 16-channel VAE vs SD 1.5's 4-channel) make ControlNet redundant for anatomy, or whether explicit structural conditioning remains complementary regardless of VAE capacity.

**The noise schedule's effect on practitioners is underappreciated.** Every sampler tuning — DDIM vs DPM-Solver vs Euler, step counts, sigma schedule — changes which part of the SNR curve gets the most compute. The EDM finding that zero terminal SNR must be enforced [[10]](https://arxiv.org/abs/2305.08891) is directly observable in generation: models trained with the common off-the-shelf cosine schedule produce slightly hazy darks and cannot generate pure-black backgrounds. The practitioner proxy for this is noticing when a model refuses to produce high-contrast results — the symptom of non-zero terminal SNR leaking into inference.

What no single child fully resolves: how the shift to **rectified flow** (FLUX, SD3) changes the prompt-engineering intuitions built on DDPM-style score matching. Rectified flow learns straight transport paths rather than curved SDE trajectories [[11]](https://arxiv.org/abs/2209.03003) — empirically this makes fewer steps viable, but whether it changes *which* prompt tokens govern *which* spatial regions in cross-attention, and therefore whether front-loading rules still apply, is not yet settled in the literature.
