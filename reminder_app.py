"""
Desktop Reminder Application for Windows
Requires: pip install schedule
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import datetime
import json
import os
import uuid
import math
import base64
import winsound
import schedule


# ─── Data File ───────────────────────────────────────────────────────────────
def _get_data_file():
    """Return path to reminders.json.
    When installed, uses %APPDATA%/Reminder Manager/ so writes do not need admin rights.
    When running from source, use the script's own directory."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        data_dir = os.path.join(appdata, "Reminder Manager")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "reminders.json")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "reminders.json")

DATA_FILE = _get_data_file()

def load_reminders():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_reminders(reminders):
    with open(DATA_FILE, "w") as f:
        json.dump(reminders, f, indent=2)


# ─── App Icon (embedded PNG) ──────────────────────────────────────────────────
_ICON_B64 = """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"""

def _make_icon(root):
    """Create a PhotoImage from the embedded base64 PNG and apply to window."""
    try:
        import base64 as _b64, io
        data = _b64.b64decode(_ICON_B64)
        from PIL import Image, ImageTk
        img  = Image.open(io.BytesIO(data))
        icon = ImageTk.PhotoImage(img)
        root.iconphoto(True, icon)
        return icon          # must keep reference alive
    except Exception:
        pass                 # Pillow absent or any error — skip icon silently
    return None


# ─── System Tray Manager ─────────────────────────────────────────────────────
class SystemTrayManager:
    """
    Manages the pystray system tray icon on a dedicated daemon thread.

    Architecture:
      • The tray icon runs in its own thread (pystray requirement).
      • All Tkinter calls are marshalled back to the main thread via
        root.after(0, ...) — Tkinter is NOT thread-safe.
      • The scheduler also runs on the main Tkinter thread via root.after(),
        so reminder popups always appear on the correct thread.

    Graceful degradation:
      If pystray or Pillow is unavailable the tray silently won't appear;
      the application falls back to minimising to the taskbar instead.
      Install with:  pip install pystray pillow
    """

    def __init__(self, app):
        self._app        = app          # ReminderApp instance
        self._tray       = None
        self._available  = False
        self._thread     = None

    # ── Build and start ───────────────────────────────────────────────────────
    def start(self):
        try:
            import pystray
            from PIL import Image as PILImage
        except ImportError:
            return   # graceful degradation — no tray icon

        try:
            tray_img = self._build_tray_image()
            menu = pystray.Menu(
                pystray.MenuItem(
                    "⏰  Open Reminder Manager",
                    self._on_open,
                    default=True          # double-click action
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self._on_exit),
            )
            self._tray = pystray.Icon(
                "ReminderManager",
                tray_img,
                "Reminder Manager",
                menu
            )
            self._available = True
            self._thread = threading.Thread(
                target=self._tray.run,
                daemon=True,
                name="TrayThread"
            )
            self._thread.start()
        except Exception:
            self._available = False

    def stop(self):
        if self._tray and self._available:
            try:
                self._tray.stop()
            except Exception:
                pass

    @property
    def available(self):
        return self._available

    # ── Menu callbacks (called from tray thread → marshal to Tk thread) ───────
    def _on_open(self, icon=None, item=None):
        """Show and raise the main window."""
        self._app.root.after(0, self._app.show_window)

    def _on_exit(self, icon=None, item=None):
        """Fully quit the application."""
        self._app.root.after(0, self._app.quit_app)

    # ── Build a 64×64 tray image from the embedded icon PNG ───────────────────
    def _build_tray_image(self):
        """Return a PIL Image for the tray icon."""
        import io as _io
        from PIL import Image as PILImage
        data = base64.b64decode(_ICON_B64)
        img  = PILImage.open(_io.BytesIO(data)).resize((64, 64), PILImage.LANCZOS)
        return img.convert("RGBA")

    # ── Notification balloon (Windows only) ───────────────────────────────────
    def notify(self, title, message):
        """Show a tray balloon notification if supported."""
        if self._tray and self._available:
            try:
                self._tray.notify(message, title)
            except Exception:
                pass


# ─── Sound Alert ─────────────────────────────────────────────────────────────
def play_alert_sound():
    def _play():
        for _ in range(3):
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            time.sleep(0.45)
    threading.Thread(target=_play, daemon=True).start()


# ─── Spinner Widget ───────────────────────────────────────────────────────────
class Spinner(tk.Frame):
    def __init__(self, parent, min_val, max_val, initial=0, width=3, bg="#0f0f1a", **kw):
        super().__init__(parent, bg=bg, **kw)
        self.min_val = min_val
        self.max_val = max_val
        self._val = initial
        btn = dict(font=("Courier New", 8, "bold"), bg="#e94560", fg="#ffffff",
                   activebackground="#c73652", activeforeground="#ffffff",
                   relief="flat", cursor="hand2", bd=0)
        tk.Button(self, text="  ▲  ", command=self._inc, **btn).grid(row=0, column=1, padx=(3,0), pady=(0,2))
        self.disp = tk.Label(self, text=f"{self._val:02d}", font=("Courier New", 16, "bold"),
                             fg="#ffffff", bg="#1a1a2e", width=width, anchor="center",
                             relief="flat", padx=8, pady=6)
        self.disp.grid(row=0, column=0, rowspan=2)
        tk.Button(self, text="  ▼  ", command=self._dec, **btn).grid(row=1, column=1, padx=(3,0), pady=(2,0))
        self.disp.bind("<MouseWheel>", lambda e: self._inc() if e.delta > 0 else self._dec())
        self.bind("<MouseWheel>",      lambda e: self._inc() if e.delta > 0 else self._dec())

    def _refresh(self):
        self.disp.config(text=f"{self._val:02d}")
        self.event_generate("<<SpinnerChanged>>")

    def _inc(self):
        self._val = self.min_val if self._val >= self.max_val else self._val + 1
        self._refresh()

    def _dec(self):
        self._val = self.max_val if self._val <= self.min_val else self._val - 1
        self._refresh()

    def get(self): return self._val
    def set(self, val):
        self._val = int(val)
        self._refresh()


