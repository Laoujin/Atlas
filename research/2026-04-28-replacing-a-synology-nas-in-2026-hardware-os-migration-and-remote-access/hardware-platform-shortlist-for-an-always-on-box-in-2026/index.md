---
title: "Hardware platform shortlist for an always-on box in 2026"
date: 2026-04-28
depth: deep
format: md
topic: "Hardware platform shortlist for an always-on box in 2026"
topic_raw: "Hardware platform shortlist for an always-on box in 2026"
issue: 40
tags: [home-server, nas, hardware, homelab, mini-pc, diy, synology]
cover: cover.svg
summary: "Five hardware categories, measured idle wattage, and a profile-by-profile shortlist for replacing a Synology NAS in 2026 — UGREEN, Aoostar, Beelink, Minisforum, Jonsbo+ASRock Rack, and the used tiny trio."
citations: 101
reading_time_min: 10
cost_usd: 9.73
duration_sec: 1001
---

> **TL;DR — pick by profile:**
> - **All-flash, lowest power, no spinning disks:** Beelink ME mini ($209-329, ~7W idle, 6× M.2 NVMe).[[49]](https://nascompares.com/review/beelink-me-mini-nas-review/)[[50]](https://www.techradar.com/computing/beelink-me-mini-nas-mini-pc-review)
> - **Turnkey 4-6 HDD Synology replacement:** UGREEN DXP4800 Plus ($620, Pentium 8505, 10GbE+2.5GbE, ~24W idle).[[29]](https://nas.ugreen.com/products/ugreen-nasync-dxp4800-plus-nas-storage)[[33]](https://www.techpowerup.com/review/ugreen-nasync-dxp4800-plus/13.html)
> - **DIY 8-bay budget:** Jonsbo N3 + CWWK i3-N305 + 32GB DDR5 ≈ $650-770 diskless.[[74]](https://selfhosting.sh/hardware/diy-nas-build/)
> - **ECC + IPMI in one box:** ASRock Rack B650D4U µATX (~$264) for AM5 with onboard BMC.[[66]](https://www.asrockrack.com/general/productdetail.asp?Model=B650D4U)
> - **Maximum bays without DIY:** Aoostar WTR Max — 6 SATA + 5 NVMe, dual 10GbE SFP+, $649-699.[[36]](https://nascompares.com/review/aoostar-wtr-max-nas-review-nas-perfection/)[[37]](https://aoostar.com/blogs/news/the-aoostar-wtr-max11bay-is-about-to-meet-you-all)

Synology DSM is still the best NAS software, but the 2025/2026 drive lock-in — Plus models gate dedup, lifespan analysis, firmware updates and pool creation behind Synology-branded drives — has driven ServeTheHome to pull its recommendation[[3]](https://www.servethehome.com/synology-lost-the-plot-with-hard-drive-locking-move/) and the community to refuse upgrades[[4]](https://www.synoforum.com/threads/synology-2025-nas-hard-drive-and-ssd-lock-in-confirmed-bye-bye-seagate-and-wd.14682/) while pricing rises with no meaningful hardware upgrades[[5]](https://www.xda-developers.com/synology-nas-hardware-pricing-value-problem/). The sections below are the alternatives — measured, not vibes.

## The five categories at a glance

| Category | Cost (typical) | Idle power | Bays / NVMe | OS freedom | Notes |
|---|---|---|---|---|---|
| Prebuilt mini-NAS (UGREEN, Aoostar, TerraMaster, Asustor, Minisforum) | $200-1,300 | 7-34W | 4-12 SATA, 2-12 M.2 | Vendor OS or BYO[[34]](https://nascompares.com/guide/truenas-on-a-ugreen-nas-installation-guide/)[[35]](https://forum.proxmox.com/threads/nas-ugreen-dxp4800-plus.177241/) | Turnkey hardware + sometimes-decent vendor OS |
| Mini-PC (Beelink, Minisforum, Aoostar, GMKtec) | $130-800 | 6-15W | 0-2 M.2, no 3.5" bay[[2]](https://www.pcbuildadvisor.com/best-mini-pc-for-home-server-the-ultimate-guide-with-comparisons/) | Full BYO | Cheapest path; no spinning bulk storage in-chassis |
| DIY mini-ITX/mATX | $500-2,500+ | 7-30W | 4-12 SATA, 1-3 M.2[[15]](https://nascompares.com/answer/diy-nas-server-build-guide-for-2026-motherboards-cpus-and-hardware-planning/) | Full BYO | Best for ECC, 10GbE, GPU, scale-out[[15]](https://nascompares.com/answer/diy-nas-server-build-guide-for-2026-motherboards-cpus-and-hardware-planning/) |
| Used enterprise USFF ("tiny trio") | $100-250 | 11-18W | 0-2 M.2, 1× 2.5" | Full BYO | TinyMiniMicro fleet; cluster-friendly[[7]](https://2ndboot.com/mini-pc-buying-guide-2026/)[[8]](https://www.servethehome.com/introducing-project-tinyminimicro-home-lab-revolution/) |
| SBC / ARM (Pi 5, Rock 5B) | $80-200 | 2-10W | USB only | Full BYO | N100 mini-PC delivers 4× perf at the same accessorized price[[9]](https://www.xda-developers.com/intel-n100-killed-raspberry-pi-home-servers/)[[10]](https://selfhosting.sh/hardware/raspberry-pi-home-server/) |

Mini-PCs idle at 5-8W against 80-120W for tower builds with desktop CPUs and spinning drives — over a year, ⚠ £50-£90 in extra electricity.[[1]](https://www.serverman.co.uk/server/home-server/best-mini-pc-home-server/)

## Idle power and the annual electricity bill

Each 1W continuous = 8.76 kWh/yr = €2.63 at €0.30/kWh or $1.40 at $0.16/kWh. Wall-meter measurements (Kill-A-Watt, headless):

| Platform class | Idle W | €/yr (EU 0.30) | $/yr (US 0.16) | Source |
|---|---|---|---|---|
| Radxa Rock 5B (eMMC only) | 1.7 | €4.5 | $2.4 | [[23]](https://bret.dk/radxa-rock_5b-review-powerful-rk3588-sbc/) |
| Raspberry Pi 5 (D0 stepping) | 2.0-2.7 | €5-7 | $3-4 | [[22]](https://www.jeffgeerling.com/blog/2024/new-2gb-pi-5-has-33-smaller-die-30-idle-power-savings/) |
| Beelink S12 Pro (N100, headless) | 6-8 | €18-21 | $10-11 | [[16]](https://bishalkshah.com.np/blog/low-power-homelab-n100-mini-pc)[[17]](https://selfhosting.sh/hardware/mini-pc-power-consumption/) |
| ASRock N100DC-ITX DIY | 6-8 | €18-21 | $10-11 | [[28]](https://www.tqdev.com/2023-asrock-n100dc-itx/) |
| Tuned i5-12400 mini-ITX (ASUS H770) | 7 | €18 | $10 | [[19]](https://mattgadient.com/7-watts-idle-on-intel-12th-13th-gen-the-foundation-for-building-a-low-power-server-nas/) |
| Beelink ME mini (N150, headless) | 7-10 | €18-26 | $10-14 | [[50]](https://www.techradar.com/computing/beelink-me-mini-nas-mini-pc-review) |
| ServeTheHome i3-N305 fanless firewall | 9-11 | €24-29 | $13-15 | [[18]](https://www.servethehome.com/almost-a-decade-in-the-making-our-fanless-intel-i3-n305-2-5gbe-firewall-review/4/) |
| Lenovo M90q Tiny Gen2 (i7) | 12-14 | €32-37 | $17-20 | [[20]](https://www.servethehome.com/lenovo-thinkcentre-m90q-tiny-gen2-tinyminimicro-review-intel/4/) |
| HP EliteDesk 705 G4 Mini (Ryzen, Debian) | 18 | €47 | $25 | [[21]](https://louwrentius.com/a-review-of-the-hp-elitedesk-705-g4-mini-pc-a-raspberry-pi-killer-with-a-caveat.html) |
| Beelink SER5 Max (Ryzen 7 5800H) | 18 | €47 | $25 | [[17]](https://selfhosting.sh/hardware/mini-pc-power-consumption/) |
| Ryzen 5600G NAS (no disks) | 25-30 | €66-79 | $35-42 | [[71]](https://blog.patshead.com/2024/03/how-efficient-is-the-most-power-efficient-nas.html) |
| Minisforum N5 Pro | 32-34 | €84-89 | $45-48 | [[46]](https://www.servethehome.com/minisforum-n5-pro-review-an-awesome-nas-platform/4/) |

Drives often dominate. Seagate IronWolf Pro 20TB: 5.5W idle (spinning) / 1.0W standby per datasheet[[24]](https://www.seagate.com/content/dam/seagate/assets/products/nas-drives/ironwolf-pro-hard-drive/files/Seagate_IronWolf_Pro_SATA_Product_Manual_24-20-16-12TB_206815300B.pdf). WD Red 14TB: 3.0W idle / 0.8W standby[[25]](https://aphnetworks.com/reviews/western-digital-red-wd140effx-14tb/2). Four IronWolf Pros always-spinning ≈ 22W = €58/$31/yr; with effective standby it drops to ~€11/$6. ⚠ ZFS resists effective spindown — transaction groups close every 5-30s and metadata writes touch every disk[[27]](https://www.truenas.com/community/threads/any-point-or-benefit-to-spinning-down-disks.105861/) — so for ZFS users the always-spinning number is the realistic one. Consumer NVMe contributes ~0.5-1W when ASPM/APST work on Linux but can balloon to ~4W on FreeBSD or with broken BIOS[[26]](https://forum.level1techs.com/t/nvme-power-consumption-when-idle-zfs/191241).

## The 2026 prebuilt mini-NAS shortlist

| Model | CPU | Bays | NIC | Idle | RAM | Price | OS |
|---|---|---|---|---|---|---|---|
| **Beelink ME mini** | Intel N150 | 6× M.2 | 2×2.5GbE | 7-10W[[50]](https://www.techradar.com/computing/beelink-me-mini-nas-mini-pc-review) | 12GB LPDDR5 | $209-329[[49]](https://nascompares.com/review/beelink-me-mini-nas-review/)[[50]](https://www.techradar.com/computing/beelink-me-mini-nas-mini-pc-review) | BYO |
| **UGREEN DXP4800 Plus** | Pentium Gold 8505 | 4 SATA + 2 M.2 | 10GbE + 2.5GbE | ~24W[[33]](https://www.techpowerup.com/review/ugreen-nasync-dxp4800-plus/13.html) | DDR5 | $620[[29]](https://nas.ugreen.com/products/ugreen-nasync-dxp4800-plus-nas-storage) | UGOS Pro or BYO[[34]](https://nascompares.com/guide/truenas-on-a-ugreen-nas-installation-guide/) |
| **UGREEN DXP6800 Pro** | i5-1235U | 6 SATA + 2 M.2 | dual 10GbE | n/a | 8GB DDR5 (→64) | ~$1,028[[30]](https://nas.ugreen.com/products/ugreen-nasync-dxp6800-pro-nas-storage) | UGOS Pro or BYO |
| **UGREEN DXP8800 Plus** | i5-1235U | 8 SATA + 2 M.2 | dual 10GbE | n/a | DDR5 | ~$1,283[[31]](https://nascompares.com/guide/the-ugreen-nasync-nas-dxp2800-dxp4800-dxp6800-dxp8800-and-dxp480t-should-you-buy/) | UGOS Pro or BYO |
| **TerraMaster F4-424 Pro** | i3-N305 | 4 SATA + 2 M.2 | 2×2.5GbE | n/a | 32GB DDR5 | $450-550[[40]](https://www.terra-master.com/products/f4-424-pro)[[41]](https://tecnoyfoto.com/en/terramaster-f4-424-pro-review-2026) | TOS or BYO |
| **TerraMaster F8 SSD Plus** | i3-N305 | 8× M.2 | 10GbE | n/a | 16GB DDR5 | n/a[[42]](https://homecloudhq.com/terramaster-f8-ssd-plus-review-2026/) | TOS or BYO |
| **Aoostar WTR Pro** | Ryzen 7 5825U | 4 SATA + 2 M.2 | n/a | n/a | BYO | $399[[38]](https://nascompares.com/review/aoostar-wtr-pro-nas-review/)[[88]](https://www.amazon.com/AOOSTAR-WTR-PRO-Ryzen-Storage/dp/B0F9WKBFQR) | BYO only |
| **Aoostar WTR Max** | Ryzen 7 PRO 8845HS | 6 SATA + 5 M.2 | dual 10GbE SFP+ | n/a | BYO ECC | $649-699[[37]](https://aoostar.com/blogs/news/the-aoostar-wtr-max11bay-is-about-to-meet-you-all)[[36]](https://nascompares.com/review/aoostar-wtr-max-nas-review-nas-perfection/)[[87]](https://www.amazon.com/AOOSTAR-WTR-MAX-Ports%EF%BC%8CUSB4-Port%EF%BC%8CSupport/dp/B0G25LTBDZ) | BYO only |
| **Minisforum N5** | Ryzen AI 9 HX 370 | 5 SATA + 3 M.2 | 10GbE+5GbE | n/a | DDR5 | $645[[45]](https://www.notebookcheck.net/Minisforum-updates-N5-and-N5-Pro-NAS-systems-with-new-pricing-and-more-storage.1084560.0.html) | Win pre / BYO |
| **Minisforum N5 Pro** | Ryzen AI 9 HX PRO 370 | 5 SATA + 3 M.2 | 10GbE+5GbE | 32-34W[[46]](https://www.servethehome.com/minisforum-n5-pro-review-an-awesome-nas-platform/4/) | up to 96GB ECC DDR5[[44]](https://store.minisforum.com/products/minisforum-n5-pro-ai-nas) | $1,019 barebone[[45]](https://www.notebookcheck.net/Minisforum-updates-N5-and-N5-Pro-NAS-systems-with-new-pricing-and-more-storage.1084560.0.html) | BYO |
| **Minisforum MS-A2** | Ryzen 9 9955HX | 3 M.2 / U.2 | dual 10GbE SFP+ + 2×2.5GbE | n/a | DDR5-5600 to 96GB | $799 barebone[[47]](https://store.minisforum.com/products/minisforum-ms-a2-workstation)[[48]](https://nascompares.com/review/minisforum-ms-a2-review-the-ms-01-killer/) | BYO |
| **Asustor Flashstor 12 Pro (FS6712X)** | Celeron N5105 | 12× M.2 | 10GbE | n/a | 4GB DDR4 | ~$799[[52]](https://www.servethehome.com/asustor-flashstor-12-pro-fs6712x-review-12x-m-2-ssd-and-10gbase-t-nas-crucial/)[[53]](https://www.amazon.com/Asustor-Flashstor-Pro-FS6712X-Quad-Core/dp/B0BZCMV1QD) | ADM or BYO |
| **Asustor FlashStor 6 Gen 2 (FS6806X)** | Ryzen V3C14 | 6× M.2 Gen4 | 10GbE + 2× USB4 | n/a | 8GB DDR5 | ~$999[[54]](https://www.techradar.com/pro/asustor-flashstor-6-gen2-fs6806x-review) | ADM or BYO |

Warranty: UGREEN ✓ 2 years[[32]](https://nas.ugreen.com/pages/warranty); TerraMaster ✓ 2-year brand-new replacement[[43]](https://www.terra-master.com/blogs/news/warranty-solution); Aoostar / Minisforum / Beelink rely on retailer terms.

Sentiment: TrueNAS forum users describe TerraMaster TOS7 as a Synology lookalike with reliability gripes[[55]](https://forums.truenas.com/t/buying-a-non-diy-nas-is-it-true-what-brave-ki-tells-me-about-terramaster-vs-ugreen/37094); Aoostar WTR Max is "almost perfect" for self-hosters running TrueNAS/Proxmox[[56]](https://www.virtualizationhowto.com/2025/06/aoostar-wtr-max-review-the-almost-perfect-nas-mini-pc/); Minisforum MS-A2 is positioned as the MS-01 successor with NAS-suitable triple M.2 + dual 10GbE SFP+[[14]](https://www.virtualizationhowto.com/2025/11/the-best-mini-pcs-for-home-labs-in-2025-ranked-by-real-performance/)[[48]](https://nascompares.com/review/minisforum-ms-a2-review-the-ms-01-killer/); Beelink/GMKtec/AOOSTAR trade support for price[[13]](https://www.pcbuildadvisor.com/what-are-the-best-mini-pc-manufacturers-minisforum-beelink-geekom-gmktec-aoostar-acemagic-trigkey-reviewed/).

## DIY mini-ITX/mATX in 2026

Three tiers, separated by power and ECC capability.

### Tier 1 — N100/N150/N305 embedded (≈$500-800 diskless)

- **ASRock N100DC-ITX** ($129.99 launch) — soldered N100, 19V DC-in, 2 SATA, 1 M.2, 1 PCIe 3.0 x4 (x2 mode).[[63]](https://www.asrock.com/mb/Intel/N100DC-ITX/) Sister **N100M** µATX has a standard 24-pin ATX connector.[[64]](https://www.servethehome.com/asrock-adopts-intel-alder-lake-n-with-n100-based-n100dc-itx-and-n100m-motherboards/)
- **CWWK / Topton 6-bay N100/N305 mini-ITX** ($136 N100, more for N305) — 6× SATA, 2× M.2, 4× i226-V 2.5GbE, DDR5, 1× PCIe x1.[[61]](https://cwwk.net/products/12th-i3-n305-n100-nas-motherboard-6-bay-dc-power-2xm-2-nvme-6xsata3-0-pcie-x1-4x-i226-v-2-5g-lan-ddr5-itx-mainboard) ⚠ Tradeoffs: soldered CPU, weak stock cooler[[62]](https://rovingclimber.com/2024/09/09/cwwk-i3-n305-nas-mini-itx-board/), some BIOSes lock C-States and pin idle at ~20W with one HDD[[73]](https://nascompares.com/answer/cwwk-n100-vs-n305-pros-cons-and-common-questions-answered/). Topton flagged as a reliability black box with no warranty path[[12]](https://homenode.tech/ultimate-guide-building-nas-want-build-hurts-2026/).
- **Topton N22 with i3-N355** is Brian Moses' 2026 DIY NAS reference build — incrementally improved over last year with 8× SATA, 2.5GbE, and a PCIe x1 slot — chosen for its budget price despite higher idle than the ASRock alternatives.[[11]](https://blog.briancmoses.com/2025/11/diy-nas-2026-edition.html)
- N305 = 8 cores @ 15W TDP vs. N100's 4 cores @ 6W → better for Plex transcoding and virtualization.[[60]](https://nascompares.com/review/the-topton-n305-nas-motherboard-hardware-deep-dive-review/)

### Tier 2 — Ryzen mainstream (≈$800-1,500 diskless)

AM5 ITX / mATX with 5600G / 7600 / 8500G in a Jonsbo N3 / N5. A 5600G NAS averages 25-30W idle excluding disks, ~50W with 4× 3.5" + NVMe[[71]](https://blog.patshead.com/2024/03/how-efficient-is-the-most-power-efficient-nas.html). ⚠ ECC caveat: 8000G non-PRO APUs do **not** support ECC[[80]](https://www.tomshardware.com/pc-components/cpus/amd-confirms-ryzen-8000g-apus-dont-support-ecc-ram-despite-initial-claims); Ryzen 7000 ECC works on ASRock Rack via AGESA but is officially unsupported[[79]](https://sunshowers.io/posts/am5-ryzen-7000-ecc-ram/).

### Tier 3 — ASRock Rack server-grade (≈$1,500-3,000 diskless)

- **ASRock Rack B650D4U** µATX, ~$264 — AM5 / EPYC 4004/4005, DDR5 ECC UDIMM, PCIe 5.0, onboard IPMI.[[66]](https://www.asrockrack.com/general/productdetail.asp?Model=B650D4U) A dual-10GbE B650D4U-2L2T/BCM variant exists for builders who want server NICs.
- **ASRock Rack X570D4I-2T** mini-ITX, ~$451 — AM4 + dual 10GbE + ECC.[[65]](https://www.amazon.com/Mini-ITX-Motherboard-Generation-Processors-X570D4I-2T/dp/B08FBNPVNC)
- **ASRock Rack EC266D2I** mini-ITX — Xeon E-2400, DDR5 ECC, PCIe 5.0 x16, IPMI.[[77]](https://www.asrockrack.com/general/productdetail.de.asp?Model=EC266D2I) Intel Xeon E-2400 keeps the desktop-with-validated-ECC pattern alive.[[78]](https://www.servethehome.com/intel-xeon-e-2400-series-brings-raptor-lake-to-servers/)

### Cases

| Case | Form factor | HDD bays | SSD bays | PSU | Notes |
|---|---|---|---|---|---|
| Jonsbo N2 | mini-ITX | 5 hot-swap 3.5" | 1 | SFX | Smallest hot-swap N-series[[57]](https://nascompares.com/2024/09/13/jonsbo-n5-vs-n4-vs-n3-vs-n2-nas-case-which-should-you-buy/)[[93]](https://www.amazon.com/N2-Aluminum-Support-Integrated-Removable/dp/B0BQJ6BCB7) |
| Jonsbo N3 | mini-ITX | 8× 3.5" | 1× 2.5" | SFX (≤105mm) | Canonical 8-bay home NAS chassis[[59]](https://www.amazon.com/Mini-ITX-Chassis-Computer-Aluminum-Support/dp/B0CMVBMVHT) |
| Jonsbo N4 | µATX | 6× 3.5" (4 hot-swap) | 2× 2.5" | SFX | Walnut wood option[[92]](https://www.amazon.com/N4-8-Drive-hot-swap-Chassis-USB3-2Gen2Type-C/dp/B0D1YH7D3J) |
| Jonsbo N5 | E-ATX (≤330mm) | 12 hot-swap 3.5" | 4× 2.5" | ATX | $249.99 on Newegg, 8 PCI slots[[58]](https://www.newegg.com/jonsbo-e-atx-full-tower-case-n-series-1mm-steel-plate-2mm-aluminium-plate-8mm-north-american-walnut-wood-cases-black-n5/p/2AM-006A-000F6)[[91]](https://www.amazon.com/JONSBO-Supports-Built-Veneer-Computer/dp/B0DG2N3PBB) |
| Fractal Node 304 | mini-ITX | 6× 3.5"/2.5" | — | full ATX (≤160mm) | 19.2L, three Silent R2 fans pre-installed[[68]](https://www.fractal-design.com/products/cases/node/node-304/black/) |
| Fractal Node 804 | µATX | 10× 3.5" | 2× 2.5" | ATX | ~$165, mATX cube[[69]](https://www.compsource.com/buy/FDCANODE804BLW/Fractal-Design-4112) |
| SilverStone CS381 | µATX | 8 hot-swap | 4× 2.5" | SFX/SFX-L | SAS3/SATA backplane, ~$400[[67]](https://www.servethehome.com/silverstone-cs381-review/) |
| Sliger CL520 | mini-ITX | — | M.2 only | — | $149 USA-made, all-flash only[[70]](https://www.sliger.com/) |

PSU rule of thumb: PicoPSU only at <40-50W loads; once 2.5/10GbE NICs and HDD spin-up surge enter the picture, move to Flex-ATX or SFX.[[72]](https://www.truenas.com/community/threads/flex-atx-or-picopsu.98913/) A Jonsbo N3 + CWWK N305 + 32GB DDR5 + TrueNAS SCALE diskless build totals ~$650-770.[[74]](https://selfhosting.sh/hardware/diy-nas-build/)

## ECC, ZFS, IPMI — what's actually required

The "ZFS demands ECC" religion outpaces the data. Matt Ahrens (ZFS co-creator): "there's nothing special about ZFS that requires/encourages the use of ECC RAM more so than any other filesystem"; he still recommends ECC + a checksumming filesystem if you care about your data.[[75]](https://news.ycombinator.com/item?id=18480016) Jim Salter dismantled the "scrub of death" myth — for corrupted data to overwrite good data, ZFS would need to flip bits in corrupted blocks such that they match their checksums, a 1-in-2^256 chance with default SHA validation.[[76]](https://jrs-s.net/2015/02/03/will-zfs-and-non-ecc-ram-kill-your-data/) Practical ZFS / OpenZFS forum consensus: use ECC if your platform supports it, do not avoid ZFS if it does not — ZFS without ECC is still better than ext4/NTFS without ECC.[[84]](https://discourse.practicalzfs.com/t/ecc-memory-is-how-important/4167)

ECC at homelab budget in 2026:

| Path | Memory | IPMI | Notes |
|---|---|---|---|
| Intel N97/N305 In-Band ECC | LPDDR5 only | ✗ | Requires dual-channel **soldered** LPDDR5 — SO-DIMM doesn't qualify[[81]](https://medium.com/@hassanalisardar001/best-mini-itx-motherboard-for-nas-n100-low-power-vs-ecc-f55932fa550b) |
| ASRock Rack B650D4U (AM5) | DDR5 ECC UDIMM | ✓ | Cleanest AM5 path[[66]](https://www.asrockrack.com/general/productdetail.asp?Model=B650D4U) |
| ASRock Rack EC266D2I (Xeon E-2400) | DDR5 ECC | ✓ | Cleanest Intel path[[77]](https://www.asrockrack.com/general/productdetail.de.asp?Model=EC266D2I) |
| Ryzen 7000 non-PRO on ASRock Rack | DDR5 ECC | ✓ | ⚠ Unofficial via AGESA[[79]](https://sunshowers.io/posts/am5-ryzen-7000-ecc-ram/) |
| Ryzen 8000G non-PRO | — | — | ✗ ECC not supported, OEM PRO only[[80]](https://www.tomshardware.com/pc-components/cpus/amd-confirms-ryzen-8000g-apus-dont-support-ecc-ram-despite-initial-claims) |
| Minisforum N5 Pro / Aoostar WTR Max | DDR5 ECC SODIMM | ✗ | Prebuilt ECC without IPMI[[44]](https://store.minisforum.com/products/minisforum-n5-pro-ai-nas)[[87]](https://www.amazon.com/AOOSTAR-WTR-MAX-Ports%EF%BC%8CUSB4-Port%EF%BC%8CSupport/dp/B0G25LTBDZ) |

If your motherboard lacks a BMC, an external KVM-over-IP adapter delivers most of the value:

- **PiKVM V4** — 1920×1200@60Hz, 35-50ms latency, ATX power control, virtual mass storage, native Tailscale/WireGuard. Industrial-grade.[[82]](https://pikvm.org/)
- **JetKVM** — $69, 1080p60 H.264 at 30-60ms, RJ12 extension port for ATX power and serial console.[[83]](https://www.cnx-software.com/2025/03/21/jetkvm-a-69-kvm-over-ip-solution-with-open-source-software/)
- Used Lenovo / Dell Tiny PCs lack BMCs entirely — pair them with PiKVM/JetKVM if remote console matters.

## Storage capacity & expansion ceilings

| Platform | HDD bays | M.2 NVMe | PCIe slot | External |
|---|---|---|---|---|
| Beelink ME mini | 0 | 6 | — | USB |
| UGREEN DXP4800 Plus | 4 | 2 | — | USB |
| UGREEN DXP8800 Plus | 8 | 2 | half-height PCIe 4.0 x4, ⚠ awkward access[[85]](https://nas.ugreen.com/products/ugreen-nasync-dxp8800-plus-nas-storage)[[105]](https://nascompares.com/2024/04/26/ugreen-dxp8800-plus-nas-review/) | USB |
| Aoostar WTR Max | 6 | 5 (mixed lanes 1.6-2.9 GB/s)[[87]](https://www.amazon.com/AOOSTAR-WTR-MAX-Ports%EF%BC%8CUSB4-Port%EF%BC%8CSupport/dp/B0G25LTBDZ) | OCuLink, USB4 | OCuLink |
| UGREEN DXP480T Plus | 0 | 4 | — | USB[[86]](https://nas-uk.ugreen.com/products/ugreen-4-slot-m2-nvme-nas) |
| Asustor FlashStor 12 Pro | 0 | 12 (asymmetric: 2× PCIe 4.0 x4, 3× x2 + 1× x2, 4× x1, 2× PCIe 3.0 x1)[[90]](https://www.thefpsreview.com/2024/11/14/asustor-flashstor-gen2-series-released-quad-core-3-8-ghz-amd-ryzen-cpu-ecc-ddr5-ram-2x-usb4-10-gigabit-ethernet-pcie-4-0-and-12-m-2-slots-for-nvme-ssds/) | — | USB |
| Jonsbo N3 + CWWK N305 | 6-8 | 2 | 1× PCIe x1 | — |
| Jonsbo N5 + ASRock Rack | 12 | 2-3 | full ATX, 8 slots | HBA-driven |

When motherboard SATA runs out, the **LSI 9300-8i** is still the canonical 12Gb/s SAS HBA — 8 ports, PCIe 3.0 x8, up to 1024 devices via expanders.[[94]](https://www.storagereview.com/review/lsi-sas-9300-8i-and-9300-8e-hbas-review)[[95]](https://www.servethehome.com/buyers-guides/top-hardware-components-napp-omnios-nas-servers/top-picks-for-napp-it-and-omnios-hbas-host-bus-adapters/) Drop one into a Jonsbo N5 or SilverStone CS381 build and you scale to 12-24 drives without rebuilding.

⚠ **USB-attached DAS is hazardous for ZFS pools.** TrueNAS warns explicitly against it[[96]](https://www.truenas.com/community/threads/why-you-should-avoid-usb-attached-drives-for-data-pool-disks.104596/). [openzfs/zfs](https://github.com/openzfs/zfs) ⭐ 12k discussions describe Zen/Zen2 + UAS producing checksum and I/O errors[[97]](https://github.com/openzfs/zfs/discussions/11741); transient USB resets can lock the entire pool until forced reboot, sometimes with data loss[[98]](https://github.com/openzfs/zfs/issues/12007). Hardware-RAID DAS like the **TerraMaster D5-300** (5-bay USB 3.1, RAID 0/1/5/10/JBOD) is safer because the host sees one logical volume rather than raw disks.[[99]](https://www.amazon.com/TerraMaster-External-Enclosure-Support-Diskless/dp/B005IOLBT2)

**Scale up vs. scale out.** Backblaze 2025 fleet AFR fell to 1.36% and 20TB+ drives are now ~23% of fleet[[100]](https://www.backblaze.com/blog/backblaze-drive-stats-for-2025/); the 24TB ST24000NM002H posted 1.11% AFR Q1 2025[[101]](https://www.backblaze.com/blog/backblaze-drive-stats-for-q1-2025/). The catch: 24TB rebuilds run 2-3 days because sequential write speeds haven't kept up with capacity[[102]](https://www.actualtechmedia.com/io/raid-disk-rebuild-times/), and IBM recommends RAID-6 over RAID-5 for 20TB+ drives because URE probability during single-parity rebuild becomes unacceptable[[103]](https://www.ibm.com/support/pages/re-evaluating-raid-5-and-raid-6-slower-larger-drives). A 6-bay desktop NAS in RAID-5 with 24TB drives delivers 100TB+ usable[[104]](https://www.newegg.com/insider/nas-storage-explained-how-to-build-the-right-capacity-for-your-data-in-2026/) — past the practical ceiling for most home users. → Buy fewer, bigger drives; run RAID-6 / RAIDZ2.

## Final shortlist by profile

| Profile | Pick | Why |
|---|---|---|
| **All-flash, lowest power** | Beelink ME mini | $209-329, ~7W idle, 6× NVMe[[49]](https://nascompares.com/review/beelink-me-mini-nas-review/)[[50]](https://www.techradar.com/computing/beelink-me-mini-nas-mini-pc-review) |
| **Synology replacement, 4-6 HDD** | UGREEN DXP4800 Plus or DXP6800 Pro | 10GbE, BYO-OS friendly, 2-year warranty[[29]](https://nas.ugreen.com/products/ugreen-nasync-dxp4800-plus-nas-storage)[[30]](https://nas.ugreen.com/products/ugreen-nasync-dxp6800-pro-nas-storage)[[34]](https://nascompares.com/guide/truenas-on-a-ugreen-nas-installation-guide/) |
| **Maximum bays prebuilt** | UGREEN DXP8800 Plus or Aoostar WTR Max | 8 SATA / 11 mixed bays + dual 10GbE[[31]](https://nascompares.com/guide/the-ugreen-nasync-nas-dxp2800-dxp4800-dxp6800-dxp8800-and-dxp480t-should-you-buy/)[[36]](https://nascompares.com/review/aoostar-wtr-max-nas-review-nas-perfection/) |
| **DIY 8-bay budget** | Jonsbo N3 + CWWK i3-N305 + 32GB DDR5 | $650-770 diskless[[74]](https://selfhosting.sh/hardware/diy-nas-build/) |
| **DIY 12-bay scale-out** | Jonsbo N5 + ASRock Rack B650D4U + LSI 9300-8i | ECC, IPMI, 12 HDD + HBA[[58]](https://www.newegg.com/jonsbo-e-atx-full-tower-case-n-series-1mm-steel-plate-2mm-aluminium-plate-8mm-north-american-walnut-wood-cases-black-n5/p/2AM-006A-000F6)[[66]](https://www.asrockrack.com/general/productdetail.asp?Model=B650D4U)[[94]](https://www.storagereview.com/review/lsi-sas-9300-8i-and-9300-8e-hbas-review) |
| **Used enterprise / cluster** | Lenovo M720q / M90q + JetKVM | $100-150 + $69 KVM[[7]](https://2ndboot.com/mini-pc-buying-guide-2026/)[[20]](https://www.servethehome.com/lenovo-thinkcentre-m90q-tiny-gen2-tinyminimicro-review-intel/4/)[[83]](https://www.cnx-software.com/2025/03/21/jetkvm-a-69-kvm-over-ip-solution-with-open-source-software/) |
| **ECC + IPMI compact** | ASRock Rack EC266D2I + Xeon E-2400 + Jonsbo N3 | Compact, ECC, BMC[[77]](https://www.asrockrack.com/general/productdetail.de.asp?Model=EC266D2I)[[78]](https://www.servethehome.com/intel-xeon-e-2400-series-brings-raptor-lake-to-servers/) |
| **Replacing a Pi for general home server** | Beelink S12 Pro N100 | 4× perf, x86, NVMe, 16GB at same accessorized price[[9]](https://www.xda-developers.com/intel-n100-killed-raspberry-pi-home-servers/) |

**Avoid:**
- ✗ SBC / Raspberry Pi for general home server — no Quick Sync transcoding; ARM cores can't keep up with even one 1080p software transcode.[[10]](https://selfhosting.sh/hardware/raspberry-pi-home-server/)
- ✗ USB-DAS for any ZFS pool.[[96]](https://www.truenas.com/community/threads/why-you-should-avoid-usb-attached-drives-for-data-pool-disks.104596/)[[97]](https://github.com/openzfs/zfs/discussions/11741)[[98]](https://github.com/openzfs/zfs/issues/12007)
- ✗ Non-PRO 8000G if you want ECC.[[80]](https://www.tomshardware.com/pc-components/cpus/amd-confirms-ryzen-8000g-apus-dont-support-ecc-ram-despite-initial-claims)
- ✗ Synology Plus 2025+ with existing third-party 16TB+ drives.[[3]](https://www.servethehome.com/synology-lost-the-plot-with-hard-drive-locking-move/)[[4]](https://www.synoforum.com/threads/synology-2025-nas-hard-drive-and-ssd-lock-in-confirmed-bye-bye-seagate-and-wd.14682/)
- ✗ Topton/CWWK boards for "I want a warranty" buyers — generic Chinese silicon, no clear support path.[[12]](https://homenode.tech/ultimate-guide-building-nas-want-build-hurts-2026/)
