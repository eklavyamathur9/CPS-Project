# Report Restructure Plan (PR #7 → Closes #6)

Target: restructure `docs/report.tex` to the assignment outline and expand
from 11 pages to ~30-35 pages, emphasizing **performance** and **security**
analysis.

## Decisions (locked)
- **No Lyapunov function** — it is not used in the project.
- Keep existing team/authors/institution/preamble as-is.
- Keep the software-only simulation framing (no real acoustic capture).
- Deterministic, representative result data (no random/GUI-dependent numbers)
  so the report is reproducible.

## Proposed Section Map (outline → LaTeX)

1. **Title / Cover** — project title, subtitle, team, instructor, institution.
2. **Understanding the Project**
   - 2.1 Targeted system aspect — design, **performance**, **security**,
     **reliability**, scalability (which are active vs. passive here).
   - 2.2 Key technical terms — one-line glossary (frequency signature,
     side-channel, WCET, deadline, tolerance, confidence, invariant,
     liveness, termination, spectrogram, FFT).
   - 2.3 Problem statement — 1-2 lines: what it does, problem solved,
     hardware used (CPU-only desktop/laptop, no controller).
3. **Technical Context of the Project**
   - 3.1 Underlying principle — why it works (unique 30 Hz-spaced signatures,
     nearest-match within 8 Hz tolerance, noise bound ±5 Hz).
   - 3.2 Why it matters for CPS/embedded — real-time deadline (50 ms),
     storage (48-entry table), performance, reliability constraints.
   - 3.3 Implementation — **TikZ labelled block diagram**; hardware specifics
     (Python 3 host, tkinter GUI, no MCU; numpy/matplotlib); software design
     (module map, pseudocode in `listings`, key functions, data structures).
   - 3.4 Testing & Results — methodology (pytest unit tests, invariants,
     multi-trial WCET median/P95, noise robustness, GUI smoke); tooling
     (Python 3, numpy, matplotlib, tkinter, pytest; no crypto); results via
     tables + figures (`make_figures.py`: WCET-vs-deadline, error
     distribution, confidence).
   - 3.5 Analysis & Evaluation — interpret results (timing ≪ 50 ms, error
     within tolerance, confidence); problems faced; bugs fixed; limitations
     (single-tone model, no shift/alt, no real audio); optimization steps
     (numpy, const table, incremental updaters, plot cap).
   - 3.6 Conclusion & Discussion — direct answer + detailed problem→solution
     flow + scope.
   - 3.7 Bibliography — Harrison et al. 2023, kbd-audio, acoustic-SCA survey.

## Files
- `docs/report.tex` — restructured + expanded.
- `docs/make_figures.py` (new) — deterministic figure generator.
- Regenerated `docs/*.png`, rebuilt `docs/report.pdf`.
- `.memory/`, `docs/PROJECT_STATE.md` notes.

## Verification
- `cd docs && pdflatex -interaction=nonstopmode report.tex` (twice) — no
  errors, ~30-35 pages.
- `python3 -m pytest tests/ -q` → 62 passing (code unchanged).
