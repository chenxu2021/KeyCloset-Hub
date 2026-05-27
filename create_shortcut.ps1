# KeyCloset Hub - 桌面快捷方式生成脚本
# 用法: 右键 → 使用 PowerShell 运行

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$vbsPath = Join-Path $projectDir "KeyClosetHub.vbs"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "KeyCloset Hub.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$vbsPath`""
$Shortcut.WorkingDirectory = $projectDir
$Shortcut.IconLocation = "shell32.dll,48"
$Shortcut.Save()

Write-Host "✓ 桌面快捷方式已创建: $shortcutPath"