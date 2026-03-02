"""
Auto-Update System for Reminder Manager
Checks for updates from a remote JSON endpoint on startup.
"""

import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk
import urllib.request
import urllib.error
import tempfile
import subprocess

# ── Version Configuration ──────────────────────────────────────────────────────
CURRENT_VERSION = "1.0.0"
UPDATE_CHECK_URL = "https://myserver.com/reminder/version.json"
# Example JSON at that URL:
# {
#   "version": "2.1.0",
#   "installer_url": "https://myserver.com/reminder/ReminderManagerSetup.exe",
#   "release_notes": "Bug fixes and performance improvements."
# }

# ── Version Comparison ─────────────────────────────────────────────────────────

def parse_version(v: str):
    """Convert '2.1.0' → (2, 1, 0) for comparison."""
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except ValueError:
        return (0,)

def is_newer(remote: str, current: str) -> bool:
    return parse_version(remote) > parse_version(current)

# ── Network Fetch ──────────────────────────────────────────────────────────────

def fetch_version_info(url: str, timeout: int = 5) -> dict | None:
    """Fetch version JSON from remote URL. Returns dict or None on failure."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"ReminderManager/{CURRENT_VERSION}"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None

# ── Download with Progress ─────────────────────────────────────────────────────

def download_installer(url: str, dest_path: str, progress_callback=None) -> bool:
    """
    Download installer to dest_path.
    progress_callback(percent: int) called periodically.
    Returns True on success.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"ReminderManager/{CURRENT_VERSION}"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk = 8192
            with open(dest_path, "wb") as f:
                while True:
                    block = resp.read(chunk)
                    if not block:
                        break
                    f.write(block)
                    downloaded += len(block)
                    if progress_callback and total:
                        progress_callback(int(downloaded * 100 / total))
        return True
    except (urllib.error.URLError, OSError):
        return False

# ── Update Popup ───────────────────────────────────────────────────────────────

class UpdateDialog(tk.Toplevel):
    """Modal dialog shown when a new version is available."""

    def __init__(self, parent, version_info: dict):
        super().__init__(parent)
        self.version_info = version_info
        self.title("Update Available")
        self.resizable(False, False)
        self.configure(bg="#0f0f1a")
        self.grab_set()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_skip)
        self._center(parent)
        self.lift()
        self.attributes("-topmost", True)

    def _center(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w)//2}+{py + (ph - h)//2}")

    def _build_ui(self):
        remote_ver = self.version_info.get("version", "?")
        notes = self.version_info.get("release_notes", "")

        pad = dict(padx=20, pady=8)

        tk.Label(self, text="🔔  Update Available",
                 font=("Courier New", 14, "bold"),
                 fg="#e94560", bg="#0f0f1a").pack(**pad, pady=(20, 4))

        tk.Label(self, text=f"Version {CURRENT_VERSION}  →  {remote_ver}",
                 font=("Courier New", 10),
                 fg="#aaaacc", bg="#0f0f1a").pack(**pad, pady=0)

        if notes:
            tk.Label(self, text=notes,
                     font=("Courier New", 9),
                     fg="#777799", bg="#0f0f1a",
                     wraplength=340, justify="left").pack(**pad)

        # Progress bar (hidden initially)
        self._progress_frame = tk.Frame(self, bg="#0f0f1a")
        self._progress_var = tk.IntVar(value=0)
        self._progress_bar = ttk.Progressbar(
            self._progress_frame,
            variable=self._progress_var,
            maximum=100, length=340
        )
        self._progress_label = tk.Label(
            self._progress_frame, text="Downloading…",
            font=("Courier New", 8), fg="#aaaacc", bg="#0f0f1a"
        )

        # Buttons
        btn_frame = tk.Frame(self, bg="#0f0f1a")
        btn_frame.pack(padx=20, pady=(12, 20), fill="x")

        self._install_btn = tk.Button(
            btn_frame, text="Download & Install",
            font=("Courier New", 10, "bold"),
            bg="#e94560", fg="#ffffff",
            activebackground="#c73350", activeforeground="#ffffff",
            relief="flat", cursor="hand2",
            command=self._on_install
        )
        self._install_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            btn_frame, text="Skip",
            font=("Courier New", 10),
            bg="#1a1a2e", fg="#aaaacc",
            activebackground="#252540", activeforeground="#ffffff",
            relief="flat", cursor="hand2",
            command=self._on_skip
        ).pack(side="left")

    def _on_install(self):
        url = self.version_info.get("installer_url", "")
        if not url:
            return
        self._install_btn.config(state="disabled", text="Downloading…")

        # Show progress bar
        self._progress_frame.pack(padx=20, pady=(0, 12), fill="x")
        self._progress_bar.pack(fill="x")
        self._progress_label.pack()

        threading.Thread(target=self._download_and_run, args=(url,), daemon=True).start()

    def _download_and_run(self, url: str):
        dest = os.path.join(tempfile.gettempdir(), "ReminderManagerSetup.exe")

        def on_progress(pct):
            self._progress_var.set(pct)
            self._progress_label.config(text=f"Downloading… {pct}%")

        ok = download_installer(url, dest, progress_callback=on_progress)

        if ok:
            self._progress_label.config(text="Launching installer…")
            self.after(500, lambda: self._launch_installer(dest))
        else:
            self._progress_label.config(text="Download failed. Check your connection.")
            self._install_btn.config(state="normal", text="Retry")

    def _launch_installer(self, path: str):
        try:
            # Launch installer, then exit app so installer can replace files
            subprocess.Popen([path], shell=False)
            self.master.destroy()
        except OSError as e:
            self._progress_label.config(text=f"Failed to launch: {e}")

    def _on_skip(self):
        self.destroy()


# ── Public API ─────────────────────────────────────────────────────────────────

def check_for_updates_async(parent_window: tk.Tk, url: str = UPDATE_CHECK_URL):
    """
    Call this once after the main window is ready.
    Runs the network check in a background thread; shows dialog on the Tk thread.
    """
    def _worker():
        info = fetch_version_info(url)
        if info and is_newer(info.get("version", "0"), CURRENT_VERSION):
            # Schedule dialog on main Tk thread
            parent_window.after(0, lambda: _show_dialog(info))

    def _show_dialog(info):
        try:
            UpdateDialog(parent_window, info)
        except tk.TclError:
            pass  # Window was destroyed before dialog could open

    threading.Thread(target=_worker, daemon=True).start()
