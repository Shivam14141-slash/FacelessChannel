# ORIN — Production System
> Claude Code project memory for the Orin YouTube channel.
> Read this file fully at the start of every session.
> Last updated: After full production system design session

---

## Who I Am

- I am building a faceless YouTube channel called **Orin**
- I am a software engineer working in corporate — this channel is my path toward creative independence and a second income source
- My **sister handles all voiceover narration** — she is an experienced voice artist
- I am the director, researcher, and script writer — she is the talent
- I am based in India
- This project is also a personal challenge to overcome procrastination and build something of my own

---

## Channel Identity

| Field | Value |
|---|---|
| **Channel Name** | Orin |
| **Niche** | Human Psychology + History + Evolution + Human Behavior |
| **Style Inspiration** | Zenn (@Zenn0009), The Thought Vortex (@the_thought_vortex), GranKhelafa (@Gran-khelafa) |
| **Tone** | Calm, curious, thoughtful — like telling a fascinating story to one friend at 11 PM |
| **Target Video Length** | 8 minutes (unlocks 2 mid-roll ad slots) |
| **Visual Style** | MS Paint / hand-drawn stick figure style — simple, flat, intentionally amateur-looking. White background, thick black outlines, flat primary colors. Exactly like Zenn's visual style. |
| **Voice Style** | Calm, deliberate, documentary tone — NOT loud YouTuber energy |
| **Narration Speed** | ~180 WPM (based on real analysis of Zenn + Thought Vortex) |

---

## Content Philosophy

- The **script is the product** — visuals and voice support the story
- Every video explores **one single idea** deeply — no scattered topics
- Scripts must sound **100% human** — never AI-generated in tone or structure
- Storytelling formula: Hook → Curiosity Gap → Historical/Evolutionary Layer → Psychological Insight → Relatable Ending
- Narration persona: *"Talking to one friend at 11 PM about something fascinating"*
- Target word count: **1,440 words = 8 minutes at 180 WPM**

---

## Planned Video Topics (Priority Order)

1. Why Humans Fear Being Judged ← **ep01 — IN PROGRESS**
2. Why Procrastination Exists
3. Why Time Feels Faster As You Age
4. Why Smart People Overthink
5. The Psychology of Loneliness
6. What Ancient Humans Did At Night
7. Why Humans Love Stories
8. Why We Compare Ourselves To Others
9. Why Humans Developed Religion
10. The Most Dangerous Bias In Human Thinking

---

## Complete Production Pipeline (End-to-End)

```
STEP 1 — RESEARCH
  Tool: Research Agent (skills/research-agent.md)
  Input: Topic name
  Process: Minimum 10 Tavily web searches across 4 rounds
           100% web-sourced facts only — zero hallucination
           Structured output mapped to script sections
  Output: /videos/[ep]/research.md

STEP 2 — SCRIPT WRITING
  Tool: Script Engine (skills/script-engine.md)
  Input: research.md
  Process: Transforms research into human-sounding
           narration-directed script with tags + timestamps
           Target: 1,440 words / 8 min / 180 WPM
  Output: /videos/[ep]/script-directed.md

STEP 3 — VOICEOVER RECORDING
  Who: Sister (experienced voice artist)
  Input: script-directed.md (guidance only — she interprets naturally)
  Process: Records in 6 batches (1-2 min each)
           2 sec silence before/after each batch
           3 takes per batch, pick best
  Tool: Any mic → Adobe Podcast Enhance (free) → Audacity polish
  Output: /videos/[ep]/audio-final.wav

STEP 4 — TRANSCRIPTION (REAL TIMESTAMPS)
  Tool: TurboScribe (free tier — 3 transcripts/day, 30 min each)
  Input: audio-final.wav
  Process: Uploads audio → exports with word-level timestamps
  Output: /videos/[ep]/transcript.srt
  Note: These REAL timestamps replace script timestamps for video sync

STEP 5 — VIDEO GENERATION
  Tool: /tools/video-generator/ (custom built in Claude Code)
  Input: transcript.srt + script-directed.md + audio-final.wav
  Process: - Reads each timestamp from transcript.srt
           - Uses script context to understand what's being said
           - Calls Claude API with MS Paint prompt
           - Generates one 1920x1080 PNG per timestamp block
           - ffmpeg stitches images + audio into .mp4
  Output: /videos/[ep]/video-raw.mp4
  Style: MS Paint stick figures, white background, flat colors,
         thick black outlines, simple shapes — exactly like Zenn

STEP 6 — PUBLISHING PREP
  Tool: Publishing Tool (skills/publishing-tool.md)
  Input: script-directed.md + video theme
  Output: /videos/[ep]/publishing.md
    - 5 title options (curiosity-driven, not clickbait)
    - YouTube description (SEO-optimized)
    - 15-20 tags
    - Thumbnail brief

STEP 7 — UPLOAD
  Platform: YouTube (@orin or closest available handle)
  Checklist: Title, description, tags, thumbnail, end screen, cards
```