# ─── Analog Clock Picker ──────────────────────────────────────────────────────
class AnalogClockPicker(tk.Frame):
    """
    Material-Design-style analog clock picker drawn on a tk.Canvas.

    Geometry:
      • 12 o'clock is at angle -π/2 (pointing straight up).
      • Each hour is 360/12 = 30° apart clockwise.
      • Hour h occupies angle:  a = (h/12)*2π - π/2
        So h=1 → 0°(right + 30° = 30° from top) which is correct.
      • Each minute tick is 6° apart.

    Interaction:
      • Click/drag on the face → snap to nearest hour or minute.
      • Release after selecting hour → auto-advance to minute mode.
      • Click the hour label (top-left of display) → switch to hour mode.
      • Click the minute label (top-right) → switch to minute mode.
      • AM / PM buttons below the display.

    Public API:
      get_hour()         → int, 0-23
      get_minute()       → int, 0-59
      set_time(h24, m)   → update both and redraw
      on_change          → callback(hour24, minute)
    """

    # Layout
    SIZE   = 220
    RADIUS = 90
    CX, CY = SIZE // 2, SIZE // 2

    # Palette
    C_BG       = "#0f0f1a"
    C_FACE     = "#1a1a2e"
    C_RIM      = "#2a2a4e"
    C_HAND     = "#e94560"
    C_DOT      = "#e94560"
    C_NUM      = "#ccccdd"
    C_SEL_BG   = "#e94560"
    C_SEL_FG   = "#ffffff"
    C_TICK     = "#3a3a5a"
    C_AMPM_ON  = "#e94560"
    C_AMPM_OFF = "#222244"
    C_DISP_ON  = "#e94560"
    C_DISP_OFF = "#555566"

    def __init__(self, parent, hour24=None, minute=None, on_change=None, **kw):
        super().__init__(parent, bg=self.C_BG, **kw)
        now = datetime.datetime.now()
        self._h24      = (hour24  if hour24  is not None else now.hour)
        self._min      = (minute  if minute  is not None else now.minute)
        self._ampm     = "AM" if self._h24 < 12 else "PM"
        self._mode     = "hour"   # "hour" | "minute"
        self._dragging = False
        self.on_change = on_change
        self._build()

    # ─────────────────────────────── BUILD ───────────────────────────────────
    def _build(self):
        # ── Digital time display ─────────────────────────────────────────────
        top = tk.Frame(self, bg=self.C_BG)
        top.pack(pady=(10, 4))

        self._hl = tk.Label(top, font=("Courier New", 26, "bold"),
                            padx=10, pady=4, cursor="hand2", bg=self.C_BG)
        self._hl.pack(side="left")
        self._hl.bind("<Button-1>", lambda e: self._set_mode("hour"))

        tk.Label(top, text=":", font=("Courier New", 26, "bold"),
                 fg="#444466", bg=self.C_BG).pack(side="left")

        self._ml = tk.Label(top, font=("Courier New", 26, "bold"),
                            padx=10, pady=4, cursor="hand2", bg=self.C_BG)
        self._ml.pack(side="left")
        self._ml.bind("<Button-1>", lambda e: self._set_mode("minute"))

        # ── AM / PM row ──────────────────────────────────────────────────────
        ap = tk.Frame(self, bg=self.C_BG)
        ap.pack(pady=(0, 8))
        self._am_btn = tk.Label(ap, text="AM", font=("Courier New", 9, "bold"),
                                padx=16, pady=5, cursor="hand2")
        self._am_btn.pack(side="left", padx=2)
        self._am_btn.bind("<Button-1>", lambda e: self._set_ampm("AM"))

        self._pm_btn = tk.Label(ap, text="PM", font=("Courier New", 9, "bold"),
                                padx=16, pady=5, cursor="hand2")
        self._pm_btn.pack(side="left", padx=2)
        self._pm_btn.bind("<Button-1>", lambda e: self._set_ampm("PM"))

        # ── Canvas clock face ────────────────────────────────────────────────
        self._cv = tk.Canvas(self, width=self.SIZE, height=self.SIZE,
                             bg=self.C_BG, highlightthickness=0)
        self._cv.pack(padx=8, pady=(0, 10))
        self._cv.bind("<Button-1>",        self._on_press)
        self._cv.bind("<B1-Motion>",       self._on_drag)
        self._cv.bind("<ButtonRelease-1>", self._on_release)

        # ── Mode label at very bottom ────────────────────────────────────────
        self._mode_lbl = tk.Label(self, font=("Courier New", 7),
                                  fg="#444466", bg=self.C_BG)
        self._mode_lbl.pack(pady=(0, 6))

        self._refresh_all()

    # ─────────────────────────────── DRAWING ─────────────────────────────────
    def _angle(self, value, total):
        """Convert value (0-based) out of total steps to canvas angle in radians.
        0 steps = 12 o'clock = -π/2 from the x-axis."""
        return (value / total) * 2 * math.pi - math.pi / 2

    def _rim_xy(self, value, total, radius):
        """Canvas x,y of a value marker on the clock rim."""
        a = self._angle(value, total)
        return (self.CX + radius * math.cos(a),
                self.CY + radius * math.sin(a))

    def _draw(self):
        cv = self._cv
        cv.delete("all")
        R  = self.RADIUS
        cx, cy = self.CX, self.CY

        # Clock face circle
        cv.create_oval(cx-R, cy-R, cx+R, cy+R,
                       fill=self.C_FACE, outline=self.C_RIM, width=2)

        if self._mode == "hour":
            self._draw_hours(cv, cx, cy, R)
        else:
            self._draw_minutes(cv, cx, cy, R)

        # Hand from centre to selected position
        if self._mode == "hour":
            h12 = self._h24 % 12   # 0-11, where 0 means 12
            hx, hy = self._rim_xy(h12 if h12 != 0 else 12, 12, R - 20)
        else:
            mx, my = self._rim_xy(self._min, 60, R - 20)
            hx, hy = mx, my

        cv.create_line(cx, cy, hx, hy, fill=self.C_HAND, width=2, capstyle="round")

        # Selection circle at hand tip
        r_dot = 14
        cv.create_oval(hx - r_dot, hy - r_dot, hx + r_dot, hy + r_dot,
                       fill=self.C_SEL_BG, outline="")

        # Label inside the selection circle
        if self._mode == "hour":
            tip_txt = str(self._h24 % 12 or 12)
        else:
            tip_txt = f"{self._min:02d}"
        cv.create_text(hx, hy, text=tip_txt,
                       font=("Courier New", 9, "bold"), fill=self.C_SEL_FG)

        # Centre dot
        cv.create_oval(cx-4, cy-4, cx+4, cy+4, fill=self.C_DOT, outline="")

    def _draw_hours(self, cv, cx, cy, R):
        nr = R - 22   # number ring radius
        for h in range(1, 13):
            # h=1 is 30° clockwise from 12, h=12 is at 12 o'clock
            # Use h directly as "h steps out of 12" from top
            hx, hy = self._rim_xy(h, 12, nr)
            is_sel = ((self._h24 % 12 or 12) == h)
            if is_sel:
                cv.create_oval(hx-13, hy-13, hx+13, hy+13,
                               fill=self.C_SEL_BG, outline="")
            cv.create_text(hx, hy, text=str(h),
                           font=("Courier New", 10, "bold"),
                           fill=self.C_SEL_FG if is_sel else self.C_NUM)

    def _draw_minutes(self, cv, cx, cy, R):
        nr = R - 22
        # Labelled marks every 5 minutes
        for m in range(0, 60, 5):
            mx, my = self._rim_xy(m, 60, nr)
            is_sel = (self._min == m)
            if is_sel:
                cv.create_oval(mx-13, my-13, mx+13, my+13,
                               fill=self.C_SEL_BG, outline="")
            cv.create_text(mx, my, text=f"{m:02d}",
                           font=("Courier New", 9, "bold"),
                           fill=self.C_SEL_FG if is_sel else self.C_NUM)

        # Tick marks for non-labelled minutes
        for m in range(60):
            if m % 5 == 0:
                continue
            a  = self._angle(m, 60)
            r1 = R - 6
            r2 = R - 12
            cv.create_line(cx + r1*math.cos(a), cy + r1*math.sin(a),
                           cx + r2*math.cos(a), cy + r2*math.sin(a),
                           fill=self.C_TICK, width=1)

    # ─────────────────────────────── REFRESH ─────────────────────────────────
    def _refresh_all(self):
        self._refresh_display_labels()
        self._refresh_ampm_ui()
        self._draw()
        mode_txt = "SELECT HOUR" if self._mode == "hour" else "SELECT MINUTE"
        self._mode_lbl.config(text=mode_txt)

    def _refresh_display_labels(self):
        h12 = self._h24 % 12 or 12
        self._hl.config(
            text=f"{h12:02d}",
            fg=self.C_DISP_ON  if self._mode == "hour" else self.C_DISP_OFF,
            bg="#1a1a2e"       if self._mode == "hour" else self.C_BG)
        self._ml.config(
            text=f"{self._min:02d}",
            fg=self.C_DISP_ON  if self._mode == "minute" else self.C_DISP_OFF,
            bg="#1a1a2e"       if self._mode == "minute" else self.C_BG)

    def _refresh_ampm_ui(self):
        for btn, label in ((self._am_btn, "AM"), (self._pm_btn, "PM")):
            on = (self._ampm == label)
            btn.config(bg=self.C_AMPM_ON  if on else self.C_AMPM_OFF,
                       fg="#ffffff"        if on else "#666688")

    # ─────────────────────────────── STATE CHANGES ───────────────────────────
    def _set_mode(self, mode):
        self._mode = mode
        self._refresh_all()

    def _set_ampm(self, ampm):
        if self._ampm == ampm:
            return
        self._ampm = ampm
        h12 = self._h24 % 12 or 12
        self._h24 = (h12 % 12) if ampm == "AM" else (h12 % 12 + 12)
        self._refresh_all()
        self._notify()

    def _apply_click(self, x, y):
        """Convert canvas click coordinates to hour or minute and apply."""
        dx = x - self.CX
        dy = y - self.CY
        # atan2 from positive-x axis; add π/2 to rotate so 0 = top
        a = math.atan2(dy, dx) + math.pi / 2
        if a < 0:
            a += 2 * math.pi

        if self._mode == "hour":
            # Snap to nearest of 12 positions
            h = round(a / (2 * math.pi) * 12) % 12
            h12 = h if h != 0 else 12   # 0 → 12
            self._h24 = (h12 % 12) if self._ampm == "AM" else (h12 % 12 + 12)
        else:
            # Snap to nearest of 60 positions
            self._min = round(a / (2 * math.pi) * 60) % 60

        self._refresh_all()
        self._notify()

    # ─────────────────────────────── EVENTS ──────────────────────────────────
    def _on_press(self, e):
        self._dragging = False
        self._apply_click(e.x, e.y)

    def _on_drag(self, e):
        self._dragging = True
        self._apply_click(e.x, e.y)

    def _on_release(self, e):
        # Auto-advance hour → minute only on a clean click (not end of drag)
        if self._mode == "hour" and not self._dragging:
            self._set_mode("minute")
        self._dragging = False

    def _notify(self):
        if self.on_change:
            self.on_change(self._h24, self._min)

    # ─────────────────────────────── PUBLIC API ───────────────────────────────
    def get_hour(self):   return self._h24
    def get_minute(self): return self._min

    def set_time(self, h24, m):
        self._h24  = int(h24)
        self._min  = int(m)
        self._ampm = "AM" if self._h24 < 12 else "PM"
        self._refresh_all()


