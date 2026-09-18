@echo off
REM Windows entry point; the real uninstaller is install.py.
where py >nul 2>nul
if %errorlevel%==0 (py -3 "%~dp0install.py" uninstall) else (python "%~dp0install.py" uninstall)