---

## Folder Structure

```
/orin/
│
├── CLAUDE.md                          ← This file (project brain)
│
├── /skills/                           ← Skill system prompts
│   ├── research-agent.md              ✅ v2.0 — web-enforced
│   ├── script-engine.md               ✅ v2.0 — 180 WPM calibrated
│   ├── publishing-tool.md             ⬜ Not built yet
│   ├── narration-playground.md        ⬜ Low priority (sister does narration)
│   └── voice-feedback.md              ⬜ Low priority (sister does narration)
│
├── /tools/                            ← Custom built tools
│   └── /video-generator/              ⬜ Building next
│       ├── main.py                    ← Main pipeline script
│       ├── scene_generator.py         ← MS Paint image generation
│       ├── video_assembler.py         ← ffmpeg stitching
│       └── requirements.txt
│
└── /videos/                           ← One folder per episode
    └── /ep01-fear-of-judgment/
        ├── research.md                ✅ Done
        ├── script.md                  ✅ Done (plain)
        ├── script-directed.md         ✅ Done (v2.1 — 8 min edition)
        ├── audio-final.wav            ⬜ Sister recording pending
        ├── transcript.srt             ⬜ After recording
        ├── video-raw.mp4              ⬜ After video generator built
        └── publishing.md              ⬜ After video done
```

---

## Skills Status

| Skill | File | Version | Status |
|---|---|---|---|
| Research Agent | research-agent.md | v2.0 | ✅ Complete |
| Script Engine | script-engine.md | v2.0 | ✅ Complete |
| Publishing Tool | publishing-tool.md | — | ⬜ Not built |
| Narration Playground | narration-playground.md | — | ⬜ Low priority |
| Voice Feedback | voice-feedback.md | — | ⬜ Low priority |

---

## Visual Style Guide — MS Paint Zenn Style

Every image generated must follow these rules exactly:

**Canvas:** 1920x1080px, white background
**Lines:** Thick (4-8px), uneven, slightly wobbly black outlines
**Characters:** Stick figures — circle head, line body, line limbs
**Eyes:** Simple dots or small circles
**Expressions:** Basic — smile, frown, neutral only
**Colors:** Flat only — red, blue, green, yellow, orange, brown, grey
**NO:** Shading, gradients, 3D, realistic textures, photorealism
**NO:** Disney/anime/polished illustration style
**Text in image:** Bold, short, handwritten-style, correctly spelled
**Compositions:** Simple, centered, lots of white space
**Format:** Always 16:9 horizontal — never vertical or square

Reference: Zenn (@Zenn0009) — every video uses this exact style

---

## Video Generator Tool — Architecture

```
Input files:
  - transcript.srt (real timestamps from TurboScribe)
  - script-directed.md (scene context)
  - audio-final.wav (sister's voiceover)

Processing:
  1. Parse transcript.srt → list of (timestamp, text) pairs
  2. For each timestamp block:
     a. Read narration text at that moment
     b. Send to Claude API with MS Paint prompt
     c. Claude describes scene elements to draw
     d. Python/Pillow draws the scene
     e. Save as 1920x1080 PNG
  3. ffmpeg assembles:
     - Images held for their timestamp duration
     - Audio overlaid
     - Subtitle text at bottom
     - Fade transitions between scenes

Output: video-raw.mp4
```

**MS Paint System Prompt (use exactly this for image generation):**
```
You are generating images for a YouTube video in MS Paint style.
Draw one scene for this narration moment: {narration_text}

Style rules — follow all of these exactly:
- White background, 1920x1080
- Stick figure humans with round heads and line bodies
- Thick uneven black outlines (wobbly, not perfect)
- Simple dot or circle eyes, basic facial expressions
- Flat colors only: red, blue, green, yellow, orange, brown, grey
- No shading, no gradients, no 3D, no realistic textures
- Simple shapes: squares, circles, rectangles, arrows, trees, rooms
- Lots of white empty space — keep it simple and readable
- If text appears in image: short, bold, correctly spelled
- Style must look like an amateur drew it quickly in MS Paint
- Funny, simple, intentionally imperfect — like Zenn on YouTube
```

