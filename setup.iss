; Inno Setup Script for Supertonic Voice
#define MyAppName "Supertonic Voice"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "yasser-27"
#define MyAppURL "https://github.com/yasser-27"
#define MyAppExeName "SupertonicVoice.exe"

[Setup]
AppId={{8B3C187E-B8C2-4E80-8777-1F4F9B4D9E2E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=SupertonicVoiceSetup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\SupertonicVoice\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SupertonicVoice\tts_worker.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SupertonicVoice\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SupertonicVoice\config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SupertonicVoice\onnx\*"; DestDir: "{app}\onnx"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\SupertonicVoice\voice_styles\*"; DestDir: "{app}\voice_styles"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\SupertonicVoice\chrome_extension\*"; DestDir: "{app}\chrome_extension"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
