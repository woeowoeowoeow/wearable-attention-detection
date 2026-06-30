import time
import csv
import tkinter as tk
from datetime import datetime
from pathlib import Path

try:
    import winsound
    _HAVE_WINSOUND = True
except ImportError:
    _HAVE_WINSOUND = False

PHASES = [
    {"name": "True Baseline", "duration_sec": 300, "instruction": "Sit still. Don't think about the task."},
    {"name": "Rest", "duration_sec": 180, "instruction": "Sit quietly."},
    {"name": "Mental Arithmetic", "duration_sec": 180, "instruction": "Count backwards from 200 by 7s, silently."},
    {"name": "Rest/Recovery", "duration_sec": 180, "instruction": "Sit quietly."},
    {"name": "Mind-Wandering", "duration_sec": 180, "instruction": "Let your mind drift on purpose."},
    {"name": "Deliberate Movement", "duration_sec": 60, "instruction": "Move your wrist/arm around."},
    {"name": "Final Rest", "duration_sec": 120, "instruction": "Sit still."},
]

LOGS_DIR = Path(__file__).parent / "logs"


class SessionTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Session Timer")
        self.root.geometry("400x250")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        container = tk.Frame(self.root)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)

        self.phase_label = tk.Label(container, text="", font=("Segoe UI", 16, "bold"))
        self.phase_label.grid(row=0, column=0, pady=(30, 5))

        self.instruction_label = tk.Label(container, text="", font=("Segoe UI", 12), wraplength=360)
        self.instruction_label.grid(row=1, column=0, pady=5)

        self.countdown_label = tk.Label(container, text="", font=("Segoe UI", 36, "bold"))
        self.countdown_label.grid(row=2, column=0, pady=(10, 5))

        self.complete_label = tk.Label(container, text="", font=("Segoe UI", 20, "bold"), fg="green")
        self.complete_label.grid(row=0, column=0, pady=(30, 5))
        self.complete_label.grid_remove()

        self.phase_index = 0
        self.phase_start_time = 0.0
        self._running = True
        self._show_timer = False
        self._countdown_after_id = None
        self._phase_after_id = None

        self._setup_logging()
        self._setup_hotkey()
        self._start_session()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_logging(self):
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._csv_path = LOGS_DIR / f"session_{timestamp}.csv"
        self._log_file = open(self._csv_path, "w", newline="")
        self._csv_writer = csv.writer(self._log_file)
        self._csv_writer.writerow(["event_timestamp_ms", "phase_name", "phase_index", "event_type"])
        self._log_file.flush()

    def _beep(self, frequency=880, duration=200):
        if _HAVE_WINSOUND:
            winsound.Beep(frequency, duration)
        else:
            print("\a", end="", flush=True)

    def _log_event(self, phase_name, phase_index, event_type):
        ts = int(time.time() * 1000)
        self._csv_writer.writerow([ts, phase_name, phase_index, event_type])
        self._log_file.flush()

    def _start_session(self):
        self._start_phase(0)

    def _start_phase(self, index):
        if index >= len(PHASES):
            self._end_session()
            return

        phase = PHASES[index]
        self.phase_index = index
        self.phase_start_time = time.time()

        self._log_event(phase["name"], index, "phase_start")
        self._beep(880, 200)

        self.phase_label.config(text=f"Phase {index + 1}: {phase['name']}")
        self.instruction_label.config(text=phase["instruction"])
        self.complete_label.grid_remove()
        self.phase_label.grid()
        self.instruction_label.grid()
        self._apply_timer_visibility()

        duration_ms = phase["duration_sec"] * 1000
        self._phase_after_id = self.root.after(duration_ms, lambda: self._start_phase(index + 1))

        self._schedule_countdown()

    def _schedule_countdown(self):
        if not self._running:
            return
        self._update_display()
        self._countdown_after_id = self.root.after(250, self._schedule_countdown)

    def _update_display(self):
        if self.phase_index >= len(PHASES):
            return
        phase = PHASES[self.phase_index]
        elapsed = time.time() - self.phase_start_time
        remaining = max(0, phase["duration_sec"] - int(elapsed))
        minutes = remaining // 60
        seconds = remaining % 60
        self.countdown_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def _end_session(self):
        self._running = False

        if self._countdown_after_id:
            self.root.after_cancel(self._countdown_after_id)
            self._countdown_after_id = None
        if self._phase_after_id:
            self.root.after_cancel(self._phase_after_id)
            self._phase_after_id = None

        self._log_event("", len(PHASES), "session_end")
        self._beep(440, 300)
        time.sleep(0.15)
        self._beep(660, 300)
        time.sleep(0.15)
        self._beep(880, 400)

        self.phase_label.grid_remove()
        self.instruction_label.grid_remove()
        self.countdown_label.config(text="")
        self.complete_label.config(text="Session Complete!")
        self.complete_label.grid()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _toggle_visibility(self):
        self.root.after(0, self._do_toggle_visibility)

    def _do_toggle_visibility(self):
        if not self._running:
            return
        try:
            if self.root.state() == "withdrawn" or not self.root.winfo_viewable():
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
            else:
                self.root.withdraw()
        except tk.TclError:
            self.root.deiconify()

    def _apply_timer_visibility(self):
        if self._show_timer:
            self.countdown_label.grid()
        else:
            self.countdown_label.grid_remove()

    def _toggle_timer(self):
        self.root.after(0, self._do_toggle_timer)

    def _do_toggle_timer(self):
        if not self._running:
            return
        self._show_timer = not self._show_timer
        self._apply_timer_visibility()

    def _setup_hotkey(self):
        try:
            import keyboard
            keyboard.add_hotkey("ctrl+shift+t", self._toggle_visibility, suppress=False)
            keyboard.add_hotkey("ctrl+shift+h", self._toggle_timer, suppress=False)
        except Exception:
            pass

    def _on_close(self):
        self._running = False
        if self._countdown_after_id:
            self.root.after_cancel(self._countdown_after_id)
        if self._phase_after_id:
            self.root.after_cancel(self._phase_after_id)
        if hasattr(self, "_log_file"):
            self._log_file.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SessionTimer()
    app.run()
