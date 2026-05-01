---
title: "Obsidian 2026: low-friction capture and AI-assisted backfill"
date: 2026-04-30
depth: deep
format: md
topic: "Low-friction capture & AI-assisted backfill"
topic_raw: "Low-friction capture & AI-assisted backfill"
issue: 49
tags: [obsidian, pkm, capture, ai, plugins, voice, mobile, ollama]
summary: "How to lower capture friction across desktop, mobile, web, voice — and how to run AI tag/metadata backfill across an existing vault in 2026."
citations: 80
reading_time_min: 13
cover: cover.svg
cost_usd: 7.65
duration_sec: 701
---

> **Decision.** In-Obsidian capture: **QuickAdd + Templater + daily-note inbox** is still the dominant 2026 combo [[1]](https://github.com/chhoumann/quickadd) [[3]](https://github.com/SilentVoid13/Templater) [[12]](https://www.obsibrain.com/blog/obsidian-daily-notes-documentation). Mobile: native Obsidian shipped widgets + Share extension + Siri capture in v1.11/1.12 [[13]](https://obsidian.md/changelog/2026-02-27-mobile-v1.12.4/) [[14]](https://obsidian.md/changelog/2026-01-12-mobile-v1.11.4/), but cold-start latency still pushes iOS power users to **Drafts** [[19]](https://thesweetsetup.com/quick-capture-to-obsidian-using-drafts/) or **Actions for Obsidian** [[17]](https://apps.apple.com/us/app/actions-for-obsidian/id1659667937) as the front-end. Web: the official **Obsidian Web Clipper** ⭐ 4.1k has replaced Omnivore, MarkDownload, and most third-party clippers [[25]](https://github.com/obsidianmd/obsidian-clipper) [[28]](https://forum.obsidian.md/t/replacing-omnivore-with-obsidian-web-clipper-available-at-firefox-chrome-add-on-store/90927). Backfill: **AI Tagger Universe** ⭐ 84 is the clearest fit for batch tag/frontmatter generation over an existing vault [[53]](https://github.com/niehu2018/obsidian-ai-tagger-universe) [[61]](https://www.makeuseof.com/letting-local-llm-organize-obsidian-notes/); run it locally via Ollama (`nomic-embed-text` for embeddings, Llama 3.1 8B or Qwen 2.5 32B for generation) for zero per-token cost and full privacy [[66]](https://github.com/logancyang/obsidian-copilot/blob/master/local_copilot.md) [[69]](https://localaimaster.com/blog/best-ollama-models). Voice: Apple Voice Memos on-device transcription for short captures [[49]](https://www.plaud.ai/blogs/news/how-to-transcribe-iphone-voice-memos), nikdanilov's Whisper plugin ⭐ 350 for anything longer [[42]](https://github.com/nikdanilov/whisper-obsidian-plugin).

## 1. In-Obsidian quick capture

The 2026 baseline is unchanged from 2024: today's daily note is the inbox, processing happens at review time, and capture is one hotkey away [[12]](https://www.obsibrain.com/blog/obsidian-daily-notes-documentation). What changed is that the two plugins doing the work are both still actively maintained and explicitly complementary.

| Plugin | ⭐ Stars | Latest release | Role |
|---|---|---|---|
| [QuickAdd](https://github.com/chhoumann/quickadd) (chhoumann) | ⭐ 2.2k | v2.12.0 (Mar 5 2026) | Capture/Template/Macro/Multi *choices* — the menu and routing layer [[1]](https://github.com/chhoumann/quickadd) |
| [Templater](https://github.com/SilentVoid13/Templater) (SilentVoid13) | ⭐ 4.9k | v2.20.0 (Apr 29 2026) | Dynamic variables, JS execution, per-template hotkeys [[3]](https://github.com/SilentVoid13/Templater) [[4]](https://silentvoid13.github.io/Templater/settings.html) |
| [Periodic Notes](https://github.com/liamcain/obsidian-periodic-notes) (liamcain) | ⭐ 1.3k | v1.0.0-beta.3 (Apr 2022) ⚠ | Daily/weekly/monthly notes — widely treated as unmaintained [[5]](https://github.com/liamcain/obsidian-periodic-notes) |
| Journals (srg-kostyrko) | — | actively maintained | The 2025/2026 Periodic Notes replacement; daily→yearly + interval journals; bulk import [[6]](https://forum.obsidian.md/t/plugin-journals/76946) |
| [Thino](https://github.com/Quorafind/Obsidian-Thino) (Quorafind) | ⭐ 1.3k | v3.0.10 (Apr 2026) | Twitter-style timestamped capture; ⚠ closed-source from v2.0.0 with paid pro [[11]](https://github.com/Quorafind/Obsidian-Thino) |

QuickAdd's *Capture* choice is the primitive — it appends or prepends formatted text to a predefined target file (typically today's daily note under a heading) on a hotkey [[2]](https://quickadd.obsidian.guide/docs/Choices/CaptureChoice/). QuickAdd's *Template* choice creates a new note from a Templater template in a chosen folder [[7]](https://www.dsebastien.net/the-must-have-obsidian-plugins-for-2026/). The two plugins do not compete: QuickAdd handles menu/prompt/routing, Templater handles dynamic variables and JS [[7]](https://www.dsebastien.net/the-must-have-obsidian-plugins-for-2026/).

**System-wide capture hotkey.** Obsidian's own hotkeys only fire when Obsidian has focus. The dominant 2026 wirings:

- **Cross-platform:** QuickAdd + the Global Hotkeys community plugin (Ctrl+Alt+A is a common binding) [[8]](https://obsidian.rocks/obsidian-quick-capture/).
- **Windows:** [AutoHotkey](https://www.autohotkey.com/) script bound to Ctrl+Alt+V activates Obsidian (or launches it) and forwards Ctrl+Alt+C into QuickAdd's capture window [[9]](https://forum.obsidian.md/t/global-hotkey-to-launch-obsidian-and-open-quickadd-capture-window-using-autohotkey-script/22626).
- **macOS:** Alfred/Raycast workflows launching the same QuickAdd capture-choice URI [[8]](https://obsidian.rocks/obsidian-quick-capture/).

**Inbox-processing pattern.** A widely-shared workflow combines Advanced URI + Templater + Hotkeys for Templates with `Opt+A`/`Opt+D`/`Opt+M` to archive, trash, or move each captured fleeting note during a daily review pass [[10]](https://forum.obsidian.md/t/quick-capture-mac-ios-and-inbox-processing/21808). The principle: capture is dumb and fast, processing is concentrated.

## 2. Mobile capture

The headline 2026 shift is that Obsidian Mobile finally shipped first-party capture surfaces — but architectural friction remains.

**Native, shipped:**

- **Mobile 1.11 (Jan 2026):** iOS Lock Screen / Control Center / Home Screen widgets, Android home-screen widgets and Quick Settings Tile, Siri "Capture using Obsidian", and a "Capture to a note" Shortcut that appends or prepends without launching the app [[14]](https://obsidian.md/changelog/2026-01-12-mobile-v1.11.4/).
- **Mobile 1.12 (Feb 27 2026):** native iOS Share extension that writes from Safari / social apps / any share-sheet source straight into the vault without launching Obsidian; "Bookmark Link" Shortcut; "Unique note" home-screen long-press action [[13]](https://obsidian.md/changelog/2026-02-27-mobile-v1.12.4/).
- **Roadmap status:** mobile UI refresh and startup-time work still in flight, but no further capture-specific items remain [[15]](https://obsidian.md/roadmap/).

⚠ The 2026 Obsidian Report Card scores mobile **3.1/5**, noting widget/Shortcut taps still cold-start the full vault — community sentiment is "still awkward and kludgy" despite 1.11/1.12 [[16]](https://practicalpkm.com/2026-obsidian-report-card/).

**Front-end apps that bypass cold-start:**

| Tool | Platform | What it gives you |
|---|---|---|
| [Drafts](https://thesweetsetup.com/quick-capture-to-obsidian-using-drafts/) (Greg Pierce) | iOS / macOS / watchOS | Since v28 *Bookmarks*: writes Markdown directly into an iCloud-stored vault without launching Obsidian; Watch complication [[19]](https://thesweetsetup.com/quick-capture-to-obsidian-using-drafts/) |
| [Actions for Obsidian](https://apps.apple.com/us/app/actions-for-obsidian/id1659667937) (Carlo Zottmann) | iOS 18.4+ | 40+ Shortcuts actions: append, prepend, create-from-template, fetch frontmatter — first-class Action-button/lock-screen building blocks [[17]](https://apps.apple.com/us/app/actions-for-obsidian/id1659667937) |
| [Quick Draft](https://forum.obsidian.md/t/quick-draft-for-obsidian-companion-mobile-app-android-ios/108209) | iOS / Android | Free companion app: text/voice/image capture, OCR, date-formatted file paths, template wrapping, Siri shortcuts; AI title generation paid [[18]](https://forum.obsidian.md/t/quick-draft-for-obsidian-companion-mobile-app-android-ios/108209) |
| [Fleeting Notes](https://www.fleetingnotes.app/posts/put-quick-notes-into-obsidian-from-anywhere) | iOS / Android / desktop | Android-first scratch-note frontend that syncs into the vault; recommended Android answer [[24]](https://www.fleetingnotes.app/posts/put-quick-notes-into-obsidian-from-anywhere) |
| Plain iOS Shortcut popup | iOS | Two-tier flow: short thoughts via system text box appending date+`#QuickNotes` to daily note; longer captures fall back to Drafts [[22]](https://nullpat.ch/posts/2025/04/quick-capture/) |

**Android specifics.** Tasker can write a timestamped Markdown file directly into the vault folder, with the caveat that sync only fires when Obsidian opens [[20]](https://forum.obsidian.md/t/tasker-for-mobile-quick-capture/95141). Harshil Chordia's open-source [home-screen widget](https://forum.obsidian.md/t/i-built-a-android-home-screen-widget-for-obsidian-view-notes-tick-off-tasks-and-quick-capture-without-opening-the-app/112819) renders pinned notes with interactive checkboxes plus a Quick Capture button that appends to today's daily note without opening Obsidian [[21]](https://forum.obsidian.md/t/i-built-a-android-home-screen-widget-for-obsidian-view-notes-tick-off-tasks-and-quick-capture-without-opening-the-app/112819).

**Apple Watch.** Still no first-party Obsidian app in 2026. Workarounds: Drafts' Watch complication, Siri Shortcuts that round-trip via iCloud, or the third-party watchOS recorder *Uplink* that drops transcribed Markdown into the vault [[23]](https://forum.obsidian.md/t/feature-apple-watch-app/17820).

## 3. Web, article, email, RSS clipping

Omnivore's November 2024 shutdown after the ElevenLabs acquihire reset the field [[29]](https://gleamr.io/blog/omnivore-shut-down-alternatives). What replaced it:

| Tool | ⭐ Stars | Use it when |
|---|---|---|
| [Obsidian Web Clipper](https://github.com/obsidianmd/obsidian-clipper) (official) | ⭐ 4.1k | Default. Highlight + clip pages, runs on Chrome/Safari/Firefox/Edge/Brave/Arc/Orion/Vivaldi + mobile. Templates for articles/recipes/references/academic. **Interpreter** feature pipes page context + `{{"prompt"}}` to BYO-LLM (Claude/GPT/Gemini/local) for summary/tags/author fields [[25]](https://github.com/obsidianmd/obsidian-clipper) [[26]](https://obsidian.md/clipper) [[27]](https://help.obsidian.md/web-clipper/interpreter) |
| [Readwise](https://github.com/readwiseio/obsidian-readwise) | ⭐ 335 | Highlight-centric: Kindle, Apple Books, Instapaper, Pocket, Medium, Twitter, PDFs, Reader. V2 added mobile sync + a Readwise MCP server (callable from Raycast or Claude) [[30]](https://github.com/readwiseio/obsidian-readwise) [[31]](https://www.stefanimhoff.de/note-taking-obsidian-readwise-ai/) |
| [MarkDownload](https://github.com/deathau/markdownload) (deathau) | ⭐ 3.8k | Generic page→Markdown via Advanced Obsidian URI; lightweight fallback when Web Clipper templates don't fit [[32]](https://github.com/deathau/markdownload) |
| [Matter](https://github.com/getmatterapp/obsidian-matter) | ⭐ 128 | Newsletter-heavy workflows; Premium $60/yr [[34]](https://www.readless.app/blog/matter-app-pricing-2026); ⚠ Obsidian plugin inactive since Nov 2022 [[33]](https://github.com/getmatterapp/obsidian-matter) |
| Raindrop.io (service) | — | Triage inbox alongside Web Clipper. ⚠ Does not store full Markdown bodies [[28]](https://forum.obsidian.md/t/replacing-omnivore-with-obsidian-web-clipper-available-at-firefox-chrome-add-on-store/90927) |
| Wallabag (self-hosted) | — | Self-hosted escape hatch for users burned by Omnivore/Pocket [[41]](https://danielprindii.com/blog/read-it-later-alternatives-after-omnivore-shutting-down) |

**Annotations (Hypothes.is):** [weichenw plugin](https://github.com/weichenw/obsidian-hypothesis-plugin) ⭐ 270 (one-way sync) [[35]](https://github.com/weichenw/obsidian-hypothesis-plugin), or [lindylearn's fork](https://github.com/lindylearn/obsidian-annotations) (bi-directional, vault edits propagate back) [[36]](https://github.com/lindylearn/obsidian-annotations).

**Email → vault.** SaaS forwarding-alias model: Email2Obsidian (free 10 lifetime emails, $2.49/mo Starter for 300/mo) [[37]](https://email2obsidian.com/), or TaskRobin (archives forwarded emails + attachments) [[38]](https://www.obsidianstats.com/plugins/taskrobin).

**RSS.** joethei's dominant RSS Reader plugin ⭐ 468 was archived August 25, 2025 [[39]](https://github.com/joethei/obsidian-rss). Replacements: Simple RSS, Local RSS, and [RSS Dashboard](https://github.com/amatya-aditya/obsidian-rss-dashboard) ⭐ 499 (aggregates RSS + YouTube + podcasts with smart tagging and embedded media playback) [[40]](https://github.com/amatya-aditya/obsidian-rss-dashboard).

## 4. Voice-to-note

A clear hierarchy emerged in 2026.

| Plugin / route | ⭐ Stars | Backends | Status |
|---|---|---|---|
| [nikdanilov / whisper-obsidian-plugin](https://github.com/nikdanilov/whisper-obsidian-plugin) | ⭐ 350 | OpenAI, Groq, Azure, Ollama, LM Studio | **Default 2026 pick.** v1.9.1 Apr 2026, hotkey recording, LLM post-processing, URL automation for iOS Shortcuts [[42]](https://github.com/nikdanilov/whisper-obsidian-plugin) |
| [djmango / obsidian-transcription](https://github.com/djmango/obsidian-transcription) | ⭐ 222 | local Whisper, OpenAI | Legacy installs. ⚠ Stagnant since v3.4.0 (Apr 2024) [[43]](https://github.com/djmango/obsidian-transcription) |
| [Smart Memos](https://github.com/Mossy1022/Smart-Memos) (Mossy1022) | ⭐ 79 | OpenAI only | Niche: one-shot transcript+summary+expansion; local-model support still on roadmap [[44]](https://github.com/Mossy1022/Smart-Memos) |
| [AudioPen → Obsidian](https://github.com/jonashaefele/audiopen-obsidian) (jonashaefele) | ⭐ 7 | AudioPen webhooks | For users who already pay for AudioPen's polishing engine; templated `{title}/{body}/{orig_transcript}` [[50]](https://github.com/jonashaefele/audiopen-obsidian) |
| [Vox](https://github.com/vincentbavitz/obsidian-vox) (vincentbavitz) | ⭐ 78 | dev's free server (100/day) | Hands-off folder-watcher with filename-prefix metadata tokens; no API keys needed [[51]](https://github.com/vincentbavitz/obsidian-vox) |
| Wispr Flow | — | proprietary | System-wide voice keyboard; vendor claims ~220 wpm vs 45 wpm typing (~4×) [[52]](https://wisprflow.ai/use-cases/obsidian) |

**Accuracy and cost.** [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text): ~$1 per 2h45m of audio with strong accent handling [[45]](https://www.xda-developers.com/free-obsidian-plugin-turns-voice-notes-pc/). Local whisper.cpp: reduced accuracy, occasional accent failures, 16GB RAM floor [[45]](https://www.xda-developers.com/free-obsidian-plugin-turns-voice-notes-pc/). WER data: Whisper Large-v3 hits 2.7% on clean English but degrades to 8–12% on real-world meetings/podcasts; accented English (Indian, Scottish) lands at 8–15% [[46]](https://novascribe.ai/how-accurate-is-whisper).

**iPhone-native option.** iOS 18+ Voice Memos does on-device transcription on iPhone 12+, ~85–90% accuracy on clean single-speaker audio — good enough that many users skip Whisper for short captures [[49]](https://www.plaud.ai/blogs/news/how-to-transcribe-iphone-voice-memos). For longer captures, the dominant DIY route is iOS Shortcuts + RoutineHub piping Voice Memos through Whisper (cloud or local Aiko) and ChatGPT, then dropping output into iCloud where the vault picks it up [[48]](https://forum.obsidian.md/t/iphone-voice-memo-obsidian/63540).

**Forum consensus.** The 2026 r/ObsidianMD pattern is a four-stage pipeline: voice memo → transcription → AI summary → structured note → vault. Friction concentrates around fragmented recordings (interruptions, Bluetooth switching) rather than transcription quality [[47]](https://forum.obsidian.md/t/anyone-using-voice-memos-ai-obsidian-workflow/113197).

## 5. AI-assisted metadata backfill

The 2026 field has fragmented into lanes — there is no single winner. Pick the lane that matches the job.

| Plugin | ⭐ Stars | Lane | Backfill capability over an existing vault |
|---|---|---|---|
| [AI Tagger Universe](https://github.com/niehu2018/obsidian-ai-tagger-universe) (niehu2018) | ⭐ 84 | Auto-tagging + frontmatter | ✓ Batch tag entire folders or whole vault; nested hierarchical tags into frontmatter; 15+ providers (Ollama, LM Studio, OpenAI, Claude, Gemini, DeepSeek, Bedrock, Vertex AI) [[53]](https://github.com/niehu2018/obsidian-ai-tagger-universe) |
| [Note Companion](https://github.com/Nexus-JPF/note-companion) (formerly File Organizer 2000) | ⭐ 832 | Inbox automation | ✓ Folder/tag/title/template suggestions; processes raw captures in batch; cloud sub, self-host, or BYO key; desktop-only [[59]](https://github.com/Nexus-JPF/note-companion) [[63]](https://systemsculpt.com/blog/best-obsidian-ai-plugins-2026) |
| [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections) (brianpetro) | ⭐ 4.9k | Semantic discovery (no tagging) | ✗ Not a backfill tool; embeddings only; ⚠ source-available license + pricing complaints in 2026 [[54]](https://github.com/brianpetro/obsidian-smart-connections) [[55]](https://github.com/brianpetro/obsidian-smart-connections/discussions/1294) |
| [Copilot for Obsidian](https://github.com/logancyang/obsidian-copilot) (logancyang) | ⭐ 6.8k | Agentic chat + RAG + file editing | ✗ Not a dedicated backfill tool; v3.2.8 added Composer V2, Bases, 128k auto-compact [[56]](https://github.com/logancyang/obsidian-copilot) [[57]](https://github.com/logancyang/obsidian-copilot/blob/master/RELEASES.md) |
| [Text Generator](https://github.com/nhaouari/obsidian-textgenerator-plugin) (nhaouari) | ⭐ 1.9k | Template-driven generation | ✓ Template-engine; reusable prompts + frontmatter-configurable settings to batch-generate metadata/summaries/aliases; OpenAI/Anthropic/Gemini/HuggingFace/local [[58]](https://github.com/nhaouari/obsidian-textgenerator-plugin) |
| Metadata Auto Classifier | ⭐ 52 | Tags + arbitrary frontmatter fields | ✓ 2025 entrant; OpenAI GPT only; classifies tags + custom frontmatter fields by user rules [[60]](https://www.obsidianstats.com/plugins/metadata-auto-classifier) |
| LLM Tagger | — | Ollama-only auto-tagging | ✓ Lighter alternative for fully-local users; tags new/modified notes automatically [[64]](https://www.obsidianstats.com/plugins/llm-tagger) |
| [Frontmatter Generator](https://github.com/HananoshikaYomaru/Obsidian-Frontmatter-Generator) | ⭐ 46 | Deterministic non-AI fallback | ✓ JS/JSON expression templates; whole-vault and per-folder commands [[65]](https://github.com/HananoshikaYomaru/Obsidian-Frontmatter-Generator) |

**Hands-on validation.** A 2026 MakeUseOf walkthrough paired AI Tagger Universe with Auto Note Mover and a locally-hosted Gemma 3 12B (via LM Studio) — the *Generate tags for vault* command retro-tagged hundreds of existing notes in under an hour of setup [[61]](https://www.makeuseof.com/letting-local-llm-organize-obsidian-notes/).

**Reddit consensus.** r/ObsidianMD splits picks across three lanes rather than crowning one winner: Smart Composer (fastest, free Llama 3.2) for writing assist, Smart Connections for semantic search, Copilot for vault-wide RAG chat [[62]](https://www.aitooldiscovery.com/guides/obsidian-reddit). Note Companion is called out as strongest "when the job is turning chaos into organized notes"; new entrants on the agent-and-retrieval frontier include Obsilo Agent (55+ tools) and Sonar (local-first) [[63]](https://systemsculpt.com/blog/best-obsidian-ai-plugins-2026).

## 6. Local-first AI backbone

The 2026 case for running tagging/summary/voice locally is concrete: notes never leave the machine, the workflow runs offline, and there is no per-token cost once the model is downloaded [[80]](https://www.xda-developers.com/using-my-local-llm-with-obsidian/). Two engines and two GUIs cover essentially the field.

| Layer | Tool | ⭐ Stars | Notes |
|---|---|---|---|
| Inference engine | llama.cpp | ⭐ 100k | Crossed 100K stars Mar 2026, faster than PyTorch (~7y) or TensorFlow (~8y) [[71]](https://aithinkerlab.com/llama-cpp-100k-github-stars-2026/) |
| Engine wrapper | Ollama | ⭐ 110k | On Apple Silicon now built on **MLX** for unified-memory speedup [[72]](https://www.morphllm.com/comparisons/llama-cpp-vs-ollama) [[74]](https://ollama.com/blog/mlx) |
| GUI alternative | LM Studio (closed-source) | — | Built-in Hugging Face browser, OpenAI-compatible server on `localhost:1234/v1` [[79]](https://tech-insider.org/lm-studio-vs-ollama-2026/) |
| Speech | [whisper.cpp](https://github.com/ggml-org/whisper.cpp) (ggml-org) | ⭐ 49k | C/C++ port of Whisper; offline GPU-accelerated [[75]](https://github.com/ggml-org/whisper.cpp) |
| Apple stack | Apple Foundation Models SDK | — | Python bindings ([apple/python-apple-fm-sdk](https://github.com/apple/python-apple-fm-sdk) ⭐ 1.0k) [[77]](https://github.com/apple/python-apple-fm-sdk); Swift API exposes guided generation, constrained tool calling, LoRA adapters [[78]](https://www.libertify.com/interactive-library/apple-intelligence-foundation-models-2025/) |

**Hardware throughput (Apple Silicon, Llama 3.1 8B):** M1/M2/M3/M4 base chips hit 15–28 tok/s through Metal; M3 Pro/Max with 18+ GPU cores reach 28–35 tok/s thanks to unified memory eliminating PCIe transfer [[73]](https://localaimaster.com/blog/mac-local-ai-setup). ⚠ Single vendor-blog source — corroborate against Ollama's own benchmarks before sizing hardware.

**Recommended models for tagging/summary in 2026:**

| Use case | Model | VRAM | MMLU |
|---|---|---|---|
| Top quality | [Llama 3.3 70B](https://www.llama.com/) | 40 GB | 86.0 [[69]](https://localaimaster.com/blog/best-ollama-models) |
| Best mid-range | [Qwen 2.5 32B](https://qwenlm.ai/) | 20 GB | 83.2 [[69]](https://localaimaster.com/blog/best-ollama-models) |
| Default 8 GB box | [Llama 3.1 8B](https://www.llama.com/) | 6 GB | — handles summarization, conversation, light coding [[70]](https://localaimaster.com/blog/best-local-ai-models-8gb-ram) |
| Email/meeting summaries | [Mistral 7B v0.3](https://mistral.ai/) | 6 GB | — terse summary specialist [[70]](https://localaimaster.com/blog/best-local-ai-models-8gb-ram) |

**Plugin integration.** Both dominant AI plugins speak local:

- **Copilot for Obsidian** → Ollama or LM Studio as drop-in OpenAI-compatible endpoints. Ollama needs `OLLAMA_ORIGINS=app://obsidian.md*` exported to bypass CORS; pull `nomic-embed-text` or `mxbai-embed-large` for fully offline RAG [[66]](https://github.com/logancyang/obsidian-copilot/blob/master/local_copilot.md).
- **Smart Connections** → embeddings created locally by default; notes never leave the machine unless cloud is explicitly enabled [[67]](https://smartconnections.app/smart-connections/). 786K community plugin downloads as of Jan 2026 [[68]](https://grokipedia.com/page/Smart_Connections_Obsidian_plugin).
- **Whisper plugin** → can post-process transcripts through the same local Ollama/LM Studio endpoint [[42]](https://github.com/nikdanilov/whisper-obsidian-plugin).

**Apple Intelligence integration.** Writing Tools are now partially exposed in Obsidian's Edit menu on macOS 15.1+ (M-series Macs, Apple Intelligence enabled) after Electron added the native API [[76]](https://forum.obsidian.md/t/support-apple-intelligence-writing-tools-on-desktop/84137). No dedicated plugin yet wraps the Foundation Models SDK directly — that's an open opportunity in 2026.

## 7. Recommended 2026 stack

A pragmatic baseline that covers all four capture surfaces and keeps backfill local-first.

| Surface | Pick | Why |
|---|---|---|
| Desktop quick capture | QuickAdd + Templater + global hotkey | Default for two years running; both plugins maintained in 2026 [[1]](https://github.com/chhoumann/quickadd) [[3]](https://github.com/SilentVoid13/Templater) [[8]](https://obsidian.rocks/obsidian-quick-capture/) |
| Daily notes engine | Journals (srg-kostyrko) | Replace Periodic Notes ⚠ unmaintained since 2022; Journals offers bulk import [[5]](https://github.com/liamcain/obsidian-periodic-notes) [[6]](https://forum.obsidian.md/t/plugin-journals/76946) |
| iOS lock-screen | Actions for Obsidian + Drafts (longer text) | Cold-start friction makes native widgets slow; Drafts → iCloud vault round-trips fastest [[17]](https://apps.apple.com/us/app/actions-for-obsidian/id1659667937) [[19]](https://thesweetsetup.com/quick-capture-to-obsidian-using-drafts/) [[22]](https://nullpat.ch/posts/2025/04/quick-capture/) |
| Android | Tasker → vault folder + Obsidian Mobile widget | Tasker direct-write is most reliable; sync triggers on next Obsidian launch [[20]](https://forum.obsidian.md/t/tasker-for-mobile-quick-capture/95141) [[14]](https://obsidian.md/changelog/2026-01-12-mobile-v1.11.4/) |
| Web/articles | Obsidian Web Clipper + Interpreter | Official, replaces Omnivore + most third-party clippers; LLM template-fills summary/tags/author [[25]](https://github.com/obsidianmd/obsidian-clipper) [[27]](https://help.obsidian.md/web-clipper/interpreter) |
| Highlights | Readwise (paid) or Hypothes.is + lindylearn (free) | Readwise covers Kindle/Pocket/Reader/PDFs; Hypothes.is covers web annotations bi-directionally [[30]](https://github.com/readwiseio/obsidian-readwise) [[36]](https://github.com/lindylearn/obsidian-annotations) |
| Email | Email2Obsidian or TaskRobin | Forwarding-alias model; both pull into vault [[37]](https://email2obsidian.com/) [[38]](https://www.obsidianstats.com/plugins/taskrobin) |
| Voice (short) | iOS Voice Memos on-device | 85–90% accuracy on clean single-speaker, no setup [[49]](https://www.plaud.ai/blogs/news/how-to-transcribe-iphone-voice-memos) |
| Voice (long) | nikdanilov Whisper plugin + Groq or local | Default 2026 plugin; Groq is cheap+fast, Ollama is free+offline [[42]](https://github.com/nikdanilov/whisper-obsidian-plugin) |
| Backfill — tags/frontmatter | AI Tagger Universe + local Ollama | Validated batch backfill; 15+ providers; runs locally [[53]](https://github.com/niehu2018/obsidian-ai-tagger-universe) [[61]](https://www.makeuseof.com/letting-local-llm-organize-obsidian-notes/) |
| Backfill — inbox triage | Note Companion | Folder/tag/title suggestions over raw captures [[59]](https://github.com/Nexus-JPF/note-companion) |
| Semantic discovery | Smart Connections (local mode) | Embeddings local-first; complementary to tagging [[67]](https://smartconnections.app/smart-connections/) |
| Local engine | Ollama + [Llama 3.1 8B](https://www.llama.com/) (default) or [Qwen 2.5 32B](https://qwenlm.ai/) (quality) | Apple Silicon MLX-accelerated; nomic-embed-text for RAG [[66]](https://github.com/logancyang/obsidian-copilot/blob/master/local_copilot.md) [[69]](https://localaimaster.com/blog/best-ollama-models) [[74]](https://ollama.com/blog/mlx) |

**Migration order for an existing vault:**

1. Switch Periodic Notes → Journals (bulk import) [[6]](https://forum.obsidian.md/t/plugin-journals/76946).
2. Install Web Clipper, retire MarkDownload + any Omnivore remnants [[25]](https://github.com/obsidianmd/obsidian-clipper) [[29]](https://gleamr.io/blog/omnivore-shut-down-alternatives).
3. Set up Ollama + `nomic-embed-text` + Llama 3.1 8B locally [[66]](https://github.com/logancyang/obsidian-copilot/blob/master/local_copilot.md).
4. Run AI Tagger Universe `Generate tags for vault` once over the existing notes [[61]](https://www.makeuseof.com/letting-local-llm-organize-obsidian-notes/).
5. Layer Smart Connections for semantic discovery, Copilot for chat — both pointed at the same Ollama endpoint [[67]](https://smartconnections.app/smart-connections/) [[66]](https://github.com/logancyang/obsidian-copilot/blob/master/local_copilot.md).
6. Mobile: install Actions for Obsidian (iOS) or pin the Obsidian widget (Android), wire one Shortcut/Tasker task to "append to today's daily note" [[17]](https://apps.apple.com/us/app/actions-for-obsidian/id1659667937) [[20]](https://forum.obsidian.md/t/tasker-for-mobile-quick-capture/95141).
