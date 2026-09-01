# Project Context

Background and motivation for the Acoustic Side-Channel Simulator.

## Assignment

**Course:** Cyber-Physical Systems (CPS)

**Topic:** Acoustic Side-Channel Attack on Mechanical Keyboards — Software-Based
Approach.

The assignment requires demonstrating a CPS with, at least: WCET/deadline,
invariants, liveness, termination, and a ranking/error function. The chosen
application is an acoustic side-channel keystroke-reconstruction model.

## Important Framing

This is a **software simulation/prototype** only. There is:
- No microphone.
- No audio recording hardware.
- No real-world acoustic capture.

Every frequency is a **predefined constant**. The project demonstrates the
side-channel *concept* and the CPS verification requirements without sensing
hardware. All documentation, reports, and the README must maintain this
accurate framing (do not claim real acoustic capture).

## Core Idea

Each key is assigned a unique frequency signature:

| Key | Frequency (Hz) |
|---|---|
| A | 440 |
| B | 470 |
| C | 500 |
| ... | ... |
| Z | 1190 |
| SPACE | 1220 |

Processing pipeline:

```
Key Press → Custom Frequency → Frequency Analysis →
Key Identification → Keystroke Reconstruction
```

## CPS Concepts Mapped

| Concept | Implementation |
|---|---|
| Application | Software acoustic side-channel simulator |
| Real-time task | Frequency → key processing |
| WCET | Max measured processing time |
| Deadline | 50 ms |
| Tolerance | 8 Hz |
| Invariant | Unique/valid frequency mapping |
| Liveness | System keeps accepting inputs |
| Termination | Finite sequence finishes |
| Ranking function | V = \|F_detected − F_expected\| |
| Safety | Invalid/ambiguous → "UNKNOWN" |
| Outcome | Reconstructed keystroke sequence |

## Key Parameter Choices

- **30 Hz spacing** between letter keys (clean, unambiguous).
- **Tolerance = 8 Hz** (well below half the 30 Hz spacing).
- **Noise ±5 Hz** (within tolerance, so robust matching is demonstrated).
- **Deadline = 50 ms** (conservatively above measured WCET).
- **UNKNOWN fallback** for out-of-tolerance frequencies (safety).

## Relevant Files

- Core app: `src/acoustic_side_channel.py`
- Visualization: `src/waveform_visualization.py`
- Tests: `tests/test_frequency.py`
- Report (LaTeX): `docs/report.tex`, compiled to `docs/report.pdf`
