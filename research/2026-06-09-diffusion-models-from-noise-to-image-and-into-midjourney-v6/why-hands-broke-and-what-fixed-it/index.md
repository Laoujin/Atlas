---
title: "Why AI hands broke — and what fixed them"
date: 2026-06-09
depth: standard
format: md
topic: "Why hands broke — and what fixed it"
topic_raw: "Why hands broke — and what fixed it"
issue: 210
tags: [diffusion-models, midjourney, stable-diffusion, FLUX, anatomy, training-data, hands, ControlNet]
summary: "A technical post-mortem on why diffusion models generated malformed hands for years — sparse training data, CLIP counting blindness, VAE resolution limits, U-Net locality, and mode-interpolation — plus the layered fixes that pushed success rates from ~30% to ~90% by 2025."
citations: 21
reading_time_min: 7
cover: cover.svg
cost_usd: 1.70
duration_sec: 626
model: "Sonnet 4.6"
---

> **TL;DR** Hands broke because of five compounding failures: sparse training data, CLIP's inability to count, U-Net locality, VAE resolution bottlenecks, and denoising mode-interpolation. No single fix worked; improvement came by stacking better data curation, higher resolution, transformer attention, and specialized conditioning. The two biggest inflection points were Midjourney v5 (March 2023) and FLUX.1 (August 2024). [[1]](https://petapixel.com/2023/03/02/why-ai-image-generators-cant-get-hands-right/) [[18]](https://vertu.com/ai-tools/the-2025-reality-check-on-ai-generated-hands-and-fingers/)

---

## Why hands were uniquely hard

Hands aren't just a difficult anatomical target — they're a confluence of *every* failure mode diffusion models have:

