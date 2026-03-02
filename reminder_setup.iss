; reminder_setup.iss
; Inno Setup 6.x installer script for Reminder Manager
; Download Inno Setup: https://jrsoftware.org/isinfo.php
;
; Usage: Right-click this file → Compile in Inno Setup IDE
;        or: iscc.exe reminder_setup.iss

#define AppName      "Reminder Manager"
#define AppVersion   "1.0.0"
#define AppPublisher "Your Company Name"
#define AppURL       "https://myserver.com/reminder/"
#define AppExeName   "ReminderManager.exe"
#define AppMutex     "ReminderManagerSingleInstance"

[Setup]
; ── Identity ──────────────────────────────────────────────────────────────────
AppId={{YOUR-GUID-HERE-GENERATE-ONE}}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}support/
AppUpdatesURL={#AppURL}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Installer

; ── Install destination ────────────────────────────────────────────────────────
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
AllowNoIcons=yes

; ── Output ─────────────────────────────────────────────────────────────────────
OutputDir=dist\installer
OutputBaseFilename=ReminderManagerSetup-{#AppVersion}
SetupIconFile=icon.ico

; ── Anti-AV best practices ────────────────────────────────────────────────────
; Do NOT use LZMA solid compression — can look like packing to some AV engines
Compression=lzma2/fast
SolidCompression=no

; ── Privileges ────────────────────────────────────────────────────────────────
; Install for current user only — no UAC prompt, no admin rights needed
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; ── Signing (fill in when you have a code-signing certificate) ────────────────
; SignTool=signtool sign /f "cert.pfx" /p "password" /t http://timestamp.sectigo.com $f
; SignedUninstaller=yes

; ── Misc ──────────────────────────────────────────────────────────────────────
WizardStyle=modern
ShowLanguageDialog=no
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
CloseApplications=yes
CloseApplicationsFilter={#AppExeName}
AppMutex={#AppMutex}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "Create a &desktop shortcut";  GroupDescription: "Additional icons:"
Name: "startupentry";   Description: "Start Reminder Manager with &Windows"; GroupDescription: "Startup:"

[Files]
; Main executable (built by PyInstaller)
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Application manifest (optional — PyInstaller may already embed it)
; Source: "ReminderManager.exe.manifest"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\{#AppName}";           Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; Desktop (optional task)
Name: "{autodesktop}\{#AppName}";     Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#AppName}"; ValueData: """{app}\{#AppExeName}"""; Flags: uninsdeletevalue; Tasks: startupentry

[Run]
; Launch app after installation (optional)
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up user data on uninstall (optional — comment out to preserve data)
; Type: filesandordirs; Name: "{userappdata}\Reminder Manager"
