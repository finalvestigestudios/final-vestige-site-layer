# Local Windows build and validation fallback when GitHub Actions cannot start runners.
# Run on a Windows x64 machine with Python 3.11+, PyInstaller 6.16.0 and
# Inno Setup 6 already installed. Produces UNSIGNED DEVELOPMENT OUTPUT ONLY.
$ErrorActionPreference = "Stop"
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$inno = Join-Path ([Environment]::GetFolderPath("ProgramFilesX86")) "Inno Setup 6\ISCC.exe"

function Require-Success([string]$step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$step failed with exit code $LASTEXITCODE."
    }
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ must be installed and available on PATH."
}
if (-not (Test-Path $inno)) {
    throw "Inno Setup 6 ISCC.exe not found at $inno. Install it before continuing."
}
$smokeDir = Join-Path $env:TEMP ("FileProofSmoke-" + [Guid]::NewGuid().ToString("N"))
$uninstaller = Join-Path $smokeDir "unins000.exe"
Push-Location $repoRoot
try {
    Write-Host "[1/6] Running source unit tests..."
    python -m unittest discover -s desktop-software/fileproof -p "test_*.py" -v
    Require-Success "Unit tests"

    Write-Host "[2/6] Checking PyInstaller availability..."
    python -m PyInstaller --version
    Require-Success "PyInstaller check"

    Write-Host "[3/6] Packaging both the GUI and CLI..."
    python -m PyInstaller --noconfirm --clean --onefile --windowed --name FileProof desktop-software/fileproof/fileproof.py
    Require-Success "GUI packaging"
    python -m PyInstaller --noconfirm --clean --onefile --console --name FileProofCLI desktop-software/fileproof/fileproof.py
    Require-Success "CLI packaging"

    Write-Host "[4/6] Building the Windows installer..."
    & $inno "desktop-software\fileproof\installer.iss"
    Require-Success "Inno Setup"
    $installer = Join-Path $repoRoot "dist\installers\FileProof-Setup-0.2.0-win64.exe"
    if (-not (Test-Path $installer)) { throw "Expected v0.2.0 installer is missing." }

    Write-Host "[5/6] Installing and exercising the installed console executable..."
    $argsInstall = @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART",
                     ('/DIR="' + $smokeDir + '"'))
    $installResult = Start-Process -FilePath $installer -ArgumentList $argsInstall -Wait -PassThru
    if ($installResult.ExitCode -ne 0) { throw "Silent installer failed." }
    $gui = Join-Path $smokeDir "FileProof.exe"
    $cli = Join-Path $smokeDir "FileProofCLI.exe"
    if (-not (Test-Path $gui) -or -not (Test-Path $cli)) {
        throw "Installed GUI and/or CLI is missing."
    }
    python desktop-software/fileproof/smoke_installed.py $cli
    Require-Success "Installed CLI smoke tests"

    Write-Host "[6/6] Uninstalling and generating installer checksum..."
    if (-not (Test-Path $uninstaller)) { throw "Inno Setup uninstaller missing." }
    $uninstallResult = Start-Process -FilePath $uninstaller -ArgumentList @(
        "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"
    ) -Wait -PassThru
    if ($uninstallResult.ExitCode -ne 0) { throw "Silent uninstaller failed." }
    if ((Test-Path $gui) -or (Test-Path $cli)) {
        throw "Installed EXE still present after uninstall."
    }
    $hash = Get-FileHash -Path $installer -Algorithm SHA256
    $checksums = Join-Path (Split-Path $installer -Parent) "SHA256SUMS.txt"
    [System.IO.File]::WriteAllText($checksums,
        ($hash.Hash + "  " + (Split-Path $installer -Leaf) + [Environment]::NewLine),
        [System.Text.UTF8Encoding]::new($false))

    $signature = Get-AuthenticodeSignature -FilePath $installer
    if ($signature.Status -ne "Valid") {
        Write-Warning "UNSIGNED DEVELOPMENT BUILD. DO NOT DISTRIBUTE OR PUBLISH."
    }
    Write-Host "Local installer smoke tests completed. Artifact: $installer"
    Write-Host "SHA256: $($hash.Hash)"
}
finally {
    # Cleanup is best effort; remove test installation if the smoke aborted early.
    if (Test-Path $uninstaller) {
        $cleanup = Start-Process -FilePath $uninstaller -ArgumentList @(
            "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"
        ) -Wait -PassThru
        if ($cleanup.ExitCode -ne 0) {
            Write-Warning "Check and remove the smoke installation manually: $smokeDir"
        }
    }
    Pop-Location
}
