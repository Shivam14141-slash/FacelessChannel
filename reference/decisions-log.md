# Orin — Decisions Log
> A record of every major decision made during project planning,
> with context and reasoning. Read-only reference document.
> Source: Initial planning conversation (June 2026)

---

## 1. Why We Started This Project

**Context:**
- Owner is a software engineer in corporate wanting to escape the 9-5
- Wanted a second income source
- Inspired by the YouTube channel Zenn (@Zenn0009)
- Three core motivations:
  1. Path out of corporate life
  2. Additional income stream
  3. Personal growth — overcoming procrastination and building communication skills

**Key insight:** Even if the channel fails financially, the owner wins on personal development. This became the psychological foundation that makes the project sustainable long-term.

---

## 2. Why This Niche (Psychology + History + Evolution)

**Decision:** Human Psychology + History + Evolution + Human Behavior

**Reasoning:**
- Closest to Zenn's content style
- Evergreen demand — these topics never go out of date
- High RPM ($3–8 USD per 1000 views) — one of the highest on YouTube
- Deep enough for 8-minute videos without padding
- Unique angle: modern psychology explained through ancient history and evolution
- What separates Orin from generic psychology channels: the evolutionary/historical root of every topic

**Rejected alternatives:** Pure psychology (too crowded), pure history (too broad)

---

## 3. Why The Channel Name Is "Orin"

**Journey:**
- Started with "Primal Minds" — already taken
- Considered: Eon, Echo Theory, Ancient Instinct, The Hidden Why — all taken or too generic
- Generated fresh names: Avar, Dura, Venn, Orin, Kael, Seren, Deep Wired, Ghost Wiring, Fossil Mind, The Beneath

**Why Orin won:**
- Celtic root meaning "origin" — subtle nod to evolutionary roots
- Short, premium, memorable — same feel as Zenn
- Easy to spell, search, and brand
- No existing brand using it (only @orinfriedman — a personal channel, not a brand)
- Sounds calm and thoughtful — matches the channel tone

---

## 4. Why Sister Does The Voiceover (Not The Owner)

**Original plan:** Owner records own voice

**What changed:**
- Owner attempted recording — struggled with pacing and delivery
- Analysis of Zenn's actual WPM (188–207) showed narration is faster and more skilled than expected
- Owner's English is non-native — more practice needed
- Sister is an experienced voice artist with prior voiceover work

**Decision:** Sister handles all narration. Owner is director, researcher, script writer.

**What this means:**
- Narration Playground skill → low priority
- Voice Feedback Tool → low priority
- Recording timeline accelerated significantly
- Quality will be higher from day one

---

## 5. Why 180 WPM Was Chosen As Target

**Original assumption:** 150 WPM (standard recommendation)

**What changed:** Real analysis of 3 reference channel transcripts

| Channel | Actual WPM |
|---|---|
| Zenn (Bliss Point video) | 207 |
| Zenn (Ancient Humans video) | 188 |
| The Thought Vortex (Dogs video) | 168 |

**Decision:** 180 WPM — between Zenn and Thought Vortex

**Reasoning:**
- 150 WPM was wrong — based on generic advice, not real data
- Sister is a native/fluent English speaker — can handle 180 comfortably
- 180 WPM = deliberate and clear without being slow
- At 180 WPM: 8 min video = 1,440 words

---

## 6. Why 8 Minutes Is The Target Video Length

**Journey:** Started with no fixed target → 7 min → 8 min

**Data that drove the decision:**
- Zenn videos: 8:00–8:30 consistently
- Thought Vortex videos: 7:33
- Industry data: 7–15 min is sweet spot for educational content
- **Critical insight:** 8 minutes unlocks 2 mid-roll ad slots on YouTube
  - Under 8 min = 1 ad slot
  - Over 8 min = 2 ad slots = roughly 2x ad revenue per view

**Decision:** Default target = 8 minutes = 1,440 words at 180 WPM

---

## 7. Why MS Paint Style Was Chosen For Visuals

**Journey:**
- Started planning cinematic AI images (Higgsfield, Leonardo.ai)
- Owner shared 16 screenshots from Zenn videos
- Realized Zenn uses static MS Paint / hand-drawn stick figure illustrations — NOT photorealistic AI images
- Nothing in Zenn's videos animates — all static frames

