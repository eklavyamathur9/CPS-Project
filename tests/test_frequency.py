"""
Unit tests for the Acoustic Side-Channel Simulator.

Covers the CPS verification requirements: invariants, ranking function,
liveness, termination, WCET deadline, and sequence reconstruction.
"""

import sys
import os
import random

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src")
)

from acoustic_side_channel import (
    KEY_FREQUENCIES,
    TOLERANCE,
    DEADLINE_MS,
    WCET_TRIALS,
    check_invariants,
    identify_key,
    process_frequency,
    generate_frequency,
    reconstruct_sequence,
    reconstruct_sequence_wcet,
    compute_confidence,
    sequence_details,
    liveness_test,
    termination_test,
    keys_from_text,
    key_from_char,
    format_report,
    export_report,
    AcousticSideChannelApp,
)

import matplotlib
matplotlib.use("Agg")  # headless backend for plotting tests

from waveform_visualization import (
    compute_spectrogram,
    generate_sine,
    update_spectrogram,
    update_sine_plot,
    save_visualizations,
)

import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import filedialog


# ----------------------------------------------------------
# INVARIANTS
# ----------------------------------------------------------

def test_all_frequencies_positive():
    """Invariant 1: every frequency is positive."""
    frequencies = list(KEY_FREQUENCIES.values())
    assert all(f > 0 for f in frequencies)


def test_unique_frequencies():
    """Invariant 2: every key has a unique frequency."""
    frequencies = list(KEY_FREQUENCIES.values())
    assert len(frequencies) == len(set(frequencies))


def test_database_not_empty():
    """Invariant 3: the frequency database is non-empty."""
    assert len(KEY_FREQUENCIES) > 0


def test_check_invariants_all_pass():
    """check_invariants() returns True for all three invariants."""
    invariants = check_invariants()
    assert all(invariants.values())


def test_invariant_set_contains_expected_keys():
    """check_invariants() reports the correct invariant set."""
    invariants = check_invariants()
    assert set(invariants.keys()) == {
        "Positive frequencies",
        "Unique frequencies",
        "Frequency database valid",
    }


# ----------------------------------------------------------
# IDENTIFICATION / RANKING FUNCTION
# ----------------------------------------------------------

def test_known_key_identified_correctly():
    """A known frequency is mapped back to its key."""
    for key, frequency in KEY_FREQUENCIES.items():
        detected, error = identify_key(frequency)
        assert detected == key


def test_unknown_key_returns_unknown():
    """A frequency far from any signature returns UNKNOWN."""
    # Base frequency offset by more than the tolerance.
    detected, error = identify_key(KEY_FREQUENCIES["A"] + 100000.0)
    assert detected == "UNKNOWN"


def test_frequency_just_below_tolerance_matches():
    """A frequency within tolerance still matches its key."""
    base = KEY_FREQUENCIES["A"]
    detected, error = identify_key(base + TOLERANCE)
    assert detected == "A"
    assert error <= TOLERANCE


def test_frequency_just_above_tolerance_is_unknown():
    """A frequency just outside tolerance returns UNKNOWN."""
    base = KEY_FREQUENCIES["A"]
    detected, error = identify_key(base + 10 + TOLERANCE)
    assert detected == "UNKNOWN"


def test_ranking_error_is_nonnegative():
    """The ranking function V is always non-negative."""
    for key, frequency in KEY_FREQUENCIES.items():
        _, error = identify_key(frequency)
        assert error >= 0


def test_noise_stays_within_tolerance():
    """Synthetic noise keeps detection within tolerance."""
    # Use an explicit fixed seed path (via random.uniform, which
    # reads the global seed). We simply verify that with small noise
    # the key is still detected; to make it deterministic, run many
    # trials within the +/-5 range.
    found = all(
        identify_key(generate_frequency("A", noise=True))[0] == "A"
        for _ in range(200)
    )
    assert found


# ----------------------------------------------------------
# PROCESSING PIPELINE
# ----------------------------------------------------------

def test_process_frequency_returns_key():
    """process_frequency() returns a valid key for a valid frequency."""
    key, error, time_ms = process_frequency(KEY_FREQUENCIES["B"])
    assert key == "B"
    assert error >= 0
    assert time_ms >= 0


# ----------------------------------------------------------
# SEQUENCE RECONSTRUCTION
# ----------------------------------------------------------

