#!/usr/bin/env python3
"""Thought Probe - Attentional Distraction Measurement Tool.

A tkinter-based desktop application for measuring attention during reading
as part of a physiological computing research study. Presents reading
passages, administers random attention probes, and logs all events with
millisecond-precision timestamps to CSV.

Usage:
    python main.py              # Run in normal mode (25 min reading)
    python main.py --test       # Run in test mode (30 sec reading, fast probes)

States: STARTUP, INSTRUCTIONS, READING, QUIZ, BREAK,
        ACCEPTABILITY_QUESTIONNAIRE, END
"""

import tkinter as tk
from tkinter import messagebox
import csv
import time
import random
import sys
import os
import ctypes
import platform

# Enable DPI awareness on Windows so tkinter renders at native resolution
# instead of being bitmap-scaled (which causes the "grainy" look).
if platform.system() == "Windows":
    try:
        # PROCESS_PER_MONITOR_DPI_AWARE — crisp on any monitor
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            # Fallback for older Windows 8.1
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            try:
                # Fallback for Windows Vista / 7
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass

from content import PASSAGES, QUESTIONNAIRE_ITEMS

# Use Segoe UI on Windows (designed for screen rendering, much sharper),
# fall back to Arial on other platforms.
FONT_FAMILY = "Segoe UI" if platform.system() == "Windows" else "Arial"


