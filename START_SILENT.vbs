Set WshShell = CreateObject("WScript.Shell")
' Run the batch file with the --silent argument to trigger background mode immediately
WshShell.Run "START_HERE.bat --silent", 0, False
Set WshShell = Nothing