**Why MS Paint style:**
- Matches the reference channel exactly
- Achievable with a custom-built tool (no paid subscriptions)
- Unique and recognizable visual identity
- Funnier and more relatable than cinematic imagery for psychology topics
- Consistent across all videos — easier to automate

**Rejected:** Cinematic AI images (wrong style), Higgsfield (wrong style + paid), Leonardo.ai (wrong style)

---

## 8. Why We're Building Our Own Video Generator Tool

**Original plan:** Use Higgsfield MCP for image generation

**Why Higgsfield was rejected:**
- Free plan: only 70 credits/month (~8 video clips or ~35 images)
- Not enough for 15-20 images per video
- MCP-generated images consume credits even on "unlimited" toggle
- Pricing history: defaulted users to annual billing without warning — 1000+ complaints
- Most importantly: produces wrong style (cinematic, not MS Paint)

**Why build our own:**
- Owner already has $20/month Claude Code subscription
- Claude API cost for image generation: ~$2-5/month
- Python + Pillow + ffmpeg = free
- 100% control over MS Paint style
- Automated pipeline from transcript → images → video
- Tool improves with every video

**Stack decided:**
- Python + Pillow = draw MS Paint images
- Claude API = decide what to draw per scene
- ffmpeg = stitch images + audio into .mp4
- TurboScribe = real timestamps for sync

---

## 9. Why TurboScribe Was Added To The Pipeline

**Problem identified:** Script timestamps are estimates based on 180 WPM averages. Sister's actual delivery will differ — different pauses, different pacing in different sections.

**Solution:** TurboScribe transcribes sister's actual recording and outputs real word-level timestamps in .srt format.

**Why TurboScribe specifically:**
- Free tier: 3 transcriptions per day, 30 min each — more than enough
- Powered by OpenAI Whisper — high accuracy
- Exports .srt format directly — perfect for video generator input
- One 8-minute voiceover = one transcription = well within free limits

**Impact on pipeline:**
- Script timestamps = guidance for sister only
- TurboScribe timestamps = actual sync data for video generation
- Images will be perfectly synced to real delivery, not estimates

---

## 10. Why Tavily Was Chosen For Research

**Decision:** Tavily MCP for web search in Research Agent

**Reasoning:**
- Built specifically for AI agents (not general search)
- Free tier: 1,000 API credits/month
- At 10 searches per video and 8 videos/month = 80 credits used = 8% of free tier
- Easy MCP integration with Claude Code
- Returns clean structured results
- No credit card required

**Setup issue encountered:** npm cache permissions error on Mac
**Fix:** `sudo chown -R $(whoami) ~/.npm` then `npm cache clean --force`

**Fallback:** Brave Search API (2,000 free searches/month) if Tavily ever changes pricing

---

## 11. Why The Research Agent Has Anti-Hallucination Rules

**Problem:** LLMs will use training data to fill gaps when web search returns nothing — and present it as fact. One wrong study citation destroys channel credibility.

**Solution built into research-agent.md:**
- Explicit rule: "You are NOT allowed to use your own knowledge"
- Minimum 10 Tavily searches per topic
- Every fact must have a source URL or publication name
- Banned phrases: "studies show", "experts say", "research suggests" without specific names
- Quality gate: 8 checkboxes all must pass before passing to Script Engine
- ⚠️ UNVERIFIED flag for anything uncertain — excluded from script

**Proven to work:** In ep01 research, agent found 10 verified facts, flagged 1 unverifiable claim, and correctly excluded it from the output.

---

## 12. Why The Script Has Narration Direction Tags

**Problem:** A script is just words — the speaker needs to know HOW to deliver each line. Especially important since sister needs direction without back-and-forth.

**Solution:** 8 narration tags embedded in every script

| Tag | Meaning | WPM |
|---|---|---|
| [CALM] | Default, conversational | ~180 |
| [SLOW] | Contrast drop | ~145 |
| [FAST] | Momentum burst | ~215 |
| [PAUSE: Xs] | Complete silence | — |
| [EMPHASIS: word] | Land hard on this word | — |
| [STRETCH] | Elongate — sounds like discovery | — |
| [RISE] | Voice lifts — building tension | — |
| [DROP] | Voice falls — quiet truth | — |

