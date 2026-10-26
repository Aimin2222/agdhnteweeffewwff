$ErrorActionPreference='Stop'
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (!(Test-Path -LiteralPath $compiler)) { throw '.NET Framework x64 compiler was not found; nothing was installed.' }
$compilerArgs=@('/nologo','/codepage:65001','/target:winexe','/platform:x64',('/out:'+(Join-Path $PSScriptRoot 'AutoCine_UI_Reference_v1.exe')),('/win32manifest:'+(Join-Path $PSScriptRoot 'ReferenceDemo.exe.manifest')),'/reference:System.Windows.Forms.dll','/reference:System.Drawing.dll','/reference:System.Web.Extensions.dll',('/reference:'+(Join-Path $PSScriptRoot 'Microsoft.Web.WebView2.Core.dll')),('/reference:'+(Join-Path $PSScriptRoot 'Microsoft.Web.WebView2.WinForms.dll')),(Join-Path $PSScriptRoot 'ReferenceDemo.cs'))
& $compiler @compilerArgs
if ($LASTEXITCODE -ne 0) { throw 'Compile failed. Close this research demo before rebuilding; no process was terminated.' }