# ─── Reminder Popup ──────────────────────────────────────────────────────────
class ReminderPopup:
    """
    Always-on-top popup.
    -topmost set once; no lift(), no focus_force(), no polling.
    Postpone section uses an AnalogClockPicker to select the new time.
    """

    def __init__(self, reminder, on_close_callback):
        self.reminder          = reminder
        self.on_close_callback = on_close_callback
        self._destroyed        = False
        self._postpone_time    = None   # (h24, minute) tuple

        self.root = tk.Toplevel()
        self.root.withdraw()
        self._build_ui()
        self.root.deiconify()
        self.root.update_idletasks()
        self.root.attributes("-topmost", True)
        self.root.after(200, lambda: self.remark_text.focus_set())
        play_alert_sound()

    # ─────────────────────────────── BUILD ───────────────────────────────────
    def _build_ui(self):
        r = self.root
        r.title("⏰ Reminder Alert")
        r.configure(bg="#0f0f1a")
        r.resizable(False, False)
        r.protocol("WM_DELETE_WINDOW", self._try_close)

        # Tall enough for the clock when postpone is visible
        W, H = 580, 720
        r.geometry(f"{W}x{H}+{(r.winfo_screenwidth()-W)//2}+{(r.winfo_screenheight()-H)//2}")

        # ── Header ──────────────────────────────────────────────────────────
        hdr = tk.Frame(r, bg="#1a1a2e", height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  ⏰  REMINDER ALERT",
                 font=("Courier New", 14, "bold"),
                 fg="#e94560", bg="#1a1a2e").pack(side="left", padx=20, pady=16)
        tk.Label(hdr, text=datetime.datetime.now().strftime("%H:%M  ·  %d %b %Y"),
                 font=("Courier New", 10), fg="#555577",
                 bg="#1a1a2e").pack(side="right", padx=20)

        # ── Scrollable body ──────────────────────────────────────────────────
        cv = tk.Canvas(r, bg="#0f0f1a", highlightthickness=0)
        sb = ttk.Scrollbar(r, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(fill="both", expand=True)

        body = tk.Frame(cv, bg="#0f0f1a")
        bid  = cv.create_window((0, 0), window=body, anchor="nw")

        def _on_cfg(e):
            cv.configure(scrollregion=cv.bbox("all"))
            cv.itemconfig(bid, width=cv.winfo_width())
        body.bind("<Configure>", _on_cfg)
        cv.bind("<Configure>", lambda e: cv.itemconfig(bid, width=e.width))
        cv.bind_all("<MouseWheel>",
                    lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))

        inner = tk.Frame(body, bg="#0f0f1a")
        inner.pack(fill="both", expand=True, padx=26, pady=14)

        # Title
        tk.Label(inner, text=self.reminder.get("title", "Reminder"),
                 font=("Courier New", 17, "bold"), fg="#ffffff", bg="#0f0f1a",
                 wraplength=520, justify="left").pack(anchor="w")

        # Date + time line  e.g. "10 March 2026 – 14:30"
        raw_date = self.reminder.get("date", "")
        time_str = self.reminder.get("time", "--:--")
        if raw_date:
            try:
                dt_label = datetime.date.fromisoformat(raw_date).strftime("%-d %B %Y")
            except Exception:
                dt_label = raw_date
            date_time_str = f"{dt_label} – {time_str}"
        else:
            date_time_str = time_str
        tk.Label(inner, text=date_time_str,
                 font=("Courier New", 12), fg="#e94560", bg="#0f0f1a").pack(
                     anchor="w", pady=(3, 0))

        desc = self.reminder.get("description", "")
        if desc:
            tk.Label(inner, text=desc, font=("Courier New", 11),
                     fg="#9999bb", bg="#0f0f1a",
                     wraplength=520, justify="left").pack(anchor="w", pady=(4, 0))

        tk.Frame(inner, bg="#e94560", height=2).pack(fill="x", pady=12)

        # ── Remark ──────────────────────────────────────────────────────────
        tk.Label(inner, text="✏  Your Remark  (required before closing)",
                 font=("Courier New", 10, "bold"),
                 fg="#e94560", bg="#0f0f1a").pack(anchor="w")

        self.remark_border = tk.Frame(inner, bg="#333355", padx=2, pady=2)
        self.remark_border.pack(fill="x", pady=(5, 2))

        self.remark_text = tk.Text(
            self.remark_border,
            font=("Courier New", 11), bg="#12122a", fg="#e8e8f0",
            insertbackground="#e94560", selectbackground="#e94560",
            selectforeground="#ffffff", relief="flat",
            height=3, wrap="word", padx=10, pady=8,
            undo=True, takefocus=True)
        self.remark_text.pack(fill="x")
        # Border highlight — only colour change, no focus_set()
        self.remark_text.bind("<FocusIn>",
            lambda e: self.remark_border.config(bg="#e94560"))
        self.remark_text.bind("<FocusOut>",
            lambda e: self.remark_border.config(bg="#333355"))
        # Ctrl+Enter on the widget — NOT on the root window
        self.remark_text.bind("<Control-Return>",
            lambda e: self._try_close() or "break")

        tk.Label(inner, text="Ctrl+Enter to confirm",
                 font=("Courier New", 8), fg="#444466",
                 bg="#0f0f1a").pack(anchor="e", pady=(0, 8))

        # ── Postpone ────────────────────────────────────────────────────────
        pf = tk.Frame(inner, bg="#0f0f1a")
        pf.pack(fill="x", pady=(2, 0))

        self.postpone_var = tk.BooleanVar(value=False)
        tk.Checkbutton(pf, text="Postpone this reminder",
                       variable=self.postpone_var,
                       command=self._toggle_postpone,
                       font=("Courier New", 10), fg="#aaaacc", bg="#0f0f1a",
                       selectcolor="#1a1a2e", activebackground="#0f0f1a",
                       activeforeground="#ffffff", cursor="hand2").pack(anchor="w")

        # ── Postpone panel (hidden until checkbox ticked) ────────────────────
        self.postpone_panel = tk.Frame(inner, bg="#0f0f1a")
        # not packed yet

        # Divider
        tk.Frame(self.postpone_panel, bg="#2a2a4e", height=1).pack(fill="x", pady=(10, 8))

        tk.Label(self.postpone_panel, text="POSTPONE TO",
                 font=("Courier New", 8, "bold"),
                 fg="#444466", bg="#0f0f1a").pack(anchor="w")

        # Quick-pick row
        qrow = tk.Frame(self.postpone_panel, bg="#0f0f1a")
        qrow.pack(anchor="w", pady=(6, 8))

        for label, mins in [("+ 5 m", 5), ("+ 15 m", 15),
                             ("+ 30 m", 30), ("+ 1 h", 60), ("+ 2 h", 120)]:
            btn = tk.Button(qrow, text=label, font=("Courier New", 8, "bold"),
                            bg="#1c1c30", fg="#8888aa",
                            activebackground="#e94560", activeforeground="#ffffff",
                            relief="flat", cursor="hand2", padx=10, pady=5, bd=0,
                            highlightthickness=1, highlightbackground="#2a2a4e")
            btn.pack(side="left", padx=3)

            def _make(m):
                def _go():
                    t = datetime.datetime.now() + datetime.timedelta(minutes=m)
                    self.postpone_clock.set_time(t.hour, t.minute)
                    self._postpone_time = (t.hour, t.minute)
                return _go
            btn.config(command=_make(mins))

        # Analog clock for postpone time
        now       = datetime.datetime.now()
        post_h    = (now.hour + 1) % 24
        post_m    = now.minute
        self._postpone_time = (post_h, post_m)

        self.postpone_clock = AnalogClockPicker(
            self.postpone_panel,
            hour24=post_h, minute=post_m,
            on_change=self._on_postpone_clock)
        self.postpone_clock.pack(pady=(0, 6))

        # ── Confirm / Snooze row ─────────────────────────────────────────────
        bf = tk.Frame(r, bg="#0f0f1a")
        bf.pack(fill="x", padx=26, pady=(4, 16))

        tk.Button(bf, text="  CONFIRM  ✓  ",
                  command=self._try_close,
                  font=("Courier New", 12, "bold"),
                  bg="#e94560", fg="#ffffff",
                  activebackground="#c73652", activeforeground="#ffffff",
                  relief="flat", cursor="hand2", pady=10).pack(side="right")

        tk.Button(bf, text="  Snooze 5 min  💤  ",
                  command=self._snooze_5,
                  font=("Courier New", 10),
                  bg="#1c1c30", fg="#aaaacc",
                  activebackground="#2a2a4e", activeforeground="#ffffff",
                  relief="flat", cursor="hand2",
                  highlightthickness=1, highlightbackground="#2a2a4e",
                  padx=10, pady=10).pack(side="right", padx=(0, 10))

    # ─────────────────────────────── HELPERS ─────────────────────────────────
    def _toggle_postpone(self):
        if self.postpone_var.get():
            self.postpone_panel.pack(anchor="w", fill="x")
        else:
            self.postpone_panel.pack_forget()

    def _on_postpone_clock(self, h24, minute):
        self._postpone_time = (h24, minute)

    def _flash_border(self, count=0):
        if self._destroyed:
            return
        cols = ["#ff8800", "#e94560", "#ff8800", "#e94560", "#333355"]
        if count < len(cols):
            self.remark_border.config(bg=cols[count])
            self.root.after(130, lambda: self._flash_border(count + 1))

    def _snooze_5(self):
        """Dismiss popup immediately and reschedule for +5 minutes today."""
        t = datetime.datetime.now() + datetime.timedelta(minutes=5)
        self._postpone_time = (t.hour, t.minute)
        # Use a synthetic remark so the mandatory-remark check is satisfied
        remark = self.remark_text.get("1.0", "end").strip() or "Snoozed 5 min"
        self._destroyed = True
        self.on_close_callback(self.reminder, remark, self._postpone_time)
        self.root.destroy()

    def _try_close(self):
        remark = self.remark_text.get("1.0", "end").strip()
        if not remark:
            self.root.bell()
            self._flash_border()
            return
        postpone_time = self._postpone_time if self.postpone_var.get() else None
        self._destroyed = True
        self.on_close_callback(self.reminder, remark, postpone_time)
        self.root.destroy()


