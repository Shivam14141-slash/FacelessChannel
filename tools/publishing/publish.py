#!/usr/bin/env python3
"""
Publishing tool for the Orin YouTube channel.

Generates YouTube-optimized titles, description, tags, and MS Paint thumbnail
for a completed episode. Runs SEPARATELY from the video pipeline — use it
only once the video is finalized.

Usage:
  # Step 1 — generate titles, description, tags:
  python3 tools/publishing/publish.py --episode ep01-fear-of-judgment

  # Step 2 — generate thumbnail after picking a title:
  python3 tools/publishing/publish.py --episode ep01-fear-of-judgment \
      --thumbnail "The Real Reason You Fear Being Judged"

Outputs:
  videos/[episode]/publishing.md   ← titles, description, tags
  videos/[episode]/thumbnail.png   ← MS Paint thumbnail (1280x720)
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request

import anthropic

EPISODES_DIR = "videos"

# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------

TITLE_SYSTEM = """\
You are a YouTube title specialist for a psychology and human behavior channel \
called Orin.

Channel style: Calm, curious, documentary — like telling a fascinating story \
to one friend at 11 PM. Reference channels: Zenn, The Thought Vortex, GranKhelafa.
Target audience: People curious about psychology, evolution, history, and what \
makes humans tick.

TITLE RULES — follow all of these exactly:
1. Max 60 characters — titles get cut off in search results after this.
2. Front-load the main keyword — YouTube's algorithm reads left to right.
3. Use the CURIOSITY GAP — the title implies something the viewer doesn't \
know yet and needs to find out.
4. Deliverable — the title must match what the video actually covers. No bait.
5. Statement OR question — never both in the same title.
6. Never start with "Why" — it signals a dry explanation. Use "The Real \
Reason", "What Actually Happens When", "The Truth About", "How Your Brain" \
instead — these signal a story.
7. No clickbait — no "You won't believe", "SHOCKING", "This will change your \
life", "Must watch".
8. Emotional resonance — the best titles make the reader feel seen \
("You've probably felt this your whole life") or curious ("Most people get \
this completely wrong").

Generate exactly 5 title options. Each title on its own line, followed by \
one short sentence explaining the psychological hook it uses.

Output format (no extra text, just this):
1. [Title]
   Hook: [one sentence]

2. [Title]
   Hook: [one sentence]

3. [Title]
   Hook: [one sentence]

4. [Title]
   Hook: [one sentence]

5. [Title]
   Hook: [one sentence]
"""

DESCRIPTION_SYSTEM = """\
You are writing a YouTube description for a psychology and human behavior \
channel called Orin.

Channel style: Calm, curious, documentary — not loud, not hype, not corporate.
Tone: Human, conversational, slightly poetic. Like the video itself.

STRUCTURE — follow this exactly:

[Line 1]: A single emotionally resonant sentence that creates curiosity or \
makes the viewer feel seen. This is the most important line — it appears \
before "Show more" and determines if someone clicks to read more.
[Line 2]: One sentence that extends or deepens line 1. Together, lines 1-2 \
should feel like the opening of a great essay, not a description of a video.

[blank line]

[Body — 3-4 sentences]: What this video actually explores. Don't summarize \
the script — describe the experience of watching. What question does it \
answer? What feeling does it leave you with?

[blank line]

─────────────────────────────
[ADD TIMESTAMPS]
─────────────────────────────

[blank line]

If this made you think, subscribe — new videos on psychology, history, and \
what it means to be human.

[blank line]

#[3-5 most relevant hashtags inline]

SEO RULES:
- Primary keyword must appear naturally in the first 2 lines.
- Use keyword variations — not the same exact phrase repeated.
- Total: 150-250 words.
- Never start with "In this video..." — most overused opener on YouTube.
- No bullet points, no headers — flowing prose only.
"""

TAGS_SYSTEM = """\
Generate exactly 20 YouTube tags for this video.

MIX:
- 5 broad tags: single words or very short phrases covering the whole channel \
niche (psychology, human behavior, evolution, history, science)
- 10 niche tags: 2-4 word phrases specific to this video's exact topic
- 5 long-tail tags: 4-6 word phrases matching how someone would actually \
search for this content

