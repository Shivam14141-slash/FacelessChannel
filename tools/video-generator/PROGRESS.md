# Video Generator Tool — Progress File
> Location: `/orin/tools/video-generator/PROGRESS.md`
> Tracks build status. See `PLAN.md` for full context, architecture, and rationale.
> Update this file every time meaningful progress is made — future sessions
> should be able to resume from this file alone (plus PLAN.md).

---

## Current Status: SCAFFOLDING BUILT — NOT YET RUN END-TO-END

All core files exist and Pass 1 has been validated against the real Zenn
test SRT. Pass 2 (Claude API) and video assembly are written but not yet
run (need `anthropic` package + API key, and `ffmpeg`, installed first).

### Files created
- `requirements.txt` — pillow (already installed, v11.3.0), anthropic (NOT yet installed)
- `transcript_parser.py` — Pass 1 (sentence reconstruction). **Tested** against
  `Testing/What Did Earth Look Like Before Humans.srt`: 252 fragments -> 124
  clean sentences with correct timestamps. Confirmed it correctly captures
  "There's no moon in the sky either." as its own sentence at [72.29 -> 73.69].
- `shapes.py` — Pillow MS Paint drawing primitives (wobbly lines/circles/rects,
  stick figures with poses + expressions, arrows, cross-out, text labels).
  **Tested** — rendered a sample image to `/tmp/shapes_test.png`, visually
  confirmed it matches the intended crude MS Paint look.
- `scene_generator.py` — Pass 2 beat planner (Claude API, model
  `claude-haiku-4-5-20251001`, batches of 15 sentences, cached to
  `scenes.json`) + `render_beat`/`render_all` which turn each beat's
  `elements` JSON into a PNG via shapes.py. **NOT yet run** (no `anthropic`
  package installed, no API key set).
- `video_assembler.py` — ffmpeg wrapper: builds a concat file (image per
  beat duration), generates `subtitles.srt` from beat text, burns subtitles,
  overlays audio -> `video-raw.mp4`. v0 = simple cuts, no crossfades yet.
  **NOT yet run** (ffmpeg not installed on this machine).
- `main.py` — CLI orchestrator wiring steps 1-4 together, with a manual
  review checkpoint between rendering and assembly (per PLAN.md Section 2
  "manual intervention" target).

### Before the v0 Zenn test run can happen
- [ ] `pip3 install anthropic` (or `pip3 install -r requirements.txt`)
- [ ] Set `ANTHROPIC_API_KEY` env var
- [ ] `brew install ffmpeg`
- [ ] Run: `python3 main.py --srt "Testing/What Did Earth Look Like Before Humans.srt" --audio "Testing/What Did Earth Look Like Before Humans_.mp3" --out-dir Testing/output`

---

## Context Snapshot (read this if resuming cold)

- **Project:** Orin YouTube channel — faceless psychology/history/evolution channel
- **This tool's job:** Replace Higgsfield. Take ep01's `transcript.srt` (TurboScribe real timestamps) + `script-directed.md` (tagged script) + `audio-final.wav` (sister's voiceover) → produce `video-raw.mp4` with MS Paint stick-figure images synced to audio + subtitles.
- **Why not Higgsfield:** wrong visual style (cinematic vs. MS Paint), credit limits too low (70/month free), billing trust issues. Full reasoning in `PLAN.md` Section 3 and `reference/decisions-log.md` Section 8.
- **Replacement stack:** Claude API (text-only, scene planning) + Pillow (drawing) + ffmpeg (assembly). Cost target $2-5/month.
- **Style bar:** MS Paint stick figures, white bg, thick wobbly black outlines, flat colors only, lots of white space — see `PLAN.md` Section 4, derived from 16 Zenn reference screenshots in `reference/reference_images/` and `reference/higgsfield_prompt.md` (which is UNTESTED — repurposed only as style-spec text, not as a Higgsfield prompt).

---

## Build Phases (from PLAN.md Section 5)

- [ ] **Phase 0 — Plan review** (current) — user reviews `PLAN.md`, confirms approach before any code
- [ ] **Phase 1 — Scaffolding** — create `main.py`, `scene_generator.py`, `video_assembler.py`, `requirements.txt` with stub functions matching the architecture in PLAN.md Section 5
- [ ] **Phase 2 — Pillow shape library** — build reusable drawing primitives (stick figure, wobbly rectangle/circle, arrow, label text, crossed-out object) per style spec in PLAN.md Section 4
- [ ] **Phase 3 — Sentence reconstruction (Pass 1)** — parse `transcript.srt` (raw TurboScribe fragments), concatenate + re-split on sentence punctuation into clean `{start, end, sentence_text}` list. Test against `Testing/*.srt`.
- [ ] **Phase 4 — Beat planner (Pass 2)** — Claude API integration in `scene_generator.py`: batch reconstructed sentences -> beat boundaries + `scene_description` per beat. System prompt derived from PLAN.md Section 4 + `higgsfield_prompt.md`. Cache to `scenes.json`. No script-directed.md required (optional context only).
- [ ] **Phase 5 — Image rendering** — Pillow renders each beat's `scene_description` to a 1920x1080 PNG using the shape library from Phase 2
- [ ] **Phase 6 — Video assembly** — `video_assembler.py` ffmpeg wrapper: image timing per beat, audio overlay, subtitle burn-in, crossfades
- [ ] **Phase 7 — v0 test run (Zenn audio)** — run full pipeline on `Testing/What Did Earth Look Like Before Humans_.mp3` + `.srt`, compare output against the real Zenn video, review beat boundaries + image quality
- [ ] **Phase 8 — v1 end-to-end on ep01** — once `audio-final.wav` and `transcript.srt` exist for ep01 (sister's recording pending)

---

## Blockers / Dependencies

- ep01's `audio-final.wav` / `transcript.srt` do not exist yet (sister's recording pending — per decisions-log.md §17). **No longer a blocker for early testing** — Phase 7 uses the Zenn test audio/SRT already provided in `Testing/` instead.
- Phase 8 (ep01 end-to-end) still waits on sister's recording + TurboScribe.

---

## Open Questions Carried From PLAN.md Section 6 (updated)

1. ~~Scene segmentation rule~~ — RESOLVED in PLAN.md Section 5.2: two-pass approach (reconstruct sentences from SRT fragments, then Claude groups into content-driven beats). To be validated against real `Testing/*.srt` in Phase 3/7.
2. Subtitle handling — burned in via ffmpeg vs. soft `.srt` for editor
3. Initial set of Pillow "scene templates" needed (will emerge from Phase 7 test against Zenn video)
4. Claude API model choice for beat planning (likely Haiku-class for cost)

---

## Decision Log For This Tool (append as decisions are made)

- 2026-06-12 — PLAN.md written, documenting Higgsfield replacement rationale and architecture. No code yet.
- 2026-06-12 — Revised plan per user feedback: removed fixed image-count target (content-driven instead), defined two-pass segmentation (sentence reconstruction from raw SRT fragments + Claude-driven beat grouping), and adopted Zenn test audio/SRT (`Testing/`) as the v0 build target ahead of ep01.

---

*Progress file version: 1.0*
*Last updated: 2026-06-12*
