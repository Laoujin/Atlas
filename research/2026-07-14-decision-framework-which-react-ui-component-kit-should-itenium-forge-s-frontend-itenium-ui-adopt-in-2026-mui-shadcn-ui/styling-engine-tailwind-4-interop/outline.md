# Outline — styling engine & Tailwind 4 interop (deep child angle)

1. MUI's styling engine in 2026: Emotion runtime CSS-in-JS status, Pigment CSS (zero-runtime) — shipped, stalled, or abandoned? What did MUI ship instead (v7/v8, CSS layers, Base UI)?
2. Documented pain of MUI + Tailwind together: specificity wars, CSS injection order (StyledEngineProvider), `important` config, CssVarsProvider / CSS variables story, real GitHub issues and forum reports.
3. shadcn/ui as native Tailwind: copy-in registry, cn()/tailwind-merge/class-variance-authority, and how Tailwind 4's CSS-first `@theme` changed setup (v4 migration, canary, breakages).
4. Mantine's CSS-modules + PostCSS model: does it coexist cleanly with Tailwind 4? PostCSS pipeline conflicts, preflight/reset collisions, real-world configs.
5. Base UI 1.0: fully unstyled primitives — what styling work it leaves you, how it pairs with Tailwind 4, data-attribute state styling, and its relationship to MUI/Radix.
6. Cascade mechanics that decide it: Tailwind 4's `@layer theme, base, components, utilities`, where each kit's CSS lands in the layer stack, preflight vs kit resets, runtime-vs-build-time cost, and `@tailwindcss/vite` wiring in a Vite/Nx setup.
