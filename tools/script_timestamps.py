#!/usr/bin/env python3
"""One-off helper: computes cumulative (M:SS) timestamps for a narration block
at 180 WPM (3 words/sec), given a sequence of spoken lines and [PAUSE: Xs] gaps.
Not part of the production pipeline — used while drafting script-directed.md.
"""
import sys

WPS = 180 / 60  # words per second


def fmt(t):
    m = int(t // 60)
    s = round(t % 60)
    if s == 60:
        m += 1
        s = 0
    return f"{m}:{s:02d}"


def run(start, items):
    t = start
    out = []
    for kind, val in items:
        if kind == "pause":
            t += val
            out.append((kind, val, fmt(t)))
        else:
            words = len(val.split())
            t += words / WPS
            out.append((kind, val, fmt(t)))
    return out, t


if __name__ == "__main__":
    pass
