@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "AUTOCINE_GPU_EFFECTS=hybrid"
echo Previous hybrid effects backend. UI and recording are unchanged.
call START_GPU.bat
exit /b %ERRORLEVEL%
