# Handoff

Context for resuming work on the Acoustic Side-Channel Simulator in a future
session.

## Current State (Done)

The project is fully scaffolded and verified:

- **Application** — `src/acoustic_side_channel.py` with core logic + tkinter GUI
  (Analysis + Waveform tabs) and an on-screen keypad.
- **Paragraph input** — multi-line `tk.Text` input box; supported keys include
  punctuation `. , ! ? ; : ' " ( ) -` (frequencies 1550–1850 Hz);
  newlines/unmapped characters skipped, leading/trailing spaces preserved
  (`_current_input()` uses `get("1.0", "end-1c")`).
- **Live updates** — clicking keypad buttons (A–Z + 0–9 + SPACE + Clear) appends a key
  and incrementally updates the sine + spectrogram plots on each press, via
  `on_key_pressed` → `update_sine_plot` / `update_spectrogram`.
- **Visualization** — `src/waveform_visualization.py` (sine waves + spectrogram,
  plus incremental updaters and a shared `compute_spectrogram` helper). Plot
  rendering is capped at `MAX_PLOT_KEYS = 30` so long paragraphs stay responsive.
- **Tests** — `tests/test_frequency.py`, 62 tests, all passing.
- **Report** — `docs/report.tex` compiled to `docs/report.pdf`.
- **Docs** — `README.md`, `CLAUDE.md`, and the full docs/ set.
- **Memory** — `.memory/CURRENT_SESSION.md`, `PROJECT_CONTEXT.md`, `HANDOFF.md`.

## How to Verify Everything Works

```bash
# Tests
python3 -m pytest tests/ -v

# App (needs a display)
python3 src/acoustic_side_channel.py

# Report
cd docs && pdflatex report.tex
```

The GUI's live-update path (`on_key_pressed` → `update_spectrogram` /
`update_sine_plot`) is best exercised by launching the app on a display; the
underlying visual math is covered by headless unit tests.

## Key Constraints (Keep These)

1. **Software-only simulation.** No microphone / audio capture. Never describe
   the project as capturing real acoustic signals.
2. **Predefined frequencies.** All frequencies are constants in
   `KEY_FREQUENCIES`.
3. Keep functions simple, docstringed, and covered by unit tests.

## Remaining / Optional Work

- Visual check: launch the GUI to confirm the Waveform tab renders both figures
  (could not be visually confirmed in a headless session).
- The LaTeX report's performance-results table uses representative values;
  regenerate/confirm if the user wants exact measured numbers.

## Command Cheatsheet

| Task | Command |
|---|---|
| Run app | `python3 src/acoustic_side_channel.py` |
| Run tests | `python3 -m pytest tests/ -v` |
| Build report | `cd docs && pdflatex report.tex` |
| Regenerate PNGs | see `docs/DEVELOPMENT_GUIDE.md` |

## Notes for AI Agents

- Always read the relevant portion of the codebase before editing.
- Run the test suite after any change to core logic.
- Match existing style: UPPER_CASE constants, docstringed functions, no
  unnecessary comments.
- Update `docs/PROJECT_STATE.md` and the `.memory/` files when the project
  changes materially.