class App:
    """Main application class managing the state machine and UI.

    The application follows a sequential state machine pattern. Each state
    is implemented as a ``show_<state>`` method that clears the content
    frame and rebuilds the UI. Transitions occur via button callbacks or
    timer expirations.

    Instance attributes for state tracking:
        - state: Current state name string
        - probe_active: Boolean flag preventing overlapping probe interruptions
        - reading_finished: Set to True when the reading timer expires (used when
          a probe is active at expiry to transition after the probe resolves)
        - current_block: Index into passage_order (0 or 1 for the two blocks)
        - current_passage_id: The passage key ("A" or "B") for the active block
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Thought Probe - Attention Research Study")
        self.root.geometry("960x720")
        self.root.minsize(800, 600)

        # -- Test mode detection -----------------------------------------------
        self.test_mode = "--test" in sys.argv

        # -- Timing configuration (compressed in test mode) --------------------
        if self.test_mode:
            self.reading_duration_ms = 30_000
            self.probe_min_s = 3
            self.probe_max_s = 5
        else:
            self.reading_duration_ms = 1_500_000  # 25 minutes
            self.probe_min_s = 60
            self.probe_max_s = 90

        # -- Session metadata --------------------------------------------------
        self.participant_id = ""
        self.condition = ""
        self.condition_order = "A_then_B"
        self.passage_order = ["A", "B"]
        self.current_block = 0
        self.current_passage_id = None
        self.state = None
        self.csv_writer = None
        self.csv_file = None
        self.data_file_path = None

        # -- Reading-phase state -----------------------------------------------
        self.probe_active = False
        self.reading_finished = False
        self.reading_start_wall = 0.0
        self.scroll_fraction = 0.0
        self.countdown_var = None
        self.reading_text = None
        self.self_caught_button = None
        self.reading_end_id = None
        self.probe_timer_id = None

        # -- Quiz state --------------------------------------------------------
        self.quiz_questions = []
        self.current_question_idx = 0
        self.quiz_selected = None

        # -- Questionnaire state -----------------------------------------------
        self.questionnaire_vars = []

        # -- Tracked ``after`` IDs for cleanup ---------------------------------
        self.after_ids = []

        # -- Admin exit (Escape-hold) state ------------------------------------
        self.escape_press_time = None
        self.escape_hold_id = None

        # -- Content frame (replaced on each state transition) ------------------
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # -- Admin exit button (always visible, bottom-right corner) -----------
        admin_frame = tk.Frame(self.root)
        admin_frame.place(relx=1.0, rely=1.0, anchor=tk.SE)
        admin_btn = tk.Button(
            admin_frame,
            text=chr(0x23F0),  # clock emoji as inconspicuous marker
            font=(FONT_FAMILY, 7),
            width=2,
            height=1,
            command=self.abort_session,
        )
        admin_btn.pack()

        # -- Fullscreen toggle -------------------------------------------------
        self.fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)

        # -- Bootstrap ---------------------------------------------------------
        self.setup_csv_dir()
        self.setup_admin_exit()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.show_startup()

    # ------------------------------------------------------------------
    #   Timer helpers
    # ------------------------------------------------------------------

    def _after(self, ms, callback):
        """Schedule ``callback`` after ``ms`` milliseconds.

        Tracks the returned ``after`` ID so it can be cancelled during
        cleanup or abort.
        """
        after_id = self.root.after(ms, callback)
        self.after_ids.append(after_id)
        return after_id

    def _cancel(self, after_id):
        """Cancel a previously scheduled ``after`` callback (no-op if None)."""
        if after_id is None:
            return
        try:
            self.root.after_cancel(after_id)
        except Exception:
            pass
        if after_id in self.after_ids:
            self.after_ids.remove(after_id)

    # ------------------------------------------------------------------
    #   CSV / data logging
    # ------------------------------------------------------------------

    def setup_csv_dir(self):
        """Create the ``data/`` directory if it does not exist."""
        try:
            os.makedirs("data", exist_ok=True)
        except OSError as exc:
            messagebox.showerror(
                "Fatal Error",
                f"Cannot create data directory:\n{exc}\n\n"
                "Please ensure the application has write permissions.",
            )
            sys.exit(1)

    def init_csv_file(self):
        """Create the session CSV file and write the header row."""
        unix_ts = int(time.time())
        filename = f"session_{self.participant_id}_{unix_ts}.csv"
        self.data_file_path = os.path.join("data", filename)
        try:
            self.csv_file = open(self.data_file_path, "w", newline="")
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow([
                "event_type", "timestamp_ms", "condition",
                "passage_id", "value", "extra",
            ])
            self.csv_file.flush()
        except IOError as exc:
            messagebox.showerror(
                "Fatal Error",
                f"Cannot create data file:\n{exc}\n\n"
                "Please check disk space and permissions.",
            )
            sys.exit(1)

    def log_event(self, event_type, value="", extra=""):
        """Append one row to the session CSV file with a millisecond timestamp.

        Rows are written immediately (``flush()`` after each write) so that
        partial data survives a crash.
        """
        if self.csv_writer is None:
            return
        timestamp_ms = int(time.time() * 1000)
        try:
            self.csv_writer.writerow([
                event_type,
                timestamp_ms,
                self.condition,
                self.current_passage_id or "",
                str(value),
                str(extra),
            ])
            self.csv_file.flush()
        except IOError as exc:
            messagebox.showerror(
                "Logging Error",
                f"Failed to write to data file:\n{exc}\n\n"
                "Data may be incomplete. Contact the experimenter.",
            )

    # ------------------------------------------------------------------
    #   UI helpers
    # ------------------------------------------------------------------

    def clear_content(self):
        """Destroy all child widgets of the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    @staticmethod
    def format_ms(ms):
        """Return ``MM:SS`` from a millisecond value."""
        total_s = ms // 1000
        return f"{total_s // 60:02d}:{total_s % 60:02d}"

    # ------------------------------------------------------------------
    #   Admin exit (Escape held for 2 seconds)
    # ------------------------------------------------------------------

    def setup_admin_exit(self):
        """Bind keyboard events for the Escape-hold-to-abort feature."""
        def on_press(event):
            if event.keysym == "Escape":
                self.escape_press_time = time.time()
                self.escape_hold_id = self.root.after(
                    2000, self.check_escape_hold
                )

        def on_release(event):
            if event.keysym == "Escape":
                self.escape_press_time = None
                if self.escape_hold_id is not None:
                    self.root.after_cancel(self.escape_hold_id)
                    self.escape_hold_id = None

        self.root.bind("<KeyPress>", on_press)
        self.root.bind("<KeyRelease>", on_release)

    def check_escape_hold(self):
        """Prompt to abort if Escape was held for 2+ seconds."""
        if self.escape_press_time is not None and (
            time.time() - self.escape_press_time >= 2
        ):
            if messagebox.askyesno(
                "Abort Session",
                "Admin abort requested.\n\nAbort the current session?",
                icon=messagebox.WARNING,
            ):
                self.abort_session()
        self.escape_hold_id = None

    def abort_session(self):
        """Log a SESSION_ABORTED event, clean up, and close the application."""
        self.log_event("SESSION_ABORTED", value="admin_abort")
        self.cleanup()
        self.root.destroy()

    def toggle_fullscreen(self, event=None):
        """Toggle borderless fullscreen mode (F11)."""
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def on_closing(self):
        """Handle the window close button."""
        if self.state not in ("END", None):
            if self.state == "STARTUP":
                self.cleanup()
                self.root.destroy()
                return
            if not messagebox.askyesno(
                "Confirm Exit",
                "Are you sure you want to exit?\n"
                "The current session will be aborted.",
            ):
                return
            self.log_event("SESSION_ABORTED", value="window_closed")
        self.cleanup()
        self.root.destroy()

    def cleanup(self):
        """Cancel all pending ``after`` callbacks and close the CSV file."""
        for after_id in self.after_ids:
            try:
                self.root.after_cancel(after_id)
            except Exception:
                pass
        self.after_ids.clear()
        if self.csv_file is not None:
            try:
                self.csv_file.close()
            except Exception:
                pass

    # ==================================================================
    #   STATE: STARTUP
    # ==================================================================

    def show_startup(self):
        """Display the startup form for participant ID, condition, and order.

        On submission, initialises the CSV file, logs SESSION_START,
        and transitions to INSTRUCTIONS.
        """
        self.clear_content()
        self.state = "STARTUP"

        frame = tk.Frame(self.content_frame, padx=40, pady=40)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="Thought Probe \u2014 Attention Research Study",
            font=(FONT_FAMILY, 18, "bold"),
        ).pack(pady=(0, 30))

        # -- Participant ID --
        tk.Label(frame, text="Participant ID:", font=(FONT_FAMILY, 14)).pack(
            anchor=tk.W
        )
        id_var = tk.StringVar()
        tk.Entry(
            frame, textvariable=id_var, font=(FONT_FAMILY, 14), width=30
        ).pack(anchor=tk.W, pady=(0, 20))

        # -- Condition (feedback / no-feedback) --
        tk.Label(frame, text="Condition:", font=(FONT_FAMILY, 14)).pack(anchor=tk.W)
        cond_var = tk.StringVar(value="feedback")
        cond_frame = tk.Frame(frame)
        cond_frame.pack(anchor=tk.W, pady=(0, 20))
        for text, value in [
            ("Feedback", "feedback"),
            ("No Feedback", "no_feedback"),
        ]:
            tk.Radiobutton(
                cond_frame,
                text=text,
                variable=cond_var,
                value=value,
                font=(FONT_FAMILY, 12),
            ).pack(side=tk.LEFT, padx=(0, 20))

        # -- Passage order --
        tk.Label(frame, text="Passage Order:", font=(FONT_FAMILY, 14)).pack(
            anchor=tk.W
        )
        order_var = tk.StringVar(value="A_then_B")
        order_frame = tk.Frame(frame)
        order_frame.pack(anchor=tk.W, pady=(0, 30))
        for text, value in [
            ("Passage A then B", "A_then_B"),
            ("Passage B then A", "B_then_A"),
        ]:
            tk.Radiobutton(
                order_frame,
                text=text,
                variable=order_var,
                value=value,
                font=(FONT_FAMILY, 12),
            ).pack(side=tk.LEFT, padx=(0, 20))

        # -- Test mode indicator --
        if self.test_mode:
            tk.Label(
                frame,
                text="[TEST MODE] Timings compressed for testing",
                font=(FONT_FAMILY, 12, "bold"),
                fg="red",
            ).pack(pady=(0, 15))

        # -- Submit --
        def submit():
            pid = id_var.get().strip()
            if not pid:
                messagebox.showwarning(
                    "Input Required", "Please enter a participant ID."
                )
                return
            self.participant_id = pid
            self.condition = cond_var.get()
            self.condition_order = order_var.get()
            self.passage_order = (
                ["A", "B"] if self.condition_order == "A_then_B" else ["B", "A"]
            )

            self.init_csv_file()
            self.log_event(
                "SESSION_START",
                value=f"condition={self.condition}",
                extra=f"order={self.condition_order}",
            )
            self.show_instructions()

        tk.Button(
            frame,
            text="Start Session",
            font=(FONT_FAMILY, 14),
            command=submit,
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
        ).pack()

    # ==================================================================
    #   STATE: INSTRUCTIONS
    # ==================================================================

    def show_instructions(self):
        """Display instructions for the upcoming reading block.

        Determines which passage to use from ``passage_order[current_block]``.
        A "Start Reading" button transitions to the READING state.
        """
        self.clear_content()
        self.state = "INSTRUCTIONS"
        self.current_passage_id = self.passage_order[self.current_block]
        passage = PASSAGES[self.current_passage_id]

        frame = tk.Frame(self.content_frame, padx=40, pady=40)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame, text="Instructions", font=(FONT_FAMILY, 18, "bold")
        ).pack(pady=(0, 20))

        instructions = (
            f"In this part of the study, you will read a passage about:\n\n"
            f"    \u201c{passage['title']}\u201d\n\n"
            "Please read carefully and at your natural pace. You will be asked comprehension questions afterward\n\n"
            "Occasionally, a popup will appear asking about your current level of attention.\n" 
            "Please respond honestly.\n\n"
            "If you notice your mind wandering at any point, you may click the \u201cI notice my mind wandering\u201d button\n"
            "that appears at the bottom of the reading screen.    \n\n"  
            "Click \u2018Start Reading\u2019 when you are ready to begin."
        )

        tk.Label(
            frame,
            text=instructions,
            font=(FONT_FAMILY, 14),
            wraplength=700,
            justify=tk.LEFT,
        ).pack(pady=(0, 30))

        if self.test_mode:
            tk.Label(
                frame,
                text="[TEST MODE] Reading will last 30 seconds",
                font=(FONT_FAMILY, 12, "bold"),
                fg="red",
            ).pack(pady=(0, 10))

        tk.Button(
            frame,
            text="Start Reading",
            font=(FONT_FAMILY, 14),
            command=self.start_reading,
            bg="#2196F3",
            fg="white",
            padx=30,
            pady=10,
        ).pack()

    # ==================================================================
    #   STATE: READING
    # ==================================================================

    def start_reading(self):
        """Begin the reading phase.

        Resets reading-phase flags, builds the reading UI (title bar with
        countdown, scrollable text widget, self-caught button), logs
        READING_START, and starts the probe and countdown timers.
        """
        self.probe_active = False
        self.reading_finished = False
        self.reading_start_wall = time.time()
        self.scroll_fraction = 0.0

        self.clear_content()
        self.state = "READING"
        passage = PASSAGES[self.current_passage_id]
        self.log_event("READING_START")

        # -- Title bar with countdown --
        top_bar = tk.Frame(self.content_frame, bg="#e0e0e0")
        top_bar.pack(fill=tk.X)

        tk.Label(
            top_bar,
            text=passage["title"],
            font=(FONT_FAMILY, 14, "bold"),
            bg="#e0e0e0",
        ).pack(side=tk.LEFT, padx=20, pady=10)

        self.countdown_var = tk.StringVar()
        self.countdown_var.set(self.format_ms(self.reading_duration_ms))
        tk.Label(
            top_bar,
            textvariable=self.countdown_var,
            font=(FONT_FAMILY, 14, "bold"),
            bg="#e0e0e0",
        ).pack(side=tk.RIGHT, padx=20, pady=10)

        # -- Scrollable reading text (slim column with generous margins) --
        text_frame = tk.Frame(self.content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=250, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.reading_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=(FONT_FAMILY, 14),
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10,
        )
        self.reading_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.reading_text.yview)

        self.reading_text.insert(tk.END, passage["text"])
        self.reading_text.config(state=tk.DISABLED)

        # -- Self-caught button (always visible, bottom-right) --
        self.self_caught_button = tk.Button(
            self.content_frame,
            text="I notice my mind wandering",
            font=(FONT_FAMILY, 11),
            bg="#FF9800",
            fg="white",
            command=self.on_self_caught,
            padx=15,
            pady=8,
        )
        self.self_caught_button.pack(side=tk.RIGHT, anchor=tk.SE, padx=20, pady=10)

        # -- Start the countdown display --
        self._after(250, self.update_countdown)

        # -- Schedule the first random thought probe --
        self.schedule_next_probe()

        # -- Schedule the end of the reading phase --
        self.reading_end_id = self._after(
            self.reading_duration_ms, self.on_reading_end
        )

    # ---- countdown -----------------------------------------------------------

    def update_countdown(self):
        """Update the countdown label every 250 ms while in READING state."""
        if self.state != "READING":
            return
        elapsed_ms = int((time.time() - self.reading_start_wall) * 1000)
        remaining = max(0, self.reading_duration_ms - elapsed_ms)
        self.countdown_var.set(self.format_ms(remaining))
        self._after(250, self.update_countdown)

    # ---- probe scheduling ----------------------------------------------------

    def schedule_next_probe(self):
        """Schedule the next thought probe after a random delay.

        The delay is drawn from ``random.uniform(probe_min_s, probe_max_s)``
        and then converted to milliseconds.  Scheduling is skipped if a
        probe is already active, preventing overlapping interruptions.

        This is the core random-probe mechanism of the study: each probe is
        independently timed so the participant cannot predict when the next
        interruption will occur.
        """
        if self.probe_active:
            return
        if self.state != "READING" or self.reading_finished:
            return

        delay_s = random.uniform(self.probe_min_s, self.probe_max_s)
        delay_ms = int(delay_s * 1000)

        self.probe_timer_id = self._after(delay_ms, self.show_probe)

    # ---- self-caught mind-wandering -----------------------------------------

    def on_self_caught(self):
        """Log a SELF_CAUGHT event when the participant clicks the button.

        Ignored while a probe interruption is active (``probe_active == True``)
        to avoid response ambiguity.
        """
        if self.probe_active:
            return
        self.log_event("SELF_CAUGHT")

    # ---- probe interruption -------------------------------------------------

    def show_probe(self):
        """Display the attention-rating probe and hide the reading passage.

        Saves the current scroll position, hides all reading widgets, and
        shows a visually distinct orange-background screen with the probe
        question and four rating buttons.  Sets ``probe_active = True`` to
        block the self-caught button and prevent overlapping probes.
        Logs PROBE_SHOWN at the moment the probe appears.
        """
        if self.probe_active or self.state != "READING":
            return

        self.probe_active = True

        # Save scroll position before hiding the text widget
        if self.reading_text is not None:
            self.scroll_fraction = self.reading_text.yview()[0]

        # Hide all reading-phase widgets
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

        self.log_event("PROBE_SHOWN")

        # Build the probe interruption UI
        self._show_probe_ui()

    def _show_probe_ui(self):
        """Build the probe interruption screen with a coloured background."""
        probe_frame = tk.Frame(self.content_frame, bg="#FFF3E0")
        probe_frame.pack(fill=tk.BOTH, expand=True)

        center = tk.Frame(probe_frame, bg="#FFF3E0")
        center.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(
            center,
            text="Where was your attention right before\nthis popup appeared?",
            font=(FONT_FAMILY, 18, "bold"),
            bg="#FFF3E0",
            justify=tk.CENTER,
        ).pack(pady=(0, 10))

        # 10-second countdown label
        self.probe_timeout_var = tk.StringVar()
        self.probe_timeout_var.set("Respond within 10 seconds")
        tk.Label(
            center,
            textvariable=self.probe_timeout_var,
            font=(FONT_FAMILY, 12),
            bg="#FFF3E0",
            fg="#888888",
        ).pack(pady=(0, 25))

        buttons = [
            (1, "Fully on the task", "#4CAF50"),
            (2, "Mostly on the task", "#8BC34A"),
            (3, "Mind wandering a little", "#FF9800"),
            (4, "Mind wandering completely", "#F44336"),
        ]

        for value, label, colour in buttons:
            btn = tk.Button(
                center,
                text=f"{value}\n{label}",
                font=(FONT_FAMILY, 16, "bold"),
                bg=colour,
                fg="white",
                width=28,
                height=3,
                command=lambda v=value: self.on_probe_response(v),
            )
            btn.pack(pady=6)

        # Start the 10-second probe timer
        self.probe_timeout_remaining = 10
        self._after(1000, self._tick_probe_timer)

    def _tick_probe_timer(self):
        """Count down the 10-second probe response window."""
        if not self.probe_active:
            return
        self.probe_timeout_remaining -= 1
        self.probe_timeout_var.set(
            f"Respond within {self.probe_timeout_remaining} seconds"
        )
        if self.probe_timeout_remaining <= 0:
            self.on_probe_timeout()
        else:
            self._after(1000, self._tick_probe_timer)

    def on_probe_timeout(self):
        """Handle a probe that expired without a response.

        Logs a PROBE_TIMEOUT event (distinct from PROBE_RESPONSE), then
        resumes reading or transitions to quiz.
        """
        response_ts_ms = int(time.time() * 1000)

        self.log_event(
            "PROBE_TIMEOUT",
            value="0",
            extra=f"response_ts={response_ts_ms}",
        )

        self.probe_active = False

        if self.reading_finished:
            self.clear_content()
            self.log_event("READING_END")
            self.show_quiz()
        else:
            self._clear_and_restore_reading()
            self.schedule_next_probe()

    def on_probe_response(self, value):
        """Handle a probe response, log it, and resume reading.

        If the reading timer expired while the probe was active
        (``reading_finished == True``), transitions directly to QUIZ.
        Otherwise restores the reading view and schedules the next probe.
        """
        response_ts_ms = int(time.time() * 1000)

        self.log_event(
            "PROBE_RESPONSE",
            value=str(value),
            extra=f"response_ts={response_ts_ms}",
        )

        self.probe_active = False

        if self.reading_finished:
            self.clear_content()
            self.log_event("READING_END")
            self.show_quiz()
        else:
            self._clear_and_restore_reading()
            self.schedule_next_probe()

    def _clear_and_restore_reading(self):
        """Destroy the probe UI and rebuild the reading view."""
        self.clear_content()
        self._restore_reading_ui()

    def _restore_reading_ui(self):
        """Rebuild the reading passage, countdown, and self-caught button.

        Restores the scroll position saved before the probe interruption.
        """
        self.state = "READING"
        passage = PASSAGES[self.current_passage_id]

        # Title bar
        top_bar = tk.Frame(self.content_frame, bg="#e0e0e0")
        top_bar.pack(fill=tk.X)
        tk.Label(
            top_bar,
            text=passage["title"],
            font=(FONT_FAMILY, 14, "bold"),
            bg="#e0e0e0",
        ).pack(side=tk.LEFT, padx=20, pady=10)

        # If we had a countdown var, keep showing it; otherwise use a fresh one
        if self.countdown_var is None:
            self.countdown_var = tk.StringVar()
            self.countdown_var.set("00:00")
        tk.Label(
            top_bar,
            textvariable=self.countdown_var,
            font=(FONT_FAMILY, 14, "bold"),
            bg="#e0e0e0",
        ).pack(side=tk.RIGHT, padx=20, pady=10)

        # Scrollable text
        text_frame = tk.Frame(self.content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=250, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.reading_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=(FONT_FAMILY, 14),
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10,
        )
        self.reading_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.reading_text.yview)

        self.reading_text.insert(tk.END, passage["text"])
        self.reading_text.config(state=tk.DISABLED)
        self.reading_text.yview_moveto(self.scroll_fraction)

        # Self-caught button
        self.self_caught_button = tk.Button(
            self.content_frame,
            text="I notice my mind wandering",
            font=(FONT_FAMILY, 12),
            bg="#FF9800",
            fg="white",
            command=self.on_self_caught,
            padx=20,
            pady=10,
        )
        self.self_caught_button.pack(
            side=tk.RIGHT, anchor=tk.SE, padx=20, pady=10
        )

    # ---- reading end ---------------------------------------------------------

    def on_reading_end(self):
        """Handle the expiry of the reading timer.

        If no probe is active, transitions to QUIZ immediately.
        If a probe is active, sets ``reading_finished = True`` so that
        ``on_probe_response`` transitions to QUIZ once the probe resolves.
        """
        self.reading_finished = True
        if not self.probe_active:
            self.log_event("READING_END")
            self.show_quiz()

    # ==================================================================
    #   STATE: QUIZ
    # ==================================================================

    def show_quiz(self):
        """Begin the quiz for the current passage, showing one question at a time."""
        self.clear_content()
        self.state = "QUIZ"
        passage = PASSAGES[self.current_passage_id]
        self.quiz_questions = passage["questions"]
        self.current_question_idx = 0
        self._display_question()

    def _display_question(self):
        """Show the current quiz question with radio-button options."""
        self.clear_content()

        question = self.quiz_questions[self.current_question_idx]
        total = len(self.quiz_questions)

        frame = tk.Frame(self.content_frame, padx=40, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)

        # Progress
        tk.Label(
            frame,
            text=f"Question {self.current_question_idx + 1} of {total}",
            font=(FONT_FAMILY, 12),
            fg="gray",
        ).pack(anchor=tk.W, pady=(0, 15))

        # Question text
        tk.Label(
            frame,
            text=question["question"],
            font=(FONT_FAMILY, 14),
            wraplength=750,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(0, 20))

        # Options as radio buttons
        self.quiz_selected = tk.IntVar(value=-1)
        for idx, option in enumerate(question["options"]):
            tk.Radiobutton(
                frame,
                text=option,
                variable=self.quiz_selected,
                value=idx,
                font=(FONT_FAMILY, 13),
                wraplength=700,
                justify=tk.LEFT,
                anchor=tk.W,
                padx=20,
                pady=5,
            ).pack(anchor=tk.W, fill=tk.X)

        # Navigation
        is_last = self.current_question_idx == total - 1
        btn_text = "Finish Quiz" if is_last else "Next Question"

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=30)

        tk.Button(
            btn_frame,
            text=btn_text,
            font=(FONT_FAMILY, 14),
            command=self._handle_quiz_answer,
            bg="#2196F3",
            fg="white",
            padx=25,
            pady=8,
        ).pack(side=tk.RIGHT)

    def _handle_quiz_answer(self):
        """Record the current answer and advance or finish the quiz."""
        selected = self.quiz_selected.get()
        if selected < 0:
            messagebox.showwarning(
                "Answer Required", "Please select an answer before continuing."
            )
            return

        question = self.quiz_questions[self.current_question_idx]
        is_correct = selected == question["correct_index"]
        self.log_event(
            "QUIZ_ANSWER",
            value=str(selected),
            extra=(
                f"qid={question['id']}|"
                f"correct={question['correct_index']}|"
                f"is_correct={is_correct}"
            ),
        )

        self.current_question_idx += 1
        if self.current_question_idx >= len(self.quiz_questions):
            self.show_break()
        else:
            self._display_question()

    # ==================================================================
    #   STATE: BREAK
    # ==================================================================

    def show_break(self):
        """Display a rest screen between blocks (or after the last block).

        The "Continue" button determines what comes next:
            - If more blocks remain, advance to INSTRUCTIONS for the next passage.
            - If all blocks are done, advance to ACCEPTABILITY_QUESTIONNAIRE.
        """
        self.clear_content()
        self.state = "BREAK"

        frame = tk.Frame(self.content_frame, padx=40, pady=40)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="Take a Short Break",
            font=(FONT_FAMILY, 18, "bold"),
        ).pack(pady=(0, 20))

        is_last_block = self.current_block >= len(self.passage_order) - 1

        if is_last_block:
            msg = (
                "You have completed both reading blocks.\n\n"
                "After you click Continue, there will be a short\n"
                "questionnaire about your experience.\n\n"
                "Thank you for your participation so far."
            )
        else:
            msg = (
                "You have finished the first reading block.\n\n"
                "When you are ready, click Continue to begin the\n"
                "second reading passage."
            )

        tk.Label(
            frame,
            text=msg,
            font=(FONT_FAMILY, 14),
            wraplength=600,
            justify=tk.LEFT,
        ).pack(pady=(0, 30))

        tk.Button(
            frame,
            text="Continue",
            font=(FONT_FAMILY, 14),
            command=self._on_break_continue,
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
        ).pack()

    def _on_break_continue(self):
        """Advance to the next block or to the questionnaire."""
        is_last_block = self.current_block >= len(self.passage_order) - 1
        if is_last_block:
            self.show_questionnaire()
        else:
            self.current_block += 1
            self.show_instructions()

    # ==================================================================
    #   STATE: ACCEPTABILITY_QUESTIONNAIRE
    # ==================================================================

    def show_questionnaire(self):
        """Display the post-session Likert-scale questionnaire.

        All items are shown on one scrollable page.  Each item uses a
        1\u20135 radio-button scale.  A "Submit" button validates that all
        items are answered before transitioning to END.
        """
        self.clear_content()
        self.state = "ACCEPTABILITY_QUESTIONNAIRE"

        # Outer canvas + scrollbar so the whole form fits on smaller screens
        canvas = tk.Canvas(self.content_frame)
        scrollbar = tk.Scrollbar(
            self.content_frame, orient=tk.VERTICAL, command=canvas.yview
        )
        scrollable = tk.Frame(canvas)

        scrollable.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # -- Title --
        tk.Label(
            scrollable,
            text="Post-Session Questionnaire",
            font=(FONT_FAMILY, 18, "bold"),
        ).pack(pady=(30, 10), padx=40, anchor=tk.W)

        # -- Likert-scale legend --
        legend_frame = tk.Frame(scrollable)
        legend_frame.pack(pady=(0, 20), padx=40, anchor=tk.W)
        tk.Label(
            legend_frame,
            text="Scale:  1 = Not at all  |  2 = Slightly  |  "
            "3 = Moderately  |  4 = Very  |  5 = Extremely",
            font=(FONT_FAMILY, 11),
            fg="gray",
        ).pack()

        # -- Items --
        self.questionnaire_vars = []
        for idx, item_text in enumerate(QUESTIONNAIRE_ITEMS):
            item_frame = tk.Frame(
                scrollable, relief=tk.GROOVE, bd=1, padx=15, pady=12
            )
            item_frame.pack(fill=tk.X, padx=40, pady=6)

            tk.Label(
                item_frame,
                text=item_text,
                font=(FONT_FAMILY, 13),
                wraplength=700,
                justify=tk.LEFT,
            ).pack(anchor=tk.W)

            var = tk.IntVar(value=-1)
            self.questionnaire_vars.append(var)

            scale_frame = tk.Frame(item_frame)
            scale_frame.pack(anchor=tk.W, pady=(8, 0))
            for scale_val in range(1, 6):
                tk.Radiobutton(
                    scale_frame,
                    text=str(scale_val),
                    variable=var,
                    value=scale_val,
                    font=(FONT_FAMILY, 12),
                ).pack(side=tk.LEFT, padx=(0, 10))

        # -- Submit --
        def submit_questionnaire():
            for idx, var in enumerate(self.questionnaire_vars):
                val = var.get()
                if val < 1:
                    messagebox.showwarning(
                        "Incomplete",
                        f"Please answer question {idx + 1}.",
                    )
                    return
            # Log all answers
            for idx, var in enumerate(self.questionnaire_vars):
                self.log_event(
                    "QUESTIONNAIRE_ANSWER",
                    value=str(var.get()),
                    extra=f"item={idx}|text={QUESTIONNAIRE_ITEMS[idx]}",
                )
            self.show_end()

        submit_frame = tk.Frame(scrollable)
        submit_frame.pack(fill=tk.X, pady=30, padx=40)
        tk.Button(
            submit_frame,
            text="Submit Questionnaire",
            font=(FONT_FAMILY, 14),
            command=submit_questionnaire,
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=10,
        ).pack()

    # ==================================================================
    #   STATE: END
    # ==================================================================

    def show_end(self):
        """Display the thank-you screen with the data file location.

        Logs SESSION_END and flushes/closes the CSV file.
        """
        self.log_event("SESSION_END")
        self.cleanup()  # close CSV file

        self.clear_content()
        self.state = "END"

        frame = tk.Frame(self.content_frame, padx=40, pady=40)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="Session Complete",
            font=(FONT_FAMILY, 20, "bold"),
            fg="#4CAF50",
        ).pack(pady=(0, 20))

        tk.Label(
            frame,
            text="Thank you for your participation.",
            font=(FONT_FAMILY, 16),
        ).pack(pady=(0, 30))

        tk.Label(
            frame,
            text="Data File Location:",
            font=(FONT_FAMILY, 12, "bold"),
        ).pack()

        # Show the data file path in a selectable text widget
        path_text = tk.Text(frame, height=2, width=60, font=(FONT_FAMILY, 11))
        path_text.insert(tk.END, self.data_file_path or "N/A")
        path_text.config(state=tk.DISABLED)
        path_text.pack(pady=(5, 30))

        tk.Button(
            frame,
            text="Close",
            font=(FONT_FAMILY, 14),
            command=self.root.destroy,
            bg="#F44336",
            fg="white",
            padx=30,
            pady=10,
        ).pack()

    # ==================================================================
    #   ENTRY POINT
    # ==================================================================

    def run(self):
        """Start the tkinter main loop."""
        self.root.mainloop()


def main():
    """Parse arguments and launch the application."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
