@echo off
setlocal EnableExtensions
REM P1 Bounded batch: 24 UNPROMOTED DPS, source-free profile physical smoke
REM and (only after exact physical PASS) existing v094 DPS/SEM/95%% solver.
REM Example: RUN_ALL_24_SIMC_NATIVE.cmd "C:\SimC\simc.exe" 7bc10711b5
REM The revision MUST match your REAL SimC binary. Never use the example SHA.
if "%~1"=="" goto usage
if "%~2"=="" goto usage
if not exist "%~1" (
  echo SIMC_BINARY_NOT_FOUND: %~1
  exit /b 3
)
cd /d "%~dp0.."
if errorlevel 1 (
  echo WORKING_DIRECTORY_FAILED
  exit /b 3
)
python integration_probes\v147_all_dps_targeted_native_batch.py --simc "%~1" --revision "%~2" --execute --max-new-physical 24 --optimize-accepted
exit /b %ERRORLEVEL%
:usage
echo USAGE: %~nx0 "C:\path\simc.exe" ACTUAL_SIMC_GIT_REVISION
echo Requires Python 3, a real Windows SimulationCraft executable and an exact revision.
echo The first valid run may execute up to 24 physical plus 144 adaptive Native calls.
exit /b 2
