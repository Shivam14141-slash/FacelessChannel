#!/usr/bin/env python3
"""
Normalize and concat batch voiceover files for the Orin pipeline.

What this does:
  1. Finds all batch_XX*.wav files in --input-dir, sorted in order
  2. Normalizes each batch to -16 LUFS (YouTube loudness standard)
     — fixes volume mismatch between batches recorded in different sessions
  3. Concatenates all normalized batches into one final WAV file

After this script:
  Open the output file in Audacity and run the final polish chain:
  Noise Reduction → Compress (3:1, -18dB) → EQ → Limiter (-1dB) → Export

Usage:
  python3 tools/concat_audio.py \
    --input-dir videos/ep01-fear-of-judgment/Batch_Audio_Enhance \
    --output videos/ep01-fear-of-judgment/audio-raw.wav
"""

from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import tempfile


def get_sorted_batches(input_dir: str) -> list:
    """Grabs every audio file in the folder, sorted by name.

    Batch naming varies per episode (e.g. "batch_01.wav" vs "ER2_Batch_01.m4a"),
    so this doesn't match a fixed prefix — it relies on the input folder being
    dedicated to one episode's batches, zero-padded so name order == take order.
    """
    files = []
    for ext in ("*.wav", "*.mp3", "*.m4a"):
        files += glob.glob(os.path.join(input_dir, ext))
    if not files:
        print(f"No .wav, .mp3, or .m4a files found in: {input_dir}")
        sys.exit(1)
    return sorted(files)


def normalize(input_path: str, output_path: str) -> None:
    """Normalize a single file to -16 LUFS using ffmpeg loudnorm filter."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar", "48000", "-ac", "2",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"\nERROR normalizing {os.path.basename(input_path)}:")
        print(result.stderr[-800:])
        sys.exit(1)


def concat(file_list: list, output_path: str) -> None:
    """Concat a list of WAV files using ffmpeg concat demuxer."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for path in file_list:
            f.write(f"file '{os.path.abspath(path)}'\n")
        list_path = f.name

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", list_path,
        "-c", "copy",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.unlink(list_path)
    if result.returncode != 0:
        print(f"\nERROR during concat:")
        print(result.stderr[-800:])
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize and concat batch voiceover files"
    )
    parser.add_argument(
        "--input-dir", required=True,
        help="Folder containing batch_01.wav, batch_02.wav, etc."
    )
    parser.add_argument(
        "--output", required=True,
        help="Output path for the merged WAV file (e.g. audio-raw.wav)"
    )
    args = parser.parse_args()

    batches = get_sorted_batches(args.input_dir)

    print(f"Found {len(batches)} batch files:")
    for b in batches:
        print(f"  {os.path.basename(b)}")

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        print(f"\nNormalizing to -16 LUFS...")
        normalized = []
        for i, batch in enumerate(batches, 1):
            name = os.path.splitext(os.path.basename(batch))[0]
            out = os.path.join(tmp, f"{i:02d}_{name}_norm.wav")
            print(f"  [{i}/{len(batches)}] {os.path.basename(batch)}...", flush=True)
            normalize(batch, out)
            normalized.append(out)

        print(f"\nConcatenating {len(normalized)} files...")
        concat(normalized, args.output)

    size_mb = os.path.getsize(args.output) / 1_000_000
    print(f"\nDone → {args.output} ({size_mb:.1f} MB)")
    print("\nNext steps:")
    print("  1. Open in Audacity")
    print("  2. Noise Reduction → Compress (3:1, -18dB) → EQ → Limiter (-1dB)")
    print("  3. Export as WAV → audio-final.wav")


if __name__ == "__main__":
    main()
