# Architecture

This document describes the architecture of the Acoustic Side-Channel Simulator.

## Overview

The system is a software-only simulation of an acoustic side-channel attack.
It assigns a unique frequency signature to each key and reconstructs typed
sequences by analyzing those frequencies. There is no microphone or audio
capture; all frequencies are predefined constants.

```
┌─────────────────────────────────────────────────────────────────┐
│                     GUI (tkinter)                               │
│  ┌──────────────┐        ┌──────────────────────────────┐      │
│  │  Input Entry │        │  Notebook (tabs)            │      │
│  │  Noise Toggle│        │  - Analysis Result          │      │
│  │  Buttons     │        │  - Waveform                 │      │
│  └──────┬───────┘        └──────────────┬───────────────┘      │
│         │                               │                      │
│         ▼                               ▼                      │
└─────────┼───────────────────────────────┼──────────────────────┘
          │                               │
          ▼                               ▼
┌──────────────────────┐      ┌──────────────────────────────────┐
│ acoustic_side_channel│      │   waveform_visualization         │
│   (core logic)       │◄────►│   (matplotlib + numpy)           │
└──────────────────────┘      │  - generate_sine                 │
                             │  - plot_sine_waves               │
                             │  - plot_spectrogram              │
                             │  - save_visualizations           │
                             └──────────────────────────────────┘
```

## Modules

### `src/acoustic_side_channel.py`

The main application and core logic engine.

**Constants**

| Constant | Value | Purpose |
|---|---|---|
| `KEY_FREQUENCIES` | dict | Key → frequency mapping (27 keys) |
| `TOLERANCE` | 8.0 | Max accepted frequency error (Hz) |
| `DEADLINE_MS` | 50.0 | Real-time deadline (ms) |

**Core functions**

| Function | Purpose |
|---|---|
| `check_invariants()` | Verifies positive/unique/valid frequencies |
| `generate_frequency(key, noise)` | Produces the synthetic frequency for a key |
| `identify_key(frequency)` | Nearest-frequency classification (returns key or UNKNOWN) |
| `process_frequency(frequency)` | Full pipeline: analysis + matching + timing |
| `reconstruct_sequence(text, noise)` | Reconstructs a full sequence, returns stats |
| `liveness_test()` | Verifies the system can process new input |
| `termination_test()` | Verifies a finite sequence terminates |
| `keys_from_text(text)` | Converts text to a list of key symbols |
| `key_from_char(char)` | Maps a single character to a key symbol (or None) |

**GUI class**: `AcousticSideChannelApp`
- Manages the tkinter interface with two tabs (Analysis, Waveform).
- Provides an on-screen **keypad** (A–Z + SPACE + Clear) whose buttons append
  keys incrementally.
- `on_key_pressed(key)` appends a key, syncs the entry text, runs the per-key
  pipeline, and updates the waveform plots **live** on each press.
- `analyze()` runs the full analysis and writes results to the text output.
- `show_visualization()` / `_build_live_canvas()` build a reusable two-panel
  figure (spectrogram + sine) that incremental updates keep refreshing.
- `clear_live()` resets the accumulated keys, entry, and live canvas.

### `src/waveform_visualization.py`

The visualization module using matplotlib and numpy.

| Function | Purpose |
|---|---|
| `generate_sine(key, ...)` | Returns `(t, signal)` for a key's sine wave |
| `plot_sine_waves(keys, ...)` | Stacked sine-plot per key; returns a Figure |
| `plot_spectrogram(keys, ...)` | Frequency-vs-time heatmap; returns a Figure |
| `compute_spectrogram(keys, noise)` | Shared FFT spectrogram computation; returns grids |
| `update_sine_plot(fig, axes, keys, noise)` | Incrementally refreshes the sine plot for a growing key list |
| `update_spectrogram(fig, ax, keys, noise)` | Incrementally refreshes the spectrogram for a growing key list |
| `save_visualizations(keys, dir)` | Saves both plots as PNG files |

## Data Flow

```
Text input
   │
   ▼
keys_from_text ──► key list (A, B, C, ...)
   │
   ▼
generate_frequency(key) ──► frequency (Hz)
   │
   ▼
process_frequency(freq) ──► (detected_key, error, time_ms)
   │                        │
   │                        ├── identify_key ──► nearest match (V = |Δf|)
   │                        └── timing (WCET collection)
   ▼
reconstruct_sequence ──► (reconstructed[], avg_time, wcet, avg_error)
```

## CPS Verification Mapping

| CPS concept | Where it lives |
|---|---|
| Application | `AcousticSideChannelApp` |
| Real-time task | `process_frequency` |
| WCET | `reconstruct_sequence` → `worst_case` |
| Deadline | `DEADLINE_MS` constant + pass/fail display |
| Invariants | `check_invariants()` |
| Liveness | `liveness_test()` |
| Termination | `termination_test()` |
| Ranking function | `identify_key` → `smallest_error` (V) |
| Safety | `identify_key` returns `"UNKNOWN"` when out of tolerance |
| Outcome | `reconstruct_sequence` returns `reconstructed[]` |

## Dependencies

- Python 3 standard library (tkinter, time, random, math, os, sys)
- numpy (waveform arrays)
- matplotlib (plotting)

No audio/microphone hardware or libraries are used.
