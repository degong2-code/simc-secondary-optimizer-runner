@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "runner\v106_windows_simple_gui.py"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Python 3 was not found. Install Python 3 with Tkinter support.
    pause
    exit /b 3
  )
  python "runner\v106_windows_simple_gui.py"
)
if errorlevel 1 (
  echo SimC optimizer window could not be started. See the error above.
  pause
)
endlocal
