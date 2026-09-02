import tkinter as tk
from tkinter import ttk, filedialog
import time
import random
import os
import sys
import math


# Allow importing from the src directory when running as a script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# 1. CUSTOM KEY -> FREQUENCY DATABASE
# ============================================================

KEY_FREQUENCIES = {
    "A": 440.0,
    "B": 470.0,
    "C": 500.0,
    "D": 530.0,
    "E": 560.0,
    "F": 590.0,
    "G": 620.0,
    "H": 650.0,
    "I": 680.0,
    "J": 710.0,

    "K": 740.0,
    "L": 770.0,
    "M": 800.0,
    "N": 830.0,
    "O": 860.0,
    "P": 890.0,
    "Q": 920.0,
    "R": 950.0,
    "S": 980.0,

    "T": 1010.0,
    "U": 1040.0,
    "V": 1070.0,
    "W": 1100.0,
    "X": 1130.0,
    "Y": 1160.0,
    "Z": 1190.0,

    "SPACE": 1220.0,

    "0": 1250.0,
    "1": 1280.0,
    "2": 1310.0,
    "3": 1340.0,
    "4": 1370.0,

    "5": 1400.0,
    "6": 1430.0,
    "7": 1460.0,
    "8": 1490.0,
    "9": 1520.0
}


# ============================================================
# CONFIGURATION
# ============================================================

# Maximum frequency difference accepted as a valid match.
TOLERANCE = 8.0

# Deadline used for the CPS real-time demonstration.
DEADLINE_MS = 50.0

# Number of trials used for robust WCET (median / P95) reporting.
WCET_TRIALS = 20


# ============================================================
# 2. INVARIANT CHECKING
# ============================================================

def check_invariants():
    """
    Checks important safety/correctness invariants.
    """

    frequencies = list(KEY_FREQUENCIES.values())

    # Invariant 1:
    # Every frequency must be positive.
    positive_frequency = all(f > 0 for f in frequencies)

    # Invariant 2:
    # Every key must have a unique frequency.
    unique_frequency = len(frequencies) == len(set(frequencies))

    # Invariant 3:
    # Frequency database cannot be empty.
    database_valid = len(KEY_FREQUENCIES) > 0

    return {
        "Positive frequencies": positive_frequency,
        "Unique frequencies": unique_frequency,
        "Frequency database valid": database_valid
    }


# ============================================================
# 3. SYNTHETIC FREQUENCY GENERATION
# ============================================================

def generate_frequency(key, noise=False):
    """
    Generates the predefined frequency for a key.

    noise=True adds a small artificial measurement error.
    This simulates imperfect frequency detection without
    requiring a microphone.
    """

    if key not in KEY_FREQUENCIES:
        raise ValueError("Unknown key")

    frequency = KEY_FREQUENCIES[key]

    if noise:
        frequency += random.uniform(-5.0, 5.0)

    return frequency


# ============================================================
# 4. FREQUENCY ANALYSIS
# ============================================================

def identify_key(detected_frequency):
    """
    Finds the key whose predefined frequency is closest
    to the detected frequency.
    """

    best_key = None
    smallest_error = float("inf")

    for key, expected_frequency in KEY_FREQUENCIES.items():

        error = abs(detected_frequency - expected_frequency)

        if error < smallest_error:
            smallest_error = error
            best_key = key

    # Ranking function:
    #
    # V = |detected_frequency - expected_frequency|
    #
    # Smaller V means a better match.

    if smallest_error <= TOLERANCE:
        return best_key, smallest_error

    return "UNKNOWN", smallest_error


# ============================================================
# 5. PROCESS ONE KEY
# ============================================================

def process_frequency(frequency):
    """
    Complete processing pipeline:

    Frequency
        ↓
    Frequency analysis
        ↓
    Frequency matching
        ↓
    Key identification
    """

    start = time.perf_counter()

    key, error = identify_key(frequency)

    end = time.perf_counter()

    execution_time_ms = (end - start) * 1000

    return key, error, execution_time_ms


# ============================================================
# 5b. STATISTICAL CONFIDENCE
# ============================================================

