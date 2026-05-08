@echo off
setlocal

cd /d "%~dp0"

echo [1/2] Building NandemoShortcut.exe and NandemoShortcutLauncher.exe...
python -m PyInstaller NandemoShortcut.spec --noconfirm
if errorlevel 1 goto :build_failed

echo [2/2] Build completed.
echo Output: "%~dp0dist\NandemoShortcut.exe"
echo Output: "%~dp0dist\NandemoShortcutLauncher.exe"
goto :end

:build_failed
echo.
echo Build failed.
echo If the EXE is running, close it and try again.

:end
echo.
pause
