@echo off
REM Windows: install Claudication (see claudication\install).
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py -3 -m claudication.install %*) else (python -m claudication.install %*)
