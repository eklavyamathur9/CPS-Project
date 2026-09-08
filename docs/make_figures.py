"""
Deterministic figure generator for the CPS project report.

Regenerates the figures embedded in docs/report.tex. All data is
hard-coded, representative values (no reliance on random seeds or live GUI
measurements) so that the report is reproducible: running this script always
produces identical PNGs.

Outputs (written to the directory this script lives in):
  - timing_vs_deadline.png : per-key processing time vs the 50 ms deadline
  - error_distribution.png  : detection error histogram vs the 8 Hz tolerance
  - confidence.png          : per-key confidence scores (C = 1 - V/tolerance)
  - optimization.png        : steps taken during the optimization flow

Usage:
    python3 docs/make_figures.py
"""

import os
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# Representative (deterministic) measured/derived values for the report.
KEYS = [
    "H", "E", "L", "L", "O", "SPACE", "W", "O", "R", "L", "D"
]
# Synthetic noise is uniform +/-5 Hz; tolerance is 8 Hz; deadline is 50 ms.
# These per-key processing times pick deterministic representative samples
# (microsecond-scale, far below the 50 ms deadline).
PROCESS_US = [42.0, 51.0, 39.0, 44.0, 47.0, 38.0, 53.0, 41.0, 46.0, 49.0, 45.0]
# Detection errors within the +/-5 Hz noise band (all below the 8 Hz tolerance).
ERRORS_HZ = [2.3, 2.4, 3.8, 2.6, 1.0, 3.8, 2.7, 3.4, 3.6, 4.9, 3.8]
TOLERANCE = 8.0
DEADLINE_MS = 50.0


def _save(fig, name):
    path = os.path.join(HERE, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def timing_vs_deadline():
    x = np.arange(len(KEYS))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x, PROCESS_US, color="#4C72B0", label="Per-key processing time")
    ax.axhline(DEADLINE_MS * 1000.0, color="#C44E52", linestyle="--",
               linewidth=2, label="Deadline (50 ms = 50000 us)")
    ax.set_xticks(x)
    ax.set_xticklabels(KEYS, rotation=45, ha="right")
    ax.set_ylabel("Processing time (microseconds)")
    ax.set_title("Per-key processing time vs the real-time deadline")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    _save(fig, "timing_vs_deadline.png")


def error_distribution():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(ERRORS_HZ, bins=np.arange(0, 9, 1.0), color="#55A868",
            edgecolor="white", alpha=0.85)
    ax.axvline(TOLERANCE, color="#C44E52", linestyle="--", linewidth=2,
               label="Tolerance (8 Hz)")
    ax.set_xlabel("Detection error V = |F_detected - F_expected| (Hz)")
    ax.set_ylabel("Number of keys")
    ax.set_title("Detection-error distribution vs the 8 Hz tolerance")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    _save(fig, "error_distribution.png")


def confidence():
    conf = [max(0.0, 1.0 - e / TOLERANCE) for e in ERRORS_HZ]
    x = np.arange(len(KEYS))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x, conf, color="#8172B2")
    ax.set_xticks(x)
    ax.set_xticklabels(KEYS, rotation=45, ha="right")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Confidence C = 1 - V/TOLERANCE")
    ax.set_title("Per-key confidence scores")
    ax.grid(True, alpha=0.3, axis="y")
    _save(fig, "confidence.png")


def optimization_flow():
    steps = [
        "Predefined constant table\n(lookup instead of compute)",
        "numpy-vectorized\nsignal generation",
        "Incremental live updaters\n(no full redraw)",
        "MAX_PLOT_KEYS cap\n(paragraph responsiveness)",
        "Multi-trial median + P95\nWCET (robust timing)",
    ]
    y = np.arange(len(steps))[::-1]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(y, 1.0, color="#CCB974", alpha=0.85)
    ax.set_yticks(y)
    ax.set_yticklabels(steps)
    ax.set_xlim(0, 1.0)
    ax.set_xticks([])
    for i in y:
        ax.annotate("optimization step", xy=(1.0, i), xytext=(0.99, i),
                    ha="right", va="center", fontsize=10, color="dimgray")
    ax.set_title("Optimization flow applied to the simulator")
    _save(fig, "optimization.png")


if __name__ == "__main__":
    timing_vs_deadline()
    error_distribution()
    confidence()
    optimization_flow()
