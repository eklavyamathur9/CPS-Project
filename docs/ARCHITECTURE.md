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
│  │ Input Text   │        │  Notebook (tabs)            │      │
│  │ (paragraph)  │        │  - Analysis Result          │      │
│  │ Noise Toggle │        │  - Waveform                 │      │
│  │ Buttons      │        │                             │      │
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
| `KEY_FREQUENCIES` | dict | Key → frequency mapping (48 keys: A–Z, 0–9, SPACE, 11 punctuation marks) |
| `TOLERANCE` | 8.0 | Max accepted frequency error (Hz) |
| `DEADLINE_MS` | 50.0 | Real-time deadline (ms) |
| `WCET_TRIALS` | 20 | Number of trials for robust median/P95 WCET |

**Core functions**

| Function | Purpose |
|---|---|
| `check_invariants()` | Verifies positive/unique/valid frequencies |
| `generate_frequency(key, noise)` | Produces the synthetic frequency for a key |
| `identify_key(frequency)` | Nearest-frequency classification (returns key or UNKNOWN) |
| `process_frequency(frequency)` | Full pipeline: analysis + matching + timing |
| `reconstruct_sequence(text, noise)` | Reconstructs a full sequence, returns stats |
| `reconstruct_sequence_wcet(text, noise, trials)` | Multi-trial WCET: returns median + P95 |
| `compute_confidence(key, error)` | Per-key confidence score in [0, 1] |
| `sequence_details(text, noise)` | Per-key frequency/error/time/confidence list |
| `format_report(text, noise, trials)` | Single report builder for GUI + export |
| `export_report(text, path, ...)` | Writes the report to a text file (optional PNGs) |
| `liveness_test()` | Verifies the system can process new input |
| `termination_test()` | Verifies a finite sequence terminates |
| `keys_from_text(text)` | Converts text to a list of key symbols |
| `key_from_char(char)` | Maps a single character to a key symbol (or None) |

**GUI class**: `AcousticSideChannelApp`
- Manages the tkinter interface with two tabs (Analysis, Waveform), a File menu
  (Export Report, Copy Results), a **multi-line input box** (accepted input is
  a full paragraph: A–Z, 0–9, SPACE and punctuation `. , ! ? ; : ' " ( ) -`;
  newlines and unsupported characters are skipped), and an on-screen **keypad**
  (A–Z + 0–9 + SPACE + Clear) whose buttons append keys incrementally.
- `_current_input()` reads the text box via `get("1.0", "end-1c")`, dropping
  only tk.Text's implicit trailing newline and preserving the user's spaces.
- `on_key_pressed(key)` appends a key to the end of the input text, runs the
  per-key pipeline, and updates the waveform plots **live** on each press.
- `analyze()` runs the full analysis by delegating to `format_report()` and
  writes the result to the text output.
- `export_report()` saves the report to disk (optionally with PNG plots).
- `copy_result()` copies the current output to the clipboard.
- `show_visualization()` / `_build_live_canvas()` build a reusable two-panel
  figure (spectrogram + sine) that incremental updates keep refreshing.
- `clear_live()` resets the accumulated keys, input text, and live canvas.

### `src/waveform_visualization.py`

The visualization module using matplotlib and numpy.

| Constant | Value | Purpose |
|---|---|---|
| `SAMPLE_RATE` | 44100 | Simulated acoustic sampling rate (Hz) |
| `DURATION` | 0.05 | Per-key burst duration (s) |
| `MAX_PLOT_KEYS` | 30 | Maximum keys rendered in one plot/update (keeps paragraph-size inputs responsive) |

| Function | Purpose |
|---|---|
| `generate_sine(key, ...)` | Returns `(t, signal)` for a key's sine wave |
| `plot_sine_waves(keys, ...)` | Stacked sine-plot per key (capped at MAX_PLOT_KEYS); returns a Figure |
| `plot_spectrogram(keys, ...)` | Frequency-vs-time heatmap (capped at MAX_PLOT_KEYS); returns a Figure |
| `compute_spectrogram(keys, noise)` | Shared FFT spectrogram computation; returns grids |
| `update_sine_plot(fig, axes, keys, noise)` | Incrementally refreshes the sine plot for a growing key list |
| `update_spectrogram(fig, ax, keys, noise)` | Incrementally refreshes the spectrogram for a growing key list |
| `save_visualizations(keys, dir)` | Saves both plots as PNG files |
| `_unique_path(directory, name)` | Returns a non-colliding (timestamped) file path |

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
compute_confidence(key, error) ──► C = 1 − error/TOLERANCE (clamped [0,1])
   │
   ▼
format_report ──► single report string (GUI output + exported file)
   │
   ▼
reconstruct_sequence_wcet ──► (median, P95) across WCET_TRIALS trials
```

## CPS Verification Mapping

| CPS concept | Where it lives |
|---|---|
| Application | `AcousticSideChannelApp` |
| Real-time task | `process_frequency` |
| WCET | `reconstruct_sequence_wcet` → median + P95 over `WCET_TRIALS` |
| Deadline | `DEADLINE_MS` constant + pass/fail display |
| Invariants | `check_invariants()` |
| Liveness | `liveness_test()` |
| Termination | `termination_test()` |
| Ranking function | `identify_key` → `smallest_error` (V) |
| Confidence | `compute_confidence` → 1 − V/TOLERANCE |
| Safety | `identify_key` returns `"UNKNOWN"` when out of tolerance |
| Outcome | `format_report` → reconstructed sequence + stats |

## Dependencies

- Python 3 standard library (tkinter, time, random, math, os, sys)
- numpy (waveform arrays)
- matplotlib (plotting)

No audio/microphone hardware or libraries are used.
