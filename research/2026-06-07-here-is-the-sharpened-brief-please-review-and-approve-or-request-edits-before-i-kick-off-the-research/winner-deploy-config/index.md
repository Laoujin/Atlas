---
title: "Winner Design Deployment Configuration"
date: 2026-06-07
depth: ceo
format: md
topic: "Winner deploy config"
topic_raw: "Winner deploy config"
issue: 194
tags: [software, deployment, network, configuration]
summary: "Network deployment of Winner Design requires a dedicated server, 1 Gbit/s wired bandwidth, and optional centralized rendering offload."
citations: 3
reading_time_min: 2
cost_usd: 0.40
duration_sec: 86
model: "Haiku 4.5"
---

> **TL;DR:** Winner Design network deployment requires a dedicated server with 1 Gbit/s bandwidth, wired network only, and UNC file paths. Optionally configure a centralized render server to offload CPU-intensive rendering tasks from workstations.

## Network Setup

[Winner Design](https://www.compusoftgroup.com) is kitchen planning CAD software that can be deployed across networked workstations. A centralized server installation is mandatory; peer-to-peer networks are not supported [[1]](https://winnerdesign.support.compusoftgroup.com/hc/en-us/articles/360011738617-How-to-install-Winner-Design-in-a-network-environment).

**Installation process:** Run the Winner Design installer on the dedicated server, selecting a local drive for the installation path. On each client PC, navigate to the server's Winner folder (via UNC path like `\\Servername\Applications\Winner`) and run `lansetup.exe` as administrator. After restarting all connected PCs, start Winner Design on a single PC first—this prepares system catalogues that all workstations will then share [[1]](https://winnerdesign.support.compusoftgroup.com/hc/en-us/articles/360011738617-How-to-install-Winner-Design-in-a-network-environment).

**Licensing:** Each client PC requires a separate USB dongle or activation code [[1]](https://winnerdesign.support.compusoftgroup.com/hc/en-us/articles/360011738617-How-to-install-Winner-Design-in-a-network-environment).

## Network Requirements

All network hardware must support at least **1 Gbit/s bandwidth**—including cables, routers, and switches [[2]](https://winnerdesign.support.compusoftgroup.com/hc/en-us/articles/4406083934737-Hardware-requirements-and-system-specification-for-Winner). **Wireless networks are unsupported**; Compusoft advises against any Wi-Fi deployments [[2]](https://winnerdesign.support.compusoftgroup.com/hc/en-us/articles/4406083934737-Hardware-requirements-and-system-specification-for-Winner).

Linux servers (Samba, Red Hat, Arch, etc.) are not supported—use Windows or a compatible NAS [[2]](https://winnerdesign.support.compusoftgroup.com/hc/en-us/articles/4406083934737-Hardware-requirements-and-system-specification-for-Winner).

## Optional: Centralized Rendering

Winner Design v12.0+ supports offloading rendering to dedicated high-CPU machines. Instead of equipping each workstation with expensive processors, a single render server (or cluster) handles all 3D rendering for the network [[3]](https://winnerdesign.support.compusoftgroup.com/hc/en-gb/articles/4412326194193-Installation-of-a-Render-Server-or-Render-Server-Cluster). Render servers communicate via a shared **Render Jobs folder** (legacy non-Flex deployments) or via the Flex cloud platform (Winner Flex customers) [[3]](https://winnerdesign.support.compusoftgroup.com/hc/en-gb/articles/4412326194193-Installation-of-a-Render-Server-or-Render-Server-Cluster).

A render server should have a fast CPU and moderate GPU for best performance [[2]](https://winnerdesign.support.compusoftgroup.com/hc/en-us/articles/4406083934737-Hardware-requirements-and-system-specification-for-Winner).
