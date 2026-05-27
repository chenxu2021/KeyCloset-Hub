' KeyCloset Hub - 桌面启动脚本
' 双击此文件即可无命令行窗口启动应用
' 将此文件复制到桌面：右键 → 发送到 → 桌面快捷方式

Set WshShell = CreateObject("WScript.Shell")
scriptDir = WshShell.CurrentDirectory
' 获取脚本所在目录（.vbs 文件位置）
Set fso = CreateObject("Scripting.FileSystemObject")
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptPath
WshShell.Run "pythonw main.py", 0, False