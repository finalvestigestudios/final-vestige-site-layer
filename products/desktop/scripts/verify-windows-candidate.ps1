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
    # R52 validates both full unittest modes and all six source smokes
    # before any Windows candidate packaging or EXE invocation.
    & $PythonCommand products/desktop/scripts/offline_source_gate.py
    if ($LASTEXITCODE -ne 0) { throw "R52 offline source verification FAILED; no Windows candidate may be built or accepted" }
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
        # R40 builds an exact six-file, no-clobber, atomically published inventory.
        & $PythonCommand products/desktop/build_inventory.py $dist
        if ($LASTEXITCODE -ne 0) { throw "R40 candidate inventory generation FAILED" }
    }
    if (-not (Test-Path -LiteralPath $dist -PathType Container)) {
        throw "No dist folder; use -Build or place six candidate EXEs plus SHA256SUMS.txt in dist."
    }
    # Evidence stays outside the exact seven-file dist candidate directory.
    $evidenceDir = Join-Path $repo "build\\candidate-evidence"
    if (-not (Test-Path -LiteralPath $evidenceDir)) {
        New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
    }
    $output = Join-Path $evidenceDir ("offline-gate-" + (Get-Date -Format "yyyyMMdd-HHmmss-fffffff") + ".json")
    & $PythonCommand products/desktop/release_gate.py $dist --smoke --report $output
    if ($LASTEXITCODE -ne 0) { throw "Offline Windows candidate gate FAILED" }
    & $PythonCommand products/desktop/report_attestation.py $output $dist
    if ($LASTEXITCODE -ne 0) { throw "R39 offline report consistency FAILED" }
    Write-Host "R39 report check is UNPINNED unless the original digest is kept in a separate trusted register."
    Write-Host "Offline candidate evidence (NOT a release authorization): $output"
}
finally {
    $env:PYTHONPATH = $oldPath
    Pop-Location
}
