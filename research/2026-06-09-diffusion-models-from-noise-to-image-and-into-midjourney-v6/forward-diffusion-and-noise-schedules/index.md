---
title: "Forward Diffusion and Noise Schedules"
date: 2026-06-09
depth: standard
format: md
topic: "Forward diffusion and noise schedules"
topic_raw: "Forward diffusion and noise schedules"
issue: 210
tags: [diffusion-models, machine-learning, generative-ai, noise-schedules, ddpm, score-matching]
summary: "How the forward diffusion process works mathematically, and how the choice of noise schedule — linear, cosine, EDM σ, or Laplace — shapes training quality, resolution behaviour, and what not to get wrong."
citations: 16
reading_time_min: 6
cover: cover.svg
model: "Sonnet 4.6"
cost_usd: 1.48
duration_sec: 587
model: "Sonnet 4.6"
---

> **TL;DR** Use **cosine** for ≤256px generation; switch to EDM's **σ-schedule** (Karras, NeurIPS 2022) for continuous-time high-quality training. Enforce **zero terminal SNR** — every common off-the-shelf schedule violates it [[5]](https://arxiv.org/abs/2305.08891). Scale the schedule (or just the input) toward more noise as resolution grows: the same cosine schedule that works at 64px will under-noise a 512px image [[4]](https://arxiv.org/abs/2301.10972).

## The Forward Process