- **Underrepresented in training data.** Faces dominate internet photos. Hands are small, peripheral, or obscured. Stability AI acknowledged that "within AI datasets, human images display hands less visibly than they do faces," with hands "relatively rarely visible in large form." [[1]](https://petapixel.com/2023/03/02/why-ai-image-generators-cant-get-hands-right/) [[2]](https://www.buzzfeednews.com/article/pranavdixit/ai-generated-art-hands-fingers-messed-up)
- **Captions don't describe them.** The LAION-5B dataset — 5.85 billion training images — contains captions that almost never describe hand anatomy. An image tagged "man smiling in park" provides zero signal about finger count or pose. [[4]](https://decrypt.co/125865/generative-ai-art-images-hands-fingers-teeth)
- **Kinematic complexity.** A human hand has 27 degrees of freedom across 16 joints. [[5]](https://arxiv.org/html/2311.17957v2) That's an enormous pose space relative to any other body part, with tiny errors in finger angle producing obviously wrong results.
- **Constant occlusion.** Hands routinely disappear behind objects, fabric, or each other. When a model sees thousands of images with partially-hidden thumbs, it learns "thumbs are sometimes absent" rather than "thumbs are hidden." [[2]](https://www.buzzfeednews.com/article/pranavdixit/ai-generated-art-hands-fingers-messed-up) [[3]](https://www.sciencefocus.com/future-technology/why-ai-generated-hands-are-the-stuff-of-nightmares-explained-by-a-scientist)
- **Humans notice immediately.** Unlike deformities in backgrounds or objects, malformed hands fall squarely in the uncanny valley. We evolved to read hands for social signaling; the visual system flags any abnormality instantly. [[4]](https://decrypt.co/125865/generative-ai-art-images-hands-fingers-teeth)

---

## The five technical failure modes

### 1. CLIP can't count

The text encoder translating "five fingers" into a vector doesn't represent cardinality reliably. CLIP operates on continuous embeddings — there's no discrete mechanism for "exactly five." Research treats any generated hand with ≥6 fingers as a counting hallucination; early SD models triggered this routinely. [[7]](https://arxiv.org/html/2510.13080v1) The deeper problem: models couldn't associate gesture-language ("thumbs up", "open palm") with correct visual structure because text-image alignment in LAION captions was weak for body-part specifics. [[8]](https://arxiv.org/html/2408.15461v2)

### 2. VAE resolution bottleneck

Early Stable Diffusion operated at 512×512 in pixel space — compressed 8× into a 64×64 latent grid. At that scale, four fingers on a normally-sized hand fit into roughly 5–8 latent pixels. The VAE decoder is responsible for painting fine detail back, but it can't recover what was never encoded. [[15]](https://www.makeuseof.com/ai-image-generators-hands-issue/) Fused and blobby digits are the direct output of a decoder trying to reconstruct a hand from ambiguous latent patches.

### 3. U-Net locality

The U-Net backbone processes images through successive downsampling and upsampling steps. Each layer has a limited receptive field. Fingers are spatially correlated — they connect to the same palm and maintain relative ordering — but U-Net's local attention often treats each finger region independently, losing the global constraint that the hand must be anatomically consistent. [[12]](https://zsky.ai/blog/flux-vs-sdxl-comparison)

### 4. Mode interpolation in denoising

During reverse diffusion, the model interpolates between learned data modes. Hands appear in countless orientations in training — open, fisted, gripping, pointing. When the denoising process samples between incompatible hand-pose modes, the output is physically impossible: joints bent backwards, fingers merged, extra digits. This is mode interpolation hallucination: "samples lie between incompatible modes, producing semantically invalid content." [[7]](https://arxiv.org/html/2510.13080v1) Counterintuitively, increasing sampling steps (25→100) *worsens* counting accuracy for hands — more refinement steps amplify mode-interpolation errors rather than correcting them. [[7]](https://arxiv.org/html/2510.13080v1)

### 5. 3D projection ambiguity

Two fingers can be visually identical when one is behind the other — the model has no depth signal to resolve the ambiguity. Prof. Peter Bentley (UCL): "These are 2D image generators that have absolutely no concept of the three-dimensional geometry of something like a hand." [[3]](https://www.sciencefocus.com/future-technology/why-ai-generated-hands-are-the-stuff-of-nightmares-explained-by-a-scientist) The HandRefiner paper formalizes this as "3D-to-2D projection ambiguity": occlusions from varying viewpoints make it impossible for a pure pixel-space model to determine finger ordering or count. [[5]](https://arxiv.org/html/2311.17957v2)

---

## What actually fixed it

No single intervention was sufficient. Improvement came from stacking multiple changes at different layers of the pipeline.

### Better training data (Midjourney v5, March 2023)

Midjourney's most impactful early fix was data curation: they explicitly prioritized images with clearly visible hands and deprioritized images where hands are obscured or peripheral. [[14]](https://www.britannica.com/topic/Why-does-AI-art-screw-up-hands-and-fingers-2230501) Combined with a new neural architecture trained on Google Cloud's AI supercluster for ~5 months, MJ v5 drove correct finger counts to "most of the time" — nearly doubling the acceptable-generation rate from ~30% to ~65%. [[16]](https://en.wikipedia.org/wiki/Midjourney) [[19]](https://deep-image.ai/blog/midjourney-v5-is-now-available-check-out-the-changes-from-v4/) [[18]](https://vertu.com/ai-tools/the-2025-reality-check-on-ai-generated-hands-and-fingers/)

### Richer captions (DALL-E 3, late 2023)

OpenAI attacked the caption problem directly. DALL-E 3 trained a specialized captioner using a two-phase fine-tuning strategy: short captions first, then long highly-descriptive captions covering "surroundings, background, coloration, styles" — including body part details. Final training mixed 95% synthetic captions (GPT-4 generated) with 5% human captions to prevent stylistic overfitting. [[10]](https://shreyansh26.github.io/post/2024-02-18_dalle3_image_recaptioner/) Better captions mean the model gets explicit signal about hand positions rather than inferring them from scene context.

### Higher resolution + dual encoders (SDXL, 2023)

Stable Diffusion XL shipped with a 1024×1024 native resolution — 4× the pixel count of SD 1.5. At 1024px, five fingers on a mid-frame hand get ~40–60 latent pixels each in the 128×128 latent grid, enough for the VAE to encode and recover distinct digits. [[11]](https://magai.co/stable-diffusion-xl-1-0/) [[20]](https://d-central.tech/ai/model/stable-diffusion-xl/) SDXL also introduced dual text encoders (OpenCLIP ViT-bigG + CLIP ViT-L in parallel), providing richer semantic representation for complex prompts. The U-Net itself grew from 860M to 2.6B parameters, enabling more nuanced feature extraction. [[11]](https://magai.co/stable-diffusion-xl-1-0/)

### Transformer attention (FLUX.1, August 2024)

The architectural shift most directly targeting U-Net locality was replacing U-Net with a Multimodal Diffusion Transformer (MMDiT) — the core innovation of FLUX.1 (Black Forest Labs). Transformers compute attention across the *entire* image in every layer, not just local patches. This means a finger at one image position is explicitly related to the palm and every other finger simultaneously. [[12]](https://zsky.ai/blog/flux-vs-sdxl-comparison) [[13]](https://www.ikomia.ai/blog/best-ai-diffusion-models-comparison-guide) The result: FLUX.1 produces "the most anatomically correct humans, with hands significantly improved, with correct finger count in the vast majority of generations." [[13]](https://www.ikomia.ai/blog/best-ai-diffusion-models-comparison-guide)

### Depth-conditioned inpainting (HandRefiner / ControlNet)

For reliable results without waiting for model updates, the community developed a ControlNet-based pipeline. [ControlNet](https://github.com/lllyasviel/controlnet) ⭐ 33.9k [[9]](https://github.com/lllyasviel/controlnet) adds structural control signals (depth maps, pose maps, edge maps) to generation without retraining the base model. HandRefiner extends this: it reconstructs anatomically correct hand geometry via Mesh Graphormer, renders a depth map, then uses a depth-conditioned ControlNet to inpaint only the hand region while preserving the rest of the image. [[5]](https://arxiv.org/html/2311.17957v2) Results: 70% of rectified images preferred in blind user surveys (50 participants); FID improves 10+ points on hand-only evaluation. [[5]](https://arxiv.org/html/2311.17957v2) A key discovery: control strength ~0.55 is a "phase transition" point — below it, the signal adjusts structure; above it, texture degrades. This enabled training on synthetic depth data without texture artifacts. [[5]](https://arxiv.org/html/2311.17957v2)

### Ground-up model rebuilds (Midjourney v6/v7)

Midjourney v6 (December 2023) was "trained from scratch over a nine-month period" — not an incremental fine-tune of v5. [[16]](https://en.wikipedia.org/wiki/Midjourney) The full rebuild enabled better text rendering, prompt fidelity, and anatomy. Midjourney v7 (April 2025) went further: CEO David Holz described it as "a totally different architecture." [[21]](https://theaitrack.com/midjourney-v7-launch/) Third-party analysis reports a ~40% reduction in anatomical errors, with six-fingered hands moving from "common" to "occasional." [[17]](https://mpgone.com/midjourney-v7-redefining-ai-image-generation-with-personalized-realism/)

### Pixel-level constraints (research)

Academic work pushed beyond ControlNet conditioning. [Hand1000](https://arxiv.org/html/2408.15461v2) fuses Mediapipe gesture features directly into the text embedding before generation — requiring only 1,000 training images per gesture, achieving a 28.6-point FID-H improvement over baseline SD. [[8]](https://arxiv.org/html/2408.15461v2) The Joint Diffusion Model approach adds hand segmentation masks as pixel-level constraints, reducing counting hallucination rate by ~23% and non-counting failures by ~84%. [[7]](https://arxiv.org/html/2510.13080v1) A multi-task learning approach (predicting both noise and segmentation mask simultaneously) achieved a 40% MPJPE reduction on hand keypoints — 92.3% improvement in hand pose accuracy. [[6]](https://arxiv.org/html/2403.10731)

---

## Progress timeline

| Year     | Milestone                      | Est. success rate† | Key change                            |
|----------|--------------------------------|--------------------|---------------------------------------|
| 2022     | SD 1.4/1.5, MJ v3/v4          | ~30%               | Baseline                              |
| Mar 2023 | Midjourney v5                  | ~65%               | Hand-prioritized data, new arch       |
| Oct 2023 | SDXL 1.0                       | ~70%               | 1024px native res, dual encoders      |
| Dec 2023 | MJ v6, DALL-E 3                | ~75–80%            | Full retrains, GPT-4 recaptioning     |
| Aug 2024 | FLUX.1 [dev]                   | ~85%               | MMDiT transformer, global attention   |
| Apr 2025 | Midjourney v7                  | ~85–90%            | New architecture, ~40% fewer errors   |

†Acceptable five-finger anatomy rate, per [[18]](https://vertu.com/ai-tools/the-2025-reality-check-on-ai-generated-hands-and-fingers/).

---

## What still breaks (2025–2026)

Even with these advances, edge cases remain stubborn:

- **Hand-object interactions.** Gripping a textured object, hands wrapped around a tool — the model must reason about physical contact, not just anatomy. [[6]](https://arxiv.org/html/2403.10731)
- **Multi-hand scenes.** Two people shaking hands, or hands overlapping, multiply the projection-ambiguity problem.
- **Unusual poses.** Fingers spread wide from a low angle, or hands partially in a fist, hit training-distribution edges.
- **Data mismatch.** Datasets focused on isolated hands don't generalize to in-context generation where hands connect to arms, hold objects, or interact with environments. [[6]](https://arxiv.org/html/2403.10731)

The hardest remaining case is hands that require physical reasoning — understanding how fingers wrap around objects or interact with other hands. That needs 3D-aware generation, not just better 2D statistics. [[3]](https://www.sciencefocus.com/future-technology/why-ai-generated-hands-are-the-stuff-of-nightmares-explained-by-a-scientist)

**Practical takeaway for Midjourney/FLUX users:** simple natural poses now generate reliably. For complex grip shots or multi-hand compositions, ControlNet conditioning or iterative inpainting remains the most reliable path until the next architectural leap.