def test_sequence_reconstruction_hello():
    """'HELLO' reconstructs to H, E, L, L, O."""
    reconstructed, _, _, _ = reconstruct_sequence("HELLO", add_noise=False)
    assert reconstructed == ["H", "E", "L", "L", "O"]


def test_sequence_reconstruction_invlalid_chars_skipped():
    """Non-alphanumeric/invalid chars are skipped in reconstruction."""
    reconstructed, _, _, _ = reconstruct_sequence("A1B!C ", add_noise=False)
    assert reconstructed == ["A", "1", "B", "C", "SPACE"]


def test_sequence_reconstruction_with_noise():
    """Sequence reconstructs correctly despite synthetic noise."""
    reconstructed, _, _, _ = reconstruct_sequence("TEST", add_noise=True)
    assert reconstructed == ["T", "E", "S", "T"]


def test_keys_from_text_handles_spaces():
    """keys_from_text() converts spaces to SPACE keys."""
    assert keys_from_text("A B") == ["A", "SPACE", "B"]


# ----------------------------------------------------------
# WCET / REAL-TIME
# ----------------------------------------------------------

def test_wcet_below_deadline():
    """The WCET must be below the deadline."""
    _, _, wcet, _ = reconstruct_sequence("HELLOWORLD", add_noise=True)
    assert wcet < DEADLINE_MS


def test_average_time_reporting():
    """Average and worst-case times are reported."""
    _, avg_time, wcet, _ = reconstruct_sequence("ABC", add_noise=False)
    assert avg_time >= 0
    assert wcet >= avg_time


# ----------------------------------------------------------
# LIVENESS & TERMINATION
# ----------------------------------------------------------

def test_liveness():
    """The system can process a new input (liveness)."""
    assert liveness_test() is True


def test_termination():
    """A finite input sequence terminates (termination)."""
    assert termination_test() is True


# ----------------------------------------------------------
# KEY CHAR MAPPING (keypad)
# ----------------------------------------------------------

def test_key_from_char_letter():
    """A letter maps to its uppercase key."""
    assert key_from_char("a") == "A"
    assert key_from_char("Z") == "Z"


def test_key_from_char_space():
    """A space maps to SPACE."""
    assert key_from_char(" ") == "SPACE"


def test_key_from_char_invalid():
    """A non-key character maps to None."""
    assert key_from_char("!") is None
    assert key_from_char("") is None


def test_key_from_char_digit():
    """A digit maps to its digit key."""
    assert key_from_char("1") == "1"
    assert key_from_char("0") == "0"


def test_all_digits_in_database():
    """All digit keys 0-9 are present in the frequency database."""
    for digit in "0123456789":
        assert digit in KEY_FREQUENCIES


def test_digit_reconstruction():
    """A sequence with digits reconstructs correctly."""
    reconstructed, _, _, _ = reconstruct_sequence("CPS101", add_noise=False)
    assert reconstructed == ["C", "P", "S", "1", "0", "1"]


def test_digit_frequencies_unique_and_positive():
    """Digit frequencies remain positive and unique."""
    digits = [KEY_FREQUENCIES[d] for d in "0123456789"]
    assert all(f > 0 for f in digits)
    assert len(digits) == len(set(digits))


# ----------------------------------------------------------
# STATISTICAL CONFIDENCE
# ----------------------------------------------------------

def test_confidence_perfect_match():
    """A zero-error match gives maximum (1.0) confidence."""
    score = compute_confidence("A", 0.0)
    assert score == 1.0


def test_confidence_at_tolerance_zero():
    """An error at the tolerance limit gives 0.0 confidence."""
    score = compute_confidence("A", TOLERANCE)
    assert score <= 1e-9


def test_confidence_unknown_zero():
    """An UNKNOWN key gives 0.0 confidence."""
    assert compute_confidence("UNKNOWN", 5.0) == 0.0


def test_confidence_clamped():
    """Confidence stays within [0, 1]."""
    for score in [
        compute_confidence("A", 0.0),
        compute_confidence("A", 4.0),
        compute_confidence("A", TOLERANCE),
        compute_confidence("UNKNOWN", 999),
    ]:
        assert 0.0 <= score <= 1.0


# ----------------------------------------------------------
# MULTI-TRIAL WCET
# ----------------------------------------------------------

