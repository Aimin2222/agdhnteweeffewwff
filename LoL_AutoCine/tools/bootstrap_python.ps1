param(
    [ValidateSet('Start', 'Setup', 'Probe', 'Diagnostics')][string]$Mode = 'Start',
    [string]$RequestedVersion = '3.12'
)
$ErrorActionPreference = 'Stop'
$appRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $appRoot
$requested = $RequestedVersion.TrimStart('-')
if (-not $requested -or $requested -eq '3') { $requested = '3.12' }
if ($requested -notmatch '^3\.\d+$') { Write-Host 'Invalid Python version.'; exit 2 }

function Find-Python {
    $candidates = @()
    if ($env:AUTOCINE_PYTHON) { $candidates += $env:AUTOCINE_PYTHON }
    $candidates += (Join-Path $appRoot '.venv\Scripts\python.exe')
    # Codex includes a real Python runtime even when Windows has no py launcher.
    $candidates += (Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        try {
            $found = & $launcher.Source "-$requested" -c 'import sys; print(sys.executable)' 2>$null
            if ($LASTEXITCODE -eq 0 -and $found) { $candidates += [string]($found | Select-Object -Last 1) }
        } catch { }
    }
    foreach ($name in @('python.exe', 'python3.exe')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command -and $command.Source -notmatch '\\WindowsApps\\') { $candidates += $command.Source }
    }
    foreach ($parent in @((Join-Path $env:LOCALAPPDATA 'Programs\Python'), $env:ProgramFiles)) {
        if (Test-Path -LiteralPath $parent) {
            $candidates += @(Get-ChildItem -LiteralPath $parent -Directory -Filter 'Python*' -ErrorAction SilentlyContinue |
                ForEach-Object { Join-Path $_.FullName 'python.exe' })
        }
    }
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (-not $candidate -or $candidate -match '\\WindowsApps\\' -or -not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
        try {
            $version = & $candidate -c "import sys,struct; print('%d.%d,%d' % (sys.version_info.major,sys.version_info.minor,struct.calcsize('P')*8))" 2>$null
            if ($LASTEXITCODE -eq 0 -and $version -eq "$requested,64") { return $candidate }
        } catch { }
    }
    return $null
}

try {
    $python = Find-Python
    if (-not $python) {
        Write-Host "[Python] Python $requested (64-bit) was not found. Install it, then run START.bat again."
        Write-Host '[Python] You may also set AUTOCINE_PYTHON to an existing python.exe.'
        exit 2
    }
    Write-Host "[Python] Found: $python"
    if ($Mode -eq 'Probe') { exit 0 }
    if ($Mode -eq 'Diagnostics') {
        # The collector uses only the standard library. Never require pip or LoL.
        & $python (Join-Path $appRoot 'tools\collect_diagnostics.py')
        exit $LASTEXITCODE
    }

    $venv = Join-Path $appRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venv -PathType Leaf)) {
        if (Test-Path -LiteralPath (Join-Path $appRoot '.venv')) {
            Write-Host '[Python] Existing .venv is incomplete. Keep it as a backup and run setup again.'
            exit 3
        }
        Write-Host '[Python] Preparing a local environment (first start only)...'
        & $python -m venv (Join-Path $appRoot '.venv')
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    & $venv -c "import sys,struct; assert sys.version_info[:2] == tuple(map(int,sys.argv[1].split('.'))) and struct.calcsize('P')==8" $requested
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[Python] Existing .venv does not match the requested Python. No files were removed.'
        exit 3
    }
    $ready = Join-Path $appRoot '.venv\autocine-ready.txt'
    $modules = 'numpy', 'PIL', 'imageio_ffmpeg', 'windows_capture', 'yt_dlp', 'pycaw', 'pyaudiowpatch', 'psutil'
    & $venv -c 'import importlib.util,sys; sys.exit(0 if all(importlib.util.find_spec(x) for x in sys.argv[1:]) else 1)' @modules
    $missing = $LASTEXITCODE -ne 0
    if ($Mode -eq 'Setup' -or $missing -or -not (Test-Path -LiteralPath $ready)) {
        Write-Host '[Python] Installing/verifying AutoCine dependencies. Internet may be needed.'
        $requirements = Join-Path $appRoot 'requirements-recovery-20261018.txt'
        if ($requested -ne '3.12' -or -not (Test-Path -LiteralPath $requirements)) {
            $requirements = Join-Path $appRoot 'requirements-dev.txt'
        }
        & $venv -m pip install -r $requirements
        if ($LASTEXITCODE -ne 0) { Write-Host '[Python] Dependency setup failed. See the error above and run SETUP_DEV_ENV.bat again.'; exit $LASTEXITCODE }
        & $venv -m pip check
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Set-Content -LiteralPath $ready -Value "Python $requested dependencies verified" -Encoding ASCII
    }
    if ($Mode -eq 'Setup') { Write-Host '[Python] Setup is complete. Run START.bat.'; exit 0 }
    & $venv (Join-Path $appRoot 'app.py')
    exit $LASTEXITCODE
} catch {
    Write-Host "[Python] Startup failed: $($_.Exception.Message)"
    exit 1
}
