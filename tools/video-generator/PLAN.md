# Video Generator Tool — Plan File
> Location: `/orin/tools/video-generator/PLAN.md`
> Status: PLANNING — not yet built
> This file is the single source of truth for what this tool is, why it exists,
> and what "done" looks like. Read this fully before writing any code.

---

## 1. Purpose — What This Tool Does

This tool turns a finished voiceover + script into a finished, ready-to-edit video.

**Input:**
- `audio-final.wav` — sister's recorded, cleaned voiceover
- `transcript.srt` — TurboScribe word-level timestamps of that voiceover (the REAL timing)
- `script-directed.md` — the tagged script (context: what's being said, narration tags, section structure)

**Output:**
- `video-raw.mp4` — a 16:9, 1920x1080 video with:
  - One MS Paint / Zenn-style stick-figure image per scene/timestamp block
  - Sister's voiceover audio playing under it
  - Bottom-of-frame subtitles synced to the real transcript timestamps
  - Simple cuts/fades between scenes

This `video-raw.mp4` is the "raw cut" — final polish (intro/outro, music, branding) still happens in CapCut/DaVinci per CLAUDE.md Step 6 onward (that's a separate, manual step — NOT part of this tool).

**Core job in one sentence:**
> Read the real timestamps, figure out what scene is happening at each moment, generate a matching MS Paint image for it, and stitch everything together into a video.

---

## 2. Efficiency Targets

This tool must be cheap, fast enough to iterate, and mostly automated — because it will run once per video, every video, indefinitely.

**No fixed image count.** The number of images is NOT a target we engineer toward — it falls out of the script content itself. Every sentence (or tightly-linked group of short sentences) that describes something visual gets its own image, depicting exactly what's being narrated at that moment. A simple 8-min video might produce 25 images; a fact-dense one might produce 40. The script drives the count, not the other way around. (See Section 5.2 for how beats are determined.)

| Metric | Target | Why |
|---|---|---|
| **Cost per video** | $2–5 USD (Claude API only) | Matches CLAUDE.md "Tools & Stack" budget. Pillow/ffmpeg/TurboScribe are free. |
| **Images per video** | Driven entirely by narration content (no hard cap) | Matches Zenn: every sentence/beat gets a literal, on-the-nose image of what's being said (see "There's no Moon" example) |
| **API calls per video** | Small number of batched calls (NOT per word, NOT per image) | Claude API processes the reconstructed sentence-level transcript in batches and returns beat boundaries + scene descriptions for many beats per call |
| **Run time (no human review)** | Under ~15 minutes end-to-end for an 8-min video | Mostly bottlenecked by Pillow drawing + ffmpeg encode, not API |
| **Manual intervention** | Zero, by default — but must support a "review images before assembling video" checkpoint | User should be able to regenerate a single bad image without re-running the whole pipeline |
| **Re-run cost on edits** | Near-zero — re-running on an unchanged transcript should not re-call the API for unchanged scenes (cache scene descriptions to a JSON file) |

**Non-goals (explicitly out of scope for v1):**
- No animation / motion graphics — Zenn's videos are 100% static frames (confirmed in decisions-log.md §7)
- No automatic music selection — music stays manual (Pixabay, per CLAUDE.md)
- No automatic YouTube upload — that's Step 7, separate
- No voice generation — sister always provides real audio

---

## 3. The Higgsfield Workaround — Exact Replacement

### 3.1 What Higgsfield was supposed to do
Original plan (per decisions-log.md §8): use **Higgsfield MCP** to generate cinematic AI images per script timestamp, one image per scene, fed into video assembly.

### 3.2 Why Higgsfield was rejected (verbatim reasoning, decisions-log.md §8)
1. **Free tier too small** — only 70 credits/month ≈ ~8 video clips or ~35 images. An 8-min video needs ~15-25 images, so one video could burn most/all of a month's free credits.
2. **MCP credits consumed even on "unlimited" toggle** — the free/unlimited mode wasn't actually free in practice.
3. **Pricing/billing trust issues** — Higgsfield has a history of defaulting users to annual billing without clear warning, with 1000+ user complaints about this.
4. **Wrong visual style entirely** — Higgsfield is built for cinematic, photorealistic, or stylized AI video/image generation. Orin's actual visual identity (confirmed from the 16 Zenn reference screenshots) is **MS Paint stick-figure**, not cinematic. Even if Higgsfield's pricing were fine, its output would need to be forced into a style it isn't designed for.

### 3.3 The exact replacement — how this tool stands in for Higgsfield

| Higgsfield's job | This tool's replacement |
|---|---|
| Take a scene description → generate a cinematic image | `scene_generator.py`: take a scene description → call **Claude API (text)** to get a structured "what to draw" spec → **Pillow** draws it as MS Paint stick figures |
| Image generation model (Soul / Cinema Studio) | Claude API is used as a **drawing planner**, not an image model — it outputs a structured description (objects, positions, colors, labels, layout) which Pillow then renders deterministically |
| Per-scene credits (paid, limited) | Per-scene Claude API text call — cheap (~$2-5/month total), no per-image image-gen cost at all, because no image-generation model is used |
| Video assembly (implied, manual) | `video_assembler.py` using **ffmpeg**: stitches Pillow-rendered PNGs + `audio-final.wav` + subtitle text from `transcript.srt` into `video-raw.mp4` |
| Style control (limited — fighting against Higgsfield's default cinematic style) | 100% style control — every shape, color, and outline is drawn by our own Pillow code following the MS Paint spec below. The "style" is code, not a prompt that can drift. |

**Key architectural insight:** Higgsfield (and any image-generation API) would be the wrong tool even if it were free, because MS Paint stick-figure scenes (circles, rectangles, stick limbs, flat fills, wobbly outlines, bold text labels) are **simple enough to draw programmatically with Pillow** — they don't need a generative image model at all. Claude's role shrinks to "scene planner" (decide WHAT goes in the frame: which props, which stick figures, what labels, what colors), and Pillow's role is "renderer" (draw exactly that, consistently, every time).

This is strictly better than Higgsfield for our use case:
- **Cheaper** — text-only API calls vs. image-generation credits
- **More consistent** — same Pillow drawing primitives every time = same visual style across all 200+ images we'll eventually generate across 10 videos
- **Fully controllable** — if a shape looks wrong, we fix the Pillow drawing function once and it's fixed forever, instead of re-prompting an image model and hoping

### 3.4 Status of `reference/higgsfield_prompt.md`
This file contains a prompt the user found on YouTube, intended for use with Higgsfield directly. **The user has confirmed it is UNTESTED — never run, taken as a starting point only.**

We are NOT using this prompt with Higgsfield (per §3.3, Higgsfield is rejected entirely). Instead, this prompt is repurposed as **the style specification source** for two places in our own pipeline:
1. The Claude API "scene planner" prompt in `scene_generator.py` (system prompt describing the MS Paint aesthetic, the "no realistic/3D/Disney/anime" exclusion list, the basic-shapes vocabulary, the color palette, text rules)
2. The Pillow drawing rules (line thickness, wobble, flat color palette, outline style)

Its content is reusable as *style guidance text* even though its original purpose (a Higgsfield image-gen prompt) is dropped.

---

## 4. Visual Style Specification (The Bar To Hit)

Derived from: CLAUDE.md "Visual Style Guide", `reference/higgsfield_prompt.md`, and direct review of the 16 reference images (Zenn channel, "What Did Ancient Humans Do All Day?").

### 4.1 Canvas
- 1920x1080px, white (or off-white/tan, per Zenn references) background
- Always 16:9 horizontal — never vertical/square

### 4.2 Characters
- Stick figures: circle/oval head, single-line body, line limbs
- Eyes: simple dots or small circles
- Expressions: basic only — smile (curve), frown (curve), neutral (line/dot)
- No detailed hair, no realistic proportions, no shading on figures

### 4.3 Lines & Shapes
- Thick (4-8px), uneven, slightly wobbly black outlines — NOT perfectly straight/clean vector lines
- Objects built from basic shapes: circles, rectangles, squares, triangles, arrows, simple tables/boxes, trees, huts, signs, screens
- Crossed-out objects (red X / strikethrough) used for negation (seen in reference images: crossed-out clock, crossed-out hospital bed)

### 4.4 Color
- Flat fills only — no gradients, no shading, no 3D
- Palette: red, blue, green, yellow, orange, brown, grey (+ white background, black outlines)
- Red specifically reserved for arrows, X-marks, and emphasis accents (per higgsfield_prompt.md)

### 4.5 Text in Images
- Bold, short, correctly-spelled, handwritten-style or simple sans-serif labels
- Used for callouts/labels (e.g., "WORK 2.5H", "EGO", "1968.") — NOT full sentences
- Subtitles (from transcript.srt) are a SEPARATE overlay layer, not baked into the same style as in-image labels — handled by ffmpeg subtitle burn-in or `drawtext`

### 4.6 Composition
- Centered, lots of white space — do not fill the whole frame
- One clear "subject" per scene (1-3 stick figures + 1-2 props max for simple scenes)
- Consistent character design across all images in one video (same head size, same line weight)

### 4.7 Explicit "Never" List
No: shading, gradients, 3D, photorealism, cinematic lighting, Disney style, anime style, polished/professional vector art, realistic humans, glossy/modern UI design, complex textures, highly detailed backgrounds.

---

## 5. Pipeline Architecture

```
┌─────────────────┐
│ transcript.srt   │──┐
│ script-directed  │  │
│ .md (optional —  │──┼──> [1] PARSE & SEGMENT
│  not present for │  │       (Section 5.2: Pass 1 reconstruct
│  Zenn test audio)│  │        sentences, Pass 2 group into beats)
│ audio.wav/mp3    │──┘         │
└──────────────────┘            v
                          List of scene "beats":
                          { start_time, end_time,
                            narration_text, scene_description }
                          (count is NOT fixed — driven by content)
                                 │
                                 v
                          [2] SCENE PLANNING (scene_generator.py)
                          For each scene block NOT already cached:
                            -> Claude API call (text-only)
                            -> Returns structured JSON:
                               { characters: [...], props: [...],
                                 labels: [...], colors: [...],
                                 layout: "description" }
                          Cache results in scenes.json
                                 │
                                 v
                          [3] IMAGE RENDERING (scene_generator.py)
                          For each scene JSON spec:
                            -> Pillow draws 1920x1080 PNG
                            -> following MS Paint style rules (Section 4)
                          Save to /images/scene_001.png ... scene_NNN.png
                                 │
                                 v
                          [4] VIDEO ASSEMBLY (video_assembler.py)
                            -> ffmpeg: each image held for its scene duration
                            -> overlay audio-final.wav
                            -> burn in subtitles from transcript.srt
                            -> simple crossfade between scenes
                          Output: video-raw.mp4
```

### 5.1 File Responsibilities

- **`main.py`** — orchestrator. Reads input file paths (CLI args or config), runs steps 1-4 in order, handles the "review checkpoint" (pause after step 3, let user inspect `/images/`, optionally regenerate specific scenes before step 4).
- **`scene_generator.py`** — steps 2 & 3. Contains:
  - The Claude API system prompt (style spec, derived from Section 4 + higgsfield_prompt.md content)
  - JSON schema for scene specs
  - Pillow drawing primitives (stick figure, wobbly rectangle, wobbly circle, arrow, label text, crossed-out object) — a small reusable shape library
  - Scene cache (`scenes.json`) so re-runs don't re-call the API for unchanged scenes
- **`video_assembler.py`** — step 4. ffmpeg wrapper:
  - Builds a concat file mapping image -> duration from scene timings
  - Burns subtitles from `transcript.srt`
  - Outputs `video-raw.mp4`
- **`requirements.txt`** — `pillow`, `anthropic` (Claude API SDK), plus notes that `ffmpeg` must be installed system-wide (not pip-installable)

### 5.2 Scene Segmentation Strategy — Content-Driven, Not Time-Driven

**This is the core of the whole tool, and it works in two passes.**

**Pass 1 — Reconstruct real sentences from the SRT.**
TurboScribe's `.srt` output is chopped into ~1-2 second fragments that frequently split mid-sentence or even mid-clause (confirmed from `Testing/What Did Earth Look Like Before Humans.srt` — e.g. fragment 1 ends mid-sentence at "the", fragment 2 continues "air going in and out of your lungs"). Raw SRT fragments are NOT usable as scene boundaries on their own.

So step one is: walk through the SRT fragments in order, concatenate their text, and re-split on sentence-ending punctuation (`.`, `?`, `!`) to rebuild full sentences. Each rebuilt sentence keeps:
- `start_time` = the start time of the SRT fragment that contained its first word
- `end_time` = the end time of the SRT fragment that contained its last word
- `text` = the full reconstructed sentence

This gives us a clean list: **[{start, end, sentence_text}, ...]** for the entire video — this is the real, accurate spine everything else hangs off.

**Pass 2 — Group sentences into visual "beats" (= one image each).**
Not every sentence needs its own image, and a few long/compound sentences might need two. So the reconstructed sentence list is sent to Claude API in batches, and Claude decides the beat boundaries:
- Most beats = 1 sentence = 1 image, depicting literally what that sentence describes (the "There's no Moon" example: the sentence says it, the image shows it — a sky with no moon, directly).
- Very short, tightly-linked sentences (e.g., "It hasn't." right after a long setup sentence) may be merged into the previous beat's image rather than getting their own near-empty frame.
- A long, visually-compound sentence (describing two distinct things) may be split into two beats/images.

For each beat, Claude returns: `{ start_time, end_time, narration_text, scene_description (what to draw, in MS Paint terms per Section 4) }`.

**This directly answers "how do we know what becomes an image":** the unit is the sentence (from real, reconstructed timestamps), the image content is a literal depiction of that sentence's subject, and Claude is the judge of merge/split exceptions — not a fixed timer. Image *count* is therefore an output of this pass, never an input constraint (per Section 2).

Section boundaries from `script-directed.md` (Hook / Curiosity Gap / Historical / Psychological / Ending) are passed to Claude as context only — they help it understand tone/section, but a beat never spans across a section boundary.

---

## 6. Open Questions / Decisions To Confirm Before/During Build

1. Exact scene segmentation rule (time-based vs. sentence/idea-based) — to be tuned against ep01's actual transcript once available.
2. Whether subtitles are burned into the video (ffmpeg `drawtext`/`subtitles` filter) or left as a soft `.srt` track for the editor to toggle in CapCut/DaVinci.
3. How many distinct "scene templates" the Pillow shape library needs initially (e.g., "two figures talking", "single figure + thought bubble", "timeline row", "before/after split") — will grow organically per video, starting minimal for ep01.
4. Claude API model choice for scene planning (cheapest model that reliably returns valid JSON — likely Haiku-class).

---

## 7. Testing Strategy — Zenn Audio First, Then ep01

ep01's `audio-final.wav` and `transcript.srt` don't exist yet (sister's recording is still pending). To avoid blocking on that, the tool is built and validated FIRST against a real, finished Zenn video:

- `/tools/video-generator/Testing/What Did Earth Look Like Before Humans_.mp3` — real Zenn audio
- `/tools/video-generator/Testing/What Did Earth Look Like Before Humans.srt` — real TurboScribe-style transcript for it (already chopped into ~1-2s fragments — exactly the format ep01's transcript will be in)

**Why this is a good test:** Zenn's actual finished video is the quality bar (per the 16 reference images). By running our pipeline on Zenn's own audio/transcript, we can generate our version of "What Did Earth Look Like Before Humans" and compare our output directly against Zenn's real video, scene-for-scene. This tells us, before ep01 even has audio:
- Is sentence reconstruction (Pass 1) working correctly on real TurboScribe output?
- Are the beat boundaries (Pass 2) sensible — roughly one image per sentence, matching where Zenn actually cuts to a new image?
- Does the MS Paint Pillow rendering hold up against Zenn's actual visual style?

`script-directed.md` won't exist for this test audio (it's not an Orin script) — the pipeline must work with JUST `transcript.srt` + audio when no script context is available, falling back gracefully (section-context becomes optional input, per the architecture diagram in Section 5).

### Definition of Done — v0 (Zenn test, build this first)
- [ ] Given the Testing folder's `.srt` + `.mp3` only (no script-directed.md), the tool produces a full `video-raw.mp4`
- [ ] Sentence reconstruction (Pass 1) produces clean, correctly-punctuated sentences with accurate start/end times
- [ ] Beat count and boundaries (Pass 2) are reviewed by user against the real Zenn video for "does a new image appear roughly where Zenn changes scenes?"
- [ ] At least one full pass of generated images is reviewable in `/images/` before assembly
- [ ] Output video plays back correctly: images timed to audio, subtitles synced

### Definition of Done — v1 (ep01, after sister's recording + TurboScribe)
- [ ] Given ep01's `transcript.srt` + `script-directed.md` + `audio-final.wav`, the tool produces `video-raw.mp4`
- [ ] Video is 1920x1080, 16:9, matches ep01's audio length
- [ ] Image count is whatever the content produces (no artificial cap), all matching the MS Paint style (Section 4)
- [ ] Subtitles visible and synced to real transcript timestamps
- [ ] Total Claude API cost for the run is within $2-5
- [ ] User can review `/images/` before final assembly and regenerate individual scenes cheaply

---

*Plan version: 1.0*
*Created: 2026-06-12*
*Status: Awaiting user review before scaffolding begins*
