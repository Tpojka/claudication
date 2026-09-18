@echo off
REM Windows: remove Claudication.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py -3 -m claudication.install uninstall) else (python -m claudication.install uninstall)
