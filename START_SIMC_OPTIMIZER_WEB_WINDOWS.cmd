@echo off
setlocal EnableExtensions
rem P1 local-only web user app. Do not install packages, alter PATH, run SimC,
rem or move/cache/promote any previously measured Native evidence here.
pushd "%~dp0" || (
  echo Cannot enter the application directory.
  pause
  exit /b 2
)
if not exist "runner\v113_local_web_api.py" goto :missing_project

rem Relative sibling location supports a portable home/work project+batch ZIP.
rem The default user home is the original Windows Native v147 location.
set "BATCH_ROOT="
if exist "%~dp0..\v147_batch\" set "BATCH_ROOT=%~dp0..\v147_batch"
if not defined BATCH_ROOT if exist "%USERPROFILE%\SIMC_Secondary_Optimizer\v147_batch\" set "BATCH_ROOT=%USERPROFILE%\SIMC_Secondary_Optimizer\v147_batch"

echo.
echo SIMC SECONDARY OPTIMIZER - local Windows web app
echo Project: %CD%
if defined BATCH_ROOT (
  echo Saved v147 Native results: %BATCH_ROOT%
  echo Note: these results are VIEW-ONLY, not imported execution caches.
) else (
  echo No saved v147_batch folder found. New user sessions remain available.
)
echo The browser will open at http://127.0.0.1:8765/ when the server is ready.
echo Press Ctrl+C in this window to stop the server.
echo.

where py >nul 2>&1
if not errorlevel 1 goto :using_py
where python >nul 2>&1
if not errorlevel 1 goto :using_python
echo ERROR: Python launcher not found. Install Python 3.12+.
goto :failed

:using_py
py -3 -c "import sys,fastapi,uvicorn; assert sys.version_info >= (3,12)" >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python 3.12+ with FastAPI and Uvicorn required.
  echo Run: py -3 -m pip install -r requirements-web.txt
  goto :failed
)
if /I "%~1"=="--check" goto :check
if defined BATCH_ROOT (
  py -3 "runner\v113_local_web_api.py" --open-browser --batch-root "%BATCH_ROOT%"
) else (
  py -3 "runner\v113_local_web_api.py" --open-browser
)
goto :finished

:using_python
python -c "import sys,fastapi,uvicorn; assert sys.version_info >= (3,12)" >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python 3.12+ with FastAPI and Uvicorn required.
  echo Run: python -m pip install -r requirements-web.txt
  goto :failed
)
if /I "%~1"=="--check" goto :check
if defined BATCH_ROOT (
  python "runner\v113_local_web_api.py" --open-browser --batch-root "%BATCH_ROOT%"
) else (
  python "runner\v113_local_web_api.py" --open-browser
)
goto :finished

:check
echo READY: Python and web dependencies found. This check ran no SimC and started no web server.
popd
endlocal
exit /b 0

:missing_project
echo ERROR: runner\v113_local_web_api.py is missing in this folder.
:failed
popd
echo.
echo The web app did not start. See the message above.
pause
endlocal
exit /b 3

:finished
set "APP_EXIT=%ERRORLEVEL%"
popd
if not "%APP_EXIT%"=="0" (
  echo.
  echo Web server stopped with an error. Check whether port 8765 is in use.
  pause
)
endlocal & exit /b %APP_EXIT%