def compute_confidence(detected_key, error):
    """
    Compute a confidence score (0.0 - 1.0) for a detected key.

    The score is based on how close the error is to the detection
    tolerance: an error of 0 gives maximum confidence, while an
    error at the tolerance limit gives the minimum. Unknown keys
    always report 0.0 confidence.

    Confidence = 1 - (error / TOLERANCE), clamped to [0, 1].
    """
    if detected_key == "UNKNOWN":
        return 0.0

    if TOLERANCE <= 0:
        return 1.0

    score = 1.0 - (error / TOLERANCE)

    return max(0.0, min(1.0, score))


def reconstruct_sequence_wcet(text, add_noise=False, trials=1):
    """
    Run the reconstruction across multiple trials and report robust
    timing statistics: median and P95 worst-case execution time.

    Returns (reconstructed, average_time, wcet_median, wcet_p95,
    average_error).
    """
    all_wcet = []

    result = reconstruct_sequence(text, add_noise=add_noise)

    all_wcet.append(result[2])

    for _ in range(trials - 1):
        r = reconstruct_sequence(text, add_noise=add_noise)
        all_wcet.append(r[2])

    all_wcet.sort()

    median = all_wcet[len(all_wcet) // 2]

    # Nearest-rank percentile: reports an exact 95th percentile for any
    # trial count (prevents under-reporting for counts not multiple of 20).
    n = len(all_wcet)
    p95_index = min(math.ceil(n * 0.95) - 1, n - 1)
    p95 = all_wcet[p95_index]

    return (
        result[0],
        result[1],
        median,
        p95,
        result[3]
    )


# ============================================================
# 6. PROCESS A COMPLETE SEQUENCE
# ============================================================

def reconstruct_sequence(text, add_noise=False):

    reconstructed = []

    total_time = 0.0
    worst_case = 0.0
    errors = []

    for character in text.upper():

        if character == " ":
            key = "SPACE"

        elif character in KEY_FREQUENCIES:
            key = character

        else:
            continue

        # Generate synthetic frequency
        frequency = generate_frequency(key, noise=add_noise)

        # Analyze frequency
        detected_key, error, execution_time = process_frequency(
            frequency
        )

        reconstructed.append(detected_key)

        total_time += execution_time

        worst_case = max(
            worst_case,
            execution_time
        )

        errors.append(error)

    count = len(reconstructed)

    if count > 0:
        average_time = total_time / count
        average_error = sum(errors) / count
    else:
        average_time = 0
        average_error = 0

    return (
        reconstructed,
        average_time,
        worst_case,
        average_error
    )


def sequence_details(text, add_noise=False):
    """
    Build a detailed per-key analysis for a text sequence.

    Returns a list of dicts, one per valid key, each containing:
        key, frequency, detected_key, error, time_ms, confidence
    """
    details = []

    for character in text.upper():
        key = key_from_char(character)

        if key is None:
            continue

        frequency = generate_frequency(key, noise=add_noise)
        detected_key, error, execution_time = process_frequency(frequency)
        confidence = compute_confidence(detected_key, error)

        details.append({
            "key": key,
            "frequency": frequency,
            "detected_key": detected_key,
            "error": error,
            "time_ms": execution_time,
            "confidence": confidence,
        })

    return details


# ============================================================
# 7. LIVENESS TEST
# ============================================================

def liveness_test():

    """
    Liveness property:

    The system must be able to process an incoming
    frequency and eventually produce an output.
    """

    test_frequency = KEY_FREQUENCIES["A"]

    key, error, execution_time = process_frequency(
        test_frequency
    )

    return key != "UNKNOWN"


# ============================================================
# 8. TERMINATION TEST
# ============================================================

def termination_test():

    """
    Demonstrates that a finite input sequence terminates.
    """

    start = time.perf_counter()

    reconstruct_sequence("TEST")

    end = time.perf_counter()

    return (end - start) < 1.0


# ============================================================
# 8b. KEY SEQUENCE HELPER
# ============================================================

def keys_from_text(text):
    """
    Convert an input string into a list of key symbols
    (e.g. "HELLO WORLD" -> ["H", "E", "L", "L", "O", "SPACE", ...]).
    """
    keys = []

    for character in text.upper():

        key = key_from_char(character)

        if key is not None:
            keys.append(key)

    return keys


def key_from_char(character):
    """
    Map a single character to a key symbol.

    - " "     -> "SPACE"
    - letter  -> uppercase letter (if it has a frequency)
    - digit   -> the digit character
    - else    -> None (not a valid key)
    """
    if character == " ":
        return "SPACE"

    character = character.upper()

    if character in KEY_FREQUENCIES:
        return character

    return None


# ============================================================
# 8c. REPORT EXPORT
# ============================================================

def format_report(text, add_noise=False, trials=WCET_TRIALS):
    """
    Build a printable text report for the current analysis.

    Returns a multi-line string.
    """
    lines = []

    lines.append("=" * 60)
    lines.append("ACOUSTIC SIDE-CHANNEL SIMULATOR - ANALYSIS REPORT")
    lines.append("=" * 60)

    lines.append(f"\nInput sequence     : {text}")
    lines.append(f"Synthetic noise    : {'ON' if add_noise else 'OFF'}")
    lines.append(f"Generated at       : {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Invariants
    invariants = check_invariants()
    lines.append("\n---------- INVARIANT CHECK ----------")
    for name, result in invariants.items():
        lines.append(f"{name:<35} : {'PASS' if result else 'FAIL'}")

    # Per-key details
    details = sequence_details(text, add_noise=add_noise)

    if details:
        lines.append("\n---------- PER-KEY FREQUENCY MAPPING ----------")
        lines.append(f"{'Key':<8}{'Freq (Hz)':>12}{'Detected':>10}"
                     f"{'Error':>10}{'Conf.':>9}{'Time (ms)':>12}")
        for d in details:
            lines.append(
                f"{d['key']:<8}{d['frequency']:>12.2f}"
                f"{d['detected_key']:>10}{d['error']:>10.2f}"
                f"{d['confidence']:>9.3f}{d['time_ms']:>12.3f}"
            )

        reconstructed = [d["detected_key"] for d in details]
        lines.append("\n---------- RECONSTRUCTED SEQUENCE ----------")
        lines.append(" ".join(reconstructed))
    else:
        lines.append("\nNo valid keys detected in the input sequence.")

    # Timing (multi-trial)
    reconstructed, avg_time, wcet_median, wcet_p95, avg_error = \
        reconstruct_sequence_wcet(
            text,
            add_noise=add_noise,
            trials=trials
        )

    lines.append("\n---------- REAL-TIME ANALYSIS ----------")
    lines.append(f"Average Execution Time            : {avg_time:.4f} ms")
    lines.append(f"WCET (median, {trials} trials)    : {wcet_median:.4f} ms")
    lines.append(f"WCET (P95, {trials} trials)       : {wcet_p95:.4f} ms")
    lines.append(f"Required Deadline                 : {DEADLINE_MS:.2f} ms")

    deadline_pass = wcet_p95 < DEADLINE_MS
    lines.append(
        f"Deadline Status                    : "
        f"{'PASS' if deadline_pass else 'FAIL'}"
    )

    lines.append("\n---------- RANKING FUNCTION ----------")
    lines.append("V = |Detected Frequency - Expected Frequency|")
    lines.append(f"Average V = {avg_error:.4f} Hz")

    # Liveness & termination
    live = liveness_test()
    lines.append("\n---------- LIVENESS ----------")
    lines.append("System can process new input      : "
                 + ("PASS" if live else "FAIL"))

    terminated = termination_test()
    lines.append("\n---------- TERMINATION ----------")
    lines.append("Finite processing terminates      : "
                 + ("PASS" if terminated else "FAIL"))

    lines.append("\n" + "=" * 60)
    lines.append("END OF REPORT")

    return "\n".join(lines)


def export_report(text, output_path, add_noise=False, trials=WCET_TRIALS,
                  export_plots=False):
    """
    Write a text report to disk, optionally saving the waveform PNG plots
    alongside it.

    Returns a list of files written.
    """
    report = format_report(text, add_noise=add_noise, trials=trials)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(report + "\n")

    files = [output_path]

    if export_plots:
        from waveform_visualization import save_visualizations

        keys = keys_from_text(text) or ["A"]
        directory = os.path.dirname(output_path) or "."
        files.extend(save_visualizations(keys, directory=directory,
                                         noise=add_noise))

    return files


# ============================================================
# 9. GUI APPLICATION
# ============================================================

class AcousticSideChannelApp:

    def __init__(self, root):

        self.root = root
        self.root.title(
            "Software Acoustic Side-Channel Simulator"
        )

        self.root.geometry("900x700")

        self.pressed_keys = []
        self.live_spec_fig = None
        self.live_spec_ax = None
        self.live_sine_fig = None
        self.live_sine_axes = None

        self.export_plots_var = tk.BooleanVar(value=True)

        self.create_interface()

    def create_interface(self):

        title = ttk.Label(
            self.root,
            text="Acoustic Side-Channel Attack Simulator",
            font=("Arial", 18, "bold")
        )

        title.pack(pady=15)

        description = ttk.Label(
            self.root,
            text=(
                "Software-only model using predefined "
                "frequency signatures"
            ),
            font=("Arial", 11)
        )

        description.pack(pady=5)

        # ----------------------------------------------------
        # INPUT
        # ----------------------------------------------------

        input_frame = ttk.Frame(self.root)

        input_frame.pack(pady=15)

        ttk.Label(
            input_frame,
            text="Enter Key Sequence:"
        ).grid(row=0, column=0, padx=5)

        self.input_entry = ttk.Entry(
            input_frame,
            width=40
        )

        self.input_entry.grid(
            row=0,
            column=1,
            padx=5
        )

        self.input_entry.insert(
            0,
            "HELLO WORLD"
        )

        self.noise_var = tk.BooleanVar(
            value=True
        )

        noise_check = ttk.Checkbutton(
            input_frame,
            text="Add synthetic frequency noise",
            variable=self.noise_var
        )

        noise_check.grid(
            row=1,
            column=1,
            pady=10
        )

        button_frame = ttk.Frame(input_frame)

        button_frame.grid(
            row=2,
            column=1,
            pady=10
        )

        self.analyze_button = ttk.Button(
            button_frame,
            text="Analyze",
            command=self.analyze
        )

        self.analyze_button.pack(side="left", padx=5)

        self.visualize_button = ttk.Button(
            button_frame,
            text="Visualize Waveform",
            command=self.show_visualization
        )

        self.visualize_button.pack(side="left", padx=5)

        self.export_button = ttk.Button(
            button_frame,
            text="Export Report",
            command=self.export_report
        )

        self.export_button.pack(side="left", padx=5)

        self.copy_button = ttk.Button(
            button_frame,
            text="Copy Result",
            command=self.copy_result
        )

        self.copy_button.pack(side="left", padx=5)

        export_plots_check = ttk.Checkbutton(
            button_frame,
            text="Include plots (PNG)",
            variable=self.export_plots_var
        )

        export_plots_check.pack(side="left", padx=5)

        # ----------------------------------------------------
        # KEYPAD (live incremental input)
        # ----------------------------------------------------

        keypad_frame = ttk.LabelFrame(
            self.root,
            text="Keypad — click a key to increment the waveform live"
        )

        keypad_frame.pack(
            padx=20,
            pady=5,
            fill="x"
        )

        keys_table = (
            "ABCDEFG",
            "HIJKLMN",
            "OPQRSTU",
            "VWXYZ",
        )

        self.keypad_buttons = {}

        for row_idx, row in enumerate(keys_table):

            for col_idx, letter in enumerate(row):

                btn = ttk.Button(
                    keypad_frame,
                    text=letter,
                    width=4,
                    command=lambda k=letter: self.on_key_pressed(k)
                )

                btn.grid(
                    row=row_idx,
                    column=col_idx,
                    padx=2,
                    pady=2
                )

                self.keypad_buttons[letter] = btn

        # Digits row (0-9) below the letters. Placed at row=5 so column 7
        # (row 4) remains a free cell and digit "7" is not covered by the
        # Clear button below.
        for col_idx, digit in enumerate("0123456789"):

            btn = ttk.Button(
                keypad_frame,
                text=digit,
                width=4,
                command=lambda k=digit: self.on_key_pressed(k)
            )

            btn.grid(
                row=5,
                column=col_idx,
                padx=2,
                pady=2
            )

            self.keypad_buttons[digit] = btn

        space_btn = ttk.Button(
            keypad_frame,
            text="SPACE",
            width=8,
            command=lambda: self.on_key_pressed("SPACE")
        )

        space_btn.grid(
            row=0,
            column=7,
            rowspan=2,
            padx=4,
            pady=2
        )

        clear_btn = ttk.Button(
            keypad_frame,
            text="Clear",
            width=8,
            command=self.clear_live
        )

        # Spans rows 2-4 (the free letter-row cells in column 7). Column 7
        # row 5 (the digit "7" cell) stays free and clickable.
        clear_btn.grid(
            row=2,
            column=7,
            rowspan=3,
            padx=4,
            pady=2
        )

        # ----------------------------------------------------
        # OUTPUT - TABS
        # ----------------------------------------------------

        self.notebook = ttk.Notebook(self.root)

        self.notebook.pack(
            padx=20,
            pady=10,
            fill="both",
            expand=True
        )

        # --- Analysis tab ---
        analysis_tab = ttk.Frame(self.notebook)

        self.notebook.add(
            analysis_tab,
            text="Analysis Result"
        )

        self.output = tk.Text(
            analysis_tab,
            height=25,
            width=100,
            font=("Courier New", 10)
        )

        scrollbar = ttk.Scrollbar(
            analysis_tab,
            command=self.output.yview
        )

        self.output.configure(
            yscrollcommand=scrollbar.set
        )

        self.output.pack(
            side="left",
            padx=10,
            pady=10,
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # --- Waveform tab ---
        self.waveform_tab = ttk.Frame(self.notebook)

        self.notebook.add(
            self.waveform_tab,
            text="Waveform"
        )

        waveform_info = ttk.Label(
            self.waveform_tab,
            text=(
                "Sine waveform and spectrogram of the key sequence. "
                "Use the 'Visualize Waveform' button to generate."
            ),
            font=("Arial", 10)
        )

        waveform_info.pack(pady=10)

        self.waveform_canvas_frame = ttk.Frame(
            self.waveform_tab
        )

        self.waveform_canvas_frame.pack(
            fill="both",
            expand=True
        )

        # Status bar
        self.status_var = tk.StringVar(value="Ready")

        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        )

        status_bar.pack(
            side="bottom",
            fill="x"
        )

    # --------------------------------------------------------
    # VISUALIZATION FUNCTION
    # --------------------------------------------------------

    def _build_live_canvas(self, noise):
        """
        Create (or recreate) the reusable two-panel figure (spectrogram on top,
        sine plot below) embedded in the Waveform tab. Stores the figures/axes
        on self so on_key_pressed can update them incrementally.
        """
        import matplotlib
        # Embedding figures in Tk requires the TkAgg backend, selected here
        # (where the display is available) rather than in the headless-safe
        # visualization module.
        matplotlib.use("TkAgg")

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from waveform_visualization import (
            plot_spectrogram,
            plot_sine_waves,
        )

        # Destroy any existing canvas widgets and figures.
        for child in self.waveform_canvas_frame.winfo_children():
            child.destroy()

        for fig in (self.live_spec_fig, self.live_sine_fig):
            if fig is not None:
                fig.clear()

        keys = self.pressed_keys or ["A"]

        self.live_spec_fig = plot_spectrogram(keys, noise=noise)
        self.live_spec_ax = self.live_spec_fig.axes[0]

        self.live_sine_fig = plot_sine_waves(keys, noise=noise)

        spec_canvas = FigureCanvasTkAgg(
            self.live_spec_fig,
            master=self.waveform_canvas_frame
        )
        spec_canvas.draw()
        spec_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        sine_canvas = FigureCanvasTkAgg(
            self.live_sine_fig,
            master=self.waveform_canvas_frame
        )
        sine_canvas.draw()
        sine_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.spec_canvas = spec_canvas

        self.live_sine_axes = self.live_sine_fig.axes

        self.notebook.select(self.waveform_tab)

    def on_key_pressed(self, key):
        """
        Handle a keypad button press: append the key, sync the entry text,
        run the per-key pipeline, and incrementally update the waveform plots.
        """
        self.pressed_keys.append(key)

        # Keep the entry text in sync with the pressed keys.
        current = self.input_entry.get()
        char = " " if key == "SPACE" else key
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, current + char)

        # Per-key processing for the status line.
        frequency = generate_frequency(key, noise=self.noise_var.get())
        detected_key, error, execution_time = process_frequency(frequency)
        confidence = compute_confidence(detected_key, error)

        self.status_var.set(
            f"Key={key}  Freq={frequency:.2f} Hz  "
            f"Detected={detected_key}  Error={error:.2f} Hz  "
            f"Conf={confidence:.3f}  Time={execution_time:.3f} ms  "
            f"[{len(self.pressed_keys)} keys]"
        )

        # Build the canvas on the first key press; update incrementally
        # on subsequent presses.
        if self.live_spec_fig is None:
            self._build_live_canvas(self.noise_var.get())
            return

        try:
            from waveform_visualization import (
                update_spectrogram,
                update_sine_plot,
            )
            noise = self.noise_var.get()
            update_spectrogram(
                self.live_spec_fig,
                self.live_spec_ax,
                self.pressed_keys,
                noise=noise
            )
            update_sine_plot(
                self.live_sine_fig,
                self.live_sine_axes,
                self.pressed_keys,
                noise=noise
            )
            self.spec_canvas.draw_idle()
        except Exception as exc:
            self.status_var.set(f"Incremental update error: {exc}")

    def clear_live(self):
        """
        Reset the accumulated pressed keys, the entry, and the live canvas.
        """
        self.pressed_keys = []

        self.input_entry.delete(0, tk.END)

        for fig in (self.live_spec_fig, self.live_sine_fig):
            if fig is not None:
                fig.clear()

        self.live_spec_fig = None
        self.live_spec_ax = None
        self.live_sine_fig = None
        self.live_sine_axes = None

        for child in self.waveform_canvas_frame.winfo_children():
            child.destroy()

        self.status_var.set("Cleared live keypad input")

    def show_visualization(self):
        """
        Build (or rebuild) the waveform visualization from the current entry
        text. Subsequent keypad presses update the plots incrementally.
        """
        # Sync the internal key list from the entry text.
        text = self.input_entry.get()
        keys = keys_from_text(text)

        if keys:
            self.pressed_keys = keys
        else:
            self.pressed_keys = ["A"]

        self.status_var.set("Generating waveform visualization...")
        self.root.update_idletasks()

        try:
            self._build_live_canvas(self.noise_var.get())
            self.status_var.set(
                "Visualization displayed for "
                + ", ".join(self.pressed_keys)
            )
        except Exception as exc:
            error_label = ttk.Label(
                self.waveform_canvas_frame,
                text=f"Visualization error: {exc}",
                foreground="red"
            )
            error_label.pack()
            self.status_var.set("Visualization failed")

    # --------------------------------------------------------
    # ANALYSIS FUNCTION
    # --------------------------------------------------------

    def analyze(self):
        """
        Run the full CPS analysis for the current input and display it.

        Delegates to format_report() so the GUI output and the exported
        report always come from the same single code path.
        """
        text = self.input_entry.get()

        self.status_var.set("Analyzing...")
        self.root.update_idletasks()

        report = format_report(
            text,
            add_noise=self.noise_var.get(),
            trials=WCET_TRIALS
        )

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, report)

        self.status_var.set("Analysis complete")

    def export_report(self):
        """
        Export the current analysis as a text report, optionally saving the
        waveform plots (PNG) alongside it.
        """
        text = self.input_entry.get()

        output_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
            title="Save Analysis Report"
        )

        if not output_path:
            self.status_var.set("Export cancelled")
            return

        self.status_var.set("Exporting report...")
        self.root.update_idletasks()

        export_plots = self.export_plots_var.get()

        try:
            files = export_report(
                text,
                output_path,
                add_noise=self.noise_var.get(),
                trials=WCET_TRIALS,
                export_plots=export_plots
            )
            self.status_var.set(
                "Report exported: " + ", ".join(files)
            )
        except Exception as exc:
            self.status_var.set(f"Export failed: {exc}")

    def copy_result(self):
        """
        Copy the analysis result text to the system clipboard.
        """
        result = self.output.get("1.0", tk.END).strip()

        if not result:
            self.status_var.set("Nothing to copy")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        self.status_var.set("Result copied to clipboard")


# ============================================================
# 10. START APPLICATION
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AcousticSideChannelApp(root)

    root.mainloop()