[DDPM](https://arxiv.org/abs/2006.11239) (Ho et al., 2020) defines the forward process as a **fixed Markov chain** that progressively destroys data by adding Gaussian noise at each step [[1]](https://arxiv.org/abs/2006.11239):

```
q(x_t | x_{t-1}) = N(x_t ; sqrt(1-β_t) x_{t-1}, β_t I)
```

Because consecutive Gaussian steps compose analytically, the process has a **closed-form marginal** — you can corrupt a clean image x₀ directly to any timestep t without simulating intermediate steps [[1]](https://arxiv.org/abs/2006.11239):

```
q(x_t | x_0) = N(x_t ; sqrt(ᾱ_t) x_0, (1-ᾱ_t) I)
x_t = sqrt(ᾱ_t) · x_0 + sqrt(1-ᾱ_t) · ε,   ε ~ N(0, I)
```

where α_t = 1 − β_t and ᾱ_t = ∏_{s=1}^{t} α_s. This reparameterized sampling form is the core of training: at each gradient step the model samples a random t, corrupts x_0 into x_t using the closed form, and learns to predict ε.

## Key Derived Quantities

Everything about the forward process reduces to how ᾱ_t evolves over time:

| Symbol            | Definition                  | Role                                  |
| :---------------- | :-------------------------- | :------------------------------------ |
| β_t               | noise variance at step t    | schedule parameter                    |
| α_t = 1−β_t       | per-step signal retention   | intermediate                          |
| ᾱ_t = ∏ α_s       | cumulative signal weight    | governs q(x_t\|x_0)                   |
| SNR(t) = ᾱ_t/(1−ᾱ_t) | signal-to-noise ratio   | natural timescale [[4]](https://arxiv.org/abs/2301.10972) |
| log-SNR(t)        | log of SNR(t)               | key training distribution axis [[7]](https://arxiv.org/abs/2407.03297) |

The SNR decreases monotonically from high (near-clean data at t=0) to near-zero (near-pure noise at t=T). Choosing a noise schedule is exactly choosing **how fast** this descent happens.

## Schedule Families

### Linear (Ho 2020)

The original DDPM linearly interpolates β_t from β₁=10⁻⁴ to β_T=0.02 over T=1000 steps [[1]](https://arxiv.org/abs/2006.11239):

```
β_t = β_1 + ((t-1)/(T-1)) · (β_T - β_1)
```

Simple and cheap, but aggressive: the ᾱ_t curve drops steeply, making images nearly indistinguishable from pure noise by roughly t=600. This wastes ~40% of training capacity on near-trivial denoising and produces non-zero terminal SNR [[5]](https://arxiv.org/abs/2305.08891). For low-resolution images (32px), the linear schedule pushes data to pure noise too quickly [[10]](https://milvus.io/ai-quick-reference/what-role-does-the-noise-schedule-play-in-a-diffusion-model).

### Cosine (Nichol & Dhariwal, 2021)

Introduced in [Improved DDPM](https://arxiv.org/abs/2102.09672) to fix aggressive early noise. ᾱ_t is defined directly as a squared cosine [[2]](https://arxiv.org/abs/2102.09672) [[9]](https://www.zainnasir.com/blog/cosine-beta-schedule-for-denoising-diffusion-models/):

```
f(t) = cos²( π/2 · (t/T + s) / (1 + s) )
ᾱ_t  = f(t) / f(0)
β_t  = 1 - ᾱ_t / ᾱ_{t-1},  clipped ≤ 0.999
```

Offset s=0.008 keeps √β_t below the 1/127.5 pixel bin size, preventing information loss from overlapping noise intervals [[9]](https://www.zainnasir.com/blog/cosine-beta-schedule-for-denoising-diffusion-models/). The result: noise is added slowly at the start (letting the model learn coarse structure first), accelerates through the middle, and tapers near t=T — producing more consistent gradient signal at all timesteps [[2]](https://arxiv.org/abs/2102.09672).

### Sigmoid

For high-resolution images, the sigmoid schedule applies smoother transitions [[8]](https://arxiv.org/abs/2502.04669) [[11]](https://www.analyticsvidhya.com/blog/2024/07/noise-schedules-in-stable-diffusion/). Higher-resolution images contain greater pixel-level redundancy — neighbouring pixels carry correlated information — making the denoising task inherently easier at identical noise levels. The sigmoid schedule's gradual S-shaped curve avoids abrupt mid-process transitions that destabilise high-res training. As resolution grows, the sigmoid outperforms cosine on stability [[8]](https://arxiv.org/abs/2502.04669).

### EDM σ-schedule (Karras et al., NeurIPS 2022)

[Elucidating the Design Space of Diffusion-Based Generative Models](https://arxiv.org/abs/2206.00364) (EDM) abandons the ᾱ_t parameterisation entirely, working directly in noise standard deviation σ [[6]](https://arxiv.org/abs/2206.00364). This decouples network preconditioning from the schedule.

Inference schedule uses a **ρ-polynomial interpolation** [[13]](https://huggingface.co/docs/diffusers/en/api/schedulers/edm_euler):

```
σ_i = (σ_max^(1/ρ) + (i/(T-1)) · (σ_min^(1/ρ) - σ_max^(1/ρ)))^ρ
```

Default parameters: σ_min=0.002, σ_max=80, ρ=7. For **training**, noise levels are drawn from a lognormal distribution P_train(σ) = LogNormal(P_mean=−1.2, P_std=1.2) rather than uniformly over discrete steps — concentrating learning on the informationally critical mid-noise region. EDM achieves FID 1.79 on CIFAR-10 (class-conditional) with 35 network evaluations [[6]](https://arxiv.org/abs/2206.00364).

### Laplace/Cauchy (Hang et al., 2024)

[Improved Noise Schedule for Diffusion Training](https://arxiv.org/abs/2407.03297) formalises the principle behind EDM's training distribution [[7]](https://arxiv.org/abs/2407.03297). Key insight: **importance sampling of log-SNR is mathematically equivalent to changing the schedule**. The critical region is **log-SNR ≈ 0** — where signal and noise energy are balanced — and concentrating training there maximises learning efficiency.

Schedules derived from target log-SNR distributions:

- **Laplace**: p(λ) = exp(−|λ−μ|/b) / (2b) — sharp peak at chosen log-SNR
- **Cauchy**: 1/π · γ/((λ−μ)²+γ²) — heavier tails for broader coverage

On ImageNet-256 with 500K iterations, Laplace achieves FID 7.96 vs cosine baseline 10.85 — **26.6% improvement** — at identical compute and architecture [[7]](https://arxiv.org/abs/2407.03297).

## Schedule Comparison

| Schedule    | Year | Key property                          | Known limitation                           |
| :---------- | :--- | :------------------------------------ | :----------------------------------------- |
| **Linear**  | 2020 | Simple; baseline                      | Aggressive; non-zero terminal SNR; bad at low-res |
| **Cosine**  | 2021 | Smooth; consistent signal across steps | Non-zero terminal SNR; under-noises at high-res |
| **Sigmoid** | 2022 | High-res stability; gradual transitions | Less adoption; application-specific tuning |
| **EDM σ**   | 2022 | Principled σ-parameterisation; SOTA FID | Different parameterisation from ᾱ-based models |
| **Laplace** | 2024 | Theoretically motivated; best FID     | Not yet default in major frameworks        |

## Resolution and Scale Dependence

Chen (2023) [[4]](https://arxiv.org/abs/2301.10972) [[14]](https://ar5iv.labs.arxiv.org/html/2301.10972) demonstrates that the **optimal schedule shifts toward noisier levels as resolution increases**. At 256×256 the cosine schedule works well; at 1024×1024 the same schedule systematically under-noises images, producing an undertrained high-noise regime.

Practical fix: rather than redesigning the schedule per resolution, **scale the input data by factor b** and keep the schedule fixed. This shifts the entire log-SNR curve uniformly downward (more noise relative to signal) — a single-parameter adjustment sufficient for single-stage generation up to 1024×1024 [[4]](https://arxiv.org/abs/2301.10972).

## The Terminal SNR Flaw

Lin et al. (WACV 2024) [[5]](https://arxiv.org/abs/2305.08891) identify a critical bug: **no standard off-the-shelf schedule achieves SNR(T) = 0**. At the final timestep t=T, the noised sample still contains residual signal. But at inference, the sampler starts from pure Gaussian noise — a condition the model was never trained on.

Consequences:

- ⚠ Stable Diffusion cannot generate very bright or very dark images — restricted to medium brightness [[5]](https://arxiv.org/abs/2305.08891)
- ⚠ Training/inference mismatch degrades sample quality across all resolutions [[15]](https://openaccess.thecvf.com/content/WACV2024/html/Lin_Common_Diffusion_Noise_Schedules_and_Sample_Steps_Are_Flawed_WACV_2024_paper.html)

**Fixes [[5]](https://arxiv.org/abs/2305.08891):**

1. Rescale β schedule to enforce SNR(T) = 0 exactly
2. Switch from ε-prediction to **v-prediction**
3. Ensure sampler always initiates from the true final timestep
4. Rescale classifier-free guidance to prevent overexposure in early steps

## VE vs VP: The SDE View

Song et al. (2021) [[3]](https://arxiv.org/abs/2011.13456) unified DDPM and SMLD as discretisations of two continuous-time SDE families [[12]](https://fanpu.io/blog/2023/score-based-diffusion-models/):

**Variance Preserving (VP-SDE)** — DDPM's continuous limit:

```
dx = -½β(t) x dt + sqrt(β(t)) dw
```

The drift term prevents variance from exploding; all ᾱ_t-based schedules (linear, cosine, sigmoid) belong to this family.

**Variance Exploding (VE-SDE)** — SMLD's continuous limit:

```
dx = sqrt(dσ²(t)/dt) dw
```

No drift; variance grows to infinity. EDM's σ_max=80 approximates this regime — the distribution at maximum noise is effectively Gaussian [[6]](https://arxiv.org/abs/2206.00364).

Both families admit a **reverse-time SDE** solvable with the score function ∇_x log p(x_t), providing a unified generative mechanism [[3]](https://arxiv.org/abs/2011.13456).

## Flow Matching: A Parallel Track

Flow matching (Lipman et al., 2022) bypasses the noise schedule entirely by learning a **velocity field** that maps noise to data via straight paths. Models including Stable Diffusion 3 and FLUX adopt rectified flow.

Key tradeoff [[16]](https://metricgate.com/blogs/flow-matching-vs-diffusion-models/): with 5–10 inference steps, rectified flow matches DDPM quality at 50+ steps. For training, flow matching defaults to a **uniform distribution in log-SNR space** — equivalent to a specific schedule choice, empirically robust across resolutions. Rectified flow achieves better FID and CLIP score than rectified flow at equivalent step counts after path straightening.

## Practical Guidance

- **Start with cosine** for ≤256px tasks; linear is strictly worse for identical compute.
- **Enforce zero terminal SNR** on any new training run — it is a free correctness fix that unblocks the full brightness range.
- **Use EDM or Laplace** when designing training from scratch; Laplace's 26% FID gain costs only a different schedule function.
- **Scale the input, not the schedule** when increasing resolution; the b-scaling fix is a one-line change that handles 1024px.
- **Track log-SNR, not t** when debugging: the nominal timestep is an arbitrary proxy; the actual quantity that controls learning difficulty is the signal-to-noise ratio.
