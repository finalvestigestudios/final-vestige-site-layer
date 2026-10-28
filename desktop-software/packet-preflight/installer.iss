#define AppName "Packet Preflight"
#define AppExe "PacketPreflight.exe"
#define AppVersion "0.1.0"
[Setup]
AppId={{8239DA45-D392-4E10-A3C0-97AAE1645102}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Final Vestige Studios
DefaultDirName={autopf}\Final Vestige Studios\{#AppName}
DefaultGroupName=Final Vestige Studios
OutputDir=..\..\dist\installers
OutputBaseFilename=PacketPreflight-Setup-{#AppVersion}-win64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#AppExe}
[Files]
Source: "..\..\dist\{#AppExe}"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