def test_wcet_median_p95_present():
    """reconstruct_sequence_wcet reports median and P95 timings."""
    _, avg_time, median, p95, _ = reconstruct_sequence_wcet(
        "HELLOWORLD", add_noise=True, trials=5
    )
    assert avg_time >= 0
    assert median >= 0
    assert p95 >= 0


def test_wcet_p95_below_deadline():
    """P95 WCET stays below the deadline."""
    _, _, _, p95, _ = reconstruct_sequence_wcet(
        "HELLOWORLD", add_noise=True, trials=WCET_TRIALS
    )
    assert p95 < DEADLINE_MS


def test_wcet_p95_nearest_rank():
    """P95 uses nearest-rank for trial counts not multiples of 20."""

    # Return an increasing, deterministic worst-case time per trial so the
    # sorted list is exactly 0, 1, 2, ..., (trials - 1).
    def fake_reconstruct(text, add_noise=False):
        fake_reconstruct.calls += 1
        return (["A"], 0.0, float(fake_reconstruct.calls - 1), 0.0)

    fake_reconstruct.calls = 0

    import acoustic_side_channel as asc

    original = asc.reconstruct_sequence
    asc.reconstruct_sequence = fake_reconstruct

    try:
        for trials, expected_index in [(10, 9), (5, 4), (20, 18)]:
            fake_reconstruct.calls = 0
            _, _, _, p95, _ = asc.reconstruct_sequence_wcet(
                "A", add_noise=False, trials=trials
            )
            # Sorted values are 0..trials-1, so P95 should slot exactly at
            # the nearest-rank index ceil(n*0.95)-1.
            assert p95 == float(expected_index)
    finally:
        asc.reconstruct_sequence = original


# ----------------------------------------------------------
# EXPORT / REPORT FILE I/O
# ----------------------------------------------------------

def test_export_report_writes_file(tmp_path):
    """export_report writes a text file containing the report."""
    out = tmp_path / "report.txt"
    files = export_report("HELLO", str(out), add_noise=False, export_plots=False)
    assert os.path.exists(files[0])
    with open(files[0], encoding="utf-8") as fh:
        content = fh.read()
    assert "END OF REPORT" in content


def test_export_report_with_plots(tmp_path):
    """export_report with plots=True writes PNG files."""
    files = export_report(
        "HELLO", str(tmp_path / "report.txt"),
        add_noise=False, export_plots=True
    )
    assert any(f.endswith(".png") for f in files)


def test_save_visualizations_uses_unique_names(tmp_path):
    """Existing PNG files are not overwritten; a unique name is used."""
    # Pre-create the default targets like the committed docs figures.
    (tmp_path / "waveform_sine.png").write_bytes(b"original")
    (tmp_path / "waveform_spectrogram.png").write_bytes(b"original")

    files = save_visualizations(["A", "B"], directory=str(tmp_path))

    assert os.path.exists(files[0])
    assert os.path.exists(files[1])
    # The default names were NOT overwritten.
    assert (tmp_path / "waveform_sine.png").read_bytes() == b"original"
    assert (tmp_path / "waveform_spectrogram.png").read_bytes() == b"original"
    # And new (unique) files were actually created.
    assert files[0].endswith(".png")
    assert files[1].endswith(".png")


# ----------------------------------------------------------
# SEQUENCE DETAILS / REPORT
# ----------------------------------------------------------

def test_sequence_details_shape():
    """sequence_details returns one dict per valid key with confidence."""
    details = sequence_details("CPS101", add_noise=False)
    assert len(details) == 6
    for d in details:
        assert d["key"] in KEY_FREQUENCIES
        assert 0.0 <= d["confidence"] <= 1.0
        assert d["error"] >= 0


def test_format_report_contains_sections():
    """format_report includes the expected report sections."""
    report = format_report("HELLO WORLD", add_noise=False)
    assert "INVARIANT CHECK" in report
    assert "RECONSTRUCTED SEQUENCE" in report
    assert "REAL-TIME ANALYSIS" in report
    assert "RANKING FUNCTION" in report
    assert "LIVENESS" in report
    assert "TERMINATION" in report
    assert "END OF REPORT" in report


# ----------------------------------------------------------
# WAVEFORM INCREMENTAL HELPERS
# ----------------------------------------------------------

