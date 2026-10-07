@echo off
setlocal
python.exe "%~dp0FGO-Resolution\scripts\settings.py"
if errorlevel 1 pause
