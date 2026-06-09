---
title: "Reverse Denoising: Architectures and the Score Network"
date: 2026-06-09
depth: deep
format: md
topic: "Reverse denoising: architectures and the score network"
topic_raw: "Reverse denoising: architectures and the score network"
issue: 210
tags: [diffusion-models, score-matching, u-net, diffusion-transformers, generative-ai]
summary: "How the denoiser that drives reverse diffusion is really a score network, and how its backbone evolved from U-Net to the transformers behind FLUX, SD3 and Sora."
citations: 52
reading_time_min: 9
cover: cover.svg
cost_usd: 4.95
duration_sec: 497
model: "Opus 4.8"
---

> **TL;DR** — The network that runs reverse denoising isn't predicting "the image"; it's estimating the **score**, the gradient of the log data density `∇ log p(x)`, which points back toward clean data at every noise level [[1]](https://yang-song.net/blog/2021/score/). Predicting noise (ε), the clean signal (x₀), velocity (v), or a flow-matching drift are all the *same target reparametrized* — for Gaussian noise the score is just `−ε/σ` [[5]](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/). The **backbone** that computes it has migrated from the convolutional **U-Net** (Stable Diffusion, ADM) to the **Diffusion Transformer** (DiT → MMDiT), which now powers [FLUX.1](https://github.com/black-forest-labs/flux) ⭐ 25.6k, SD3.5, and Sora because attention scales more smoothly than convolution [[18]](https://ar5iv.labs.arxiv.org/html/2212.09748)[[45]](https://medium.com/@kdk199604/dit-how-transformers-are-replacing-u-nets-in-diffusion-models-21cf9c95f259).

## The one idea: the denoiser is a score network

Reverse denoising looks like "remove a little noise, repeat." Mathematically it's gradient ascent on probability. A **score-based model** is a network `s_θ(x)` trained to approximate the **score function** — the gradient of the log-density `∇ₓ log p(x)` — which sidesteps the intractable normalizing constant that plagues density models [[1]](https://yang-song.net/blog/2021/score/). Once you know the score at every noise level, you generate samples by **Langevin dynamics**: repeatedly step along the score and inject a little Gaussian noise [[1]](https://yang-song.net/blog/2021/score/). Song & Ermon's NCSN did exactly this — estimate scores across many noise scales, then sample with annealed Langevin dynamics — and it is the direct precursor to modern diffusion [[6]](https://www.emergentmind.com/topics/noise-conditional-score-networks-ncsn).

Three classical results glue "denoising" to "score":

- **Denoising score matching** (Vincent, 2011): training a denoising autoencoder to reconstruct clean data from a Gaussian-corrupted input is *mathematically equivalent* to matching the score of the noised density — and it avoids the second derivatives plain score matching needs [[3]](https://direct.mit.edu/neco/article/23/7/1661/7677/A-Connection-Between-Score-Matching-and-Denoising).
- **Tweedie / Miyasawa**: for `Y = X + σε`, the posterior mean is `E[X|Y] = Y + σ²∇log p_σ(Y)`, equivalently `E[ε|Y] = −σ²∇log p_σ(Y)` — so minimizing the denoising MSE *recovers the score directly* [[4]](https://scoste.fr/posts/score_matching/).
- **The ε↔score identity**: for Gaussian perturbations `∇log p = −ε/σ`, which makes DDPM's noise-prediction network a reparametrized score model, `s_θ(xₜ,t) = −ε_θ(xₜ,t)/√(1−ᾱₜ)` [[5]](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/)[[36]](https://hal.cse.msu.edu/teaching/2024-spring-deep-learning/21-diffusion-models/).

Ho et al.'s **DDPM** uses the ε-prediction objective, and its simplified loss coincides with multi-scale denoising score matching [[7]](https://ar5iv.labs.arxiv.org/html/2006.11239). Song et al.'s **score-SDE** framework unifies everything: a forward noising SDE has a closed-form **reverse-time SDE**, `dx = [f − g²∇log pₜ] dt + g dw`, driven solely by the score, plus a deterministic **probability-flow ODE**, `dx = [f − ½g²∇log pₜ] dt`, that shares the same marginals and enables exact likelihoods [[2]](https://arxiv.org/pdf/2011.13456). Everything below is *how to build the box that outputs `s_θ`*.

## Backbone 1 — the U-Net denoiser

The denoiser inherits its skeleton from the **U-Net** of Ronneberger et al. (2015): a fully convolutional encoder–decoder with a contracting path (two 3×3 convs + ReLU, then 2× max-pool), a symmetric expanding path of up-convolutions, and **skip connections** that concatenate encoder features into the matching decoder stage to preserve spatial detail [[8]](https://arxiv.org/abs/1505.04597)[[9]](https://uw-madison-datascience.github.io/ML-X-Nexus/Toolbox/Models/UNET.html). Because it outputs a tensor the same size as its input, it is a natural fit for predicting per-pixel noise — which is exactly why [diffusers](https://github.com/huggingface/diffusers) ⭐ 33.8k packages it as the default `UNet2DConditionModel` [[17]](https://github.com/huggingface/diffusers).

Dhariwal & Nichol's **ADM** ("Diffusion Models Beat GANs," 2021) ablated this skeleton into the dominant form and beat GANs on ImageNet (FID 2.97 / 4.59 / 7.72 at 128/256/512) [[10]](https://arxiv.org/abs/2105.05233). The diffusion-specific changes:

| Modification | What it does | Source |
|---|---|---|
| More depth over width | better FID at fixed compute | [[11]](https://ar5iv.labs.arxiv.org/html/2105.05233) |
| Multi-head attention (64 ch/head) at 32², 16², 8² | global coherence at low resolutions | [[11]](https://ar5iv.labs.arxiv.org/html/2105.05233) |
| BigGAN residual blocks for up/downsampling | stable feature rescaling | [[11]](https://ar5iv.labs.arxiv.org/html/2105.05233) |
| Residual rescale by 1/√2 | training stability | [[11]](https://ar5iv.labs.arxiv.org/html/2105.05233) |
| Adaptive Group Norm (AdaGN) | injects timestep + class embedding into each res block | [[11]](https://ar5iv.labs.arxiv.org/html/2105.05233) |

The **timestep** enters as a sinusoidal positional embedding (or random Fourier features), MLP-projected and added into residual blocks or fed through AdaGN [[13]](https://iclr-blogposts.github.io/2026/blog/2026/diffusion-architecture-evolution/). Rombach et al.'s **Latent Diffusion** (CVPR 2022) then made two moves that defined Stable Diffusion: run the U-Net in a compressed **VAE latent space**, and add **cross-attention layers** so the denoiser becomes a text/conditional generator [[12]](https://arxiv.org/abs/2112.10752). The Stable Diffusion U-Net has four stages — channels `{320, 640, 1280, 1280}` — each with 2–3 ResNet blocks plus 8-head self-attention and 8-head cross-attention to CLIP embeddings [[14]](https://medium.com/@spoorthisetty99/conditioning-in-diffusion-models-a-deep-dive-into-ldms-dits-and-vanilla-u-nets-610262d3fe71). Its open-source footprint cemented the design: [CompVis/stable-diffusion](https://github.com/CompVis/stable-diffusion) ⭐ 73k (Jun 2026) [[15]](https://github.com/CompVis/stable-diffusion) and the original [latent-diffusion](https://github.com/CompVis/latent-diffusion) ⭐ 14k [[16]](https://github.com/CompVis/latent-diffusion).

## Backbone 2 — Diffusion Transformers (DiT → MMDiT)

Peebles & Xie's **DiT** discards the U-Net entirely: a plain transformer operating on **patchified latents**. A VAE downsamples the image 8× to a 32×32×4 latent, which is cut into p×p patches yielding `T = (I/p)²` tokens; halving the patch size quadruples token count and Gflops [[19]](https://www.wpeebles.com/DiT). Conditioning uses **adaLN-zero**: scale/shift parameters are regressed from the *summed* timestep+class embedding, and the per-block residual modulation is zero-initialized so each block starts as the identity function [[18]](https://ar5iv.labs.arxiv.org/html/2212.09748). This beats both cross-attention and in-context conditioning while being the most compute-efficient [[20]](https://apxml.com/courses/advanced-diffusion-architectures/chapter-3-transformer-diffusion-models/dit-conditioning). The headline result is a clean **scaling law**: higher-Gflops DiTs consistently reach lower FID, with DiT-XL/2 hitting FID-50K 2.27 on ImageNet 256² [[19]](https://www.wpeebles.com/DiT). Repo: [facebookresearch/DiT](https://github.com/facebookresearch/DiT) ⭐ 8.6k [[28]](https://github.com/facebookresearch/DiT).

The template propagated fast:

- **SD3 → MMDiT** (Esser et al., 2024): separate weights per modality (image vs text) but a *joined sequence* for shared attention, conditioned on two CLIP encoders plus T5, trained under reweighted Rectified Flow; scales 450M → 8B params without saturating [[21]](https://arxiv.org/abs/2403.03206)[[22]](http://stability.ai/news-updates/stable-diffusion-3-research-paper).
- **FLUX.1** ([Black Forest Labs](https://github.com/black-forest-labs/flux) ⭐ 25.6k, Aug 2024): a 12B rectified-flow transformer hybridizing MMDiT "double-stream" blocks (text+image tokens jointly attended) with "single-stream" parallel DiT blocks, conditioned on T5-XXL + CLIP [[23]](https://huggingface.co/black-forest-labs/FLUX.1-dev)[[24]](https://arxiv.org/html/2507.09595v1)[[29]](https://github.com/black-forest-labs/flux).
- **Sora**: a DiT over **spacetime patches** of video latents as tokens, enabling variable resolution and duration [[25]](https://openai.com/index/video-generation-models-as-world-simulators/).
- **PixArt-α** keeps cross-attention to inject text into DiT blocks, reaching near-SOTA at ~1% of RAPHAEL's training cost [[26]](https://arxiv.org/abs/2310.00426); **Hunyuan-DiT** is a multi-resolution DiT with bilingual Chinese/English understanding [[27]](https://arxiv.org/abs/2405.08748).
- **SiT** (Scalable Interpolant Transformers, ECCV 2024) keeps the DiT backbone *wholesale* but swaps the diffusion formulation for a flexible stochastic-interpolant/flow framework, then decouples four design axes (discrete vs. continuous time, prediction target, interpolant choice, and a deterministic vs. stochastic sampler) from the fixed network [[51]](https://arxiv.org/abs/2401.08740). Holding architecture and compute constant, SiT-XL/2 beats DiT at every size — FID-50K 2.06 at 256² — because the sampler's diffusion coefficient can be tuned separately from learning [[51]](https://arxiv.org/abs/2401.08740)[[52]](https://github.com/willisma/SiT). Repo: [willisma/SiT](https://github.com/willisma/SiT) ⭐ 1.2k.

## The prediction target: ε, x₀, v, or flow

The architectures above all output *something*, and the choice of target changes training stability and few-step behaviour — but every option maps back to the same score.

| Parametrization | Network predicts | Notes | Source |
|---|---|---|---|
| **ε-prediction** | the added noise | DDPM default; `L_simple = E‖ε − ε_θ‖²`; `s_θ = −ε_θ/√(1−ᾱₜ)` | [[7]](https://ar5iv.labs.arxiv.org/html/2006.11239)[[36]](https://hal.cse.msu.edu/teaching/2024-spring-deep-learning/21-diffusion-models/) |
| **x₀-prediction** | the clean signal | better behaved at high noise | [[37]](https://apxml.com/courses/advanced-diffusion-architectures/chapter-4-advanced-diffusion-training/advanced-loss-functions) |
| **v-prediction** | velocity `v = αₜ·ε − σₜ·x₀` | ~constant variance across t; standard for distillation/few-step | [[30]](https://arxiv.org/abs/2202.00512)[[37]](https://apxml.com/courses/advanced-diffusion-architectures/chapter-4-advanced-diffusion-training/advanced-loss-functions) |
| **Flow-matching / rectified flow** | drift `v = X₁ − X₀` along straight paths | `Xₜ = t·X₁ + (1−t)·X₀`; equals v-pred up to weighting | [[35]](https://arxiv.org/abs/2209.03003) |

Karras et al.'s **EDM** generalizes the lot with preconditioning: `D_θ = c_skip·x + c_out·F_θ(c_in·x; c_noise)`, with coefficients chosen so the effective target has unit variance at every noise level (`c_skip = σ_data²/(σ²+σ_data²)`, `c_out = σ·σ_data/√(σ²+σ_data²)`, loss weight `λ(σ) = 1/c_out²`) [[31]](https://arxiv.org/abs/2206.00364)[[32]](https://valentinpratz.de/posts/2024-11-15-edm/). **Min-SNR** then frames training as multi-task learning, clamping per-timestep weights `wₜ = min(SNR(t), γ)` with default γ=5 — giving 3.4× faster convergence and a then-record FID 2.06; notably, constant weighting matches ε-prediction, SNR weighting matches x₀, and v-prediction divides the weight by (SNR+1) [[33]](https://arxiv.org/abs/2303.09556)[[34]](https://arxiv.org/html/2303.09556v3). The takeaway: parametrization is a *variance-reduction and weighting* choice, not a different model.

## Conditioning the score network

A text-to-image score network must steer `∇log p(x)` toward `∇log p(x | prompt)`. Three mechanisms, often combined:

- **Cross-attention text injection.** Latent Diffusion turns the denoiser into a conditional generator by feeding frozen text-encoder embeddings as the keys/values of cross-attention layers [[12]](https://arxiv.org/abs/2112.10752). Imagen showed that generic frozen LLMs like **T5** are surprisingly effective, and that scaling the *text encoder* boosts fidelity and alignment more than scaling the diffusion model itself [[40]](https://arxiv.org/pdf/2205.11487). SD3 concatenates three encoders — OpenCLIP-ViT/G, CLIP-ViT/L, and T5-xxl [[41]](https://huggingface.co/stabilityai/stable-diffusion-3-medium).
- **adaLN conditioning.** In DiT/MMDiT the condition is regressed into per-block scale/shift instead of attended to — lower FID and cheaper than cross-attention [[20]](https://apxml.com/courses/advanced-diffusion-architectures/chapter-3-transformer-diffusion-models/dit-conditioning).
- **Guidance.** Dhariwal & Nichol's classifier guidance pushes samples with a noisy-image classifier's gradient (sampling ∝ `p(y|x)^s`) [[10]](https://arxiv.org/abs/2105.05233). Ho & Salimans' **classifier-free guidance** drops the classifier: jointly train a conditional and unconditional model and *combine the two score estimates* at sample time [[38]](https://arxiv.org/abs/2207.12598) — exposed in diffusers as `guidance_scale` (higher = follows prompt more closely, too high = artifacts) [[39]](https://huggingface.co/docs/diffusers/en/using-diffusers/conditional_image_generation).

Underneath it all, **latent diffusion** is the architectural enabler: the VAE offloads perceptual detail so the score network operates on a small latent grid, slashing compute versus pixel-space diffusion [[12]](https://arxiv.org/abs/2112.10752).

## State of the art and trade-offs (2026)

The defining story of 2024–2026 is the **U-Net → DiT migration**. U-Nets dominated 2021–2023 (SDXL at 2.57B params) but hit a scaling ceiling around ~2.6B; as data and compute grew, the bottleneck shifted from local fidelity to global semantic alignment, which favors attention [[45]](https://medium.com/@kdk199604/dit-how-transformers-are-replacing-u-nets-in-diffusion-models-21cf9c95f259). The consensus rationale: attention strictly generalizes convolution and scales more smoothly, so at matched size U-Nets underperform DiTs [[45]](https://medium.com/@kdk199604/dit-how-transformers-are-replacing-u-nets-in-diffusion-models-21cf9c95f259)[[13]](https://iclr-blogposts.github.io/2026/blog/2026/diffusion-architecture-evolution/).

| System | Backbone | Target | Text encoders | Source |
|---|---|---|---|---|
| Stable Diffusion 1.x | U-Net + cross-attn | ε | CLIP | [[14]](https://medium.com/@spoorthisetty99/conditioning-in-diffusion-models-a-deep-dive-into-ldms-dits-and-vanilla-u-nets-610262d3fe71) |
| SD3.5 | MMDiT + adaLN + QK-norm | rectified flow | CLIP-G, CLIP-L, T5-XXL | [[43]](https://learnopencv.com/stable-diffusion-3/)[[44]](https://stability.ai/news/introducing-stable-diffusion-3-5) |
| FLUX.1 (12B) | hybrid MMDiT + parallel DiT | rectified flow | T5-XXL, CLIP | [[23]](https://huggingface.co/black-forest-labs/FLUX.1-dev)[[24]](https://arxiv.org/html/2507.09595v1) |
| Ideogram 4.0 (9.3B) | single-stream DiT, 34 layers | — | Qwen3-VL-8B | [[49]](https://ideogram.ai/blog/ideogram-4.0/) |
| Midjourney | undisclosed diffusion | undisclosed | undisclosed | [[48]](https://ucstrategies.com/news/midjourney-v6-photorealism-specs-pricing-discord-workflow-2026/) |

⚠ **Midjourney remains a closed box** — a proprietary diffusion service tuned heavily for aesthetics, with no published architecture; any specifics about its internals are speculation [[48]](https://ucstrategies.com/news/midjourney-v6-photorealism-specs-pricing-discord-workflow-2026/). [FLUX.1 Krea](https://bfl.ai/blog/flux-1-krea-dev) (July 2025) is a useful public reference for where production is heading: a rectified-flow transformer explicitly targeting de-saturated photorealism over the over-saturated "AI look" [[42]](https://bfl.ai/blog/flux-1-krea-dev).

On the **efficiency** axis, the action is distillation: knowledge, progressive, consistency, score, and adversarial distillation collapse sampling to 1–4 steps, where training-free samplers still need 10+ [[46]](https://arxiv.org/html/2510.08431v1). Latent Consistency Models predict the PF-ODE solution in latent space for 2–4 steps; SDXL-Turbo uses adversarial+score distillation for a single step; SDXL-Lightning uses progressive adversarial distillation [[47]](https://arxiv.org/html/2406.05768v2/). The forward edge is **unified multimodal / autoregressive** generation — GPT Image, HunyuanImage, Transfusion — with hybrid AR+diffusion transformers blending sequence modeling and diffusion objectives [[50]](https://arxiv.org/pdf/2506.07999).

**Bottom line for the prompt engineer:** the model that turns your prompt into pixels is a score network — a noise/velocity predictor wrapped in a U-Net or (increasingly) a transformer — whose `guidance_scale` knob literally scales how hard the combined conditional-minus-unconditional score pulls the sample toward your words [[38]](https://arxiv.org/abs/2207.12598)[[39]](https://huggingface.co/docs/diffusers/en/using-diffusers/conditional_image_generation).
