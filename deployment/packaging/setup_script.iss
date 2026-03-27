; Inno Setup Script for Aamusted Counselling Management System
; Highly Recommended: Install Inno Setup (jrsoftware.org) then run this script.

#define MyAppName "USTED Counselling System"
#define MyAppVersion "2.1.0"
#define MyAppPublisher "USTED Counselling System"
#define MyAppURL "https://github.com/kingenious0/Aamusted-Counselling"
#define MyAppExeName "USTED_Counseling_System.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{4787FF60-AAMU-STED-SYS-SETUP}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist_installer
OutputBaseFilename=Usted_Counselling_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
CloseApplications=force
; SetupIconFile=..\..\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Run at Windows Startup"; GroupDescription: "Additional Options:"; Flags: checkedonce

[Files]
Source: "..\..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Include templates and assets if they are NOT already bundled in the --onefile EXE
; (PyInstaller usually bundles them if specified in .spec or build script)
; Source: "..\..\templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "..\..\static\*"; DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "..\..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
