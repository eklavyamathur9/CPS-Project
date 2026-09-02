"""
Waveform visualization module for the Acoustic Side-Channel Simulator.

Provides two visualization modes:
1. Sine waveform: plots the sine wave sin(2*pi*f*t) for each key's frequency.
2. Spectrogram: plots a frequency-vs-time heatmap showing key frequencies
   as bands over time (simulated).

Uses matplotlib + numpy. All functions return matplotlib Figure objects so
they can be embedded into tkinter via FigureCanvasTkAgg, or saved to disk.
"""

import numpy as np
import matplotlib

import matplotlib.pyplot as plt
import os
import time

from acoustic_side_channel import KEY_FREQUENCIES

SAMPLE_RATE = 44100  # Hz (simulated acoustic sampling rate)
DURATION = 0.05      # seconds per key (50 ms)


def generate_sine(key, duration=DURATION, sample_rate=SAMPLE_RATE, noise=False):
    """
    Generate a numpy array representing a sine wave for a key.

    frequency = KEY_FREQUENCIES[key]
    signal    = sin(2 * pi * frequency * t)

    If noise=True, add small random noise to simulate measurement error.
    """
    if key not in KEY_FREQUENCIES:
        raise ValueError(f"Unknown key: {key}")

    frequency = KEY_FREQUENCIES[key]

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    signal = np.sin(2 * np.pi * frequency * t)

    if noise:
        signal += np.random.uniform(-0.2, 0.2, t.shape)

    return t, signal


def plot_sine_waves(keys, title="Key Frequency Waveforms", noise=False):
    """
    Plot stacked sine waves for a sequence of keys.

    Returns a matplotlib Figure.
    """
    fig, axes = plt.subplots(
        len(keys), 1,
        figsize=(9, 1.4 * max(len(keys), 1)),
        sharex=True
    )

    if len(keys) == 1:
        axes = [axes]

    for ax, key in zip(axes, keys):
        t, signal = generate_sine(key, noise=noise)

        frequency = KEY_FREQUENCIES[key]

        ax.plot(t * 1000, signal, linewidth=0.8)
        ax.set_ylabel(f"{key}\n{frequency:.0f} Hz", fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, DURATION * 1000)

    axes[-1].set_xlabel("Time (ms)")

    fig.suptitle(title, fontsize=13, fontweight="bold")

    fig.tight_layout()

    return fig


