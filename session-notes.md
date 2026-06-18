# Session Notes — Fix/Scene Branch
> Last updated: 2026-06-18
> Branch: `Fix/Scene`
> Repo: `git@github.com:Shivam14141-slash/FacelessChannel.git`

---

## Where We Left Off

### Baseline (safe, locked)
`scene_generator.py` is on **v6-creative-selective** — committed at `8b2a8fb`.
`Testing/output/` contains the v6 168-beat run (images + video). **Do not touch this folder.**
To roll back: `git checkout 8b2a8fb -- tools/video-generator/scene_generator.py`

### Active experiment
`scene_generator.py` is now on **TestV1** (`PROMPT_VERSION = "TestV1-tighter-split-richer-creative"`).
All TestV1 output goes to `Testing/output_test/` — completely separate from baseline.

**Next action — run TestV1:**
```bash
source ~/.zshrc && cd tools/video-generator && python3 main.py \
  --srt "Testing/What Did Earth Look Like Before Humans.srt" \
  --audio "Testing/What Did Earth Look Like Before Humans_.mp3" \
  --out-dir Testing/output_test \
  --no-review
```

---

## What This Session Built

### v6-creative-selective — the key improvement

Added a **CREATIVE INTERPRETATION** section to the `SYSTEM_PROMPT` in `scene_generator.py`.

Haiku now asks "does this beat earn creative treatment?" before describing each scene.

**Criteria for earning it:**
- Abstract concept (fear, identity, time, memory, evolution, consciousness)
- Emotional peak (hook, revelation, key insight, ending)
- Ironic or paradoxical idea
- Clear contrast or transformation (before/after, then/now)

**If earned → pick ONE technique:**

| Technique | What it does |
|---|---|
| Visual Metaphor | Show the underlying idea through analogy, not what's literally happening |
| Unexpected Angle | Show the consequence/reaction/inside view instead of the subject |
| Humor | Witty visual twist using irony or absurdity in the MS Paint style |
| Contrast / Split Frame | Divide frame into two halves showing opposing states |

**If not earned → describe literally** (same as v5). Transitions, physical actions, factual setup sentences stay literal.

Each technique has 2 examples in the prompt (one psychological, one historical/physical) so Haiku recognizes the pattern across different narration types.

### Bug fix: JSON extraction in `plan_beats()`
Replaced `rfind("]")` with bracket-counting to find the exact matching `]` for the first `[`. Prevents crash when the model returns trailing text or two arrays in the same response.

---

## Version History & What We Learned

| Version | PROMPT_VERSION | Beats | What changed | Result |
|---|---|---|---|---|
| v5 | `v5-granularity-numbers-devices` | 161 | Granularity improvements, abstract-idea visual devices, STAY FLAT AND SIMPLE, FINAL CHECK | Best at the time |
| v6 | `v6-granularity2-shape-override` | 161 | Added "shape override" for dinosaurs/fire/planets | Worse — too skeletal |
| v7 | `v7-rich-descriptions-style-prefix` | 174 | Removed shape override, stronger STYLE_PREFIX, tighter split | Dinosaur scenes still inconsistent |
| v7b | same as v7 | 174 | Fixed seed=42 | Terrible — orange circle in 80% of images |
| v7b (no seed) | same as v7 | 174 | Removed seed | Still rejected |
| **v6-creative-selective** | `v6-creative-selective` | **168** | Selective creative techniques (metaphor/angle/humor/contrast) with 2 examples each | **Best version — user approved ✅** |

**Key learnings:**
- Fixed seed in FLUX = compositional motif bleeds across all images. Never use fixed seed.
- Shape override (geometric primitives) makes images too sparse/skeletal.
- FLUX Dev is worse than Schnell for MS Paint flat style.
- Style prefix additions for animals/fire/planets cause unintended side effects.
- Selective creativity (only beats that earn it) is better than forced creativity on every beat.
- Two examples per technique in the prompt gives Haiku a pattern to recognize, not just a single case to copy.

---

## Current File State (v6-creative-selective)

### `tools/video-generator/scene_generator.py`
- `PROMPT_VERSION = "v6-creative-selective"`
- `MODEL = "claude-haiku-4-5-20251001"`
- `BATCH_SIZE = 15`
- Split threshold: ~4 seconds per beat
- Creative section: 4 techniques × 2 examples each, selective application
- JSON extraction: bracket-counting (not rfind)

### `tools/video-generator/image_gen.py`
- `FAL_MODEL = "fal-ai/flux/schnell"`
- STYLE_PREFIX = v2 (original, locked — do NOT add more constraints)
- No seed parameter (random per image)

### `tools/video-generator/video_assembler.py`
- Uses concat filter (NOT concat demuxer) — sync-drift fix, do not revert
- `FPS = 30`, frame-accurate duration computation via `compute_frame_durations()`
- `burn_subtitles=False` (ffmpeg on this machine lacks libass)

---

## What Still Needs Work

### Style consistency (partially solved, ongoing)
The three problem categories that still break the MS Paint flat style:
1. **Dinosaurs / prehistoric creatures** — FLUX renders detailed skin/scales
2. **Fire / lava / volcanoes** — cinematic glow and gradients
3. **Space objects (planets/moons)** — realistic surface texture

**Proposed next approach (NOT yet implemented):**
- Switch to `fal-ai/flux-lora` + a flat/vector style LoRA from HuggingFace
  - **Cost implication:** flux-lora runs on FLUX Dev, ~$8/run vs ~$1/run for Schnell
  - Candidate LoRAs: Nano Banana (flat illustration), renderartist Simple Vector
  - Decision deferred — v6-creative-selective was validated first before committing to LoRA cost

---

## Environment Notes

- FAL_KEY and ANTHROPIC_API_KEY are in `~/.zshrc` — always run with `source ~/.zshrc && python3 ...`
- ffmpeg is installed via Homebrew but **lacks libass** (no subtitle burning support)
- SSH key for GitHub: `~/.ssh/id_ed25519_github`
- Python 3.9 (system), dependencies in `tools/video-generator/requirements.txt`

---

## Run Command

```bash
source ~/.zshrc && cd tools/video-generator && python3 main.py \
  --srt "Testing/What Did Earth Look Like Before Humans.srt" \
  --audio "Testing/What Did Earth Look Like Before Humans_.mp3" \
  --out-dir Testing/output \
  --no-review
```

---

## Test Assets (Zenn reference video)
```
tools/video-generator/Testing/
  What Did Earth Look Like Before Humans.srt   ← transcript
  What Did Earth Look Like Before Humans_.mp3  ← audio
  output/scenes.json                           ← v6-creative-selective beat plan (168 beats)
  output/images/scene_001.png … scene_168.png  ← current images (v6-creative-selective) ✅
  output/video-raw.mp4                         ← current video (v6-creative-selective) ✅
  output/video-raw-v6-run1.mp4                 ← saved v6 run 1 for reference
```
