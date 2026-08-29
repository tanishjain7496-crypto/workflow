Set WinScriptHost = CreateObject("WScript.Shell")
scriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WinScriptHost.Run Chr(34) & scriptPath & "\launch_all.bat" & Chr(34), 0
Set WinScriptHost = Nothing