def compute_spectrogram(keys, noise=False):
    """
    Compute the frequency/time/magnitude grids for a simulated spectrogram
    of a sequence of keys.

    This shared helper is used both by the static plotter and the incremental
    updater so the rendering math stays identical and unit-testable.

    Returns (time_ms, freq_grid, mag_grid) where:
        time_ms    : 1D array of frame start times (ms)
        freq_grid  : 2D array of frequencies per frame (Hz)
        mag_grid   : 2D array of log-scale magnitudes per frame
    """
    if not keys:
        keys = ["A"]

    # Build a composite time series: concatenate one sine burst per key.
    composite = np.array([])

    for key in keys:
        _, signal = generate_sine(key, noise=noise)
        envelope = np.hanning(signal.shape[0])
        composite = np.concatenate([composite, signal * envelope])

    # Pad to a minimum length to keep the plot legible.
    min_samples = int(SAMPLE_RATE * DURATION * 2)
    if composite.shape[0] < min_samples:
        composite = np.pad(composite, (0, min_samples - composite.shape[0]))

    # Manual spectrogram: slide a Hann window, take FFT magnitudes per frame.
    window = int(SAMPLE_RATE * DURATION * 0.5)  # half the per-key duration
    hop = int(window // 2)

    frequencies = []
    times = []
    magnitudes = []

    for start in range(0, composite.shape[0] - window, hop):
        frame = composite[start:start + window] * np.hanning(window)
        spectrum = np.abs(np.fft.rfft(frame))
        freqs = np.fft.rfftfreq(window, 1.0 / SAMPLE_RATE)

        # Only keep the band of interest (350-1600 Hz) for clarity.
        mask = (freqs >= 350) & (freqs <= 1600)
        frequencies.append(freqs[mask])
        times.append(start / SAMPLE_RATE)
        magnitudes.append(spectrum[mask])

    freq_grid = np.array(frequencies)
    time_grid = np.array(times)
    mag_grid = np.array(magnitudes)

    # Log-scale the magnitude for contrast.
    mag_display = 10.0 * np.log10(mag_grid + 1e-12)

    return time_grid * 1000, freq_grid, mag_display


def plot_spectrogram(keys, title="Frequency Spectrogram", noise=False):
    """
    Plot a simulated spectrogram: frequency (Hz) on the y-axis, time on the
    x-axis, with each key shown as a horizontal band at its assigned frequency.

    Returns a matplotlib Figure.
    """
    if not keys:
        keys = ["A"]

    time_ms, freq_grid, mag_display = compute_spectrogram(keys, noise=noise)

    fig, ax = plt.subplots(figsize=(9, 4.5))

    ax.pcolormesh(
        time_ms,
        freq_grid.T,
        mag_display.T,
        shading="auto",
        cmap="inferno"
    )

    # Overlay the expected frequency lines for each key.
    for i, key in enumerate(keys):
        freq = KEY_FREQUENCIES[key]
        ax.axhline(
            freq,
            color="cyan",
            linewidth=1.0,
            linestyle="--",
            alpha=0.5
        )
        ax.text(
            (i * DURATION + DURATION / 2) * 1000,
            freq + 25,
            f"{key}",
            color="cyan",
            fontsize=9,
            ha="center"
        )

    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_ylim(350, 1600)
    ax.grid(True, alpha=0.2)

    fig.suptitle(title, fontsize=13, fontweight="bold")

    fig.tight_layout()

    return fig


def _update_spectrogram_artists(ax, time_ms, freq_grid, mag_display):
    """
    (Re)draw the pcolormesh on an existing axes from precomputed grids.

    Used by update_spectrogram to incrementally refresh the heatmap.
    """
    # Remove the previous image/collection artists so the axes re-render.
    for collection in list(ax.collections):
        collection.remove()

    ax.pcolormesh(
        time_ms,
        freq_grid.T,
        mag_display.T,
        shading="auto",
        cmap="inferno"
    )


def update_spectrogram(fig, ax, keys, noise=False):
    """
    Incrementally refresh the spectrogram on an existing figure/axes to show
    the current accumulated key sequence.

    Returns True on success. The caller is responsible for redrawing the
    canvas via FigureCanvasTkAgg.draw().
    """
    time_ms, freq_grid, mag_display = compute_spectrogram(keys, noise=noise)

    _update_spectrogram_artists(ax, time_ms, freq_grid, mag_display)

    # Refresh key labels. Remove any text artists we previously added and
    # re-add them for the current key list.
    for artist in list(ax.texts):
        artist.remove()

    for i, key in enumerate(keys):
        freq = KEY_FREQUENCIES[key]
        ax.text(
            (i * DURATION + DURATION / 2) * 1000,
            freq + 25,
            f"{key}",
            color="cyan",
            fontsize=9,
            ha="center"
        )

    ax.set_xlim(0, max(len(keys), 2) * DURATION * 1000)
    ax.relim()
    ax.autoscale_view(scalex=False, scaley=False)

    fig.canvas.draw_idle()

    return True


def update_sine_plot(fig, axes, keys, noise=False):
    """
    Incrementally refresh the stacked sine-wave plot on an existing figure/axes
    to show the current accumulated key sequence.

    Returns True on success. The caller redraws the canvas via
    FigureCanvasTkAgg.draw().
    """
    if not keys:
        keys = ["A"]

    # Clear each existing axes and redraw one sine per key.
    for axis in axes:
        axis.clear()

    for ax, key in zip(axes, keys):
        t, signal = generate_sine(key, noise=noise)
        frequency = KEY_FREQUENCIES[key]
        ax.plot(t * 1000, signal, linewidth=0.8)
        ax.set_ylabel(f"{key}\n{frequency:.0f} Hz", fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, DURATION * 1000)

    axes[-1].set_xlabel("Time (ms)")

    fig.canvas.draw_idle()

    return True


def _unique_path(directory, name):
    """
    Return a file path under `directory` that does not already exist.

    If `name` is already taken, a timestamped variant is used (e.g.
    "waveform_sine_20260901_103000.png") so committed/other figures are
    never silently overwritten.
    """
    path = os.path.join(directory, name)

    if not os.path.exists(path):
        return path

    base, ext = os.path.splitext(name)
    stamp = time.strftime("%Y%m%d_%H%M%S")

    candidate = os.path.join(directory, f"{base}_{stamp}{ext}")

    # Collision on the timestamped name (unlikely, but keep trying).
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(
            directory,
            f"{base}_{stamp}_{counter}{ext}"
        )
        counter += 1

    return candidate


def save_visualizations(keys, directory=".", noise=False):
    """
    Save both sine-wave and spectrogram figures as PNG files.

    Uses non-colliding filenames so existing PNGs are never overwritten.

    Returns the list of file paths created (sine, then spectrogram).
    """
    sine_fig = plot_sine_waves(keys, noise=noise)
    spec_fig = plot_spectrogram(keys, noise=noise)

    sine_path = _unique_path(directory, "waveform_sine.png")
    spec_path = _unique_path(directory, "waveform_spectrogram.png")

    sine_fig.savefig(sine_path, dpi=150)
    spec_fig.savefig(spec_path, dpi=150)

    plt.close(sine_fig)
    plt.close(spec_fig)

    return [sine_path, spec_path]
