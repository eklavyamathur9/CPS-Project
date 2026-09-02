# Development Guide

Guidance for developers and AI agents who want to extend or modify the
Acoustic Side-Channel Simulator.

---

## Setup

```bash
pip install -r requirements.txt
```

Requires Python 3, tkinter, numpy, matplotlib, and pytest (for tests).

---

## Running the Application

```bash
python3 src/acoustic_side_channel.py
```

The GUI opens with two tabs:
- **Analysis Result**: textual output of the CPS analysis.
- **Waveform**: sine + spectrogram plots (generated via the "Visualize
  Waveform" button).

There is also an on-screen **keypad** (A–Z + 0–9 + SPACE + Clear). Clicking a
keypad button appends the key to the accumulated sequence and **incrementally
updates the waveform plots live** on every key press. The status bar shows the
latest per-key frequency, detected key, error, and processing time.

---

## How Live Incremental Updates Work

Each keypad press calls `on_key_pressed(key)` in the GUI, which:
1. Appends the key to `self.pressed_keys`.
2. Syncs the entry text.
3. Runs the per-key pipeline (`generate_frequency` → `process_frequency`).
4. Calls `update_spectrogram()` and `update_sine_plot()` on the existing
   figures so the plots grow with each key (no full redraw of the window).

The plots are built once by `_build_live_canvas()` on the first key press (or
via the "Visualize Waveform" button), then refreshed incrementally. The
"Clear" button resets everything.

The pure visual math lives in `waveform_visualization.py` and is unit-tested,
so the GUI wiring stays thin and the logic stays headless-testable.

---

## Project Layout

```
src/
  acoustic_side_channel.py      # core logic + GUI
  waveform_visualization.py     # matplotlib visualization module
tests/
  test_frequency.py             # unit tests
docs/
  report.tex / report.pdf       # submission report
```

---

## Adding a New Key

1. Add the key to `KEY_FREQUENCIES` in `src/acoustic_side_channel.py`.
   Choose a frequency that is at least `2 × TOLERANCE` away from existing
   frequencies to avoid ambiguity.
2. Update the `keys_from_text` mapping if the character is non-alphabetic
   (e.g. a space → `"SPACE"`).
3. (Optional) Update the frequency table in `docs/report.tex`.
4. Add/update a unit test in `tests/test_frequency.py`.

---

## Changing the Tolerance or Deadline

These are constants in `src/acoustic_side_channel.py`:

- `TOLERANCE` — max accepted frequency error (Hz). Effects on the test
  `test_frequency_just_below_tolerance_matches` and
  `test_frequency_just_above_tolerance_is_unknown`.
- `DEADLINE_MS` — real-time deadline. Checked by `test_wcet_below_deadline`.

---

## Modifying the Waveform Module

Functions in `src/waveform_visualization.py`:

- `generate_sine(key, duration, sample_rate, noise)` — returns `(t, signal)`.
- `plot_sine_waves(keys, title, noise)` — returns a matplotlib `Figure`.
- `plot_spectrogram(keys, title, noise)` — returns a matplotlib `Figure`.
- `save_visualizations(keys, directory, noise)` — saves PNGs, used by the
  report.

To change the plotted frequency band in the spectrogram, adjust the mask
`(freqs >= 350) & (freqs <= 1600)`.

---

## Running Tests

```bash
python3 -m pytest tests/ -v
```

Always run the full test suite after modifying the core logic.

---

## Rebuilding the Report

```bash
cd docs
pdflatex report.tex
```

The report embeds `waveform_sine.png` and `waveform_spectrogram.png` from the
`docs/` directory. Regenerate them if you change keys or the sequence. Note
that `save_visualizations` writes timestamped filenames to avoid overwriting,
so to refresh the tracked report figures, save the plots directly to the
canonical `waveform_sine.png` / `waveform_spectrogram.png` paths:

```bash
cd src
python3 -c "
import matplotlib; matplotlib.use('Agg')
from waveform_visualization import plot_sine_waves, plot_spectrogram
keys = ['H','E','L','L','O','SPACE','W','O','R','L','D']
plot_sine_waves(keys, noise=False).savefig('../docs/waveform_sine.png', dpi=150)
plot_spectrogram(keys, noise=False).savefig('../docs/waveform_spectrogram.png', dpi=150)
"
```

---

## Coding Conventions

- Python 3, standard library + numpy/matplotlib.
- Docstrings on all public functions.
- `UPPER_CASE` constants for configuration.
- Self-contained, testable functions.
- No comments except section markers and function docstrings.

---

## Testing Checklist (CPS Verification)

Before considering a change complete:

- [ ] `python3 -m pytest tests/ -v` passes.
- [ ] Invariants still hold (`check_invariants`).
- [ ] Liveness and termination tests pass.
- [ ] WCET stays below `DEADLINE_MS`.

## Do NOT

- Add audio/microphone capture features. Keep it a simulation.
- Rename the release claim to imply real acoustic signal capture.
