# build.ps1
# Full build pipeline: clean → PyInstaller → Inno Setup → output summary
# Run from project root: .\build.ps1
# Optional: .\build.ps1 -Version "1.2.0" -Sign

param(
    [string]$Version   = "1.0.0",
    [switch]$Sign      = $false,
    [string]$CertFile  = "cert.pfx",
    [string]$CertPass  = "",
    [string]$Timestamp = "http://timestamp.sectigo.com"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Helpers ───────────────────────────────────────────────────────────────────
function Log($msg) { Write-Host "▶  $msg" -ForegroundColor Cyan }
function Ok($msg)  { Write-Host "✔  $msg" -ForegroundColor Green }
function Err($msg) { Write-Host "✖  $msg" -ForegroundColor Red; exit 1 }

function Require($cmd) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Err "Required tool not found: $cmd"
    }
}

# ── Prerequisites ─────────────────────────────────────────────────────────────
Require python
Require pyinstaller

$HasInno = Get-Command iscc -ErrorAction SilentlyContinue
$HasSigntool = Get-Command signtool -ErrorAction SilentlyContinue

# ── 0. Bump version in version_info.txt ───────────────────────────────────────
Log "Setting version to $Version"
$parts = $Version -split "\." | ForEach-Object { [int]$_ }
while ($parts.Count -lt 4) { $parts += 0 }
$verTuple = "($($parts -join ", "))"
$verStr   = "$Version.0"

(Get-Content version_info.txt) `
    -replace "filevers=\([\d, ]+\)", "filevers=$verTuple" `
    -replace "prodvers=\([\d, ]+\)", "prodvers=$verTuple" `
    -replace '"FileVersion",\s+"[\d.]+"', """FileVersion"",      ""$verStr""" `
    -replace '"ProductVersion",\s+"[\d.]+"', """ProductVersion"",   ""$verStr""" |
    Set-Content version_info.txt

# Also patch reminder_setup.iss
(Get-Content reminder_setup.iss) `
    -replace '#define AppVersion\s+"[\d.]+"', "#define AppVersion   ""$Version""" |
    Set-Content reminder_setup.iss

Ok "Version set to $Version"

# ── 1. Clean previous build ───────────────────────────────────────────────────
Log "Cleaning previous build artifacts..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist, __pycache__
Ok "Clean complete"

# ── 2. PyInstaller build ──────────────────────────────────────────────────────
Log "Running PyInstaller..."
& pyinstaller `
    --clean `
    reminder_app.spec

if ($LASTEXITCODE -ne 0) { Err "PyInstaller failed" }
Ok "PyInstaller complete → dist\ReminderManager.exe"

# ── 3. Code signing (optional) ────────────────────────────────────────────────
if ($Sign) {
    if (-not $HasSigntool) { Err "signtool.exe not found (install Windows SDK)" }
    if (-not (Test-Path $CertFile)) { Err "Certificate not found: $CertFile" }

    Log "Signing EXE..."
    $signArgs = @(
        "sign",
        "/f", $CertFile,
        "/t", $Timestamp,
        "/fd", "SHA256"
    )
    if ($CertPass) { $signArgs += @("/p", $CertPass) }
    $signArgs += "dist\ReminderManager.exe"

    & signtool @signArgs
    if ($LASTEXITCODE -ne 0) { Err "Code signing failed" }
    Ok "EXE signed"
}
else {
    Write-Host "ℹ  Skipping code signing (use -Sign to enable)" -ForegroundColor Yellow
}

# ── 4. Inno Setup ────────────────────────────────────────────────────────────
if ($HasInno) {
    Log "Building installer with Inno Setup..."
    New-Item -ItemType Directory -Force "dist\installer" | Out-Null
    & iscc reminder_setup.iss
    if ($LASTEXITCODE -ne 0) { Err "Inno Setup failed" }
    Ok "Installer created → dist\installer\ReminderManagerSetup-$Version.exe"

    if ($Sign) {
        Log "Signing installer..."
        $setupExe = "dist\installer\ReminderManagerSetup-$Version.exe"
        $signArgs = @("sign", "/f", $CertFile, "/t", $Timestamp, "/fd", "SHA256")
        if ($CertPass) { $signArgs += @("/p", $CertPass) }
        $signArgs += $setupExe
        & signtool @signArgs
        if ($LASTEXITCODE -ne 0) { Err "Installer signing failed" }
        Ok "Installer signed"
    }
}
else {
    Write-Host "ℹ  iscc not found — skipping Inno Setup step" -ForegroundColor Yellow
}

# ── 5. Size report ───────────────────────────────────────────────────────────
Log "Build summary"
$exePath  = "dist\ReminderManager.exe"
$isPath   = "dist\installer\ReminderManagerSetup-$Version.exe"

if (Test-Path $exePath) {
    $exeMB = [math]::Round((Get-Item $exePath).Length / 1MB, 1)
    Ok "EXE size: $exeMB MB  ($exePath)"
}
if (Test-Path $isPath) {
    $isMB  = [math]::Round((Get-Item $isPath).Length / 1MB, 1)
    Ok "Installer size: $isMB MB  ($isPath)"
}

Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "  Build complete — version $Version" -ForegroundColor White
Write-Host "════════════════════════════════════════" -ForegroundColor DarkGray
