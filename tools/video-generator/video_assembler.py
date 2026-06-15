"""
Step 4 — video assembly (PLAN.md Section 5).

Takes the rendered scene images + their beat timings + the audio track and
stitches them into video-raw.mp4 with ffmpeg:
  - each image is held on screen for its beat's duration
  - audio is overlaid
  - subtitles (built from the beats' narration text) are burned in

v0: simple cuts between images (no crossfades yet — see PLAN.md Section 6
open questions; crossfades can be added later without changing this
module's interface).

Requires ffmpeg on PATH (brew install ffmpeg).
"""

from __future__ import annotations

import os
import subprocess


def _format_srt_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    h, millis = divmod(millis, 3600000)
    m, millis = divmod(millis, 60000)
    s, millis = divmod(millis, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{millis:03d}"


def write_srt(beats: list[dict], srt_path: str) -> None:
    """Build a subtitle file from the beats' narration text."""
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, beat in enumerate(beats, start=1):
            f.write(f"{i}\n")
            f.write(
                f"{_format_srt_timestamp(beat['start'])} --> "
                f"{_format_srt_timestamp(beat['end'])}\n"
            )
            f.write(f"{beat['text']}\n\n")


FPS = 30


def compute_frame_durations(beats: list[dict]) -> list[float]:
    """
    Compute each image's on-screen duration in seconds, rounded to whole
    frames at FPS, so that the cut points land on exact frame boundaries
    with no cumulative rounding drift.

    The ffmpeg concat demuxer's per-file `duration` directive is quantized
    to the image2 demuxer's default 1/25s timebase — each cut can be off by
    up to ~0.02s, and across ~60+ cuts that error accumulates to ~1s of
    drift (images appearing visibly ahead of the narration by the second
    half of the video). Pre-rounding each duration to a whole number of
    frames here, and deriving it from cumulative frame-boundary positions
    (not from each beat's own duration independently), means rounding error
    never compounds — every cut's frame position is anchored to its own
    beat['start'] time, not to the sum of previous (rounded) durations.

    Each image is held until the *next* beat's start time (not just its own
    end time), so silent gaps between beats are absorbed into the previous
    image's display time instead of being dropped from the timeline.

    The video timeline starts at t=0, but the first beat's narration doesn't
    start until beats[0]['start'] (a leading silence). The first image's
    duration covers that lead-in too (0 -> beats[1]['start']) so every later
    cut still lands exactly on its beat's start.
    """
    n = len(beats)
    frame_bounds = []
    for i in range(n):
        start = 0.0 if i == 0 else beats[i]["start"]
        frame_bounds.append(round(start * FPS))
    frame_bounds.append(round(beats[-1]["end"] * FPS))

    durations = []
    for i in range(n):
        frames = frame_bounds[i + 1] - frame_bounds[i]
        frames = max(1, frames)
        durations.append(frames / FPS)
    return durations


def assemble_video(image_paths: list[str], beats: list[dict], audio_path: str,
                    output_path: str, work_dir: str = ".",
                    burn_subtitles: bool = False) -> str:
    """
    Build video-raw.mp4 from rendered images + beat timings + audio.
    Returns the output path.

    Each image is fed in as its own `-loop 1 -framerate 30 -t <dur>` input
    (duration pre-rounded to whole frames by compute_frame_durations), then
    stitched with the `concat` filter. This avoids the concat *demuxer*'s
    25fps timebase, whose per-cut rounding error accumulated to ~1s of
    drift by the second half of the video.

    burn_subtitles defaults to False because the Homebrew ffmpeg build on
    this machine isn't compiled with libass, so the `subtitles` filter isn't
    available ("Filter not found"). Re-enable once ffmpeg has libass
    (`brew reinstall ffmpeg` with libass support).
    """
    srt_path = os.path.join(work_dir, "subtitles.srt")
    write_srt(beats, srt_path)

    durations = compute_frame_durations(beats)

    cmd = ["ffmpeg", "-y"]
    for path, dur in zip(image_paths, durations):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.6f}", "-i", os.path.abspath(path)]
    audio_index = len(image_paths)
    cmd += ["-i", audio_path]

    n = len(image_paths)
    filter_parts = [f"[{i}:v]format=yuv420p[v{i}]" for i in range(n)]
    concat_inputs = "".join(f"[v{i}]" for i in range(n))
    filter_parts.append(f"{concat_inputs}concat=n={n}:v=1:a=0[vcat]")

    out_label = "vcat"
    if burn_subtitles:
        # Commas inside force_style must be escaped (\,) so ffmpeg's filter
        # parser doesn't treat them as separators between -vf filters.
        force_style = (
            "FontName=Arial\\,FontSize=20\\,PrimaryColour=&H00FFFFFF\\,"
            "OutlineColour=&H00000000\\,BorderStyle=3\\,Alignment=2"
        )
        filter_parts.append(
            f"[vcat]subtitles=filename='{srt_path}':force_style='{force_style}'[vout]"
        )
        out_label = "vout"

    filter_complex = ";".join(filter_parts)

    cmd += [
        "-filter_complex", filter_complex,
        "-map", f"[{out_label}]",
        "-map", f"{audio_index}:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path,
    ]

    subprocess.run(cmd, check=True)
    return output_path
