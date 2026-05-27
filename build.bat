@echo off
REM ============================================================
REM KeyCloset Hub - PyInstaller 一键打包脚本
REM
REM 功能: 将 KeyCloset Hub 打包为独立 .exe 文件
REM 输出: dist/KeyClosetHub.exe
REM
REM 前置条件:
REM   1. Python 3.8+ 已安装
REM   2. 已安装依赖: pip install -r requirements.txt
REM   3. 已安装 PyInstaller: pip install pyinstaller
REM ============================================================

echo.
echo ========================================
echo   KeyCloset Hub - PyInstaller Build
echo ========================================
echo.

REM 清理旧的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /f /q *.spec

echo [1/3] 正在打包为单文件 .exe ...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name KeyClosetHub ^
    --add-data "keycloset;keycloset" ^
    --hidden-import markdown ^
    --hidden-import markdown.extensions.extra ^
    --hidden-import markdown.extensions.codehilite ^
    --hidden-import markdown.extensions.fenced_code ^
    --hidden-import pygments ^
    --hidden-import pygments.lexers ^
    --hidden-import cryptography ^
    --hidden-import cryptography.hazmat.backends.openssl ^
    --clean ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 打包失败，请检查错误信息。
    pause
    exit /b 1
)

echo.
echo [2/3] 打包完成！
echo.

REM 检查输出文件
if exist "dist\KeyClosetHub.exe" (
    echo [3/3] 输出文件:
    echo        %CD%\dist\KeyClosetHub.exe
    echo.
    echo ========================================
    echo   打包成功！双击 dist\KeyClosetHub.exe 即可运行
    echo ========================================
) else (
    echo [ERROR] 未找到输出文件，打包可能失败。
)

echo.
pause