def test_generate_sine_shape():
    """generate_sine returns time and signal arrays of matching length."""
    duration = 0.01
    sample_rate = 1000
    t, signal = generate_sine(
        "A",
        duration=duration,
        sample_rate=sample_rate,
        noise=False
    )
    assert t.shape == signal.shape
    assert signal.shape[0] == int(sample_rate * duration)


def test_compute_spectrogram_grid_shapes():
    """compute_spectrogram returns consistent grid dimensions."""
    time_ms, freq_grid, mag_grid = compute_spectrogram(["A", "B"], noise=False)
    # One frame per time step.
    assert time_ms.shape[0] == freq_grid.shape[0] == mag_grid.shape[0]
    # Magnitude grid matches frequency grid in the frequency axis.
    assert mag_grid.shape == freq_grid.shape


def test_compute_spectrogram_single_and_multi_key():
    """Spectrogram grows with the number of added keys."""
    time_1, _, _ = compute_spectrogram(["A"], noise=False)
    time_2, _, _ = compute_spectrogram(["A", "B"], noise=False)
    assert time_2.shape[0] >= time_1.shape[0]


def test_update_spectrogram_no_error():
    """Incrementally updating a spectrogram figure does not raise."""
    fig, ax = plt.subplots()
    assert update_spectrogram(fig, ax, ["A"], noise=False) is True
    assert update_spectrogram(fig, ax, ["A", "B", "C"], noise=False) is True
    plt.close(fig)


def test_update_sine_plot_no_error():
    """Incrementally updating a sine plot does not raise."""
    fig, ax = plt.subplots()
    axes = [ax]
    assert update_sine_plot(fig, axes, ["A"], noise=False) is True
    assert update_sine_plot(fig, axes, ["A", "B"], noise=False) is True
    plt.close(fig)


# ----------------------------------------------------------
# GUI METHODS (tested via lightweight stubs, no Tk root needed)
# ----------------------------------------------------------

class _StubText:
    """Minimal text-widget stub exposing get/delete/insert used by analyze()."""

    def __init__(self):
        self._content = ""

    def get(self, start, end):
        return self._content

    def delete(self, start, end):
        self._content = ""

    def insert(self, index, text):
        self._content += text


class _StubRoot:
    """Minimal root stub exposing the clipboard methods used by copy_result."""

    def __init__(self):
        self._clipboard = ""

    def clipboard_clear(self):
        self._clipboard = ""

    def clipboard_append(self, text):
        self._clipboard += text

    def clipboard_get(self):
        return self._clipboard

    def update_idletasks(self):
        return None


def _make_stub_app(text, plot_var=False):
    """Build an object exposing the attributes the GUI methods use."""
    app = type("StubApp", (), {})()
    app.output = _StubText()
    app.root = _StubRoot()
    app.status_var = type("Var", (), {"set": lambda self, v: None})()
    app.noise_var = type("Var", (), {"get": lambda self: False})()
    app.export_plots_var = type("Var", (), {"get": lambda self: plot_var})()
    app.input_entry = type(
        "Entry", (),
        {"get": lambda self: text, "delete": lambda *a: None,
         "insert": lambda *a: None},
    )()
    return app


def test_analyze_produces_report_content():
    """analyze() delegates to format_report() and fills the output widget."""
    app = _make_stub_app("CPS101")
    AcousticSideChannelApp.analyze(app)
    content = app.output.get("1.0", tk.END)
    assert "INVARIANT CHECK" in content
    assert "END OF REPORT" in content
    assert "C P S 1 0 1" in content


def test_copy_result_writes_clipboard():
    """copy_result() copies the analysis output to the clipboard."""
    app = _make_stub_app("AB1")
    AcousticSideChannelApp.analyze(app)
    AcousticSideChannelApp.copy_result(app)
    assert "INVARIANT CHECK" in app.root.clipboard_get()


def test_export_report_gui(monkeypatch, tmp_path):
    """GUI export_report() writes a report to the chosen path."""
    target = str(tmp_path / "report.txt")
    monkeypatch.setattr(
        filedialog,
        "asksaveasfilename",
        lambda **kwargs: target
    )
    app = _make_stub_app("HELLO")
    AcousticSideChannelApp.export_report(app)
    assert os.path.exists(target)
    with open(target, encoding="utf-8") as fh:
        assert "END OF REPORT" in fh.read()

