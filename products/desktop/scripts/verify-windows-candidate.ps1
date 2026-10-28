# Final Vestige Labs: runner-independent Windows x64 candidate validation.
# This script never publishes, signs or uploads binaries. Run from trusted source.
[CmdletBinding()]
param(
    [string]$PythonCommand = "python",
    [switch]$Build
)
$ErrorActionPreference = "Stop"
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) {
    throw "Run this script on a real Windows x64 machine."
}
if (-not [Environment]::Is64BitOperatingSystem) {
    throw "The six-app candidate requires Windows x64."
}
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
Push-Location $repo
$oldPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = Join-Path $repo "products\desktop"
    & $PythonCommand -m unittest discover -s products/desktop/tests -v
    if ($LASTEXITCODE -ne 0) { throw "Desktop regression tests FAILED" }
    $dist = Join-Path $repo "dist"
    if ($Build) {
        # Only remove generated files from previous builds in the explicit dist
        # folder. Never touch source files or any unrelated directory.
        if (Test-Path -LiteralPath $dist) {
            throw "dist already exists: use an empty checkout or inspect/remove previous build artifacts manually."
        }
        New-Item -ItemType Directory -Path $dist | Out-Null
        $apps = @(
            "LedgerDiffLite","InvoiceTwinScout","SpendMapLite",
            "PolicyDeltaDesk","GrantAuditStudioPro","ProcureGuardStudioPro"
        )
        foreach ($app in $apps) {
            & $PythonCommand -m PyInstaller --noconfirm --clean --onefile --windowed --paths products/desktop --name $app --distpath $dist --workpath "build/$app" --specpath build/specs "products/desktop/launchers/$app.py"
            if ($LASTEXITCODE -ne 0) { throw "Packaging FAILED for $app" }
        }
        # Generate inventory deterministically with exclusively known artifacts.
        $inventory = @()
        foreach ($app in $apps) {
            $exe = Join-Path $dist ($app + ".exe")
            if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
                throw "Missing packaged binary: $exe"
            }
            $sha = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
            $inventory += "$sha  $app.exe"
        }
        $manifest = Join-Path $dist "SHA256SUMS.txt"
        [System.IO.File]::WriteAllLines($manifest, $inventory, [System.Text.Encoding]::ASCII)
    }
    if (-not (Test-Path -LiteralPath $dist -PathType Container)) {
        throw "No dist folder; use -Build or place six candidate EXEs plus SHA256SUMS.txt in dist."
    }
    $output = Join-Path $dist ("offline-gate-" + (Get-Date -Format "yyyyMMdd-HHmmss-fffffff") + ".json")
    & $PythonCommand products/desktop/release_gate.py $dist --smoke --report $output
    if ($LASTEXITCODE -ne 0) { throw "Offline Windows candidate gate FAILED" }
    Write-Host "Offline candidate evidence (NOT a release authorization): $output"
}
finally {
    $env:PYTHONPATH = $oldPath
    Pop-Location
}
