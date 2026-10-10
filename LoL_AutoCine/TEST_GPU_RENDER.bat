@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
if not exist "diagnostics" mkdir "diagnostics"
> "diagnostics\gpu_test_launcher.log" echo GPU render test launcher
py -3 -c "import sys; print(sys.executable)" >> "diagnostics\gpu_test_launcher.log" 2>&1
if not errorlevel 1 goto launch_py
if exist ".venv\Scripts\python.exe" goto launch_venv
python -c "import sys; print(sys.executable)" >> "diagnostics\gpu_test_launcher.log" 2>&1
if not errorlevel 1 goto launch_python
set "test_result=2"
echo No usable Python found. Install Python 3 with the py launcher.
>> "diagnostics\gpu_test_launcher.log" echo ERROR: No usable Python found.
goto finish
:launch_py
py -3 tools\gpu_render_test.py %*
goto result
:launch_venv
".venv\Scripts\python.exe" tools\gpu_render_test.py %*
goto result
:launch_python
python tools\gpu_render_test.py %*
:result
set "test_result=%ERRORLEVEL%"
:finish
>> "diagnostics\gpu_test_launcher.log" echo Exit code: %test_result%
echo.
echo Test exit code: %test_result%
echo See diagnostics\gpu_test_launcher.log and gpu_test_startup logs.
echo Run COLLECT_DIAGNOSTICS.bat after checking the output.
pause
exit /b %test_result%
