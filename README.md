# Atlas

The publishing target for [Scout](https://github.com/Laoujin/Scout) — a Jekyll site, served by GitHub Pages, themed via [Compass](https://github.com/Laoujin/Compass). Each research run lands here as a folder under `research/<date>-<slug>/`; GitHub Pages rebuilds and the post is live at your `github.io` URL.

This repo is the **template**. You don't run Scout from here — you fork Scout, the installer creates *your* Atlas (a clone of this), and Scout pushes research into it.

## The three repos

|         | What it is              | You touch it when                                              |
|---------|-------------------------|----------------------------------------------------------------|
| Scout   | Research runner         | Installing, updating the runner, tuning skills                 |
| Atlas   | Your published site     | Tweaking `_config.yml` (theme, title) — Scout writes the rest  |
| Compass | Jekyll theme (submodule)| Customising layout, palette, or card style                     |

## Get your own Atlas

The Scout installer creates it for you:

```bash
curl -fsSL https://raw.githubusercontent.com/Laoujin/Scout/main/install.sh \
  | bash -s -- --config=s5.cartography.v1
```

See [Scout's README](https://github.com/Laoujin/Scout) for the full flow. The installer forks Scout, scaffolds *your* Atlas with an empty `research/` and Compass as a submodule, generates a deploy key, and enables GitHub Pages.

## Theme it

Three knobs in `_config.yml` — push, GitHub Pages rebuilds:

```yaml
skeleton: s5            # site layout: s1..s6
palette:  cartography   # rust paper cartography midnight minimal fieldnotes solarized nord
card:     v1            # research-card variant: v1..v7
```

Preview every variant before committing via Compass's `serve.ps1` — see [Compass README](https://github.com/Laoujin/Compass).

[Pick visually](https://laoujin.github.io/Scout/#your-atlas) if you'd rather see them side-by-side.

## Layout

```txt
_config.yml         theme + repo wiring (skeleton/palette/card, baseurl, scout_repo)
index.html          home — lists everything in research/
research/           one folder per run: index.md, index.html, citations.jsonl, cover.svg
compass/            theme submodule — layouts, includes, palettes, card variants
```

Each research folder has both `index.md` (the source Scout wrote) and `index.html` (Jekyll's render — the live page). The `.md` is what the "Raw" link in the page footer points at.

## Bump the theme

When Compass ships layout changes:

```bash
git submodule update --remote compass
git commit -am "bump compass"
git push
```

## Preview locally

```bash
bundle install
bundle exec jekyll serve
```

Or Docker (no local Ruby):

```bash
docker run --rm -p 4000:4000 -v "$PWD:/srv/jekyll" jekyll/jekyll:4 jekyll serve --host 0.0.0.0
```

Open <http://localhost:4000/Atlas/>. The `baseurl` is `/Atlas` to match deployed project Pages — change `_config.yml` if you serve from root.
