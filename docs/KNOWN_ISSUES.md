# Known Issues and Limitations

This document tracks known limitations and edge cases of the Acoustic
Side-Channel Simulator. These are inherent to the software-simulation approach.

---

## Known Limitations

### 1. Software Simulation, Not Real Acoustic Capture

The system uses predefined frequency constants and does not capture or analyze
real acoustic signals. It is a demonstration of the side-channel *concept* and
its CPS verification, not a functional attack on real keyboards.

### 2. No Real-World Noise Model

The synthetic noise is a simple uniform ±5 Hz offset on the frequency. It does
not model real ambient noise, microphone characteristics, or multi-path
effects. In a real deployment, classification accuracy would be lower.

### 3. Frequent-Key Ambiguity Margin

With 30 Hz spacing and an 8 Hz tolerance, error bands touch at a drift of
about 15 Hz. Frequencies drifting beyond that would be misclassified. This is
acceptable for the tolerance chosen but is a theoretical boundary.

### 4. SPACE Frequency Distance

SPACE (1220 Hz) is 30 Hz above Z (1190 Hz) — the same spacing as letters, so
it behaves consistently with the rest of the table.

### 5. Unknown Variants

If the user enters characters outside the supported keys (A–Z, 0–9, and
space) — e.g., punctuation or symbols — they are silently skipped by
`reconstruct_sequence` and `keys_from_text`. They are not treated as keys or
shown as UNKNOWN.

### 6. Timing Resolution

Execution times are measured with `time.perf_counter`. On fast machines many
calls measure near 0 ms; WCET values can be dominated by scheduler noise
rather than the algorithm itself.

### 7. GUI Needs a Display

The tkinter GUI requires a graphical display. Headless environments cannot
launch the app (though tests and the waveform module work headlessly).

---

## Edge Cases

| Input | Behavior |
|---|---|
| Empty string | No keys; zero average time/error; GUI shows no mapping lines |
| Lowercase letters | Converted to uppercase |
| Digits | Mapped to digit keys 0–9 (supported) |
| Punctuation / symbols | Skipped silently |
| Out-of-tolerance frequency | `identify_key` returns `"UNKNOWN"` |
| Very long sequence | Processes each key independently; linear O(n) in keys |

---

## Future Improvements (Out of Current Scope)

- Real acoustic FFT analysis (requires a microphone — conflicts with the
  software-only design constraint).
- Support for function keys, shift/ctrl modifiers, and punctuation.
- More sophisticated noise/error models (Gaussian, burst errors).

> Note: digit keys (0–9), per-key statistical confidence, and robust
> multi-trial WCET (median + P95) are now implemented and covered by tests.

---

## Reporting Bugs

Run the tests to confirm the baseline:

```bash
python3 -m pytest tests/ -v
```

If a failure or unexpected behavior occurs, note:
- Exact input used
- Whether noise was enabled
- Expected vs. actual output