# ─── Main Application ─────────────────────────────────────────────────────────
class ReminderApp:
    def __init__(self, start_minimized=False):
        self.root = tk.Tk()
        self.root.title("Desktop Reminder Manager")
        self.root.configure(bg="#0f0f1a")
        self.root.geometry("900x660")
        self.root.minsize(640, 480)
        self.root.resizable(True, True)
        self._icon = _make_icon(self.root)   # keep reference so GC doesn't collect

        self.reminders     = load_reminders()
        self.active_popups = set()
        self.current_filter = "All"

        self._tray_manager = SystemTrayManager(self)
        self._tray_manager.start()

        self._build_ui()
        self._schedule_all()
        self._tick()

        # Intercept window close: hide to tray instead of destroying
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Start minimized to tray if launched with --minimized flag
        # (used by Windows Startup shortcut so it doesn't flash on login)
        if start_minimized:
            self.root.after(200, self.hide_window)

    # ─────────────────────────────── TTK STYLES ──────────────────────────────
    def _style_ttk(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview", background="#1a1a2e", foreground="#ccccdd",
                    fieldbackground="#1a1a2e", rowheight=30, font=("Courier New", 10))
        s.configure("Treeview.Heading", background="#111128", foreground="#e94560",
                    font=("Courier New", 10, "bold"))
        s.map("Treeview", background=[("selected", "#e94560")],
              foreground=[("selected", "#ffffff")])

    # ─────────────────────────────── BUILD UI ────────────────────────────────
    def _build_ui(self):
        self._style_ttk()

        # Top bar
        tb = tk.Frame(self.root, bg="#1a1a2e", height=64)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        tk.Label(tb, text="  ⏰  REMINDER MANAGER",
                 font=("Courier New", 15, "bold"),
                 fg="#e94560", bg="#1a1a2e").pack(side="left", padx=24, pady=16)
        tk.Button(tb, text="+ NEW REMINDER",
                  command=self._open_add_dialog,
                  font=("Courier New", 10, "bold"),
                  bg="#e94560", fg="#ffffff",
                  activebackground="#c73652",
                  relief="flat", cursor="hand2",
                  padx=14, pady=6).pack(side="right", padx=(4, 20), pady=16)

        # ⋮ App menu — always-visible Minimize / Quit actions
        self._app_menu = tk.Menu(self.root, tearoff=0, bg="#1a1a2e",
                                 fg="#ccccdd", activebackground="#e94560",
                                 activeforeground="#ffffff",
                                 font=("Courier New", 10), bd=0)
        self._app_menu.add_command(
            label="⬇  Hide to Tray / Minimise",
            command=self._on_window_close
        )
        self._app_menu.add_separator()
        self._app_menu.add_command(
            label="✕  Quit Application",
            command=self.quit_app
        )

        def _show_app_menu(event=None):
            btn = event.widget
            try:
                self._app_menu.tk_popup(
                    btn.winfo_rootx(),
                    btn.winfo_rooty() + btn.winfo_height()
                )
            finally:
                self._app_menu.grab_release()

        menu_btn = tk.Button(tb, text="⋮",
                             font=("Courier New", 14, "bold"),
                             bg="#1a1a2e", fg="#666688",
                             activebackground="#2a2a3e",
                             activeforeground="#e94560",
                             relief="flat", cursor="hand2",
                             padx=10, pady=6, bd=0)
        menu_btn.pack(side="right", pady=16)
        menu_btn.bind("<Button-1>", _show_app_menu)

        # Filter bar
        fb = tk.Frame(self.root, bg="#111128", height=46)
        fb.pack(fill="x")
        fb.pack_propagate(False)
        self.filter_btns = {}
        for lbl, key in [("All","All"),("Pending","Pending"),
                          ("Done","Done"),("Overdue","Overdue")]:
            b = tk.Button(fb, text=f"  {lbl}  ",
                          command=lambda k=key: self._set_filter(k),
                          font=("Courier New", 10, "bold"),
                          relief="flat", cursor="hand2",
                          padx=10, pady=8, bd=0)
            b.pack(side="left", padx=6, pady=7)
            self.filter_btns[key] = b
        self._update_filter_btns()

        tk.Frame(self.root, bg="#e94560", height=2).pack(fill="x")

        # ── Notebook: List tab + Calendar tab ────────────────────────────────
        nb_style = ttk.Style()
        nb_style.configure("Dark.TNotebook",
                           background="#0f0f1a", borderwidth=0)
        nb_style.configure("Dark.TNotebook.Tab",
                           background="#1a1a2e", foreground="#666688",
                           font=("Courier New", 10, "bold"),
                           padding=[16, 7])
        nb_style.map("Dark.TNotebook.Tab",
                     background=[("selected","#e94560")],
                     foreground=[("selected","#ffffff")])

        self.notebook = ttk.Notebook(self.root, style="Dark.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=18, pady=12)

        # ── Tab 0: List ───────────────────────────────────────────────────────
        lf = tk.Frame(self.notebook, bg="#0f0f1a")
        self.notebook.add(lf, text="  📋  List  ")

        cols = ("Title", "Date", "Time", "Days / Type", "Status")
        self.tree = ttk.Treeview(lf, columns=cols, show="headings", height=16)
        # Static minimums; _resize_columns() distributes remaining space
        for col, minw, anc in [("Title",160,"w"),("Date",96,"center"),
                                ("Time",64,"center"),("Days / Type",130,"w"),
                                ("Status",80,"center")]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=minw, minwidth=minw, anchor=anc)
        sb2 = ttk.Scrollbar(lf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb2.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")
        # Responsive columns: redistribute on resize
        self.tree.bind("<Configure>", self._resize_columns)
        for tag, fg in [("done","#44cc88"),("overdue","#ff6655"),
                        ("paused","#666688"),("pending","#ccccdd")]:
            self.tree.tag_configure(tag, foreground=fg)

        # ── Tab 1: Calendar view ──────────────────────────────────────────────
        cf = tk.Frame(self.notebook, bg="#0f0f1a")
        self.notebook.add(cf, text="  📅  Calendar  ")

        cal_outer = tk.Frame(cf, bg="#0f0f1a")
        cal_outer.pack(fill="both", expand=True, padx=18, pady=12)

        # Left: calendar widget (with reminder-dot markers)
        cal_left = tk.Frame(cal_outer, bg="#1a1a2e",
                            highlightthickness=1, highlightbackground="#2a2a4e")
        cal_left.pack(side="left", anchor="n")
        tk.Label(cal_left, text="CLICK A DATE TO VIEW REMINDERS",
                 font=("Courier New", 7, "bold"),
                 fg="#444466", bg="#1a1a2e").pack(pady=(8, 0))
        self.cal_view = CalendarPicker(
            cal_left,
            date=datetime.date.today(),
            on_change=self._cal_view_date_selected)
        self.cal_view.pack(padx=10, pady=(4, 10))

        # Right: reminder list for selected day
        cal_right = tk.Frame(cal_outer, bg="#0f0f1a")
        cal_right.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=4)

        self.cal_day_lbl = tk.Label(cal_right,
                                    text="",
                                    font=("Courier New", 12, "bold"),
                                    fg="#e94560", bg="#0f0f1a")
        self.cal_day_lbl.pack(anchor="w", pady=(0, 8))

        cal_list_frame = tk.Frame(cal_right, bg="#0f0f1a")
        cal_list_frame.pack(fill="both", expand=True)

        self.cal_listbox = tk.Listbox(
            cal_list_frame,
            font=("Courier New", 11),
            bg="#1a1a2e", fg="#ccccdd",
            selectbackground="#e94560", selectforeground="#ffffff",
            relief="flat", borderwidth=0,
            activestyle="none",
            height=14)
        cal_sb = ttk.Scrollbar(cal_list_frame, orient="vertical",
                               command=self.cal_listbox.yview)
        self.cal_listbox.configure(yscrollcommand=cal_sb.set)
        self.cal_listbox.pack(side="left", fill="both", expand=True)
        cal_sb.pack(side="right", fill="y")

        tk.Label(cal_right,
                 text="Double-click a reminder to edit it",
                 font=("Courier New", 8), fg="#333355",
                 bg="#0f0f1a").pack(anchor="w", pady=(6, 0))
        self.cal_listbox.bind("<Double-1>", self._cal_list_edit)

        # Update calendar markers after list is populated
        self.root.after(100, self._refresh_cal_view)
        # Re-refresh calendar tab whenever it's selected
        self.notebook.bind("<<NotebookTabChanged>>",
                           lambda e: self._refresh_cal_view()
                           if self.notebook.index("current") == 1 else None)

        # Bottom bar — action buttons + live clock
        br = tk.Frame(self.root, bg="#0f0f1a")
        br.pack(fill="x", padx=18, pady=(0, 14))

        btn_cfg = dict(font=("Courier New", 10), relief="flat",
                       cursor="hand2", padx=12, pady=6)
        tk.Button(br, text="✏  Edit", command=self._edit_selected,
                  bg="#1a1a2e", fg="#aaaacc",
                  activebackground="#2a2a4e",
                  activeforeground="#ffffff", **btn_cfg).pack(side="left")
        tk.Button(br, text="🗑  Delete", command=self._delete_selected,
                  bg="#2a0a10", fg="#e94560",
                  activebackground="#3a1020", **btn_cfg).pack(side="left", padx=6)
        tk.Button(br, text="⏸  Toggle", command=self._toggle_selected,
                  bg="#0f0f1a", fg="#666688",
                  activebackground="#1a1a2e", **btn_cfg).pack(side="left")

        # Tray status dot — updated after tray starts
        self.tray_lbl = tk.Label(br, text="", font=("Courier New", 8),
                                 fg="#333355", bg="#0f0f1a")
        self.tray_lbl.pack(side="right", padx=(0, 10))

        self.clock_lbl = tk.Label(br, text="", font=("Courier New", 9),
                                  fg="#333355", bg="#0f0f1a")
        self.clock_lbl.pack(side="right")
        self._tick_clock()
        # Update tray indicator after a short delay (tray thread needs time)
        self.root.after(1500, self._update_tray_label)

        # Right-click context menu on tree rows
        self._ctx_menu = tk.Menu(self.root, tearoff=0, bg="#1a1a2e",
                                 fg="#ccccdd", activebackground="#e94560",
                                 activeforeground="#ffffff",
                                 font=("Courier New", 10), bd=0)
        self._ctx_menu.add_command(label="✏  Edit",   command=self._edit_selected)
        self._ctx_menu.add_command(label="🗑  Delete", command=self._delete_selected)
        self._ctx_menu.add_separator()
        self._ctx_menu.add_command(label="⏸  Toggle Active", command=self._toggle_selected)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self._edit_selected())

        self._refresh_list()

    def _tick_clock(self):
        self.clock_lbl.config(
            text=datetime.datetime.now().strftime("%H:%M:%S  ·  %A, %d %b %Y"))
        self.root.after(1000, self._tick_clock)

    def _update_tray_label(self):
        if self._tray_manager.available:
            self.tray_lbl.config(
                text="● Running in tray",
                fg="#20c870",
                cursor="hand2"
            )
            self.tray_lbl.bind("<Button-1>", lambda e: self.hide_window())
            self.tray_lbl.bind("<Enter>",
                lambda e: self.tray_lbl.config(fg="#44ee99"))
            self.tray_lbl.bind("<Leave>",
                lambda e: self.tray_lbl.config(fg="#20c870"))
        else:
            self.tray_lbl.config(
                text="○ Install pystray + pillow for tray support",
                fg="#555533",
                cursor="arrow"
            )

    # ─────────────────────────────── FILTER ──────────────────────────────────
    def _set_filter(self, key):
        self.current_filter = key
        self._update_filter_btns()
        self._refresh_list()

    def _update_filter_btns(self):
        palette = {"All":"#e94560","Pending":"#e8a020",
                   "Done":"#20c870","Overdue":"#ff5540"}
        for key, btn in self.filter_btns.items():
            if key == self.current_filter:
                c = palette[key]
                btn.config(bg=c, fg="#ffffff",
                           activebackground=c, activeforeground="#ffffff")
            else:
                btn.config(bg="#1a1a2e", fg="#666688",
                           activebackground="#222240", activeforeground="#ccccdd")

    # ─────────────────────────────── LIST ────────────────────────────────────
    def _status(self, r):
        if not r.get("active", True):
            return "Done" if r.get("history") else "Paused"
        now  = datetime.datetime.now()
        hist = r.get("history", [])

        if not r.get("days"):
            # One-time reminder: use the stored date if present, else today
            date_str = r.get("date") or now.strftime("%Y-%m-%d")
            try:
                dt = datetime.datetime.strptime(
                    date_str + " " + r.get("time", "00:00"), "%Y-%m-%d %H:%M")
                if dt.date() > now.date():
                    return "Pending"   # future date — not yet due
                return "Overdue" if now > dt else "Pending"
            except Exception:
                return "Pending"

        # Repeating reminder
        if hist:
            try:
                last = datetime.datetime.fromisoformat(hist[-1]["timestamp"])
                if last.date() == now.date():
                    return "Done"
            except Exception:
                pass
        if now.strftime("%A") in r.get("days", []):
            try:
                dt = datetime.datetime.strptime(
                    now.strftime("%Y-%m-%d ") + r.get("time", "00:00"),
                    "%Y-%m-%d %H:%M")
                return "Overdue" if now > dt else "Pending"
            except Exception:
                pass
        return "Pending"

    def _refresh_list(self):
        self._refresh_cal_view()
        for item in self.tree.get_children():
            self.tree.delete(item)
        flt = self.current_filter
        for r in self.reminders:
            st = self._status(r)
            if flt != "All" and st != flt:
                continue
            # Build the Days/Type display string
            if r.get("days"):
                days = ", ".join(r["days"])
            elif r.get("date"):
                try:
                    d = datetime.date.fromisoformat(r["date"])
                    days = d.strftime("%d %b %Y")   # e.g. "15 Mar 2025"
                except Exception:
                    days = "One-time"
            else:
                days = "One-time"
            tag  = {"Done":"done","Overdue":"overdue","Paused":"paused"}.get(st,"pending")
            # Format the Date cell
            raw_date = r.get("date", "")
            if raw_date:
                try:
                    date_disp = datetime.date.fromisoformat(raw_date).strftime("%d-%m-%Y")
                except Exception:
                    date_disp = raw_date
            else:
                date_disp = "—"
            self.tree.insert("", "end", iid=r["id"], tags=(tag,),
                             values=(r.get("title",""), date_disp,
                                     r.get("time",""), days, st))

    # ─────────────────────────────── ACTIONS ─────────────────────────────────
    def _open_add_dialog(self):
        AddReminderDialog(self.root, self._on_reminder_added)

    def _on_reminder_added(self, reminder):
        self.reminders.append(reminder)
        save_reminders(self.reminders)
        self._schedule_all()
        self._refresh_list()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if messagebox.askyesno("Delete", "Delete selected reminder(s)?"):
            ids = set(sel)
            self.reminders = [r for r in self.reminders if r["id"] not in ids]
            save_reminders(self.reminders)
            self._schedule_all()
            self._refresh_list()

    def _toggle_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        ids = set(sel)
        for r in self.reminders:
            if r["id"] in ids:
                r["active"] = not r.get("active", True)
        save_reminders(self.reminders)
        self._schedule_all()
        self._refresh_list()

    # ─────────────────────────────── RESPONSIVE COLUMNS ─────────────────────
    def _resize_columns(self, event=None):
        """Distribute available Treeview width: Title and Days get elastic space."""
        total = self.tree.winfo_width()
        if total < 10:
            return
        # Fixed-width columns
        date_w   = 96
        time_w   = 68
        status_w = 90
        # Elastic columns share the remainder equally
        elastic = max(80, (total - date_w - time_w - status_w - 4) // 2)
        self.tree.column("Title",       width=elastic)
        self.tree.column("Date",        width=date_w)
        self.tree.column("Time",        width=time_w)
        self.tree.column("Days / Type", width=elastic)
        self.tree.column("Status",      width=status_w)

    # ─────────────────────────────── EDIT ────────────────────────────────────
    def _edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        rid = sel[0]
        reminder = next((r for r in self.reminders if r["id"] == rid), None)
        if reminder is None:
            return
        AddReminderDialog(self.root, self._on_reminder_updated, existing=reminder)

    def _on_reminder_updated(self, updated):
        """Replace the reminder with the same id in-place."""
        for i, r in enumerate(self.reminders):
            if r["id"] == updated["id"]:
                # Preserve history from the original
                updated["history"] = r.get("history", [])
                self.reminders[i] = updated
                break
        save_reminders(self.reminders)
        self._schedule_all()
        self._refresh_list()

    # ─────────────────────────────── CONTEXT MENU ────────────────────────────
    def _show_context_menu(self, event):
        row = self.tree.identify_row(event.y)
        if not row:
            return
        self.tree.selection_set(row)
        try:
            self._ctx_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._ctx_menu.grab_release()

    # ─────────────────────────────── CALENDAR VIEW ──────────────────────────
    def _refresh_cal_view(self):
        """Mark dates that have reminders and refresh the selected-day list."""
        if not hasattr(self, "cal_view"):
            return
        # Collect all unique dates that have active one-time reminders
        marked = set()
        for r in self.reminders:
            if r.get("date") and r.get("active", True):
                try:
                    marked.add(datetime.date.fromisoformat(r["date"]))
                except Exception:
                    pass
        self.cal_view.mark_dates(marked)
        self._cal_view_date_selected(self.cal_view.get_date())

    def _cal_view_date_selected(self, date):
        """User clicked a date in the Calendar tab — show that day's reminders."""
        if not hasattr(self, "cal_day_lbl"):
            return
        today = datetime.date.today()
        if date == today:
            day_str = date.strftime("%A, %d %b %Y") + "  (today)"
        else:
            day_str = date.strftime("%A, %d %b %Y")
        self.cal_day_lbl.config(text=day_str)

        self.cal_listbox.delete(0, "end")
        self._cal_day_ids = []   # parallel list of reminder IDs

        # Find reminders for this date
        day_name = date.strftime("%A")
        date_iso = date.isoformat()

        for r in self.reminders:
            matches = False
            if r.get("date") == date_iso:
                matches = True
            elif r.get("days") and day_name in r["days"]:
                matches = True
            if not matches:
                continue

            status = self._status(r)
            icon   = {"Done":"✓ ","Overdue":"⚠ ","Paused":"⏸ "}.get(status, "⏰ ")
            time_s = r.get("time", "--:--")
            title  = r.get("title", "(no title)")
            repeat = f"  [{', '.join(r['days'][:2])}{'…' if len(r.get('days',[]))>2 else ''}]" if r.get("days") else ""
            self.cal_listbox.insert("end", f"  {icon}{time_s}   {title}{repeat}")
            self._cal_day_ids.append(r["id"])

            # Colour the row
            colour = {"Done":"#44cc88","Overdue":"#ff6655","Paused":"#555577"}.get(
                status, "#ccccdd")
            self.cal_listbox.itemconfig("end", fg=colour)

        if self.cal_listbox.size() == 0:
            self.cal_listbox.insert("end", "  No reminders for this day")
            self._cal_day_ids.append(None)
            self.cal_listbox.itemconfig("end", fg="#333355")

    def _cal_list_edit(self, event):
        """Double-click on calendar list → open edit dialog."""
        if not hasattr(self, "_cal_day_ids"):
            return
        sel = self.cal_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._cal_day_ids) or self._cal_day_ids[idx] is None:
            return
        rid = self._cal_day_ids[idx]
        reminder = next((r for r in self.reminders if r["id"] == rid), None)
        if reminder:
            AddReminderDialog(self.root, self._on_reminder_updated, existing=reminder)

    # ─────────────────────────────── SCHEDULER ───────────────────────────────
    def _schedule_all(self):
        schedule.clear()
        day_map = {
            "Monday":    schedule.every().monday,
            "Tuesday":   schedule.every().tuesday,
            "Wednesday": schedule.every().wednesday,
            "Thursday":  schedule.every().thursday,
            "Friday":    schedule.every().friday,
            "Saturday":  schedule.every().saturday,
            "Sunday":    schedule.every().sunday,
        }
        for r in self.reminders:
            if not r.get("active", True):
                continue
            t    = r.get("time", "")
            days = r.get("days", [])
            if days:
                for day in days:
                    if day in day_map:
                        try:
                            day_map[day].at(t).do(self._trigger_reminder, r)
                        except Exception:
                            pass

    def _tick(self):
        schedule.run_pending()
        self._check_onetime()
        self.root.after(10000, self._tick)

    def _check_onetime(self):
        now     = datetime.datetime.now()
        now_str = now.strftime("%H:%M")
        today   = now.strftime("%Y-%m-%d")
        for r in self.reminders:
            if not r.get("active", True):
                continue
            if r.get("days"):
                continue
            if r.get("time") != now_str:
                continue
            # Only fire on the specific date (default = today for legacy reminders)
            reminder_date = r.get("date") or today
            if reminder_date != today:
                continue
            if r["id"] not in self.active_popups:
                self._trigger_reminder(r)
                r["active"] = False
                save_reminders(self.reminders)
                self.root.after(0, self._refresh_list)

    def _trigger_reminder(self, reminder):
        rid = reminder["id"]
        if rid in self.active_popups:
            return
        self.active_popups.add(rid)

        def callback(rem, remark, postpone_time):
            self.active_popups.discard(rid)
            rem.setdefault("history", []).append({
                "timestamp": datetime.datetime.now().isoformat(),
                "remark":    remark
            })
            if postpone_time:
                ph, pm = postpone_time
                # Work out the date for the postponed reminder:
                # If the postponed time is earlier in the day than now (rare
                # edge case) the user presumably means tomorrow; otherwise today.
                now_snap = datetime.datetime.now()
                snap_dt  = now_snap.replace(hour=ph, minute=pm, second=0)
                if snap_dt <= now_snap:
                    snap_date = (now_snap + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    snap_date = now_snap.strftime("%Y-%m-%d")
                self.reminders.append({
                    "id":             str(uuid.uuid4()),
                    "title":          rem["title"],
                    "description":    rem.get("description", ""),
                    "time":           f"{ph:02d}:{pm:02d}",
                    "date":           snap_date,
                    "days":           [],
                    "active":         True,
                    "postponed_from": rid,
                    "history":        []
                })
                self._schedule_all()
            save_reminders(self.reminders)
            self.root.after(0, self._refresh_list)

        # Popup is a Toplevel — appears regardless of main window visibility.
        # We push a tray notification first so the user sees the alert even
        # if the screen is busy.  The popup itself is always-on-top.
        self._tray_manager.notify(
            "⏰  " + reminder.get("title", "Reminder"),
            reminder.get("description", "Time to act on this reminder!")
        )
        self.root.after(0, lambda: ReminderPopup(reminder, callback))

    # ─────────────────────────────── WINDOW VISIBILITY ───────────────────────
    def _on_window_close(self):
        """X button clicked — behaviour depends on tray availability."""
        if self._tray_manager.available:
            # Hide completely; tray icon is the only way back
            self.hide_window()
            self._tray_manager.notify(
                "Reminder Manager",
                "Still running in the background — reminders will keep firing. "
                "Right-click the tray icon to open or exit."
            )
        else:
            # pystray not installed: ask user what they want
            answer = messagebox.askyesnocancel(
                "Close Reminder Manager",
                "pystray is not installed so the system tray is unavailable.\n\n"
                "• Yes  — minimise to taskbar (scheduler keeps running)\n"
                "• No   — quit the application entirely\n"
                "• Cancel — go back",
                parent=self.root
            )
            if answer is True:
                self.root.iconify()          # minimise; scheduler keeps ticking
            elif answer is False:
                self.quit_app()             # full exit
            # answer is None → Cancel → do nothing

    def hide_window(self):
        """Remove window from taskbar and hide it entirely."""
        self.root.withdraw()

    def show_window(self):
        """Restore the main window from tray / hidden state.
        Never calls focus_force() — that would steal focus from reminder popups."""
        self.root.deiconify()
        self.root.lift()
        # Brief topmost pulse brings the window to front without locking focus
        self.root.attributes("-topmost", True)
        self.root.after(150, lambda: self.root.attributes("-topmost", False))

    def quit_app(self):
        """Cleanly stop tray thread, cancel pending callbacks, destroy root."""
        # Stop accepting new close requests
        try:
            self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        except Exception:
            pass
        self._tray_manager.stop()
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self.root.mainloop()



# ─── Calendar Picker Widget ───────────────────────────────────────────────────
class CalendarPicker(tk.Frame):
    """
    Custom month-grid calendar drawn on a tk.Canvas.

    Palette matches the rest of the app (dark navy / red accent).
    No external dependencies beyond tkinter.

    Public API:
      get_date()           → datetime.date  (selected date)
      set_date(d)          → set selected date and redraw
      on_change            → callback(date: datetime.date)
    """

    C_BG        = "#0f0f1a"
    C_HEADER    = "#1a1a2e"
    C_CELL      = "#0f0f1a"
    C_HOVER     = "#1a1a3a"
    C_SEL_BG    = "#e94560"
    C_SEL_FG    = "#ffffff"
    C_TODAY_FG  = "#e94560"
    C_WKDAY_FG  = "#ccccdd"
    C_WKEND_FG  = "#8888aa"
    C_HDR_FG    = "#aaaacc"
    C_GRID      = "#1e1e38"
    C_NAV       = "#e94560"
    C_DISABLED  = "#333344"

    CELL_W = 36
    CELL_H = 30
    PAD_X  = 12
    PAD_Y  = 8

    MONTHS = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    WDAYS  = ["Mo","Tu","We","Th","Fr","Sa","Su"]

    def __init__(self, parent, date=None, on_change=None, **kw):
        super().__init__(parent, bg=self.C_BG, **kw)
        today = datetime.date.today()
        self._sel  = date if date else today
        self._view = datetime.date(self._sel.year, self._sel.month, 1)
        self._today = today
        self.on_change = on_change
        self._hover = None

        # Canvas sized to fit 7 columns × 6 rows + header
        cw = self.CELL_W * 7 + self.PAD_X * 2
        ch = self.CELL_H * 7 + self.PAD_Y * 3 + 24   # +24 for month/year nav row
        self._cw = cw
        self._ch = ch

        self._marked = set()   # dates highlighted with a dot (for calendar view)

        self.canvas = tk.Canvas(self, width=cw, height=ch,
                                bg=self.C_BG, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Motion>",         self._on_motion)
        self.canvas.bind("<Leave>",          self._on_leave)
        self.canvas.bind("<Button-1>",       self._on_click)

        self._draw()

    # ── Drawing ───────────────────────────────────────────────────────────────
    def _draw(self):
        c = self.canvas
        c.delete("all")

        cw, ch = self._cw, self._ch
        x0 = self.PAD_X

        # ── Navigation row ────────────────────────────────────────────────────
        nav_y = self.PAD_Y + 10
        # ← button
        c.create_text(x0 + 12, nav_y, text="◀", fill=self.C_NAV,
                      font=("Courier New", 12, "bold"), tags="nav_prev",
                      anchor="center")
        # Month Year label (clickable to jump to today)
        month_label = f"{self.MONTHS[self._view.month-1]}  {self._view.year}"
        c.create_text(cw // 2, nav_y, text=month_label,
                      fill="#e0e0f0", font=("Courier New", 11, "bold"),
                      anchor="center", tags="nav_month")
        # → button
        c.create_text(cw - x0 - 12, nav_y, text="▶", fill=self.C_NAV,
                      font=("Courier New", 12, "bold"), tags="nav_next",
                      anchor="center")

        # Thin divider
        div_y = nav_y + 16
        c.create_line(x0, div_y, cw - x0, div_y, fill=self.C_GRID, width=1)

        # ── Weekday header ────────────────────────────────────────────────────
        wd_y = div_y + self.CELL_H // 2 + 4
        for col, wd in enumerate(self.WDAYS):
            cx = x0 + col * self.CELL_W + self.CELL_W // 2
            fg = self.C_WKEND_FG if col >= 5 else self.C_HDR_FG
            c.create_text(cx, wd_y, text=wd, fill=fg,
                          font=("Courier New", 8, "bold"), anchor="center")

        # ── Day grid ─────────────────────────────────────────────────────────
        import calendar as _cal
        cal = _cal.monthcalendar(self._view.year, self._view.month)

        grid_y0 = wd_y + self.CELL_H // 2 + 6
        self._cells = {}   # (row, col) → date | None

        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                if day == 0:
                    self._cells[(row, col)] = None
                    continue

                d    = datetime.date(self._view.year, self._view.month, day)
                cx   = x0 + col * self.CELL_W + self.CELL_W // 2
                cy   = grid_y0 + row * self.CELL_H + self.CELL_H // 2
                is_sel   = (d == self._sel)
                is_today = (d == self._today)
                is_wkend = (col >= 5)
                is_hover = (d == self._hover)

                self._cells[(row, col)] = d

                # Cell background
                r1 = cx - self.CELL_W // 2 + 2
                r2 = cy - self.CELL_H // 2 + 2
                r3 = cx + self.CELL_W // 2 - 2
                r4 = cy + self.CELL_H // 2 - 2

                if is_sel:
                    c.create_oval(r1, r2, r3, r4,
                                  fill=self.C_SEL_BG, outline="", tags="cell")
                    txt_fg = self.C_SEL_FG
                elif is_hover:
                    c.create_oval(r1, r2, r3, r4,
                                  fill=self.C_HOVER, outline="", tags="cell")
                    txt_fg = self.C_WKDAY_FG
                else:
                    txt_fg = (self.C_TODAY_FG if is_today
                              else (self.C_WKEND_FG if is_wkend else self.C_WKDAY_FG))

                # Today ring (when not selected)
                if is_today and not is_sel:
                    c.create_oval(r1, r2, r3, r4,
                                  fill="", outline=self.C_SEL_BG,
                                  width=1, tags="cell")

                font_weight = "bold" if (is_sel or is_today) else "normal"
                c.create_text(cx, cy, text=str(day), fill=txt_fg,
                              font=("Courier New", 10, font_weight),
                              anchor="center", tags=f"day_{row}_{col}")

                # Small dot below the number for dates that have reminders
                if d in self._marked and not is_sel:
                    dot_y = cy + self.CELL_H // 2 - 5
                    c.create_oval(cx-3, dot_y-3, cx+3, dot_y+3,
                                  fill=self.C_SEL_BG, outline="", tags="cell")

    # ── Event helpers ─────────────────────────────────────────────────────────
    def _xy_to_cell(self, x, y):
        """Return (row, col) from canvas coords, or None if outside grid."""
        import calendar as _cal
        x0 = self.PAD_X
        nav_h = self.PAD_Y + 10 + 16 + self.CELL_H // 2 + 4 + self.CELL_H // 2 + 6
        if y < nav_h:
            return None
        col = (x - x0) // self.CELL_W
        row = (y - nav_h) // self.CELL_H
        cal = _cal.monthcalendar(self._view.year, self._view.month)
        if 0 <= row < len(cal) and 0 <= col < 7:
            return (int(row), int(col))
        return None

    def _xy_to_nav(self, x, y):
        """Return 'prev', 'next', 'month' or None depending on click zone."""
        nav_y = self.PAD_Y + 10
        if abs(y - nav_y) > 16:
            return None
        if x < self.PAD_X + 30:
            return "prev"
        if x > self._cw - self.PAD_X - 30:
            return "next"
        return "month"

    def _on_motion(self, event):
        rc = self._xy_to_cell(event.x, event.y)
        if rc and self._cells.get(rc):
            new_hover = self._cells[rc]
        else:
            new_hover = None
        if new_hover != self._hover:
            self._hover = new_hover
            self._draw()

    def _on_leave(self, event):
        if self._hover is not None:
            self._hover = None
            self._draw()

    def _on_click(self, event):
        nav = self._xy_to_nav(event.x, event.y)
        if nav == "prev":
            self._go_month(-1)
            return
        if nav == "next":
            self._go_month(+1)
            return
        if nav == "month":
            # Jump to today
            self._sel  = self._today
            self._view = datetime.date(self._today.year, self._today.month, 1)
            self._draw()
            if self.on_change:
                self.on_change(self._sel)
            return
        rc = self._xy_to_cell(event.x, event.y)
        if rc:
            d = self._cells.get(rc)
            if d:
                self._sel = d
                self._draw()
                if self.on_change:
                    self.on_change(self._sel)

    def _go_month(self, delta):
        """Advance or retreat by delta months."""
        m = self._view.month + delta
        y = self._view.year
        while m > 12: m -= 12; y += 1
        while m < 1:  m += 12; y -= 1
        self._view = datetime.date(y, m, 1)
        self._draw()

    # ── Public API ────────────────────────────────────────────────────────────
    def mark_dates(self, dates):
        """Mark a set of datetime.date objects with a red dot indicator."""
        self._marked = set(dates)
        self._draw()

    def get_date(self):
        return self._sel

    def set_date(self, d):
        self._sel  = d
        self._view = datetime.date(d.year, d.month, 1)
        self._draw()

# ─── Add Reminder Dialog ──────────────────────────────────────────────────────
class AddReminderDialog:
    DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    def __init__(self, parent, on_save, existing=None):
        self.on_save  = on_save
        self.existing = existing          # None = Add mode, dict = Edit mode
        self._syncing = False
        self._edit_mode = existing is not None

        self.win = tk.Toplevel(parent)
        self.win.title("✏  Edit Reminder" if self._edit_mode else "⏰  New Reminder")
        self.win.configure(bg="#0f0f1a")
        self.win.grab_set()
        self.win.resizable(True, True)

        SW = parent.winfo_screenwidth()
        SH = parent.winfo_screenheight()
        W  = min(680, int(SW * 0.75))
        H  = min(760, int(SH * 0.88))
        self.win.geometry(f"{W}x{H}+{(SW-W)//2}+{(SH-H)//2}")
        self.win.minsize(540, 560)
        self._icon_ref = _make_icon(self.win)
        self._build()

    def _lbl(self, parent, text):
        tk.Label(parent, text=text, font=("Courier New", 10, "bold"),
                 fg="#e94560", bg="#0f0f1a").pack(anchor="w", pady=(14, 3))

    def _entry(self, parent):
        wrap = tk.Frame(parent, bg="#e94560", padx=1, pady=1)
        wrap.pack(fill="x")
        e = tk.Entry(wrap, font=("Courier New", 12), bg="#1a1a2e", fg="#ffffff",
                     insertbackground="#e94560", relief="flat")
        e.pack(fill="x", ipady=7, padx=1, pady=1)
        return e

    def _build(self):
        # Header
        hdr = tk.Frame(self.win, bg="#1a1a2e", height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        hdr_text = "✏  EDIT REMINDER" if self._edit_mode else "⏰  NEW REMINDER"
        tk.Label(hdr, text=hdr_text,
                 font=("Courier New", 13, "bold"),
                 fg="#e94560", bg="#1a1a2e").pack(side="left", padx=22, pady=14)

        # Scrollable body
        outer_cv = tk.Canvas(self.win, bg="#0f0f1a", highlightthickness=0)
        outer_sb = ttk.Scrollbar(self.win, orient="vertical", command=outer_cv.yview)
        outer_cv.configure(yscrollcommand=outer_sb.set)
        outer_sb.pack(side="right", fill="y")
        outer_cv.pack(fill="both", expand=True)

        body   = tk.Frame(outer_cv, bg="#0f0f1a")
        body_w = outer_cv.create_window((0, 0), window=body, anchor="nw")

        def _cfg(e):
            outer_cv.configure(scrollregion=outer_cv.bbox("all"))
            outer_cv.itemconfig(body_w, width=outer_cv.winfo_width())
        body.bind("<Configure>", _cfg)
        outer_cv.bind("<Configure>",
                      lambda e: outer_cv.itemconfig(body_w, width=e.width))
        outer_cv.bind_all("<MouseWheel>",
                          lambda e: outer_cv.yview_scroll(
                              int(-1*(e.delta/120)), "units"))

        pad = tk.Frame(body, bg="#0f0f1a")
        pad.pack(fill="both", expand=True, padx=24, pady=6)

        # Title & description
        self._lbl(pad, "Title")
        self.title_entry = self._entry(pad)
        if self._edit_mode:
            self.title_entry.insert(0, self.existing.get("title", ""))
        self.title_entry.focus_set()

        self._lbl(pad, "Description  (optional)")
        self.desc_entry = self._entry(pad)
        if self._edit_mode:
            self.desc_entry.insert(0, self.existing.get("description", ""))

        # ── Date section ──────────────────────────────────────────────────────
        self._lbl(pad, "Date")

        date_row = tk.Frame(pad, bg="#0f0f1a")
        date_row.pack(anchor="w", fill="x", pady=(0, 4))

        # Left: calendar widget
        cal_frame = tk.Frame(date_row, bg="#1a1a2e",
                             highlightthickness=1, highlightbackground="#2a2a4e")
        cal_frame.pack(side="left", anchor="n")
        tk.Label(cal_frame, text="CALENDAR PICKER",
                 font=("Courier New", 7, "bold"),
                 fg="#444466", bg="#1a1a2e").pack(pady=(8, 0))

        # Determine initial date
        if self._edit_mode and self.existing.get("date"):
            try:
                _init_date = datetime.date.fromisoformat(self.existing["date"])
            except Exception:
                _init_date = datetime.date.today()
        else:
            _init_date = datetime.date.today()

        self.cal = CalendarPicker(cal_frame, date=_init_date,
                                  on_change=self._cal_changed)
        self.cal.pack(padx=10, pady=(4, 10))

        # Right: selected-date readout + "no date" note
        date_info = tk.Frame(date_row, bg="#0f0f1a")
        date_info.pack(side="left", anchor="n", padx=(20, 0), pady=4)

        tk.Label(date_info, text="SELECTED DATE",
                 font=("Courier New", 8, "bold"),
                 fg="#666688", bg="#0f0f1a").pack(anchor="w")

        self.date_lbl = tk.Label(date_info, text="",
                                 font=("Courier New", 14, "bold"),
                                 fg="#e94560", bg="#0f0f1a")
        self.date_lbl.pack(anchor="w", pady=(4, 8))

        tk.Label(date_info,
                 text="ℹ  If you check days below,\nthe date is ignored\n(repeating reminders fire\nevery matching weekday).",
                 font=("Courier New", 8),
                 fg="#444466", bg="#0f0f1a", justify="left").pack(anchor="w")

        self._refresh_date_label()

        # ── Time section ─────────────────────────────────────────────────────
        self._lbl(pad, "Time")

        time_row = tk.Frame(pad, bg="#0f0f1a")
        time_row.pack(anchor="w", fill="x", pady=(0, 8))

        # Left column: spinners + preview
        left = tk.Frame(time_row, bg="#0f0f1a")
        left.pack(side="left", anchor="n", padx=(0, 16))

        sp_row = tk.Frame(left, bg="#0f0f1a")
        sp_row.pack(anchor="w")

        now = datetime.datetime.now()
        # Pre-fill time from existing reminder if editing
        if self._edit_mode:
            try:
                _tp = self.existing.get("time", "00:00").split(":")
                init_h, init_m = int(_tp[0]), int(_tp[1])
            except Exception:
                init_h, init_m = now.hour, now.minute
        else:
            init_h, init_m = now.hour, now.minute

        hg = tk.Frame(sp_row, bg="#0f0f1a")
        hg.pack(side="left", padx=(0, 6))
        tk.Label(hg, text="HOUR", font=("Courier New", 8, "bold"),
                 fg="#666688", bg="#0f0f1a").pack()
        self.hour_sp = Spinner(hg, 0, 23, initial=init_h, bg="#0f0f1a")
        self.hour_sp.pack()

        tk.Label(sp_row, text=":", font=("Courier New", 22, "bold"),
                 fg="#e94560", bg="#0f0f1a").pack(side="left", padx=4, pady=(18, 0))

        mg = tk.Frame(sp_row, bg="#0f0f1a")
        mg.pack(side="left", padx=(6, 0))
        tk.Label(mg, text="MIN", font=("Courier New", 8, "bold"),
                 fg="#666688", bg="#0f0f1a").pack()
        self.min_sp = Spinner(mg, 0, 59, initial=init_m, bg="#0f0f1a")
        self.min_sp.pack()

        self.prev_lbl = tk.Label(left, text="",
                                 font=("Courier New", 13, "bold"),
                                 fg="#aaaacc", bg="#0f0f1a")
        self.prev_lbl.pack(pady=(12, 0))

        # Right column: analog clock
        right = tk.Frame(time_row, bg="#1a1a2e",
                         highlightthickness=1, highlightbackground="#2a2a4e")
        right.pack(side="left", anchor="n")

        tk.Label(right, text="CLOCK  PICKER",
                 font=("Courier New", 7, "bold"),
                 fg="#444466", bg="#1a1a2e").pack(pady=(8, 0))

        self.clock = AnalogClockPicker(
            right, hour24=init_h, minute=init_m,
            on_change=self._clock_changed)
        self.clock.pack(padx=10, pady=(0, 10))

        # Wire spinners ↔ clock (bidirectional, guarded by _syncing flag)
        self.hour_sp.bind("<<SpinnerChanged>>", lambda e: self._spinner_changed())
        self.min_sp.bind("<<SpinnerChanged>>",  lambda e: self._spinner_changed())

        self._refresh_preview()

        # ── Repeat days ───────────────────────────────────────────────────────
        self._lbl(pad, "Repeat on days  (overrides date — fires every matching weekday)")
        df = tk.Frame(pad, bg="#0f0f1a")
        df.pack(anchor="w")
        existing_days = set(self.existing.get("days", [])) if self._edit_mode else set()
        self.day_vars = {}
        for i, day in enumerate(self.DAYS):
            var = tk.BooleanVar(value=(day in existing_days))
            self.day_vars[day] = var
            r, c = i // 4, i % 4
            tk.Checkbutton(df, text=day[:3], variable=var,
                           font=("Courier New", 9), fg="#ccccdd", bg="#0f0f1a",
                           selectcolor="#1a1a2e", activebackground="#0f0f1a",
                           activeforeground="#ffffff").grid(
                               row=r, column=c, sticky="w", padx=8, pady=3)

        # Save / Update button (always visible, outside scroll canvas)
        btn_label = "UPDATE REMINDER  ✓" if self._edit_mode else "SAVE REMINDER  ✓"
        tk.Button(self.win, text=btn_label,
                  command=self._save,
                  font=("Courier New", 12, "bold"),
                  bg="#e94560", fg="#ffffff",
                  activebackground="#c73652",
                  relief="flat", cursor="hand2",
                  padx=22, pady=10).pack(pady=16)

    # ─────────────────────────────── SYNC ────────────────────────────────────
    def _cal_changed(self, date):
        """Calendar date selected → update date label."""
        self._refresh_date_label()

    def _refresh_date_label(self):
        d     = self.cal.get_date()
        today = datetime.date.today()
        delta = (d - today).days    # always computed; positive = future
        if delta == 0:
            suffix = "  (today)"
        elif delta == 1:
            suffix = "  (tomorrow)"
        elif delta > 1:
            suffix = f"  (in {delta} days)"
        else:
            suffix = "  (past)"
        self.date_lbl.config(
            text=d.strftime("%A, %d %b %Y") + suffix,
            fg="#e94560" if delta >= 0 else "#ff6655"
        )

    def _clock_changed(self, h24, minute):
        """Clock dial clicked → update spinners."""
        if self._syncing:
            return
        self._syncing = True
        self.hour_sp.set(h24)
        self.min_sp.set(minute)
        self._syncing = False
        self._refresh_preview()

    def _spinner_changed(self):
        """Spinner scrolled → update clock dial."""
        if self._syncing:
            return
        self._syncing = True
        self.clock.set_time(self.hour_sp.get(), self.min_sp.get())
        self._syncing = False
        self._refresh_preview()

    def _refresh_preview(self):
        h  = self.hour_sp.get()
        m  = self.min_sp.get()
        ap = "AM" if h < 12 else "PM"
        h12 = h % 12 or 12
        self.prev_lbl.config(text=f"{h:02d}:{m:02d}   {h12}:{m:02d} {ap}")

    # ─────────────────────────────── SAVE ────────────────────────────────────
    def _save(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Missing", "Please enter a title.",
                                   parent=self.win)
            return
        # In edit mode keep the original id and active state;
        # history is re-attached by _on_reminder_updated.
        rid    = self.existing["id"]     if self._edit_mode else str(uuid.uuid4())
        active = self.existing.get("active", True) if self._edit_mode else True
        selected_days = [d for d, v in self.day_vars.items() if v.get()]
        # Date only applies to one-time (non-repeating) reminders
        reminder_date = None if selected_days else self.cal.get_date().isoformat()
        self.on_save({
            "id":          rid,
            "title":       title,
            "description": self.desc_entry.get().strip(),
            "time":        f"{self.hour_sp.get():02d}:{self.min_sp.get():02d}",
            "date":        reminder_date,
            "days":        selected_days,
            "active":      active,
            "history":     []
        })
        self.win.destroy()


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys as _sys
    start_minimized = "--minimized" in _sys.argv or "-minimized" in _sys.argv
    app = ReminderApp(start_minimized=start_minimized)
    app.run()