RULES:
- Total character count must be under 500 (YouTube's tag limit)
- First tag = the single most important keyword for this video
- No repetition — each tag must be meaningfully different
- No # symbols — plain text only
- All lowercase

Return a single comma-separated line. No numbers, no explanations, nothing else.
"""

THUMBNAIL_SYSTEM = """\
You are designing a YouTube thumbnail for a psychology/history channel called \
Orin. The visual style is MS Paint — white background, stick figures with \
round heads and line bodies, thick uneven black outlines, flat colors only \
(red, blue, green, yellow, orange, brown, grey). Simple, intentionally \
imperfect, like the channel Zenn on YouTube.

THUMBNAIL REQUIREMENTS:
- ONE clear focal point — one stick figure or one strong central element
- High contrast — thick black outlines, one bold flat color accent
- Emotionally striking — should make someone stop mid-scroll
- Must be readable and recognizable at 98x98 pixels (comment section size)
- The image should visually tell the story of the title even without text
- Optional: max 3-word bold text overlay if it adds impact

Given the video title, describe the PERFECT MS Paint thumbnail scene. Be \
very specific about what is drawn, where things are positioned, what the \
single color accent is, and whether a text overlay appears.

Then on separate lines, add:
TEXT_OVERLAY: [3 words maximum, or NONE]
COLOR_ACCENT: [exactly one of: red, blue, green, yellow, orange]

The scene description (not the metadata lines) will be sent directly to an \
AI image generator — make it concrete, not abstract. Describe actual shapes \
and positions, not moods.

CRITICAL — the scene description must never mention any literal words, \
letters, or text content (e.g. do not write "with bold letters reading X" or \
"a sign saying Y" inside the scene description). The image model cannot spell \
reliably, even short words — that is why TEXT_OVERLAY exists as a separate \
field. Text is added afterward by Pillow, never by the image generator \
itself. The scene description should describe ONLY drawable shapes, poses, \
and props — zero text content of any kind.
"""

FLUX_STYLE_PREFIX = (
    "MS Paint style illustration, white background, thick uneven wobbly black "
    "outlines, stick figure humans with round circle heads and simple line bodies, "
    "flat colors only no shading no gradients no 3D no realistic textures, "
    "simple geometric shapes, amateur hand-drawn look intentionally imperfect, "
    "Zenn YouTube channel visual style, lots of white empty space — "
)

# FLUX cannot render text reliably — all text overlays are drawn with Pillow
# after the image is generated, never inside the FLUX prompt itself.
IMPACT_FONT = "/System/Library/Fonts/Supplemental/Impact.ttf"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _read_script(episode_dir: str) -> str:
    for name in ["script-directed.md", "script.md"]:
        path = os.path.join(episode_dir, name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    print(f"ERROR: No script file found in {episode_dir}")
    sys.exit(1)


def _call_sonnet(client: anthropic.Anthropic, system: str,
                 user: str, max_tokens: int = 1024) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text.strip()


def _overlay_text(image_path: str, text: str, color_accent: str,
                  max_height_ratio: float = 0.16) -> None:
    """Draws bold short text onto a generated thumbnail using Pillow.

    FLUX hallucinates spelling on any text it renders, so text is always
    added after the fact instead of being requested in the FLUX prompt.

    Shrinks to fit both a max width AND a max height, since the bottom strip
    of a thumbnail often has a figure standing close to the edge — sizing on
    width alone can let the stroked text clip into it.
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    text = text.upper()

    max_width = w * 0.88
    max_height = h * max_height_ratio
    size = 120
    while size > 24:
        font = ImageFont.truetype(IMPACT_FONT, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        stroke_width = max(4, size // 14)
        total_w = (bbox[2] - bbox[0]) + stroke_width * 2
        total_h = (bbox[3] - bbox[1]) + stroke_width * 2
        if total_w <= max_width and total_h <= max_height:
            break
        size -= 4

    margin = h * 0.025
    y = h - margin - (total_h / 2)
    draw.text(
        (w / 2, y), text, font=font,
        fill=color_accent, stroke_width=stroke_width, stroke_fill="black",
        anchor="mm",
    )
    img.save(image_path)


# --------------------------------------------------------------------------
# Step 1 — generate titles, description, tags
# --------------------------------------------------------------------------

def generate_assets(episode_dir: str, episode_name: str) -> None:
    script = _read_script(episode_dir)
    client = anthropic.Anthropic()

    topic = episode_name.split("-", 1)[-1].replace("-", " ").title()
    context = f"Episode: {episode_name}\nTopic: {topic}\n\nFULL SCRIPT:\n\n{script}"

    print("Generating titles...")
    titles = _call_sonnet(client, TITLE_SYSTEM, context)

    print("Generating description...")
    description = _call_sonnet(client, DESCRIPTION_SYSTEM, context, max_tokens=1024)

    print("Generating tags...")
    tags = _call_sonnet(client, TAGS_SYSTEM, context, max_tokens=256)

    out_path = os.path.join(episode_dir, "publishing.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Publishing Assets — {episode_name}\n\n")

        f.write("## Titles (pick one)\n\n")
        f.write(titles + "\n\n")
        f.write("**Chosen title:** _(fill in after reviewing above)_\n\n")
        f.write("---\n\n")

        f.write("## Description\n\n")
        f.write(description + "\n\n")
        f.write("---\n\n")

        f.write("## Tags\n\n")
        f.write(tags + "\n\n")
        f.write("---\n\n")

        f.write("## Thumbnail\n\n")
        f.write("_Run the thumbnail step after choosing a title:_\n\n")
        f.write("```\n")
        f.write(f'python3 tools/publishing/publish.py --episode {episode_name} \\\n')
        f.write('    --thumbnail "Your Chosen Title"\n')
        f.write("```\n")

    print(f"\nDone → {out_path}")
    print("\nNext steps:")
    print("  1. Open publishing.md and pick a title")
    print("  2. Run the thumbnail step with your chosen title")


# --------------------------------------------------------------------------
# Step 2 — generate thumbnail
# --------------------------------------------------------------------------

def generate_thumbnail(episode_dir: str, episode_name: str, title: str,
                       avoid: str | None = None) -> None:
    try:
        import fal_client
    except ImportError:
        print("ERROR: fal_client not installed. Run: pip install fal-client")
        sys.exit(1)

    client = anthropic.Anthropic()

    print(f'Designing thumbnail for: "{title}"')
    user_msg = f"Video title: {title}"
    if avoid:
        user_msg += f"\n\nDo not repeat this concept — it was already rejected: {avoid}"
    scene_text = _call_sonnet(client, THUMBNAIL_SYSTEM, user_msg, max_tokens=512)
    print(f"\nThumbnail concept:\n{scene_text}\n")

    # Parse metadata lines and clean scene description
    text_overlay = None
    color_accent = "red"
    clean_lines = []
    for line in scene_text.split("\n"):
        if line.startswith("TEXT_OVERLAY:"):
            val = line.replace("TEXT_OVERLAY:", "").strip()
            if val.upper() != "NONE":
                text_overlay = val
        elif line.startswith("COLOR_ACCENT:"):
            color_accent = line.replace("COLOR_ACCENT:", "").strip().lower()
        else:
            clean_lines.append(line)
    scene_description = " ".join(clean_lines).strip()

    flux_prompt = FLUX_STYLE_PREFIX + scene_description

    print("Generating thumbnail scene via FLUX...")
    result = fal_client.run(
        "fal-ai/flux/schnell",
        arguments={
            "prompt": flux_prompt,
            "image_size": {"width": 1280, "height": 720},
            "num_inference_steps": 4,
            "num_images": 1,
            "enable_safety_checker": False,
        },
    )

    image_url = result["images"][0]["url"]
    out_path = os.path.join(episode_dir, "thumbnail.png")
    urllib.request.urlretrieve(image_url, out_path)

    if text_overlay:
        print(f'Adding text overlay via Pillow: "{text_overlay}"')
        _overlay_text(out_path, text_overlay, color_accent)

    print(f"\nDone → {out_path}")
    print("Upload this as your YouTube custom thumbnail (1280x720).")


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Orin publishing tool")
    parser.add_argument(
        "--episode", required=True,
        help="Episode folder name (e.g. ep01-fear-of-judgment)"
    )
    parser.add_argument(
        "--thumbnail", default=None, metavar="TITLE",
        help="Chosen title — generates thumbnail.png and skips asset generation"
    )
    parser.add_argument(
        "--avoid", default=None, metavar="CONCEPT",
        help="Describe a previously rejected thumbnail concept to steer away from"
    )
    args = parser.parse_args()

    episode_dir = os.path.join(EPISODES_DIR, args.episode)
    if not os.path.isdir(episode_dir):
        print(f"ERROR: Episode folder not found: {episode_dir}")
        sys.exit(1)

    if args.thumbnail:
        generate_thumbnail(episode_dir, args.episode, args.thumbnail, avoid=args.avoid)
    else:
        generate_assets(episode_dir, args.episode)


if __name__ == "__main__":
    main()
