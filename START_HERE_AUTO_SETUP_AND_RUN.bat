@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
pushd "%~dp0" >nul 2>&1
if errorlevel 1 goto :folder_error

if not exist "runner\v113_local_web_api.py" (
  echo [ERROR] This file must be next to START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd
  echo and the runner folder. Please extract the ZIP first.
  goto :failed
)
if not exist "requirements-web.txt" (
  echo [ERROR] Missing requirements-web.txt. Extract the complete ZIP.
  goto :failed
)

echo ================================================
echo  SIMC SECONDARY OPTIMIZER - EASY START
echo ================================================
echo  This helper checks Python, installs required
echo  web libraries only with your permission,
echo  and starts the LOCAL app on 127.0.0.1.
echo  No SimC calculation or season update is run.
echo.

:check_python
set "SYS_PY="
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys; sys.exit(0 if sys.version_info.major == 3 and sys.version_info.minor >= 12 else 1)" >nul 2>&1
  if not errorlevel 1 set "SYS_PY=py -3"
)
if not defined SYS_PY (
  where python >nul 2>&1
  if not errorlevel 1 (
    python -c "import sys; sys.exit(0 if sys.version_info.major == 3 and sys.version_info.minor >= 12 else 1)" >nul 2>&1
    if not errorlevel 1 set "SYS_PY=python"
  )
)
if not defined SYS_PY goto :python_missing

set "VENV_DIR=%LOCALAPPDATA%\SIMC_Secondary_Optimizer\web-python"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
if not exist "%VENV_PY%" goto :setup_venv
"%VENV_PY%" -c "import sys,fastapi,uvicorn; sys.exit(0 if sys.version_info.major == 3 and sys.version_info.minor >= 12 else 1)" >nul 2>&1
if errorlevel 1 goto :setup_venv
goto :start_app

:setup_venv
echo [SETUP] Python 3.12+ found. Web libraries need setup.
echo         Libraries will go into your local app environment:
echo         %VENV_DIR%
echo         Existing SimC files, settings, and results stay unchanged.
choice /C YN /N /M "Install or repair web libraries now? [Y/N]: "
if errorlevel 2 goto :cancelled
echo.
if not exist "%VENV_PY%" (
  %SYS_PY% -m venv "%VENV_DIR%"
  if errorlevel 1 goto :venv_failed
)
"%VENV_PY%" -m pip install --disable-pip-version-check --no-input -r "requirements-web.txt"
if errorlevel 1 goto :pip_failed
"%VENV_PY%" -c "import sys,fastapi,uvicorn; sys.exit(0 if sys.version_info.major == 3 and sys.version_info.minor >= 12 else 1)" >nul 2>&1
if errorlevel 1 goto :pip_failed
echo [READY] Web libraries installed.
echo.

:start_app
if /I "%~1"=="--check" (
  echo [READY] Local Python environment is working. No server started.
  goto :ok
)
echo [START] Opening local app. Close this window or press Ctrl+C to stop it.
echo [START] http://127.0.0.1:8765/
echo.
set "BATCH_ROOT="
if exist "%~dp0..\v147_batch\" set "BATCH_ROOT=%~dp0..\v147_batch"
if not defined BATCH_ROOT if exist "%USERPROFILE%\SIMC_Secondary_Optimizer\v147_batch\" set "BATCH_ROOT=%USERPROFILE%\SIMC_Secondary_Optimizer\v147_batch"
if defined BATCH_ROOT (
  "%VENV_PY%" "runner\v113_local_web_api.py" --open-browser --batch-root "%BATCH_ROOT%"
) else (
  "%VENV_PY%" "runner\v113_local_web_api.py" --open-browser
)
set "APP_EXIT=%ERRORLEVEL%"
if not "%APP_EXIT%"=="0" goto :app_failed
goto :ok

:python_missing
if "%PYTHON_INSTALL_ATTEMPTED%"=="1" goto :manual_python
echo [PYTHON] Python 3.12 or newer was not found.
where winget >nul 2>&1
if errorlevel 1 goto :manual_python
choice /C YN /N /M "Install official Python 3.12 with Windows Package Manager? [Y/N]: "
if errorlevel 2 goto :manual_python
set "PYTHON_INSTALL_ATTEMPTED=1"
winget install --id Python.Python.3.12 --exact --source winget --accept-source-agreements --accept-package-agreements
if errorlevel 1 goto :manual_python
echo [PYTHON] Installation attempted. Rechecking...
goto :check_python

:manual_python
echo Please install Python 3.12+ from the official Python website,
echo then double-click this helper again.
echo https://www.python.org/downloads/windows/
choice /C YN /N /M "Open the official Python download page? [Y/N]: "
if not errorlevel 2 start "" "https://www.python.org/downloads/windows/"
goto :failed

:venv_failed
echo [ERROR] Could not make a user-local Python environment.
goto :failed
:pip_failed
echo [ERROR] Dependency install failed. Read the pip error above.
echo Check internet access and the requirements-web.txt file.
echo No optimizer or SimC run was started.
goto :failed
:app_failed
echo [ERROR] The local web server exited with an error.
echo Check the output above or whether port 8765 is already in use.
goto :failed
:cancelled
echo [CANCELLED] No package installation was requested.
goto :ok
:folder_error
echo [ERROR] Could not open the extracted folder.
goto :failed
:failed
echo.
echo Press any key to close this window.
pause >nul
popd >nul 2>&1
endlocal
exit /b 1
:ok
popd >nul 2>&1
endlocal
exit /b 0
