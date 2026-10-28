#define AppName "FileProof"
#define AppVersion "0.2.0"
#define AppPublisher "Final Vestige Studios"
[Setup]
AppId={{F7D3B4A2-AB45-45A9-9B6C-F27A540D8720}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\\Final Vestige Studios\\FileProof
DefaultGroupName=Final Vestige Studios
OutputDir=..\\..\\dist\\installers
OutputBaseFilename=FileProof-Setup-{#AppVersion}-win64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\\FileProof.exe
[Files]
Source: "..\\..\\dist\\FileProof.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\\..\\dist\\FileProofCLI.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\\FileProof"; Filename: "{app}\\FileProof.exe"
Name: "{autodesktop}\\FileProof"; Filename: "{app}\\FileProof.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
[Run]
Filename: "{app}\\FileProof.exe"; Description: "Launch FileProof"; Flags: nowait postinstall skipifsilent
