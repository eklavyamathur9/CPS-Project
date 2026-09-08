# Project State

Current status of the Acoustic Side-Channel Simulator project as of the last
session.

## Status Legend

- **DONE** — implemented and verified
- **IN PROGRESS** — actively being worked on
- **PENDING** — planned but not started

---

## Code

| Component | File | Status |
|---|---|---|
| Core logic (key/frequency DB, matching, invariants, liveness, termination) | `src/acoustic_side_channel.py` | DONE |
| GUI (tabs: Analysis + Waveform, noise toggle, analyze + visualize buttons) | `src/acoustic_side_channel.py` | DONE |
| Multi-line paragraph input (tk.Text + scrollbar; newlines skipped) | `src/acoustic_side_channel.py` | DONE |
| On-screen keypad with live incremental waveform updates | `src/acoustic_side_channel.py` | DONE |
| Punctuation keys (11 marks, 1550–1850 Hz, spectrogram band to 1900 Hz) | `src/acoustic_side_channel.py`, `src/waveform_visualization.py` | DONE |
| Waveform visualization (sine + spectrogram) with MAX_PLOT_KEYS cap | `src/waveform_visualization.py` | DONE |
| Incremental updaters (update_sine_plot, update_spectrogram) | `src/waveform_visualization.py` | DONE |

## Tests

| Test file | Count | Status |
|---|---|---|
| `tests/test_frequency.py` | 62 | DONE (all passing) |

## Documentation

| File | Status |
|---|---|
| `README.md` | DONE |
| `CLAUDE.md` | DONE |
| `docs/ARCHITECTURE.md` | DONE |
| `docs/PROJECT_STATE.md` | DONE |
| `docs/DECISIONS.md` | DONE |
| `docs/DEVELOPMENT_GUIDE.md` | DONE |
| `docs/KNOWN_ISSUES.md` | DONE |

## Report

| File | Status |
|---|---|
| `docs/report.tex` | DONE (restructured, 31 pages) |
| `docs/report.pdf` | DONE (31 pages, compiles clean) |
| `docs/REPORT_PLAN.md` | DONE (accepted expansion plan) |
| `docs/make_figures.py` | DONE (deterministic figure generator) |
| `docs/{timing_vs_deadline,error_distribution,confidence,optimization}.png` | DONE (result figures) |

## Memory

| File | Status |
|---|---|
| `.memory/CURRENT_SESSION.md` | DONE |
| `.memory/PROJECT_CONTEXT.md` | DONE |
| `.memory/HANDOFF.md` | DONE |

---

## Verification Results

### Tests

```bash
python3 -m pytest tests/ -v
# 62 passed
```

### Report Compilation

```bash
cd docs
pdflatex report.tex   # run twice
# report.pdf, 31 pages, no undefined references
```

The LaTeX report was restructured to the assignment outline
(`cps notes.txt`) and expanded to 31 pages. It now covers:
targeted aspects (performance + security focus), technical terms,
problem statement, underlying principle (incl. real-world background),
CPS relevance, system architecture (TikZ diagram), hardware/platform
details, software design (full 48-key frequency DB table, function
reference, WCET/liveness/termination pseudocode, storage footprint),
design decisions, optimization flow, testing methodology (traceability
table, 62 tests, per-key + pangram results, punctuated paragraph,
sample report output), results figures, theoretical + statistical +
complexity analysis, performance analysis, problems/bugs/limitations,
security + reliability analysis, conclusion, related-work comparison,
and bibliography.

### Visualization

The waveform PNGs are generated to `docs/waveform_sine.png` and
`docs/waveform_spectrogram.png` and embedded in the LaTeX report. The
result figures (`timing_vs_deadline.png`, `error_distribution.png`,
`confidence.png`, `optimization.png`) are generated reproducibly by
`docs/make_figures.py` using deterministic representative values:

```bash
python3 docs/make_figures.py
```

---

## Next Steps

1. Final end-to-end verification and merge of the punctuation-keys PR.
2. Merge PR #7 (report restructure, drives issue #6).