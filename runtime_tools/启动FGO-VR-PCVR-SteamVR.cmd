@echo off
setlocal
call "%~dp0Launch-PCVR-SteamVR.cmd" %*
exit /b %errorlevel%
