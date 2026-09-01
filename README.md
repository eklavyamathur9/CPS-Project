# Acoustic Side-Channel Attack on Mechanical Keyboards

**A Software-Based Keystroke Reconstruction Using Frequency Signatures**

This project is a **software-based simulation** of an acoustic side-channel
attack on a mechanical keyboard. Each key is assigned a unique frequency
signature; the system analyzes these frequencies and reconstructs the typed
keystroke sequence. It demonstrates the acoustic side-channel concept and the
associated Cyber-Physical Systems (CPS) verification requirements entirely in
software, **without a microphone or audio capture hardware**.

---

## Features

- **Custom frequency database**: 27 keys (A–Z + SPACE), each with a unique frequency.
- **Software frequency generation**: synthetic signal with optional measurement noise.
- **Frequency analysis & matching**: nearest-frequency classification with a tolerance.
- **Keystroke reconstruction**: rebuilds the typed sequence from detected frequencies.
- **CPS verification**:
  - WCET / average execution time measurement
  - Deadline checking (50 ms)
  - Invariant checking (positive, unique, valid frequencies)
  - Liveness and termination tests
  - Ranking function V = |F_detected − F_expected|
  - Safety via the `UNKNOWN` state
- **Waveform visualization**:
  - Sine waveform per key
  - Simulated frequency spectrogram
  - **Live incremental updates**: an on-screen keypad (A–Z + SPACE + Clear)
    appends each key press and grows the plots in real time
- **On-screen keypad**: click keys to build a sequence live; each press updates
  both plots incrementally

---

## Requirements

- Python 3
- tkinter (usually included with Python)
- numpy
- matplotlib
- pytest (for tests)

```bash
pip install -r requirements.txt
```

---

## Running the Application

```bash
python3 src/acoustic_side_channel.py
```

A GUI opens where you can enter a key sequence (e.g. `HELLO WORLD`), toggle
synthetic noise, and either **Analyze** or **Visualize Waveform**. You can also
use the on-screen **keypad**: every key click appends to the sequence and
**incrementally updates the waveform plots live**.

The analysis tab reports:
- Invariant check results
- Per-key frequency mapping
- Reconstructed sequence
- Real-time analysis (avg time, WCET, deadline pass/fail)
- Ranking function V
- Liveness and termination results

The waveform tab displays:
- A sine waveform for each key
- A simulated frequency spectrogram

Both plots grow live as you click keypad keys (use **Clear** to reset).

---

## Running the Tests

```bash
python3 -m pytest tests/ -v
```

28 unit tests cover the CPS invariants, identification, reconstruction,
deadline, liveness, termination, key mapping, and the incremental waveform
helpers.

---

## Building the Report

```bash
cd docs
pdflatex report.tex
```

Produces `docs/report.pdf`.

---

## Project Structure

```
CPSProject/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── src/
│   ├── acoustic_side_channel.py      # Main app + core logic + keypad GUI
│   └── waveform_visualization.py     # matplotlib sine + spectrogram + live updaters
├── tests/
│   └── test_frequency.py             # 28 unit tests
├── docs/
│   ├── report.tex                    # LaTeX report
│   ├── report.pdf                    # Compiled report
│   ├── ARCHITECTURE.md
│   ├── PROJECT_STATE.md
│   ├── DECISIONS.md
│   ├── DEVELOPMENT_GUIDE.md
│   └── KNOWN_ISSUES.md
└── .memory/
    ├── CURRENT_SESSION.md
    ├── PROJECT_CONTEXT.md
    └── HANDOFF.md
```

---

## Key Frequencies

| Key | Hz | Key | Hz |
|---|---|---|---|
| A | 440 | N | 830 |
| B | 470 | O | 860 |
| C | 500 | P | 890 |
| D | 530 | Q | 920 |
| E | 560 | R | 950 |
| F | 590 | S | 980 |
| G | 620 | T | 1010 |
| H | 650 | U | 1040 |
| I | 680 | V | 1070 |
| J | 710 | W | 1100 |
| K | 740 | X | 1130 |
| L | 770 | Y | 1160 |
| M | 800 | Z | 1190 |
| SPACE | 1220 | | |

---

## License

Educational project for a Cyber-Physical Systems course.
