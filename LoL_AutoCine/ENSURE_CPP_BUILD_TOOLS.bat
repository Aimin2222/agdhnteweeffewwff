@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo ================================================================
echo LoL AutoCine - C++ Build Tools Auto Installer
echo ================================================================

echo [1/4] Checking existing MSVC...
where cl >nul 2>nul
if not errorlevel 1 (
  echo [PASS] MSVC cl.exe is already available.
  exit /b 0
)

set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE%" (
  for /f "usebackq delims=" %%V in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSINSTALL=%%V"
  if defined VSINSTALL (
    echo [PASS] Visual Studio Build Tools found: !VSINSTALL!
    exit /b 0
  )
)

echo [2/4] Checking winget...
where winget >nul 2>nul
if errorlevel 1 (
  echo [FAIL] winget is not available on this Windows installation.
  echo Install Microsoft App Installer, then run this file again.
  exit /b 2
)

echo [3/4] Installing Microsoft Visual Studio Build Tools...
echo [INFO] This requires administrator permission and may take several minutes.
echo [INFO] Only the C++ desktop build workload is requested.
echo.
winget install -e --id Microsoft.VisualStudio.BuildTools --accept-source-agreements --accept-package-agreements --override "--quiet --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
if errorlevel 1 (
  echo [WARN] winget installation returned a non-zero code.
  echo [INFO] The installer may have been cancelled or may require UAC approval.
)

echo [4/4] Verifying the installation...
if exist "%VSWHERE%" (
  for /f "usebackq delims=" %%V in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSINSTALL=%%V"
)
if defined VSINSTALL (
  echo [PASS] Build Tools installation detected: !VSINSTALL!
  exit /b 0
)

where cl >nul 2>nul
if not errorlevel 1 (
  echo [PASS] cl.exe is available.
  exit /b 0
)

echo [FAIL] Visual Studio Build Tools could not be detected after installation.
echo Please run ENSURE_CPP_BUILD_TOOLS.bat again and approve any UAC prompt.
exit /b 3
