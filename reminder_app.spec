# reminder_app.spec
# Optimized PyInstaller spec file for Reminder Manager
# Run with: pyinstaller reminder_app.spec
#
# Prerequisites:
#   pip install pyinstaller
#   Optional: pip install pyinstaller-hooks-contrib

import sys
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

block_cipher = None

# ── Analysis ───────────────────────────────────────────────────────────────────
a = Analysis(
    ["reminder_app.py"],
    pathex=[],
    binaries=[],
    datas=[
        # Include updater module alongside main app
        ("updater.py", "."),
    ],
    hiddenimports=[
        # tkinter sub-modules PyInstaller sometimes misses
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.simpledialog",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],

    # ── CRITICAL: Exclude everything you don't use ─────────────────────────────
    excludes=[
        # Scientific / data stack (never used in this app)
        "numpy", "pandas", "scipy", "matplotlib",
        "PIL", "Pillow", "cv2", "sklearn",

        # Web / network frameworks
        "flask", "django", "fastapi", "aiohttp",
        "requests",          # app uses urllib only
        "urllib3", "certifi", "charset_normalizer", "idna",

        # Crypto / SSL (not needed for simple urllib HTTP)
        # Comment these out if you re-enable HTTPS update checks via requests
        # "ssl", "cryptography",

        # Test frameworks
        "pytest", "unittest", "doctest",

        # Build / packaging tools
        "setuptools", "pip", "pkg_resources",
        "distutils",

        # Logging extras rarely needed
        "logging.handlers",

        # XML / HTML parsers not used
        "xml.etree", "html.parser", "html5lib", "lxml",

        # Database drivers
        "sqlite3",           # comment out if you add local DB later
        "sqlalchemy", "psycopg2", "pymysql",

        # Tkinter backends we don't use
        "tkinter.test",
        "turtle",

        # Python extras
        "pdb", "profile", "cProfile",
        "pickle", "shelve",
        "multiprocessing",
        "concurrent.futures",
        "asyncio",
        "email",
        "mailbox",
        "imaplib", "smtplib", "poplib",
        "ftplib", "telnetlib",
        "xmlrpc",
        "http.server",
        "socketserver",

        # Unused stdlib
        "calendar",
        "curses",
        "readline",
        "rlcompleter",
        "plistlib",
        "ctypes.test",
        "lib2to3",
        "ensurepip",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ── Remove unused binaries auto-detected by PyInstaller ───────────────────────
# Filter out DLLs we know are not needed to trim further
EXCLUDE_BINARIES = {
    # OpenSSL — comment out if HTTPS updater via requests needs it
    # "_ssl",
    # Tcl/Tk extras we don't use
    "tcl86t.dll", "tk86t.dll",   # keep only if Tk version differs
}

# (Advanced) Strip unused collected items:
a.binaries = [(name, path, kind)
              for name, path, kind in a.binaries
              if not any(ex.lower() in name.lower() for ex in EXCLUDE_BINARIES)]

# ── PYZ (bytecode archive) ─────────────────────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── EXE ────────────────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="ReminderManager",          # Final EXE name
    debug=False,
    bootloader_ignore_signals=False,

    # ── Anti-AV: do NOT strip symbols, do NOT use UPX ─────────────────────────
    strip=False,                     # stripping can confuse AV heuristics
    upx=False,                       # UPX packing is the #1 cause of AV flags
    upx_exclude=[],

    # ── Console & icon ─────────────────────────────────────────────────────────
    console=False,                   # --noconsole: no terminal window
    disable_windowed_traceback=True,

    # ── Windows version metadata (reduces AV suspicion) ────────────────────────
    version="version_info.txt",      # See version_info.txt below
    icon="icon.ico",                 # Provide a real .ico file
)
