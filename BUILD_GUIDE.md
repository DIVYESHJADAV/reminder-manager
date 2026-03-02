# Reminder Manager — Build & Distribution Guide

## Project Structure

```
reminder-manager/
├── reminder_app.py          # Main application
├── updater.py               # Auto-update module
├── reminder_app.spec        # PyInstaller config (optimized)
├── version_info.txt         # Windows PE version metadata
├── ReminderManager.exe.manifest  # Windows app manifest
├── reminder_setup.iss       # Inno Setup installer script
├── build.ps1                # Full build pipeline (PowerShell)
├── icon.ico                 # App icon (you provide this)
├── version.json             # Hosted on your server for update checks
└── dist/
    ├── ReminderManager.exe           # Built by PyInstaller
    └── installer/
        └── ReminderManagerSetup-1.0.0.exe   # Built by Inno Setup
```

---

## 1. EXE Size Reduction (20 MB → ~6 MB)

### Quick build command
```powershell
pyinstaller --clean reminder_app.spec
```

### Why the spec file, not a raw command?
The `.spec` file gives fine-grained control over `excludes=[]` — the single biggest lever for size reduction. The raw command has no way to exclude specific stdlib modules.

### What gets excluded and why

| Module group | Reason excluded | Approx saving |
|---|---|---|
| `numpy`, `pandas`, `scipy` | Data science stack, never imported | ~6 MB |
| `matplotlib` | Chart library | ~3 MB |
| `requests`, `urllib3`, `certifi` | App uses `urllib` (stdlib) for updates | ~1 MB |
| `PIL` / `Pillow` | Image processing, not used | ~2 MB |
| `asyncio`, `multiprocessing` | App is threaded with `threading` | ~0.5 MB |
| `email`, `smtplib`, `imaplib` | No email features | ~0.3 MB |
| `sqlite3` | App uses JSON files for storage | ~0.5 MB |
| `setuptools`, `pip` | Build tools, never runtime | ~1.5 MB |
| `tkinter.test`, `turtle` | Unused Tk extras | ~0.3 MB |

### UPX: do NOT use it
UPX (`upx=True`) saves ~30% but is the **#1 cause of AV false positives**. The size savings are not worth the detection risk. Set `upx=False` in the spec (already done).

---

## 2. Reducing Antivirus False Positives

Current typical result with a raw PyInstaller build: **3–8 / 72** on VirusTotal.  
Goal: **0–1 / 72**.

### Root causes of false positives

| Cause | Fix |
|---|---|
| UPX compression | `upx=False` ✓ (already in spec) |
| No version metadata | `version_info.txt` ✓ |
| No code signature | Sign with a real cert (see below) |
| No app manifest | `ReminderManager.exe.manifest` ✓ |
| Generic EXE name | Use `ReminderManager.exe`, not `app.exe` |
| `strip=True` | `strip=False` ✓ (already in spec) |

### Priority order for AV reduction

**Level 1 — Free, do now** (already implemented in these files):
- Proper version metadata via `version_info.txt`
- App manifest declaring `asInvoker` trust level
- Meaningful EXE name
- No UPX

**Level 2 — Submit for whitelisting** (free, takes 1–5 days):
Submit your EXE to these AV vendors' false-positive portals:
- Windows Defender: https://www.microsoft.com/en-us/wdsi/filesubmission
- Avast: https://www.avast.com/en-us/report-a-false-positive.php
- AVG: https://www.avg.com/en-us/submit-sample
- Bitdefender: https://www.bitdefender.com/submit/

**Level 3 — Code signing certificate** (~$50–$300/year):
```powershell
# After getting a cert (.pfx file):
.\build.ps1 -Version "1.0.0" -Sign -CertFile "mycert.pfx" -CertPass "mypassword"
```

Recommended CAs for individual developers:
- **Sectigo** (~$70/yr) — most widely recognized
- **DigiCert** (~$300/yr) — highest trust
- **SignPath.io** — free for open source

A valid code signature typically reduces detections to **0 / 72**.

### Things to avoid in your app code
- No `subprocess.Popen` with shell commands (already avoided)
- No downloading EXEs and running them silently (updater prompts user)
- No writing to `HKLM` registry (Inno Setup uses `HKCU`)
- No modifying system files
- Store data in `%APPDATA%`, not next to the EXE

---

## 3. Auto-Update System

### How it works
```
App starts
    │
    ▼ (background thread, non-blocking)
Fetch version.json from your server
    │
    ├─ version same or older → do nothing
    │
    └─ newer version found → show UpdateDialog popup
                                    │
                                    ├─ user clicks "Skip" → close dialog
                                    │
                                    └─ user clicks "Download & Install"
                                            │
                                            ▼
                                    Download installer to %TEMP%
                                            │
                                            ▼
                                    Launch installer (subprocess.Popen)
                                            │
                                            ▼
                                    Exit app (so installer can replace files)
```

### Integrating into reminder_app.py
Add two lines to your main window's `__init__` after the window is shown:

```python
# At top of file:
from updater import check_for_updates_async, CURRENT_VERSION

# In ReminderApp.__init__, after mainloop setup but before mainloop():
self.root.after(3000, lambda: check_for_updates_async(self.root))
# 3-second delay so the update check doesn't slow initial startup
```

### Hosting version.json

**Option A — GitHub Releases** (free, recommended):
```
https://github.com/youruser/reminder-manager/releases/latest/download/version.json
```
Update `UPDATE_CHECK_URL` in `updater.py` to this URL.

In each release, upload:
- `version.json` (updated version number + installer URL)
- `ReminderManagerSetup-X.Y.Z.exe`

**Option B — Simple web server**:
Upload `version.json` to any static hosting (GitHub Pages, Netlify, S3, Cloudflare R2).

### version.json format
```json
{
  "version": "1.2.0",
  "installer_url": "https://github.com/youruser/reminder-manager/releases/download/v1.2.0/ReminderManagerSetup-1.2.0.exe",
  "release_notes": "Fixed postpone timer. Added dark mode option.",
  "min_supported_version": "1.0.0"
}
```

---

## 4. Full Build Pipeline

### First-time setup
```powershell
# Install PyInstaller
pip install pyinstaller

# Install Inno Setup (download from https://jrsoftware.org/isinfo.php)
# After install, ensure iscc.exe is in PATH
```

### Release workflow
```powershell
# 1. Build everything (no signing)
.\build.ps1 -Version "1.1.0"

# 2. Build + sign (requires cert)
.\build.ps1 -Version "1.1.0" -Sign -CertFile "cert.pfx" -CertPass "password"

# 3. Upload to GitHub Releases or your server:
#    - dist\installer\ReminderManagerSetup-1.1.0.exe
#    - version.json (update version + installer_url)
```

### Expected output sizes

| File | Target size |
|---|---|
| `ReminderManager.exe` | ~6–8 MB |
| `ReminderManagerSetup-X.Y.Z.exe` | ~5–7 MB (installer compresses it) |

---

## 5. Security Best Practices Summary

| Practice | Status |
|---|---|
| Store user data in `%APPDATA%` | ✅ Already implemented |
| No admin rights required | ✅ `asInvoker` manifest |
| HTTPS for update checks | ✅ urllib with HTTPS URL |
| User prompted before installing update | ✅ UpdateDialog requires click |
| Installer downloaded to `%TEMP%`, not app dir | ✅ |
| No silent background installs | ✅ |
| UPX disabled | ✅ |
| Version metadata embedded | ✅ |
| Code signing | ⬜ Requires your certificate |
| AV vendor whitelisting | ⬜ Submit after first build |
