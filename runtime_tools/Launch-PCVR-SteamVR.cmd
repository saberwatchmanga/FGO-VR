@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0FGO-PC\scripts\launch_pc.ps1" -Mode PcVr -OpenXrRuntime SteamVR %*
set "FGOVR_EXIT=%errorlevel%"
if not "%FGOVR_EXIT%"=="0" pause
exit /b %FGOVR_EXIT%
