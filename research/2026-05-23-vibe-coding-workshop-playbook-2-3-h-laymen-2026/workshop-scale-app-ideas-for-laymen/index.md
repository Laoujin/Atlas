---
title: "Workshop-scale app ideas for laymen"
date: 2026-05-23
depth: deep
format: md
topic: "Workshop-scale app ideas for laymen"
topic_raw: "Workshop-scale app ideas for laymen"
issue: 56
tags: [vibe-coding, workshop, app-ideas, beginners, lovable, bolt, project-ideas]
cover: cover.svg
summary: "Five reliable app-idea menus that a non-developer can ship in 2-3 hours with an AI builder, plus the failure modes to swap out."
citations: 58
reading_time_min: 16
cost_usd: 10.34
duration_sec: 834
model: "Opus 4.7"
---

> **TL;DR.** For a 2-3 hour layman vibe-coding workshop, lock the scope shape to **single user, single screen, no auth, localStorage-or-nothing persistence** — the "rectangle of stuff on a page" pattern [[1]](https://wisedesk.fyi/vibe-coding/vibe-coding-ideas-for-beginners/) [[86]](https://justinmckelvey.com/blog/vibe-coding-examples). From that shape, five reliable menus stack roughly by technical depth: **(1) calculators and personal trackers** (tip, BMI, habit, expense splitter) [[12]](https://www.dyad.sh/blog/vibe-coding-project-ideas) [[13]](https://vibecoding.app/blog/how-to-vibe-code), **(2) decision toys and generators** (random-restaurant wheel, name generator, Wordle clone) [[19]](https://v0.app/chat/random-restaurant-picker-vdNJgvws2l7) [[35]](https://medium.com/@basil.chatha8/building-a-wordle-clone-in-30min-with-ai-no-coding-experience-a948fe4c490e), **(3) fetch-and-render with one no-key API** (Open-Meteo weather card, PokéAPI Pokédex, ISS tracker) [[44]](https://open-meteo.com/) [[46]](https://pokeapi.co/) [[51]](http://open-notify.org/Open-Notify-API/ISS-Location-Now/), **(4) scratch-an-itch family or teacher utilities** (meal planner, lesson critique, baby-sleep dashboard) [[76]](https://www.aol.com/articles/im-hr-professional-vibe-coded-000001657.html) [[78]](https://www.edweek.org/technology/a-district-expects-to-save-200k-from-ai-powered-vibe-coding-heres-how/2026/05) [[80]](https://wangyi.ai/blog/2025/06/03/baby-sleep-tracker/), and **(5) micro-games** (Pong, Hangman, falling-objects catcher) [[25]](https://madewithlovable.com/categories/entertainment) [[36]](https://imagilabs.com/pages/hour-of-code-vibe-coding). The categories that consistently blow the timebox: multi-user marketplaces, real-time multiplayer, anything with payments, native mobile App Store deploys, and OAuth-provider integrations [[2]](https://www.saastr.com/the-complete-guide-to-vibe-coding-hard-won-lessons-for-building-your-first-commercial-app/) [[87]](https://www.sharetribe.com/academy/can-you-vibe-code-a-marketplace/) [[90]](https://medium.com/@a_kill_/pt-1-2-vibe-coding-my-way-to-the-app-store-539d90accc45) [[91]](https://www.geeky-gadgets.com/vibe-coding-games/) — when an attendee proposes one, swap it for the single-user variant.

## What "workshop-scale" actually means

Instructors converge on a sharp shape. Stanford's non-developer Lovable course caps four modules' output at a **to-do list or feedback form** [[8]](https://uit.stanford.edu/service/techtraining/class/vibe-coding-non-developers-build-apps-and-websites-lovabledev). Dyad's beginner guide names todos and quizzes as the sweet spot — "small enough to finish in an afternoon, complex enough to teach real patterns" — and even pins concrete UI shape: 4 multiple-choice answers, a score counter, a 30-second countdown [[12]](https://www.dyad.sh/blog/vibe-coding-project-ideas). At Singapore's 65labs, instructor Sherry Jiang puts it bluntly: "vibe coding is best suited to very simple, lightweight, straightforward consumer apps — not anything very technical" [[4]](https://www.aol.com/news/joined-vibe-coding-workshop-learn-040201765.html). The Innovation Co-Lab at Duke ran the same format in February 2026 for the same audience [[70]](https://colab.duke.edu/event/vibe-coding-beginners-02-19-2026/).

The constraint table laymen should hold their idea against:

| Axis              | Workshop-fits           | Cut to fit                         | Source                                |
|-------------------|--------------------------|------------------------------------|---------------------------------------|
| User accounts     | None (or device-local)  | OAuth/email login                  | [oauth-trap][s2], [security-tax][s10] |
| Screens           | 1 (max 2 with settings) | Multi-page navigation              | [pomodoro-mvp][s6]                    |
| Data              | localStorage or in-memory | Backend DB, RLS, schemas         | [snaplama][s9], [lovable-sec][s92]    |
| User roles        | 1                       | Buyer + seller + admin             | [marketplaces][s87]                   |
| Realtime          | None                    | Websockets, multiplayer sync       | [kills-the-vibe][s91]                 |
| Money flow        | None                    | Stripe, refunds, idempotency       | [pay-edges][s88]                      |
| Native            | Web only (deployed URL) | iOS/Android App Store              | [70-30-debug][s90]                    |
| Third-party SaaS  | None or 1 no-key API    | Twilio/SendGrid + key plumbing     | [twilio-setup][s93]                   |

[s2]: https://www.saastr.com/the-complete-guide-to-vibe-coding-hard-won-lessons-for-building-your-first-commercial-app/
[s6]: https://calvinjku.medium.com/it-took-me-three-months-to-vibe-code-a-simple-pomodoro-app-a5bd57eee144
[s9]: https://www.snaplama.com/blog/how-to-create-app-in-lovable-step-by-step-guide
[s10]: https://sola.security/blog/vibe-coding-security-vulnerabilities/
[s87]: https://www.sharetribe.com/academy/can-you-vibe-code-a-marketplace/
[s88]: https://roobykon.com/blog/posts/vibe-coding-for-marketplaces
[s90]: https://medium.com/@a_kill_/pt-1-2-vibe-coding-my-way-to-the-app-store-539d90accc45
[s91]: https://www.geeky-gadgets.com/vibe-coding-games/
[s92]: https://docs.lovable.dev/tips-tricks/avoiding-security-pitfalls
[s93]: https://www.twilio.com/en-us/blog/developers/vibe-coding-with-an-agent-and-twilio-sms

The "last 10% is 90%" effect is real. Calvin Ku reached 90% on a "simple" Pomodoro in three days and then spent months on the last 10% once OAuth, accessibility, and DB wiring entered scope — his post-mortem rule: **one primary loop and one settings screen, defer everything else** [[6]](https://calvinjku.medium.com/it-took-me-three-months-to-vibe-code-a-simple-pomodoro-app-a5bd57eee144). Over 60% of security issues in vibe-coded apps come from the moment login enters the picture — missing row-level security, exposed API keys, client-side-only auth, IDOR — and beginners cannot debug any of these live [[10]](https://sola.security/blog/vibe-coding-security-vulnerabilities/) [[92]](https://docs.lovable.dev/tips-tricks/avoiding-security-pitfalls). Tool choice should match scope too: v0 or Tempo for a single component or landing page; Lovable, Bolt, or Replit only when stored data is actually needed [[5]](https://lovable.dev/guides/vibe-coding-apps-8-options-for-beginners). Five minutes of up-front "one paragraph + screens list" documentation saves hours of redirects later [[7]](https://base44.com/blog/common-vibe-coding-mistakes).

## Menu 1 — Calculators and personal trackers

The safest first project. Each fits one screen, ≤3 inputs, and either localStorage or no persistence at all.

| App                          | What it does                                            | Persistence  | Source                                |
|------------------------------|---------------------------------------------------------|--------------|---------------------------------------|
| [Tip Calculator][m1a]        | Bill × tip % ÷ people, with 15/18/20/25 % presets       | none         | [vibecoding.app][m1b]                 |
| [Pomodoro Timer][m1c]        | 25-min focus, browser notification, task list           | localStorage | [Ann Jose build][m1d], [Dyad][m1e]    |
| [Habit Tracker][m1f]         | Named habit, emoji icon, 30-day streak grid             | localStorage | [Questera 2026 roadmap][m1g]          |
| [BMI Buddy][m1h]             | Height + weight → BMI + category                        | none         | [Lovable deploy][m1h]                 |
| [AllCalculator BMI][m1i]     | Same shape, second worked example                       | none         | [Lovable deploy][m1i]                 |
| [Simple Mortgage Calc][m1j]  | Principal + rate + term → monthly payment               | none         | [Lovable deploy][m1j]                 |
| [Handy Calc Lab][m1k]        | Bundles BMI / EMI / Age / GST / interest                | none         | [Lovable deploy][m1k]                 |
| [Event Countdown][m1l]       | Birthday/wedding countdown, multi-event list            | localStorage | [Lovable deploy][m1l]                 |
| [Meeting Cost Calculator][m1m] | Attendees × rate × duration → $ wasted                | none         | [Taskade 2026 list][m1m]              |
| [Expense Splitter][m1n]      | Group expenses → minimum-transfer settlement            | localStorage | [Devpost Bolt build][m1n]             |

[m1a]: https://vibecoding.app/blog/how-to-vibe-code
[m1b]: https://vibecoding.app/blog/how-to-vibe-code
[m1c]: https://annjose.com/post/vibe-coding-pomodoro-app/
[m1d]: https://annjose.com/post/vibe-coding-pomodoro-app/
[m1e]: https://www.dyad.sh/blog/vibe-coding-project-ideas
[m1f]: https://www.questera.ai/blogs/vibe-coding-for-beginners-complete-starter-roadmap-2026
[m1g]: https://www.questera.ai/blogs/vibe-coding-for-beginners-complete-starter-roadmap-2026
[m1h]: https://bmi-buddy-site.lovable.app/
[m1i]: https://allcalculator.lovable.app/bmi
[m1j]: https://simple-mortgage-calculator-web-app.lovable.app/
[m1k]: https://handy-calc-lab.lovable.app/bmi-calculator
[m1l]: https://my-custom-event-countdown.lovable.app/
[m1m]: https://www.taskade.com/blog/vibe-calculator-apps
[m1n]: https://devpost.com/software/modern-expense-splitter-calculator

The tip calculator [[13]](https://vibecoding.app/blog/how-to-vibe-code), Ann Jose's themed Pomodoro Flow [[22]](https://annjose.com/post/vibe-coding-pomodoro-app/), Questera's habit-tracker template [[71]](https://www.questera.ai/blogs/vibe-coding-for-beginners-complete-starter-roadmap-2026), and the four Lovable-deployed calculators [[15]](https://allcalculator.lovable.app/bmi) [[16]](https://bmi-buddy-site.lovable.app/) [[17]](https://simple-mortgage-calculator-web-app.lovable.app/) [[24]](https://handy-calc-lab.lovable.app/bmi-calculator) all demonstrate the same structural pattern: one input form, one output panel, one optional localStorage list. Event Countdown [[18]](https://my-custom-event-countdown.lovable.app/) and the Devpost expense splitter [[23]](https://devpost.com/software/modern-expense-splitter-calculator) push the high end of "still fits in 2-3 hours" — useful when an attendee wants a slightly meatier challenge. Taskade's 2026 calculator roundup adds Meeting Cost Calc, QR Code Studio, Color Palette Extractor and Multiplication Playground in the same scope band [[14]](https://www.taskade.com/blog/vibe-calculator-apps).

## Menu 2 — Decision toys, generators, and word games

Higher fun-per-prompt ratio than calculators. Output is the whole point, so attendees iterate on **what comes out** rather than **what gets stored**.

| App                       | What it does                                                | Source                                |
|---------------------------|-------------------------------------------------------------|---------------------------------------|
| [Random Restaurant Picker][m2a] | One button → random restaurant from your list         | [v0 community][m2a]                   |
| [Whee'Lunch][m2b]         | Spin-the-wheel lunch decider                                | [Vercel deploy][m2b]                  |
| [WheelWise][m2c]          | Generic random picker — names, winners, yes/no              | [Vercel deploy][m2c]                  |
| [Roblox Name Generator][m2d] | Stylised random username generator                       | [Lovable deploy][m2d]                 |
| [My Poké Creator][m2e]    | Random Pokémon-style character generator                    | [Lovable deploy][m2e]                 |
| [yes-no tarot ai][m2f]    | Novelty tarot oracle, single-card answer                    | [Lovable deploy][m2f]                 |
| [Meowmoire][m2g]          | Upload cat photo → shareable meme                           | [Lovable deploy][m2g]                 |
| [Mixels.ai][m2h]          | AI pixel-art generator and editor                           | [Lovable deploy][m2h]                 |
| [Mighty Drums][m2i]       | Step-sequencer drum machine with MIDI export                | [Lovable deploy][m2i]                 |
| [Gradient Generator][m2j] | Pick HSL stops → live gradient + CSS                        | [Lovable how-to][m2j]                 |
| [ToolsFlow Color Picker][m2k] | HEX / RGB / HSL converter                               | [Lovable deploy][m2k]                 |
| [Wordle clone (30-min)][m2l] | Five-letter daily word, Wordle-style colour feedback     | [Medium write-up][m2l]                |
| [QuizGenius][m2m]         | Make-or-take AI-generated trivia quizzes                    | [Lovable deploy][m2m]                 |

[m2a]: https://v0.app/chat/random-restaurant-picker-vdNJgvws2l7
[m2b]: https://wheelunch.vercel.app/
[m2c]: https://wheel-wise-roan.vercel.app/
[m2d]: https://roblox-name-generator.lovable.app
[m2e]: https://www.mypokecreator.com
[m2f]: https://yesnotarotai.com/
[m2g]: https://www.meowmoire.com
[m2h]: https://mixels.ai/
[m2i]: https://beatmaker.midimighty.com
[m2j]: https://lovable.dev/how-to/productivity-tools/gradient-generator
[m2k]: https://toolsflow.lovable.app/color-picker
[m2l]: https://medium.com/@basil.chatha8/building-a-wordle-clone-in-30min-with-ai-no-coding-experience-a948fe4c490e
[m2m]: https://quiz-genius-ai-fun.lovable.app

A non-coder documented building the Wordle clone above end-to-end in **30 minutes** with v0.dev plus shadcn — well under one workshop block [[35]](https://medium.com/@basil.chatha8/building-a-wordle-clone-in-30min-with-ai-no-coding-experience-a948fe4c490e). The "boring random name" generator pattern shows up across Roblox Name Generator [[28]](https://roblox-name-generator.lovable.app), My Poké Creator [[30]](https://www.mypokecreator.com), and the wheels [[20]](https://wheelunch.vercel.app/) [[21]](https://wheel-wise-roan.vercel.app/) — all built on the same `randomChoice(array)` skeleton. Lovable explicitly publishes a "Build Interactive Games in Minutes" page [[39]](https://lovable.dev/solutions/use-case/front-end-app-interactive-games) and a step-by-step gradient-generator how-to [[43]](https://lovable.dev/how-to/productivity-tools/gradient-generator); Bolt launched an official community Gallery in 2025 specifically to surface this scale of project [[41]](https://bolt.new/~/gallery). For a more curated source pool, Questera's 2025 ideas list adds AI meme generator, mood-playlist generator, interactive story engine, and generative art gallery in the same band [[40]](https://www.questera.ai/blogs/12-vibe-coding-projects-to-try-out-in-2025).

## Menu 3 — Fetch-and-render with one no-key API

Promote attendees from "stuff stored in my browser" to "I called a real internet thing". Hard rule: **one API, no auth, no key juggling**. Mixed Analytics's 2026 curated list is the canonical menu instructors pick from [[67]](https://mixedanalytics.com/blog/list-actually-free-open-no-auth-needed-apis/).

| App archetype             | API                  | Why it fits                                | Sources                                 |
|---------------------------|----------------------|---------------------------------------------|-----------------------------------------|
| Weather card              | [Open-Meteo][a1a]    | No key, no sign-up, no credit card          | [docs][a1a], [DEV tutorial][a1b]        |
| Pokédex                   | [PokeAPI][a2a]       | 100 req/IP/min, no auth                     | [docs][a2a], [JQQ vanilla-JS][a2b]      |
| Currency converter        | [Frankfurter][a3a]   | 200 currencies, no key                      | [docs][a3a]                             |
| Random-dog button         | [Dog CEO][a4a]       | One-endpoint random image                   | [docs][a4a], [DEV walkthrough][a4b]     |
| ISS live tracker          | [Open Notify][a5a]   | lat/lon now + pass-times                    | [docs][a5a], [101 Computing][a5b]       |
| Astronomy picture of day  | [NASA APOD][a6a]     | `DEMO_KEY` works out of the box             | [docs][a6a], [APOD app guide][a6b]      |
| Address on a map          | [Leaflet + OSM][a7a] | Pan/zoom + Nominatim geocode, no key        | [Leaflet][a7a], [Nominatim demo][a7b]   |
| Dad-joke / advice card    | [icanhazdadjoke][a8a] | Plain GET, JSON via Accept header          | [docs][a8a], [Wes Bos][a8b]             |
| Random joke or advice     | [Advice Slip][a9a] / [JokeAPI][a9b] / [Chuck Norris][a9c] | All no-auth      | [Advice][a9a], [JokeAPI][a9b], [Chuck][a9c] |
| Trivia quiz               | [Open Trivia DB][a10a] | Categorised Q&A, no auth                  | [docs][a10a]                            |
| Recipe finder             | [TheMealDB][a11a]    | Random + search by ingredient               | [docs][a11a], [Tuts+ build][a11b]       |
| Word definition           | [Free Dictionary][a12a] | GET-only `/api/v2/entries/en/<word>`     | [docs][a12a]                            |
| Wikipedia card            | [MediaWiki REST][a13a] | `/page/summary/<title>` for topic blurb   | [docs][a13a]                            |
| Next SpaceX launch        | [SpaceX REST][a14a]  | `/latest` and `/next` mission JSON          | [docs][a14a]                            |

[a1a]: https://open-meteo.com/
[a1b]: https://dev.to/0012303/open-meteo-api-free-weather-data-for-any-location-no-key-no-limits-no-bs-2j2
[a2a]: https://pokeapi.co/
[a2b]: https://www.jamesqquick.com/blog/build-a-pokedex-with-vanilla-javascript/
[a3a]: https://frankfurter.dev/
[a4a]: https://dog.ceo/dog-api/
[a4b]: https://dev.to/terieyenike/dog-app-using-javascript-with-an-api-j09
[a5a]: http://open-notify.org/Open-Notify-API/ISS-Location-Now/
[a5b]: https://www.101computing.net/real-time-iss-tracker/
[a6a]: https://api.nasa.gov/
[a6b]: https://medium.com/@HardikKawale/explore-the-universe-create-your-nasa-apod-web-app-step-by-step-guide-bc0e283929de
[a7a]: https://leafletjs.com/examples.html
[a7b]: https://derickrethans.nl/leaflet-and-nominatim.html
[a8a]: https://icanhazdadjoke.com/api
[a8b]: https://wesbos.com/javascript/13-ajax-and-fetching-data/76-dad-jokes
[a9a]: https://api.adviceslip.com/
[a9b]: https://sv443.net/jokeapi/v2/
[a9c]: https://api.chucknorris.io/
[a10a]: https://opentdb.com/api_config.php
[a11a]: https://www.themealdb.com/api.php
[a11b]: https://webdesign.tutsplus.com/recipe-search-tool-using-javascript-and-themealdb-api--cms-93090t
[a12a]: https://dictionaryapi.dev/
[a13a]: https://api.mediawiki.org/wiki/Getting_started_with_Wikimedia_APIs
[a14a]: https://api.spacexdata.com/

Open-Meteo is the strongest single starting point — explicitly **no API key, no sign-up, no credit card** with a CC-BY JSON feed and 10K free daily calls [[44]](https://open-meteo.com/), and there is a March 2026 DEV tutorial that walks a layman through the entire fetch [[45]](https://dev.to/0012303/open-meteo-api-free-weather-data-for-any-location-no-key-no-limits-no-bs-2j2). PokéAPI is the second-most-cited beginner target [[46]](https://pokeapi.co/) with James Q Quick's vanilla-JS Pokédex as the canonical short tutorial [[47]](https://www.jamesqquick.com/blog/build-a-pokedex-with-vanilla-javascript/). The full archetype set is canonised in Strapi's 2026 portfolio list (weather dashboard, movie search, currency converter, recipe app) [[68]](https://strapi.io/blog/api-project-ideas) and DEV's "12 free and fun APIs" mapping [[69]](https://dev.to/mukeshkuiry/12-free-and-fun-api-for-your-next-project-5eem).

## Menu 4 — Scratch-an-itch apps (with real human stories)

The most motivating menu for laymen, because the build is **about them**. Use these as inspiration framing during the workshop's "what should I build?" opening.

| Builder                  | App                          | Tool / time             | Source                              |
|--------------------------|------------------------------|--------------------------|-------------------------------------|
| Kevin Roose (journalist) | [LunchBox Buddy][p1] — fridge photo → lunch ideas | Bolt, ~10 min       | [NYT][p1]                           |
| Laura Zaccaria (HR)      | Family Meal Planner          | Cursor, evenings         | [AOL/Insider][p2]                   |
| Harshal Patil (PM)       | Tinder-style baby-name ranker | Lovable, 1h 15m         | [own blog][p3]                      |
| Michael Dugmore (eng)    | Weekly Family Planner (WeekDoc) | Cloudflare, Christmas break | [own blog][p4]                  |
| Miguel Parente (PM/dad)  | BrincaIdea — toy photos → playtime ideas | Cursor + v0    | [Medium][p5]                        |
| Arlyn Gajilan (editor)   | Tobey's Tutor — AI tutor for dyslexic son | Feb→June 2025  | [Scientific American][p6]           |
| Juliann Nelson (PM)      | Personal habit tracker       | Windsurf + Claude, 1 day | [Medium][p7]                        |
| Yi (parent)              | Baby Sleep Tracker (Nanit re-render) | Cursor, weekend  | [own blog][p8]                      |
| Karima Williams (non-coder) | Crash Out Diary — emotional venting | Claude + Lovable | [Essence][p9]                     |
| Peninsula SD biology teacher | LessonLens — AI lesson-video critique | Claude Code  | [EdWeek][p10]                       |
| James Cantonwine (Peninsula SD) | Scholarship search, CTE budget, school-comparison | Claude Code | [EdWeek][p10]                  |
| Cynthia Chen (designer)  | Dog-e-dex — snap-a-dog Pokédex | Claude + Replit/Cursor, 2 months | [Yahoo Tech][p11]              |
| Doher Pablo (employee)   | Travel-receipt expense app   | Power Apps + Copilot, 2h | [Microsoft Source][p12]             |
| MS leaders + kids        | Lemonade-stand manager, homework tracker, "nightmare-management" | GitHub Spark, ~20m each | [Microsoft Source][p12] |

[p1]: https://www.nytimes.com/2025/02/27/technology/personaltech/vibecoding-ai-software-programming.html
[p2]: https://www.aol.com/articles/im-hr-professional-vibe-coded-000001657.html
[p3]: https://www.harshal-patil.com/post/lovable-family-app-vibe-coding-2025h1
[p4]: https://michael-dugmore.pages.dev/p/family-planner-vibe-coding-rules-and-weekdoc/
[p5]: https://miguelparente.medium.com/when-parenting-meets-vibe-coding-making-every-playtime-special-d4b306672c59
[p6]: https://www.scientificamerican.com/article/how-one-mom-used-vibe-coding-to-build-an-ai-tutor-for-her-dyslexic-son/
[p7]: https://medium.com/@julianntnelson/my-first-vibe-coding-project-building-a-habit-tracker-app-with-ai-ffafaea9897f
[p8]: https://wangyi.ai/blog/2025/06/03/baby-sleep-tracker/
[p9]: https://www.essence.com/lifestyle/health-wellness/crash-out-diary/
[p10]: https://www.edweek.org/technology/a-district-expects-to-save-200k-from-ai-powered-vibe-coding-heres-how/2026/05
[p11]: https://tech.yahoo.com/apps/articles/block-product-designer-spent-2-000001720.html
[p12]: https://news.microsoft.com/source/features/ai/vibe-coding-and-other-ways-ai-is-changing-who-can-build-apps-and-how/

The pattern across these cases: **a specific person solving a specific problem in their own life**, not a generic tutorial example. Roose's LunchBox Buddy shipped in roughly 10 minutes [[83]](https://www.nytimes.com/2025/02/27/technology/personaltech/vibecoding-ai-software-programming.html). Patil's baby-name ranker — ELO scoring, 10-accent pronunciation preview — took 75 minutes on Lovable's free tier [[75]](https://www.harshal-patil.com/post/lovable-family-app-vibe-coding-2025h1). Peninsula SD reports building tools that replaced $30-40K commercial products in a few hours [[78]](https://www.edweek.org/technology/a-district-expects-to-save-200k-from-ai-powered-vibe-coding-heres-how/2026/05). Microsoft's case study has a non-technical employee shipping a 2-hour expense app and parents-with-kids building lemonade-stand managers and "nightmare-management" apps in ~20-minute sessions [[81]](https://news.microsoft.com/source/features/ai/vibe-coding-and-other-ways-ai-is-changing-who-can-build-apps-and-how/). The Vibe Coder Blog's 2026 kids guide names the four archetypes that work best for the youngest builders: flashcard quiz, collection tracker, tiny browser game, gratitude/mood journal [[85]](https://blog.vibecoder.me/vibe-coding-for-kids-first-app).

Use these stories at the start of the workshop ⚠ before participants try to invent something. The single biggest scope-down lever is **"build the thing you genuinely need this week"** — it limits feature creep because the builder knows when it is enough.

## Menu 5 — Micro-games (under 200 lines of state)

Games are the most popular ask in mixed-audience workshops, so have a short list ready. Stick to single-player or hot-seat; **never real-time multiplayer** [[91]](https://www.geeky-gadgets.com/vibe-coding-games/).

| Game                  | Mechanic                                       | Source / reference deploy             |
|-----------------------|------------------------------------------------|---------------------------------------|
| [Falling-objects catch][g1] | Move paddle to catch falling treats      | [imagi × Lovable Hour of Code][g1]      |
| [Pong][g2]            | Two paddles, one ball, score to 10              | [Retro Paddle Battle][g2]             |
| [Hangman][g3]         | 5-min word timer, alphabet keyboard             | [Hangin' Man][g3]                     |
| [Wordle clone][g4]    | 5-letter daily word, color feedback             | [30-min build][g4]                    |
| Asteroids             | Single ship, rotate + thrust + shoot            | [madewithlovable showcase][g5]        |
| CandyClicker          | One button, incrementing counter, upgrades       | [madewithlovable][g5]                 |
| Anxiety Balloon Pop   | Tap to pop, calming variant of whack-a-mole     | [madewithlovable][g5]                 |
| DOOMscroll            | Browser game *about* doomscrolling              | [HN thread][g6]                       |
| Piece Together        | Animated jigsaw puzzles                         | [HN thread][g6]                       |
| Latin Learner         | Flashcards (Anki-lite)                          | [HN thread][g6]                       |

[g1]: https://imagilabs.com/pages/hour-of-code-vibe-coding
[g2]: https://retro-paddle-battle-fun.lovable.app
[g3]: https://www.hanginman.xyz/
[g4]: https://medium.com/@basil.chatha8/building-a-wordle-clone-in-30min-with-ai-no-coding-experience-a948fe4c490e
[g5]: https://madewithlovable.com/categories/entertainment
[g6]: https://news.ycombinator.com/item?id=45642527

The imagi × Lovable Hour of Code canonised the **falling-objects catcher** as the first vibe-coded game template — class-tested across schools — and the prompt that works is concretely "create a game where a cat catches falling treats and earns points" [[36]](https://imagilabs.com/pages/hour-of-code-vibe-coding). madewithlovable's entertainment showcase enumerates Pong, Asteroids, CandyClicker, Hangin' Man and Anxiety Balloon Pop, all hosted at public lovable.app URLs [[25]](https://madewithlovable.com/categories/entertainment) [[26]](https://retro-paddle-battle-fun.lovable.app) [[27]](https://www.hanginman.xyz/). Cursor-built quiz games scaled to 7 hours for 100 AI-generated questions [[37]](https://medium.com/@wolfe.maykut_19364/vibe-coding-how-i-built-an-ai-powered-iphone-game-in-just-7-hours-no-programming-required-457cbcf6ea66) — drop to ~20 hand-picked questions to land at 2-3 hours.

## What doesn't fit — and the swap

When an attendee proposes any of these, swap to the right-hand column on the spot. The same patterns repeat across every instructor write-up surveyed.

| Bad-fit idea                       | Why it breaks                                          | Workshop swap                                    | Source                       |
|------------------------------------|--------------------------------------------------------|---------------------------------------------------|------------------------------|
| Uber / Airbnb for X (marketplace)  | 3 user types × 3 UIs; auth + payments + admin           | Directory page with seed data + "request" form    | [Sharetribe][f1]             |
| Instagram / Twitter / TikTok clone | Uploads, feeds, auth, moderation                        | Single-user photo wall with hardcoded captions    | [McKelvey survey][f2]        |
| Stripe / Patreon / paid subscriptions | Idempotency, webhooks, refunds, disputes             | Tip-jar QR (link to existing payment URL)         | [Roobykon][f3], [McKelvey][f2] |
| Real-time multiplayer game         | Websockets, state sync, latency                         | Single-player or hot-seat on one device           | [Geeky-gadgets][f4]          |
| Native iOS/Android (App Store)     | 70 % time debugging native-platform context loss        | PWA via Lovable/Bolt — same URL, installable     | [App Store memoir][f5]       |
| OAuth login (Google / GitHub)      | RLS, exposed keys, IDOR, client-side bypass             | Local pseudonym field saved in localStorage       | [Sola Security][f6], [Lovable docs][f7] |
| Twilio SMS / SendGrid email        | Account, API keys, billing, terminal-level config       | "Copy this text" button or `mailto:` link         | [Twilio post][f8]            |
| ML training / RAG / vector DB      | Embedding pipelines, eval, infra                        | One LLM call per click via the builder's built-in | [SaaStr][f9]                 |
| "Productivity app for everyone"    | No audience, no shape                                    | One-role utility for one named person             | [Nucamp 2026][f10]           |
| Generic "social network"           | Same as Instagram clone but vaguer                      | Personal page with hardcoded "guestbook"          | [McKelvey][f2]               |

[f1]: https://www.sharetribe.com/academy/can-you-vibe-code-a-marketplace/
[f2]: https://justinmckelvey.com/blog/vibe-coding-examples
[f3]: https://roobykon.com/blog/posts/vibe-coding-for-marketplaces
[f4]: https://www.geeky-gadgets.com/vibe-coding-games/
[f5]: https://medium.com/@a_kill_/pt-1-2-vibe-coding-my-way-to-the-app-store-539d90accc45
[f6]: https://sola.security/blog/vibe-coding-security-vulnerabilities/
[f7]: https://docs.lovable.dev/tips-tricks/avoiding-security-pitfalls
[f8]: https://www.twilio.com/en-us/blog/developers/vibe-coding-with-an-agent-and-twilio-sms
[f9]: https://www.saastr.com/the-complete-guide-to-vibe-coding-hard-won-lessons-for-building-your-first-commercial-app/
[f10]: https://www.nucamp.co/blog/vibe-coding-in-2026-beginner-projects-you-can-build-and-monetize

Sharetribe's 60-hour marketplace post-mortem is the clearest case study: a forum has one user type, a marketplace has three — buyer, seller, admin — and the resulting build cascaded with seven consecutive "fixed!" declarations on one booking bug [[87]](https://www.sharetribe.com/academy/can-you-vibe-code-a-marketplace/). Roobykon adds the payment-edge-case angle: 45% of AI-generated code reportedly contains an OWASP Top 10 vulnerability, and AI consistently skips idempotency keys, webhook signatures, refund and dispute paths [[88]](https://roobykon.com/blog/posts/vibe-coding-for-marketplaces). For mobile, the App Store memoir is unambiguous: "30% of the time prompting the AI for code that works and 70% of the time debugging various errors that show up due to the AI constantly losing context" [[90]](https://medium.com/@a_kill_/pt-1-2-vibe-coding-my-way-to-the-app-store-539d90accc45). Even Twilio's own vibe-coding blog admits the setup (account, API keys, appsettings.json, terminal comfort) is itself a barrier for beginners [[93]](https://www.twilio.com/en-us/blog/developers/vibe-coding-with-an-agent-and-twilio-sms).

Hackathon facilitators report scope is the single biggest demoraliser; the facilitator's job is explicitly to **narrow it**, favouring visual / user-facing features over backend depth [[3]](https://thetechenabler.substack.com/p/hosting-a-vibe-coding-hackathon). Jiang at 65labs frames the cultural rule: "building is so fast now that it's often smarter to start over than to patch a messy product" — so accept the scope-down rather than fight it [[4]](https://www.aol.com/news/joined-vibe-coding-workshop-learn-040201765.html).

## Picking one app for your workshop

If you have to commit to a default, pick from this short list. They are picked by ratio of "successful ships" to "stuck attendees" across the sources surveyed.

1. **Tip / split calculator** — for a mixed-audience adult workshop. Single screen, instant satisfaction, mobile-first feels real [[13]](https://vibecoding.app/blog/how-to-vibe-code).
2. **Habit tracker with emoji + 30-day grid** — for participants who want something they will actually use. localStorage only [[71]](https://www.questera.ai/blogs/vibe-coding-for-beginners-complete-starter-roadmap-2026).
3. **Open-Meteo weather card for "my city"** — for the one-API milestone. No key, deploys cleanly [[44]](https://open-meteo.com/) [[45]](https://dev.to/0012303/open-meteo-api-free-weather-data-for-any-location-no-key-no-limits-no-bs-2j2).
4. **Falling-objects catcher** — for kids, classrooms, anyone who wants a game. Class-tested as Hour-of-AI canonical [[36]](https://imagilabs.com/pages/hour-of-code-vibe-coding).
5. **A scratch-an-itch tool the attendee names in the first 10 minutes** — overrides everything above. Patil and Roose both picked things that mattered to them, and that motivation carried them through [[75]](https://www.harshal-patil.com/post/lovable-family-app-vibe-coding-2025h1) [[83]](https://www.nytimes.com/2025/02/27/technology/personaltech/vibecoding-ai-software-programming.html).

Final rule of thumb for sizing → **if the attendee cannot describe the idea as "one screen with [list of widgets] and a button that does X"**, it is not workshop-scale; help them shrink it before any prompt is typed [[7]](https://base44.com/blog/common-vibe-coding-mistakes) [[12]](https://www.dyad.sh/blog/vibe-coding-project-ideas).
