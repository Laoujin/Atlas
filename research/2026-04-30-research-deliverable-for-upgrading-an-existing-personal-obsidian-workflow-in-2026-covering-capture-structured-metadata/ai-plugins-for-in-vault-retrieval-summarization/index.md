---
title: "Obsidian AI plugins for in-vault retrieval & summarization (Apr 2026)"
date: 2026-04-30
depth: standard
format: md
topic: "AI plugins for in-vault retrieval & summarization"
topic_raw: "AI plugins for in-vault retrieval & summarization"
issue: 49
tags: [obsidian, ai, rag, semantic-search, plugins, summarization]
summary: "Pick Smart Connections for local-first retrieval, Copilot for polished vault chat with optional Plus tier, Smart Composer for Cursor-style edits, Khoj for cross-device self-hosted second-brain. Text Generator and the small ai-summary plugins cover dedicated summarization."
citations: 20
reading_time_min: 5
cover: cover.svg
cost_usd: 2.03
duration_sec: 315
---

> **Decision (Apr 2026).** Two-plugin baseline: **Smart Connections** for local-first semantic retrieval + related-notes sidebar [[1]](https://github.com/brianpetro/obsidian-smart-connections) [[2]](https://smartconnections.app/smart-connections/), and **Copilot for Obsidian** for polished vault chat with Ollama or cloud models [[4]](https://github.com/logancyang/obsidian-copilot) [[14]](https://www.xda-developers.com/using-my-local-llm-with-obsidian/). Add **Smart Composer** if you want Cursor-style `@file` edits and one-click apply [[7]](https://github.com/glowingjade/obsidian-smart-composer). Pick **Khoj** instead if you need the same brain on phone/WhatsApp/browser, self-hosted [[9]](https://github.com/khoj-ai/khoj). For pure summarization, **Text Generator** templates [[11]](https://github.com/nhaouari/obsidian-textgenerator-plugin) cover most workflows; the dedicated `obsidian-ai-summary` is only worth installing for weekly/monthly link-walking review notes [[16]](https://github.com/irbull/obsidian-ai-summary).

## Landscape

The 2026 ecosystem has split into clear lanes — retrieval engines, chat-with-vault assistants, agentic surfaces, and template-driven generators [[12]](https://systemsculpt.com/blog/best-obsidian-ai-plugins-2026). Most users only need one from each of the first two columns.

| Lane | What it does | Top picks |
|---|---|---|
| Retrieval / discovery | Embeds every note locally, surfaces related ones in a sidebar, exposes a Lookup view | Smart Connections [[2]](https://smartconnections.app/smart-connections/) |
| Chat with vault (RAG) | Conversational Q&A grounded in your notes via embeddings + LLM | Copilot [[4]](https://github.com/logancyang/obsidian-copilot), Smart Composer [[7]](https://github.com/glowingjade/obsidian-smart-composer), Khoj [[10]](https://docs.khoj.dev/clients/obsidian/) |
| Editor-grade writing assistant | `@file` mentions, Apply-Edit, inline rewrites | Smart Composer [[8]](https://github.com/glowingjade/obsidian-smart-composer/wiki/2.3-Vault-Search-(RAG)) |
| Template-driven generation | Reusable prompts (summary, outline, expand) tied to frontmatter | Text Generator [[11]](https://github.com/nhaouari/obsidian-textgenerator-plugin) |
| Dedicated summarization | One-shot summarize commands with chunking | obsidian-ai-summarize [[17]](https://github.com/ravenwits/obsidian-ai-summarize), obsidian-ai-summary [[16]](https://github.com/irbull/obsidian-ai-summary) |
| Agentic (read+edit+create) | Autonomous tool calls that modify the vault | Obsidian Chat / Vault AI Chat (early) [[20]](https://forum.obsidian.md/t/plugin-obsidian-chat-an-agentic-ai-assistant-that-lives-in-your-vault/112346) |

## Head-to-head: the four plugins worth installing

| | Smart Connections | Copilot for Obsidian | Smart Composer | Khoj |
|---|---|---|---|---|
| Repo | [brianpetro/obsidian-smart-connections](https://github.com/brianpetro/obsidian-smart-connections) ⭐ 4.9k | [logancyang/obsidian-copilot](https://github.com/logancyang/obsidian-copilot) ⭐ 6.8k | [glowingjade/obsidian-smart-composer](https://github.com/glowingjade/obsidian-smart-composer) ⭐ 2.2k | [khoj-ai/khoj](https://github.com/khoj-ai/khoj) ⭐ 34k |
| Primary lane | Retrieval + related-notes [[1]](https://github.com/brianpetro/obsidian-smart-connections) | Vault chat / RAG [[4]](https://github.com/logancyang/obsidian-copilot) | Editor + chat hybrid [[7]](https://github.com/glowingjade/obsidian-smart-composer) | Cross-device second brain [[9]](https://github.com/khoj-ai/khoj) |
| Local embeddings out of box | ✓ ships with on-device model [[2]](https://smartconnections.app/smart-connections/) | ✗ optional; needs Ollama+nomic-embed-text or API [[6]](https://github.com/logancyang/obsidian-copilot/blob/master/local_copilot.md) | ✓ via Ollama / LM Studio [[7]](https://github.com/glowingjade/obsidian-smart-composer) | ✓ self-hosted server handles it [[9]](https://github.com/khoj-ai/khoj) |
| LLM providers | Local + 100+ via APIs (Claude, Gemini, GPT, Llama 3) [[1]](https://github.com/brianpetro/obsidian-smart-connections) | OpenRouter (rec.), OpenAI, Anthropic, Gemini, Cohere, Ollama, LM Studio [[4]](https://github.com/logancyang/obsidian-copilot) | OpenAI, Anthropic, Gemini, Groq, DeepSeek, OpenRouter, Azure, Ollama, LM Studio [[7]](https://github.com/glowingjade/obsidian-smart-composer) | gpt, claude, gemini, llama, qwen, mistral [[9]](https://github.com/khoj-ai/khoj) |
| RAG / vault chat | Smart Chat (free in core) [[2]](https://smartconnections.app/smart-connections/) | Vault QA mode, semantic indexing optional [[4]](https://github.com/logancyang/obsidian-copilot) | `@Vault` or Cmd+Shift+Enter [[8]](https://github.com/glowingjade/obsidian-smart-composer/wiki/2.3-Vault-Search-(RAG)) | Chat over docs + web [[10]](https://docs.khoj.dev/clients/obsidian/) |
| Apply-Edit / inline rewrites | ✗ retrieval only | Command palette quick actions [[4]](https://github.com/logancyang/obsidian-copilot) | ✓ one-click Apply [[7]](https://github.com/glowingjade/obsidian-smart-composer) | ✗ chat-only |
| Multimodal context | ✗ | YouTube, web, PDF, EPUB, images [[4]](https://github.com/logancyang/obsidian-copilot) | Websites, images, YouTube transcripts [[7]](https://github.com/glowingjade/obsidian-smart-composer) | PDF, image, Word, Notion, org-mode [[9]](https://github.com/khoj-ai/khoj) |
| Agent / tool-use | ✗ (use MCP externally) [[19]](https://3sztof.github.io/posts/obsidian-smart-connections-mcp/) | Plus tier: autonomous Agent mode [[4]](https://github.com/logancyang/obsidian-copilot) | MCP support for tools [[7]](https://github.com/glowingjade/obsidian-smart-composer) | Custom agents, automations [[9]](https://github.com/khoj-ai/khoj) |
| Privacy posture | Local-first, offline after index [[2]](https://smartconnections.app/smart-connections/) | Local with Ollama; cloud by default [[14]](https://www.xda-developers.com/using-my-local-llm-with-obsidian/) | Local with Ollama; cloud optional [[7]](https://github.com/glowingjade/obsidian-smart-composer) | Self-host or Khoj cloud [[9]](https://github.com/khoj-ai/khoj) |
| Pricing | Core free; Pro plugins via supporter sub or one-time founding [[3]](https://smartconnections.app/pro-plugins/) | BYOK free; Plus $14.99/mo or $139.99/yr; Self-Host Supporter $349.99 one-time [[5]](https://www.obsidiancopilot.com/en/pricing) | Free with own keys/subs; Gemini API works as free tier [[7]](https://github.com/glowingjade/obsidian-smart-composer) | Free open-source self-host; managed cloud tiers [[9]](https://github.com/khoj-ai/khoj) |

## Where each one wins

**Smart Connections — pick for retrieval + connections sidebar.** It's the only one in the comparison that ships local on-device embeddings with zero configuration and keeps working offline once indexed [[2]](https://smartconnections.app/smart-connections/). The 2026 review consensus is that it's the best "find related notes while I write" experience and free for the core plugin [[12]](https://systemsculpt.com/blog/best-obsidian-ai-plugins-2026). Pro adds inline connections and ranking knobs but is optional [[3]](https://smartconnections.app/pro-plugins/).

**Copilot for Obsidian — pick for the most polished chat-with-vault.** Native Ollama support, "Relevant Notes" auto-injecting context, and broad multimodal handling (YouTube, PDF, EPUB, images) [[4]](https://github.com/logancyang/obsidian-copilot) [[14]](https://www.xda-developers.com/using-my-local-llm-with-obsidian/). The free tier is fully functional with your own API keys; Plus ($14.99/mo, $139.99/yr) unlocks Agent mode, time-window queries, and a built-in model [[5]](https://www.obsidiancopilot.com/en/pricing). Going fully local is well-documented: install Ollama, pull a chat model + `nomic-embed-text`, point at `localhost:11434` [[6]](https://github.com/logancyang/obsidian-copilot/blob/master/local_copilot.md).

**Smart Composer — pick if you want Cursor-in-Obsidian.** `@file` mentions feed exact files into context, `@Vault` triggers RAG retrieval, and Apply-Edit lets you accept AI rewrites with one click [[7]](https://github.com/glowingjade/obsidian-smart-composer) [[8]](https://github.com/glowingjade/obsidian-smart-composer/wiki/2.3-Vault-Search-(RAG)). MCP support means you can plug in external tools/data sources. Best for editor-heavy workflows where chat and writing blur.

**Khoj — pick if "vault" extends past Obsidian.** It's a self-hostable second brain reachable from Obsidian, Emacs, browser, desktop, phone, or WhatsApp [[9]](https://github.com/khoj-ai/khoj). Indexes Markdown, PDF, Notion, Word, org-mode. Heavier setup (Docker/server) than the in-process plugins, but unmatched if you want one knowledge base across surfaces — and the 34k-star repo is the most actively maintained of the bunch [[10]](https://docs.khoj.dev/clients/obsidian/).

## Summarization specifically

Most users don't need a dedicated summarization plugin in 2026 — Copilot, Smart Composer, and Text Generator all handle "summarize this note / selection" via prompt or template [[11]](https://github.com/nhaouari/obsidian-textgenerator-plugin) [[4]](https://github.com/logancyang/obsidian-copilot). The two narrow tools earn install only in specific cases:

| Use case | Tool | Notes |
|---|---|---|
| Weekly/monthly review note that walks all linked notes and dumps a summary per link | [obsidian-ai-summary](https://github.com/irbull/obsidian-ai-summary) ⭐ 39 | Niche but well-shaped for periodic notes [[16]](https://github.com/irbull/obsidian-ai-summary) |
| One-shot summarize command with chunking + placement profiles | [obsidian-ai-summarize](https://github.com/ravenwits/obsidian-ai-summarize) ⭐ 18 | Smaller scope than Text Generator, simpler UX [[17]](https://github.com/ravenwits/obsidian-ai-summarize) |
| Reusable summary templates with frontmatter overrides | [Text Generator](https://github.com/nhaouari/obsidian-textgenerator-plugin) ⭐ 1.9k | Ships GPT-5 + thinking-model support; community template gallery [[11]](https://github.com/nhaouari/obsidian-textgenerator-plugin) |

## Operational notes

- **Indexing cost.** First-build embedding on a 5,000-note vault takes 20–30 min locally; index lives in `.obsidian/` and updates incrementally [[15]](https://insiderllm.com/guides/obsidian-local-llm-guide/). Plan for the first run, not the steady state.
- **Local-only stack** that's known-good in 2026: Ollama + `nomic-embed-text` for embeddings + Qwen 2.5 (or Llama 3) for chat, wired into Copilot or Smart Composer [[6]](https://github.com/logancyang/obsidian-copilot/blob/master/local_copilot.md) [[14]](https://www.xda-developers.com/using-my-local-llm-with-obsidian/).
- **Don't double-index.** Running Smart Connections + Copilot Vault QA + Smart Composer RAG simultaneously means three separate embedding indexes over the same vault. Pick one chat plugin; let Smart Connections handle the discovery sidebar [[13]](https://forum.obsidian.md/t/alternatives-to-smart-connections/108886).
- **Agentic plugins** (Obsidian Chat, Vault AI Chat) can read+edit+create files autonomously [[20]](https://forum.obsidian.md/t/plugin-obsidian-chat-an-agentic-ai-assistant-that-lives-in-your-vault/112346) — interesting but immature; the more reliable 2026 pattern is wiring Smart Connections retrieval into Claude Code or another external agent via MCP [[19]](https://3sztof.github.io/posts/obsidian-smart-connections-mcp/).
- The community-maintained [Awesome Obsidian AI Tools](https://github.com/danielrosehill/awesome-obsidian-ai-tools) ⭐ 115 list is the right index when you need to look beyond these picks [[18]](https://github.com/danielrosehill/awesome-obsidian-ai-tools).