**Key calibration insight:** [SLOW] does NOT mean crawl. It means contrast — dropping from 180 to ~145 WPM. The gap between CALM and SLOW is what creates impact, not absolute slowness.

---

## 13. The Script Structure — Why This 5-Part Formula

Based on analysis of Zenn, Thought Vortex, and GranKhelafa:

1. **Hook (0:00–0:30)** — Stop them cold. Never introduce yourself. First line mid-thought.
2. **Curiosity Gap (0:30–1:30)** — The real question. Challenge what they think they know.
3. **Historical/Evolutionary Layer (1:30–4:30)** — Take them back in time. Make ancient feel real. This is the heart.
4. **Psychological Insight (4:30–7:00)** — Connect ancient to modern. Named studies. The "aha."
5. **Relatable Ending (7:00–8:00)** — Land it. Leave them thinking. No call to action. No summary.

**Why this structure works:** The evolutionary/historical layer is Orin's unique differentiator. Most psychology channels skip straight to the science. Orin always answers "why did this evolve?" first.

---

## 14. Ep01 — Why "Why Humans Fear Being Judged"

**From a list of 10 candidate topics, this was ranked #1 because:**
- Universal — everyone has felt this
- High emotional resonance — relief is the target ending emotion
- Strong evolutionary hook — social rejection = death in ancient times
- Excellent research available — Eisenberger UCLA study, Gilovich spotlight effect, Asch conformity
- Perfect for the channel's hook style — starts with a physical feeling

**Research quality achieved:**
- 14 Tavily searches
- 4 full sources fetched and read
- 10 verified facts with citations
- 3 named peer-reviewed studies (Eisenberger 2003, Gilovich 2000, Asch 1951)
- 1 unverified claim correctly flagged and excluded

---

## 15. Tools Considered And Rejected

| Tool | Why Rejected |
|---|---|
| Higgsfield | Wrong visual style, unreliable pricing, annual billing trap |
| Leonardo.ai | Wrong visual style (photorealistic) |
| ChatGPT free | Already used for initial planning — switched to Claude for production |
| Own voice narration | Non-native English + skill gap — sister is better choice |
| 150 WPM target | Based on generic advice — real channel data showed 168-207 WPM |
| Cinematic images | Not Zenn's actual style — confirmed from frame-by-frame analysis |
| Narration Playground | Low priority since sister handles narration |
| Voice Feedback Tool | Low priority since sister handles narration |

---

## 16. The "11 PM Friend Rule"

**Origin:** Defined early in planning as the core narration persona.

**Rule:** When writing or delivering a script, imagine you are talking to your closest friend at 11 PM about something fascinating you just discovered. Not performing. Not presenting. Just sharing.

**What this prevents:**
- AI-sounding corporate language
- Over-formal academic tone
- Motivational speaker energy
- Documentary narrator stiffness

**Applied to scripts:** Any line that wouldn't sound natural in that 11 PM conversation gets rewritten.

---

## 17. Current Status (End of Planning Phase)

**Completed:**
- ✅ Channel name: Orin
- ✅ Niche locked
- ✅ CLAUDE.md v2.0
- ✅ research-agent.md v2.0
- ✅ script-engine.md v2.0
- ✅ ep01 research.md (14 searches, 10 verified facts)
- ✅ ep01 script-directed.md v2.1 (1,440 words, 8 min)
- ✅ Tavily MCP connected and tested
- ✅ Visual style confirmed (MS Paint)
- ✅ Pipeline fully designed

**Next actions (in order):**
1. Build `/orin/tools/video-generator/` in Claude Code
2. Sister records ep01 voiceover
3. Adobe Podcast Enhance → Audacity polish
4. TurboScribe → transcript.srt
5. Run video generator → video-raw.mp4
6. Build publishing-tool.md
7. Upload ep01 to YouTube

---

*Document version: 1.0*
*Created: June 2026*
*Purpose: Reference only — CLAUDE.md is the active source of truth*
