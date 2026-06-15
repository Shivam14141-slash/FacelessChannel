"""
Orchestrator for the Orin video generator (PLAN.md Section 5).

Pipeline:
  1. Parse & reconstruct sentences from transcript.srt   (transcript_parser.py)
  2. Plan beats (Claude API, cached to scenes.json)      (scene_generator.py)
  3. Render each beat to a PNG                           (scene_generator.py)
  4. [review checkpoint — pause here unless --no-review]
  5. Assemble video-raw.mp4                              (video_assembler.py)

Usage:
  python3 main.py --srt path/to/transcript.srt --audio path/to/audio.mp3 \\
      --out-dir output/ [--script path/to/script-directed.md] [--no-review]

For the v0 Zenn test (PLAN.md Section 7):
  python3 main.py \\
      --srt "Testing/What Did Earth Look Like Before Humans.srt" \\
      --audio "Testing/What Did Earth Look Like Before Humans_.mp3" \\
      --out-dir Testing/output
"""

from __future__ import annotations

import argparse
import os

import scene_generator
import transcript_parser
import video_assembler


def _read_section_context(script_path: str | None) -> str | None:
    if not script_path or not os.path.exists(script_path):
        return None
    with open(script_path, "r", encoding="utf-8") as f:
        return f.read()


def run(srt_path: str, audio_path: str, out_dir: str,
        script_path: str | None = None, no_review: bool = False,
        force_replan: bool = False) -> str:
    os.makedirs(out_dir, exist_ok=True)
    images_dir = os.path.join(out_dir, "images")
    cache_path = os.path.join(out_dir, "scenes.json")
    output_path = os.path.join(out_dir, "video-raw.mp4")

    # Step 1 — parse & reconstruct sentences
    fragments = transcript_parser.parse_srt(srt_path)
    sentences = transcript_parser.reconstruct_sentences(fragments)
    print(f"[1/4] Reconstructed {len(sentences)} sentences from "
          f"{len(fragments)} transcript fragments.")

    # Step 2 — plan beats (cached)
    section_context = _read_section_context(script_path)
    beats = scene_generator.plan_beats(
        sentences, section_context=section_context,
        cache_path=cache_path, force=force_replan,
    )
    print(f"[2/4] Planned {len(beats)} visual beats (cached at {cache_path}).")

    # Step 3 — render images
    image_paths = scene_generator.render_all(beats, out_dir=images_dir)
    print(f"[3/4] Rendered {len(image_paths)} images to {images_dir}/")

    # Review checkpoint
    if not no_review:
        print("\nReview the images in", images_dir)
        print("Edit scenes.json and re-run with the same command to "
              "regenerate specific images, or pass --no-review to skip "
              "this checkpoint.")
        answer = input("Continue to video assembly now? [y/N] ").strip().lower()
        if answer != "y":
            print("Stopping before assembly. Re-run the same command to continue.")
            return ""

    # Step 4 — assemble video
    video_assembler.assemble_video(
        image_paths, beats, audio_path, output_path, work_dir=out_dir,
    )
    print(f"[4/4] Done -> {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Orin video generator")
    parser.add_argument("--srt", required=True, help="Path to transcript.srt")
    parser.add_argument("--audio", required=True, help="Path to audio file (wav/mp3)")
    parser.add_argument("--out-dir", required=True, help="Output directory")
    parser.add_argument("--script", default=None,
                         help="Optional path to script-directed.md for section context")
    parser.add_argument("--no-review", action="store_true",
                         help="Skip the manual review checkpoint before assembly")
    parser.add_argument("--force-replan", action="store_true",
                         help="Ignore scenes.json cache and re-call the API")
    args = parser.parse_args()

    run(
        srt_path=args.srt,
        audio_path=args.audio,
        out_dir=args.out_dir,
        script_path=args.script,
        no_review=args.no_review,
        force_replan=args.force_replan,
    )


if __name__ == "__main__":
    main()
