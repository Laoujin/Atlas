Score network foundations: score function, denoising score matching, Tweedie's formula, and the equivalence between the score, noise (epsilon) prediction, and the reverse-time SDE/ODE.
The U-Net denoiser: encoder-decoder with skip connections, residual blocks, self/cross-attention, timestep embeddings, and why it became the dominant diffusion backbone (ADM, Stable Diffusion).
Diffusion Transformers (DiT, SiT, MMDiT): patchify, adaLN-zero conditioning, scaling behaviour, and adoption in SD3, FLUX, Sora, PixArt.
Prediction parametrizations and training targets: epsilon vs x0 vs v-prediction vs flow-matching velocity, loss weighting, and how each maps to the score.
Conditioning the score network: cross-attention text injection, adaLN, classifier-free guidance, and latent diffusion (VAE compression).
State of the art and trade-offs in 2026: U-Net vs transformer backbones, production architectures (FLUX, SD3.5, Imagen, etc.), efficiency, and where the field is heading.
