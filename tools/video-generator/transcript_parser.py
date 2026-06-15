"""
Pass 1 of the segmentation pipeline (PLAN.md Section 5.2).

TurboScribe .srt files are chopped into ~1-2 second fragments that often
split mid-sentence or mid-clause. This module reconstructs full, correctly
punctuated sentences from those fragments while preserving accurate
start/end timestamps (taken from the fragments that contained the first
and last word of each sentence).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TURBOSCRIBE_WATERMARK = re.compile(
    r"\(Transcribed by TurboScribe\.[^)]*\)\s*", re.IGNORECASE
)

SENTENCE_END_RE = re.compile(r'[.?!]+["\')\]]*$')


@dataclass
class Fragment:
    start: float
    end: float
    text: str


@dataclass
class Sentence:
    start: float
    end: float
    text: str


def timestamp_to_seconds(ts: str) -> float:
    """Convert 'HH:MM:SS,mmm' to seconds (float)."""
    hms, ms = ts.split(",")
    h, m, s = hms.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_srt(path: str) -> list[Fragment]:
    """Parse an .srt file into a list of timed text fragments."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = re.split(r"\n\s*\n", raw.strip())
    fragments = []

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if len(lines) < 2:
            continue

        # lines[0] = index, lines[1] = "start --> end", lines[2:] = text
        time_line = None
        text_lines = []
        for line in lines[1:]:
            if "-->" in line:
                time_line = line
            else:
                text_lines.append(line)

        if time_line is None or not text_lines:
            continue

        start_str, end_str = [t.strip() for t in time_line.split("-->")]
        text = " ".join(text_lines)
        text = TURBOSCRIBE_WATERMARK.sub("", text).strip()

        if not text:
            continue

        fragments.append(
            Fragment(
                start=timestamp_to_seconds(start_str),
                end=timestamp_to_seconds(end_str),
                text=text,
            )
        )

    return fragments


def reconstruct_sentences(fragments: list[Fragment]) -> list[Sentence]:
    """
    Re-split fragment text on sentence-ending punctuation to rebuild full
    sentences, while tracking which fragment each word came from so the
    rebuilt sentence keeps accurate start/end timestamps.
    """
    # Flatten fragments into a list of (word, fragment_start, fragment_end)
    words = []
    for frag in fragments:
        for word in frag.text.split():
            words.append((word, frag.start, frag.end))

    sentences = []
    buffer = []
    sentence_start = None

    for word, frag_start, frag_end in words:
        if sentence_start is None:
            sentence_start = frag_start

        buffer.append(word)

        if SENTENCE_END_RE.search(word):
            sentences.append(
                Sentence(
                    start=sentence_start,
                    end=frag_end,
                    text=" ".join(buffer),
                )
            )
            buffer = []
            sentence_start = None

    # Anything left over (no trailing punctuation) becomes a final sentence
    if buffer:
        sentences.append(
            Sentence(
                start=sentence_start,
                end=words[-1][2],
                text=" ".join(buffer),
            )
        )

    return sentences


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else (
        "Testing/What Did Earth Look Like Before Humans.srt"
    )

    fragments = parse_srt(path)
    sentences = reconstruct_sentences(fragments)

    print(f"{len(fragments)} fragments -> {len(sentences)} sentences\n")
    for s in sentences:
        print(f"[{s.start:7.2f} -> {s.end:7.2f}] {s.text}")
