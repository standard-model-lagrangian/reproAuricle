"""Split a session into analysis windows using the activity annotations."""
from dataclasses import dataclass

import numpy as np

from .io import NO_ANNOTATION


@dataclass
class Window:
    start: int  # sample index
    stop: int
    label: int  # activity label of the segment the window sits in
    prev_label: int  # label of the preceding segment (NO_ANNOTATION if none)
    t_since_prev_s: float  # time from the end of the preceding segment to window start
    next_label: int  # label of the following segment (NO_ANNOTATION if none)
    t_until_next_s: float  # time from window end to the start of the following segment


def segments(activity):
    """Contiguous runs of a constant label as (start, stop, label)."""
    edges = np.flatnonzero(np.diff(activity) != 0) + 1
    starts = np.r_[0, edges]
    stops = np.r_[edges, len(activity)]
    return [(int(a), int(b), int(activity[a])) for a, b in zip(starts, stops)]


def make_windows(activity, fs, window_s=60.0, min_window_s=30.0, settle_s=10.0,
                 labels=(0,), unannotated_skip_s=300.0):
    """Tile each segment whose label is in `labels` with windows of `window_s`.

    The first `settle_s` of every segment is skipped so transients from the previous
    manoeuvre do not dominate. A trailing remainder of at least `min_window_s` becomes a
    shorter window. Records without an activity channel (label NO_ANNOTATION) are tiled from
    `unannotated_skip_s` (setup period) to the end whatever `labels` says, so their windows mix
    activities; analyses that need pure rest drop label NO_ANNOTATION (docs/METHOD.md §3).
    """
    win, mn, settle = int(window_s * fs), int(min_window_s * fs), int(settle_s * fs)
    segs = segments(activity)
    out = []
    for k, (a, b, lab) in enumerate(segs):
        if lab == NO_ANNOTATION:
            a = max(a, int(unannotated_skip_s * fs))
        elif lab not in labels:
            continue
        prev = segs[k - 1][2] if k > 0 else NO_ANNOTATION
        nxt = segs[k + 1][2] if k + 1 < len(segs) else NO_ANNOTATION
        s = a + settle
        while b - s >= mn:
            e = min(s + win, b)
            out.append(Window(s, e, lab, prev, (s - a) / fs, nxt, (b - e) / fs))
            s = e
    return out
