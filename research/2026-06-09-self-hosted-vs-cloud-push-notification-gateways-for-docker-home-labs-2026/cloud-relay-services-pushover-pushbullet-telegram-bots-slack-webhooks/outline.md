Architecture & delivery model of each cloud relay (Pushover, Pushbullet, Telegram bots, Slack incoming webhooks): what each is, platforms/apps it delivers to, message API shape, iOS/Android reach.
Pricing & cost model: Pushover one-time per-platform, Pushbullet Pro, Telegram free, Slack free/paid tiers and webhook availability — total cost for a homelab.
Homelab/Docker integration & automation: sending via curl from a container, Apprise/shoutrrr support, native support in Uptime Kuma, Home Assistant, Grafana, Watchtower, n8n — which is easiest to wire up.
Reliability, rate limits, delivery latency, message size limits, and the separate-infrastructure hedge for alerting.
Privacy, security, encryption and data handling: Telegram Cloud Chats not E2E, bot token exposure, Slack data retention, Pushover/Pushbullet privacy posture.
Service health, longevity and momentum: Pushbullet's feature removals and decline, Pushover's stability and acquisition, Telegram Bot API evolution, Slack legacy/incoming webhook deprecation history — bus-factor for cloud services.
