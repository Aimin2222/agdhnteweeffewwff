# LoL AutoCine: import ORIGINAL PNG bytes from a ZIP into the GitHub working tree.
# Requires Windows PowerShell 5.1+ and a local clone of this repository.
# Usage:
# powershell -NoProfile -ExecutionPolicy Bypass -File .\LoL_AutoCine\tools\upload_original_killframes_from_zip.ps1 -ZipPath "C:\...\キルフレーム.zip"
# Add -Push to commit & git push from the dedicated branch only.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [string]$ZipPath,
    [switch]$Push
)
$ErrorActionPreference = "Stop"
$branch = "autocine/chatgpt-killframes-abcd-theme-assets-20261013"
$repo = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$target = Join-Path $repo "LoL_AutoCine\assets\kill_concepts"
$archivePath = (Resolve-Path -LiteralPath $ZipPath).ProviderPath
if (-not (Test-Path -LiteralPath (Join-Path $repo ".git"))) {
    throw "Git repository not found at $repo. Clone the repository using GitHub Desktop first."
}
$gitAvailable = [bool](Get-Command git -ErrorAction SilentlyContinue)
if ($gitAvailable) {
    $activeBranch = (& git -C $repo branch --show-current | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { throw "git branch query failed." }
} else {
    # GitHub Desktop includes Git internally but may not put git.exe on PATH.
    $headFile = Join-Path $repo ".git\HEAD"
    if (-not (Test-Path -LiteralPath $headFile)) { throw "Cannot identify active branch." }
    $headText = (Get-Content -LiteralPath $headFile -Raw).Trim()
    $activeBranch = $headText -replace '^ref: refs/heads/', ''
}
if ($activeBranch -ne $branch) {
    throw "Wrong branch: '$activeBranch'. Switch to '$branch' in GitHub Desktop before running."
}
if ($Push -and -not $gitAvailable) {
    throw "-Push needs Git for Windows on PATH. Run without -Push, then use GitHub Desktop's Commit and Push."
}
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
New-Item -ItemType Directory -Path $target -Force | Out-Null
$zipInfo = Get-Item -LiteralPath $archivePath
$zipHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
$archive = [System.IO.Compression.ZipFile]::OpenRead($archivePath)
$records = New-Object 'System.Collections.Generic.List[object]'
$namesUsed = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
$added = 0
$unchanged = 0
try {
    $images = @($archive.Entries | Where-Object { $_.Name -match '(?i)\.png$' -and $_.Length -gt 0 })
    if ($images.Count -eq 0) { throw "This ZIP contains no PNG files. Nothing imported." }
    foreach ($entry in $images) {
        if ($entry.Length -gt (100 * 1024 * 1024)) {
            throw ("Single PNG exceeds GitHub's 100 MiB Git limit: " + $entry.FullName)
        }
        $sourceName = $entry.FullName.Replace('\','/')
        $baseName = [System.IO.Path]::GetFileName($sourceName)
        $baseName = [regex]::Replace($baseName, '[<>:"/\\|?*\x00-\x1F]', '_')
        if ([string]::IsNullOrWhiteSpace($baseName)) { throw "Invalid file name in ZIP." }
        $saveName = $baseName
        $counter = 1
        while (-not $namesUsed.Add($saveName)) {
            $counter++
            $saveName = [System.IO.Path]::GetFileNameWithoutExtension($baseName) + ("__{0:d3}" -f $counter) + ".png"
        }
        $destination = Join-Path $target $saveName
        $tempPath = $destination + ".import-partial"
        if (Test-Path -LiteralPath $tempPath) { Remove-Item -LiteralPath $tempPath -Force }
        try {
            $sourceStream = $entry.Open()
            try {
                $destStream = [System.IO.File]::Create($tempPath)
                try { $sourceStream.CopyTo($destStream) }
                finally { $destStream.Dispose() }
            }
            finally { $sourceStream.Dispose() }
            $fileStream = [System.IO.File]::OpenRead($tempPath)
            try {
                $magic = New-Object byte[] 8
                $count = $fileStream.Read($magic, 0, 8)
                $expected = [byte[]](137,80,78,71,13,10,26,10)
                $valid = ($count -eq 8)
                if ($valid) {
                    for ($i=0; $i -lt 8; $i++) {
                        if ($magic[$i] -ne $expected[$i]) { $valid = $false; break }
                    }
                }
                if (-not $valid) { throw "Not a valid PNG header: $sourceName" }
            }
            finally { $fileStream.Dispose() }
            $hash = (Get-FileHash -LiteralPath $tempPath -Algorithm SHA256).Hash.ToLowerInvariant()
            if (Test-Path -LiteralPath $destination) {
                $existingHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
                if ($existingHash -ne $hash) {
                    throw "Different original file already exists. Refusing overwrite: $saveName"
                }
                $unchanged++
                Remove-Item -LiteralPath $tempPath -Force
            } else {
                Move-Item -LiteralPath $tempPath -Destination $destination
                $added++
            }
            $records.Add([ordered]@{
                zip_entry = $sourceName
                stored_file = $saveName
                bytes = [int64]$entry.Length
                sha256 = $hash
            })
        }
        finally {
            if (Test-Path -LiteralPath $tempPath) { Remove-Item -LiteralPath $tempPath -Force }
        }
    }
}
finally { $archive.Dispose() }
$manifest = [ordered]@{
    purpose = "Exact-pixel original source boards; no redesign or alpha processing yet"
    source_archive = $zipInfo.Name
    source_archive_size = [int64]$zipInfo.Length
    source_archive_sha256 = $zipHash
    source_image_count = $records.Count
    assets = @($records.ToArray())
}
$manifestPath = Join-Path $target "source_import_manifest.json"
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
Write-Host "Imported $added new original PNG(s), $unchanged unchanged. Total $($records.Count)." -ForegroundColor Green
Write-Host "Original files: $target"
Write-Host "Manifest: $manifestPath"
Write-Host "No image bytes were recompressed, resized or redrawn."
if ($Push) {
    & git -C $repo add -- "LoL_AutoCine/assets/kill_concepts/"
    if ($LASTEXITCODE -ne 0) { throw "git add failed." }
    $staged = @(& git -C $repo diff --cached --name-only)
    $unexpected = @($staged | Where-Object { $_ -notlike 'LoL_AutoCine/assets/kill_concepts/*' })
    if ($unexpected.Count -gt 0) {
        throw ("Unrelated staged paths found: " + ($unexpected -join ', ') + ". Unstage them before running -Push.")
    }
    if ($staged.Count -eq 0) { Write-Host "No new changes to push."; exit 0 }
    & git -C $repo commit -m "assets: import original ChatGPT kill-frame concept boards"
    if ($LASTEXITCODE -ne 0) { throw "git commit failed. You can commit and push using GitHub Desktop." }
    & git -C $repo push origin $branch
    if ($LASTEXITCODE -ne 0) { throw "git push failed. Retry using GitHub Desktop (Push origin)." }
    Write-Host "Pushed original PNGs to the dedicated branch." -ForegroundColor Green
} else {
    Write-Host "Next: in GitHub Desktop, review the changed PNGs, Commit, then Push origin."
    Write-Host "Or rerun with -Push to commit and push using Git for Windows."
}
