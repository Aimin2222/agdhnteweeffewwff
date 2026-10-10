@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "AUTOCINE_GPU_EFFECTS=cpu"
echo CPU effects comparison. Encoder selection remains unchanged.
call START.bat
exit /b %ERRORLEVEL%
