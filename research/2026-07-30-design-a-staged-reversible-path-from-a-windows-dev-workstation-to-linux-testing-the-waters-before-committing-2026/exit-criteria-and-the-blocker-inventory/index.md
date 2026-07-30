---
title: "Exit criteria and the blocker inventory: decide the Linux switch on evidence, not vibes"
date: 2026-07-30
depth: ceo
format: md
topic: "Exit criteria and the blocker inventory for a Windows-to-Linux switch (2026) — cataloguing Windows-only dependencies before committing, and defining measurable go/no-go criteria instead of vibes."
topic_raw: "gradual linux migration from Windows (first testing the waters)."
tags: [linux, windows, migration, dotnet, workstation, decision-framework]
summary: "A fill-in blocker inventory plus tickable go/no-go criteria and a pre-committed rollback date for a Windows-to-Linux workstation trial."
citations: 8
reading_time_min: 3
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 155
issue: 14
---

> **Decision.** Do the inventory *before* the install: exactly one class — kernel anti-cheat games and locked-down corporate MDM — is a genuine hard blocker in 2026 [[5]](https://en.wikipedia.org/wiki/Kernel-level_anti-cheat) [[3]](https://learn.microsoft.com/en-us/intune/fundamentals/platform-guide-linux); everything else in a .NET/TypeScript workstation is a soft blocker with a known price. Then run a fixed-length trial against tickable criteria, with a pre-committed rollback date — retrospectives that succeeded treated the switch as a tool-selection problem with a per-app verdict list, not a conversion [[8]](https://www.xda-developers.com/i-cant-imagine-using-windows-in-2026-after-moving-to-linux/).

## Blocker inventory — fill this in first

| Class | Ask of each item | Usual 2026 verdict | Severity |
|--------------------|--------------------------------------------------|--------------------------------------------------------------------------|----------|
| Hardware | Is the exact model on Ubuntu's certified list? Suspend, Wi-Fi, dock, fingerprint? | Certified ThinkPad/Dell/HP: fine. Uncertified + Nvidia + fingerprint: expect fixes [[7]](https://ubuntu.com/certified) | Soft ⚠ |
| Employer policy | Does MDM/conditional access admit a Linux device? | Intune supports enrolled **Ubuntu LTS + GNOME, corporate-owned only**; anything else fails compliance [[3]](https://learn.microsoft.com/en-us/intune/fundamentals/platform-guide-linux) | Hard if unlisted |
| Dev toolchain | Does the IDE/SDK have a native Linux build? | Visual Studio proper: **never** on Linux, Microsoft reconfirmed 2025 [[1]](https://visualstudiomagazine.com/articles/2025/09/22/confirmed-finally-again-no-visual-studio-ide-for-linux-macos.aspx) → [Rider](https://www.jetbrains.com/rider/) or VS Code. SQL Server runs in Docker; SSMS doesn't — Azure Data Studio retired Feb 2026, so VS Code mssql or DBeaver [[6]](https://learn.microsoft.com/en-us/sql/tools/whats-happening-azure-data-studio) | Soft |
| WinForms/WPF | Do you still *maintain* desktop Windows apps? | Designers are Windows-only → keep a VM | Soft (Hard if daily) |
| Office / collab | Native client or web? | Teams native Linux client retired; PWA is the supported path [[2]](https://techcommunity.microsoft.com/blog/microsoftteamsblog/microsoft-teams-progressive-web-app-now-available-on-linux/3669846). Excel VBA/Adobe: no equivalent | Soft; Hard for macro/Adobe work |
| Personal / civic | Kernel anti-cheat? eID? | EAC/BattlEye block Linux unless the studio opts in [[5]](https://en.wikipedia.org/wiki/Kernel-level_anti-cheat). Belgian eID middleware is officially packaged for Debian/Ubuntu/RPM [[4]](https://eid.belgium.be/en/linux-eid-software-installation) | Anti-cheat = Hard; eID = non-issue |

**Triage rule:** *hard* = no Linux path at any cost → keep a Windows partition or a second machine. *Soft* = works, costs setup time or a VM → allowed to hurt during the trial. *Non-issue* → delete from the list; don't re-litigate it later.

## Go/no-go criteria — tick, don't feel

- [ ] Zero unresolved **hard** blockers (VM/partition counts as resolved only if you accept it permanently).
- [ ] **21 consecutive days** without booting Windows for anything unplanned.
- [ ] Suspend/resume survives **20 cycles** incl. dock and external display, no black screen.
- [ ] Full solution build + test suite green, wall-clock within **110%** of the Windows baseline you measured *before* wiping.
- [ ] Every app in the inventory has a working replacement or an explicit **decided-to-drop** mark — no blanks.
- [ ] One real deploy to the homelab done end-to-end from Linux.
- [ ] Zero unrecovered data-loss or "couldn't work today" incidents.

## Rollback date

Pick it now: **trial start + 60 days**. On that date you either wipe the Windows partition or restore it — no third option. Any criterion unticked at the date defaults to revert. Undated trials don't fail, they dissolve.
