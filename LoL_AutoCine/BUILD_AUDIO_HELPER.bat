@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo ================================================================
echo LoL AutoCine - Native Audio Helper Build
echo ================================================================
echo Started: %date% %time%
echo Working directory: %CD%
echo.

echo [1/3] Looking for Microsoft C++ compiler...
where cl >nul 2>nul
if errorlevel 1 (
  echo [INFO] MSVC cl.exe was not found.
  echo [INFO] Auto-installing Microsoft Visual Studio Build Tools if needed...
  call "%CD%\ENSURE_CPP_BUILD_TOOLS.bat"
  if errorlevel 1 (
    echo [FAIL] Could not prepare MSVC Build Tools.
    echo Finished: %date% %time%
    pause
    exit /b 2
  )
)

set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
set "VSINSTALL="
if exist "%VSWHERE%" (
  for /f "usebackq delims=" %%V in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSINSTALL=%%V"
)
if defined VSINSTALL (
  if exist "!VSINSTALL!\VC\Auxiliary\Build\vcvars64.bat" (
    call "!VSINSTALL!\VC\Auxiliary\Build\vcvars64.bat" >nul
  )
)

where cl >nul 2>nul
if errorlevel 1 (
  echo [FAIL] MSVC cl.exe is still unavailable after Build Tools setup.
  echo Finished: %date% %time%
  pause
  exit /b 3
)

echo [PASS] MSVC compiler is ready.
if not exist tools\native_audio\lol_audio_helper.cpp (
  echo [FAIL] Native audio helper source is missing.
  pause
  exit /b 4
)
if not exist tools\bin mkdir tools\bin

echo [2/3] Building native process-loopback helper...
cl /nologo /std:c++17 /EHsc /O2 /W3 /DUNICODE /D_UNICODE tools\native_audio\lol_audio_helper.cpp /Fe:tools\bin\lol_audio_helper.exe /link ole32.lib mmdevapi.lib avrt.lib
if errorlevel 1 (
  echo [FAIL] Native audio helper build failed.
  echo Finished: %date% %time%
  pause
  exit /b 5
)

echo [3/3] Verifying helper...
if not exist tools\bin\lol_audio_helper.exe (
  echo [FAIL] Helper EXE was not created.
  pause
  exit /b 6
)

echo [PASS] Native LoL process-loopback helper created:
echo        %CD%\tools\bin\lol_audio_helper.exe
echo Finished: %date% %time%
pause
exit /b 0
