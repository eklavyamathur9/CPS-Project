# Decisions

Key design decisions made during the development of the Acoustic Side-Channel
Simulator, along with their rationale.

---

## 1. Software-Only Simulation (No Microphone)

**Decision:** Model the side-channel attack entirely in software using
predefined frequency constants.

**Rationale:** The project is a prototype/simulation. It demonstrates the
acoustic side-channel reconstruction concept and CPS verification without
requiring audio capture hardware. This keeps the scope feasible and the claims
technically accurate.

---

## 2. Frequency Spacing (30 Hz increments from 440 Hz)

**Decision:** Frequencies increase by 30 Hz from `A` (440 Hz) to `Z` (1190 Hz),
with SPACE at 1220 Hz.

**Rationale:** Provides clean, equally spaced signatures that are easy to
illustrate in tables and plots, and are well separated relative to the 8 Hz
tolerance.

---

## 3. Tolerance = 8 Hz

**Decision:** `TOLERANCE = 8.0` Hz.

**Rationale:** With 30 Hz separation between adjacent keys, an 8 Hz tolerance
leaves comfortable margin: a wrongly shifted frequency would need to drift
>15 Hz to cross into the next key's band. At the same time it is large enough
that the small synthetic noise (±5 Hz) still produces valid matches.

---

## 4. Noise Model (±5 Hz uniform)

**Decision:** When noise is enabled, add `random.uniform(-5.0, 5.0)` to the
frequency.

**Rationale:** Simulates imperfect frequency detection without a microphone.
The ±5 Hz range stays within the 8 Hz tolerance, so robust classification is
demonstrated even under synthetic measurement error.

---

## 5. Nearest-Neighbor Matching with UNKNOWN Fallback

**Decision:** `identify_key` selects the key with the smallest absolute error
`V = |F_detected − F_expected|`, but returns `"UNKNOWN"` if the smallest error
exceeds the tolerance.

**Rationale:** This both implements the ranking function (minimize V) and the
safety property (never force an incorrect key when no good match exists).

---

## 6. Deadline = 50 ms

**Decision:** `DEADLINE_MS = 50.0`.

**Rationale:** A reasonable real-time constraint for a keystroke-processing
task. Actual measured execution times are far below this, so the WCET
requirement is comfortably satisfied and easy to verify.

---

## 7. Tkinter + Separate Notebook Tabs

**Decision:** The GUI uses a `ttk.Notebook` with an "Analysis" tab and a
"Waveform" tab.

**Rationale:** Separates textual analysis results from graphical waveforms,
keeping the interface clean and making the waveform demonstration a distinct,
optional step.

---

## 8. Matplotlib Figures Embedded via FigureCanvasTkAgg

**Decision:** The waveform module returns matplotlib `Figure` objects that the
GUI embeds using `FigureCanvasTkAgg`.

**Rationale:** Allows the same plotting code to be reused both in the GUI and
to save PNG files for the LaTeX report.

---

## 9. Manual Spectrogram (sliding FFT window)

**Decision:** The spectrogram is computed manually with a sliding Hann
window + `numpy.fft.rfft`, rather than `matplotlib.pyplot.specgram`.

**Rationale:** Gives finer control over the plotted frequency band (350–1300 Hz)
and lets us overlay the expected key-frequency lines for emphasis.

---

## 10. Type hints / Over-Engineering Avoidance

**Decision:** Keep functions self-contained and simple; no speculative
abstractions or configuration beyond what is needed.

**Rationale:** Follows the principle of minimal code that solves the problem,
making the project easy to understand and test.