---

## Audio Processing Chain

```
Sister records voiceover in batches
  → Adobe Podcast Enhance (podcast.adobe.com) — FREE
    Upload raw audio → download enhanced version
  → Audacity final polish:
      1. Noise Reduction
      2. Normalize to -3dB
      3. Compression (3:1 ratio, threshold -18dB)
      4. EQ: cut below 80Hz, boost 3-5kHz
      5. Limiter at -1dB
  → Export as WAV → audio-final.wav
  → Upload to TurboScribe → export transcript.srt
```

---

## Narration Speed Analysis (Real Data)

Based on analysis of 3 reference channel videos:

| Channel | WPM | Style |
|---|---|---|
| Zenn (Bliss Point) | 207 | Fast, punchy |
| Zenn (Ancient Humans) | 188 | Measured, calm |
| The Thought Vortex | 168 | Deliberate, clear |
| **Orin target** | **180** | Between Zenn and Vortex |

**At 180 WPM:**
- 8 min video = 1,440 words (default target)
- [SLOW] tag = ~145 WPM (contrast drop)
- [FAST] tag = ~215 WPM (momentum burst)
- [PAUSE] tags add ~1:15 to total runtime

---

## Tools & Stack

| Tool | Purpose | Cost |
|---|---|---|
| Claude Code | Production OS brain | $20/month (you have this) |
| Tavily MCP | Web research for Research Agent | Free (1000 searches/month) |
| Claude API | MS Paint image generation | ~$2-5/month |
| Adobe Podcast Enhance | Audio cleanup | Free |
| Audacity | Audio post-processing | Free |
| TurboScribe | Audio → timestamped transcript | Free (3/day) |
| Python + Pillow + ffmpeg | Video generation tool | Free |
| Pixabay Music | Background music | Free |
| CapCut / DaVinci Resolve | Optional final polish | Free |

**Total monthly cost: ~$2-5 (Claude API only)**

---

## Reference Channels

| Channel | Handle | WPM | What to Learn |
|---|---|---|---|
| Zenn | @Zenn0009 | 188–207 | MS Paint visual style, hook structure |
| The Thought Vortex | @the_thought_vortex | 168 | Script depth, science + history blend |
| GranKhelafa | @Gran-khelafa | unknown | Historical storytelling edge |

**Zenn's visual formula (confirmed from frame analysis):**
- Static images only — nothing animates
- One image per 2-4 seconds of narration
- Text subtitle at bottom synced to speech
- Simple scene change = cut or fade
- Same MS Paint style throughout entire video

---

## Growth & Monetization Timeline

```
Month 1-2  →  Build pipeline. Upload ep01.
Month 3-4  →  2 videos/month. Refine workflow.
Month 5-6  →  Consistency. Don't obsess over analytics.
Month 6-12 →  Double down on what works.
Month 12+  →  Approaching monetization (1K subs, 4K watch hours)
Month 18-24 → Evaluate channel as income supplement
```

**RPM expectation:** Psychology/history = $3–8 USD per 1000 views

---

## Rules Claude Must Always Follow

1. **Scripts must never sound AI-generated.** Rewrite anything generic.
2. **Research Agent must use Tavily for every fact.** No training data.
3. **Always save outputs to correct folder.** Never leave work in chat only.
4. **Visual style = MS Paint only.** No photorealism, no polished art.
5. **8 minutes = 1,440 words.** Never write short and pad — write right.
6. **Sister does narration.** Do not give voice coaching to the owner.
7. **Remind of 11 PM friend rule** if script sounds formal or stiff.
8. **This is a long game.** If owner seems anxious about growth, remind of 18-month timeline.

---

## Session Start Checklist

When starting a new Claude Code session:
1. Which episode are we working on?
2. Which step in the pipeline are we on?
3. Any carry-over notes from last session?

Then load the relevant skill file and continue.

---

*Version: 2.0 — Major update after full production system design*
*Key changes: Sister does narration, MS Paint visual style confirmed,
video generator tool planned, TurboScribe added to pipeline,
180 WPM target locked from real channel analysis*
