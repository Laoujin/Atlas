What integration architectures connect Slack to Claude Code (Slack app modes, Socket Mode vs Events API, GitHub-webhook bridges, ngrok-style local relays)?
What existing open-source projects implement Slack ↔ Claude Code remote control today (claude-slack, claude-code-action variants, MCP-Slack bridges) — features, stars, maintenance status?
How does the Claude Code SDK / CLI enable headless and programmatic invocation suited for chat-driven control (--print, --output-format stream-json, --resume, session IDs, custom system prompts)?
What does Anthropic officially provide or recommend for remote-controlling Claude Code (Slack MCP server, Claude on Slack, GitHub Action triggers, hooks, subagents, Bedrock/Vertex paths)?
What operational pitfalls do practitioners report — authentication, secrets, rate limits, long-running tasks, threading replies, output truncation, cost runaway, prompt injection from messages?
What end-to-end reference architectures or recipes exist for "Slack message → Claude Code agent in repo → reply in thread" (event handler → queue/worker → Claude Code CLI → response formatter)?
