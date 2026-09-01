import tkinter as tk
from tkinter import ttk
import time
import random
import os
import sys


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

    "SPACE": 1220.0
}


# ============================================================
# CONFIGURATION
# ============================================================

# Maximum frequency difference accepted as a valid match.
TOLERANCE = 8.0

# Deadline used for the CPS real-time demonstration.
DEADLINE_MS = 50.0


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
    - else    -> None (not a valid key)
    """
    if character == " ":
        return "SPACE"

    character = character.upper()

    if character in KEY_FREQUENCIES:
        return character

    return None


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

        clear_btn.grid(
            row=2,
            column=7,
            rowspan=2,
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

        self.status_var.set(
            f"Key={key}  Freq={frequency:.2f} Hz  "
            f"Detected={detected_key}  Error={error:.2f} Hz  "
            f"Time={execution_time:.3f} ms  "
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

        self.output.delete(
            "1.0",
            tk.END
        )

        text = self.input_entry.get()

        self.status_var.set("Analyzing...")
        self.root.update_idletasks()

        # ----------------------------------------------
        # INVARIANT CHECK
        # ----------------------------------------------

        invariants = check_invariants()

        self.output.insert(
            tk.END,
            "========== INVARIANT CHECK ==========\n\n"
        )

        for name, result in invariants.items():

            status = "PASS" if result else "FAIL"

            self.output.insert(
                tk.END,
                f"{name:<35} : {status}\n"
            )

        # Below is the full analysis. It needs to catch the
        # "Unknown key" case where an invalid symbol is entered.

        # Map symbols and skip invalid symbols in the same way
        # the original code did, but also compute the correct
        # frequency mapping for the display.

        mapped = []

        for character in text.upper():

            if character == " ":
                key = "SPACE"

            elif character in KEY_FREQUENCIES:
                key = character

            else:
                key = None

            if key is not None:
                mapped.append(key)

        # Compute reconstruction stats. The original
        # reconstruct_sequence filters invalid symbols itself,
        # so use the raw text.
        reconstructed, avg_time, wcet, avg_error = \
            reconstruct_sequence(
                text,
                add_noise=self.noise_var.get()
            )

        # ----------------------------------------------
        # FREQUENCY MAPPING
        # ----------------------------------------------

        self.output.insert(
            tk.END,
            "\n========== FREQUENCY MAPPING ==========\n\n"
        )

        for key in mapped:

            frequency = generate_frequency(
                key,
                noise=self.noise_var.get()
            )

            detected_key, error, execution_time = \
                process_frequency(frequency)

            self.output.insert(
                tk.END,
                f"{key:<8} "
                f"Freq={frequency:8.2f} Hz   "
                f"Detected={detected_key:<7} "
                f"Error={error:6.2f} Hz   "
                f"Time={execution_time:6.3f} ms\n"
            )

        # ----------------------------------------------
        # RECONSTRUCTED OUTPUT
        # ----------------------------------------------

        self.output.insert(
            tk.END,
            "\n========== RECONSTRUCTED SEQUENCE ==========\n\n"
        )

        self.output.insert(
            tk.END,
            " ".join(reconstructed)
        )

        # ----------------------------------------------
        # PERFORMANCE
        # ----------------------------------------------

        self.output.insert(
            tk.END,
            "\n\n========== REAL-TIME ANALYSIS ==========\n\n"
        )

        self.output.insert(
            tk.END,
            f"Average Execution Time : "
            f"{avg_time:.4f} ms\n"
        )

        self.output.insert(
            tk.END,
            f"Worst Case Execution Time (WCET) : "
            f"{wcet:.4f} ms\n"
        )

        self.output.insert(
            tk.END,
            f"Required Deadline : "
            f"{DEADLINE_MS:.2f} ms\n"
        )

        if wcet < DEADLINE_MS:

            self.output.insert(
                tk.END,
                "Deadline Status : PASS\n"
            )

        else:

            self.output.insert(
                tk.END,
                "Deadline Status : FAIL\n"
            )

        # ----------------------------------------------
        # RANKING FUNCTION
        # ----------------------------------------------

        self.output.insert(
            tk.END,
            "\n========== RANKING FUNCTION ==========\n\n"
        )

        self.output.insert(
            tk.END,
            "V = |Detected Frequency - Expected Frequency|\n"
        )

        self.output.insert(
            tk.END,
            f"Average V = {avg_error:.4f} Hz\n"
        )

        # ----------------------------------------------
        # LIVENESS
        # ----------------------------------------------

        live = liveness_test()

        self.output.insert(
            tk.END,
            "\n========== LIVENESS ==========\n\n"
        )

        self.output.insert(
            tk.END,
            "System can process new input : "
            + ("PASS\n" if live else "FAIL\n")
        )

        # ----------------------------------------------
        # TERMINATION
        # ----------------------------------------------

        terminated = termination_test()

        self.output.insert(
            tk.END,
            "\n========== TERMINATION ==========\n\n"
        )

        self.output.insert(
            tk.END,
            "Finite processing terminates : "
            + ("PASS\n" if terminated else "FAIL\n")
        )

        self.status_var.set("Analysis complete")


# ============================================================
# 10. START APPLICATION
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AcousticSideChannelApp(root)

    root.mainloop()
