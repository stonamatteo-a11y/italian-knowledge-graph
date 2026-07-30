$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepositoryRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Port = 7777
$NoBrowser = $false
$CheckOnly = $false
$ServerProcess = $null

function Stop-WithError {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [int]$Code = 1
    )
    [Console]::Error.WriteLine("IKG launcher error: $Message")
    exit $Code
}

for ($Index = 0; $Index -lt $args.Count; $Index++) {
    switch ($args[$Index]) {
        "--port" {
            if ($Index + 1 -ge $args.Count) {
                Stop-WithError "--port requires a value" 2
            }
            $Index++
            $ParsedPort = 0
            if (-not [int]::TryParse($args[$Index], [ref]$ParsedPort)) {
                Stop-WithError "port must be a number" 2
            }
            $Port = $ParsedPort
        }
        "--no-browser" { $NoBrowser = $true }
        "--check-only" { $CheckOnly = $true }
        default { Stop-WithError "unknown option: $($args[$Index])" 2 }
    }
}

$PythonExecutable = $null
$PythonPrefix = @()
foreach ($Candidate in @(
    @{ Name = "py"; Prefix = @("-3") },
    @{ Name = "python"; Prefix = @() },
    @{ Name = "python3"; Prefix = @() }
)) {
    if (-not (Get-Command $Candidate.Name -ErrorAction SilentlyContinue)) {
        continue
    }
    $PreviousErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Candidate.Name @($Candidate.Prefix) `
            (Join-Path $RepositoryRoot "scripts\launcher_support.py") version *> $null
        $CandidateExitCode = $LASTEXITCODE
    }
    catch {
        $CandidateExitCode = 1
    }
    finally {
        $ErrorActionPreference = $PreviousErrorPreference
    }
    if ($CandidateExitCode -eq 0) {
        $PythonExecutable = $Candidate.Name
        $PythonPrefix = $Candidate.Prefix
        break
    }
}

if (-not $PythonExecutable) {
    Stop-WithError (
        "Python 3.10 or newer is required. Install Python manually, then run this launcher again. " +
        "IKG does not install Python automatically."
    )
}

$SupportScript = Join-Path $RepositoryRoot "scripts\launcher_support.py"
$VersionOutput = & $PythonExecutable @PythonPrefix $SupportScript version
if ($LASTEXITCODE -ne 0) {
    Stop-WithError "Python 3.10 or newer is required"
}

Write-Host "Python: $VersionOutput ($PythonExecutable)"
Write-Host "Repository: $RepositoryRoot"
Write-Host "URL: http://127.0.0.1:$Port"

Push-Location $RepositoryRoot
try {
    & $PythonExecutable @PythonPrefix $SupportScript project
    if ($LASTEXITCODE -ne 0) {
        if ($CheckOnly) {
            Stop-WithError "the project is not installed or runtime dependencies are unavailable"
        }
        Write-Host "Preparing the local editable installation..."
        & $PythonExecutable @PythonPrefix -m pip install --no-deps --no-build-isolation -e .
        if ($LASTEXITCODE -ne 0) {
            Stop-WithError "editable installation failed; no remote packages were downloaded"
        }
        & $PythonExecutable @PythonPrefix $SupportScript project
        if ($LASTEXITCODE -ne 0) {
            Stop-WithError (
                "FastAPI or Uvicorn is missing. Install project requirements manually and retry."
            )
        }
    }

    & $PythonExecutable @PythonPrefix $SupportScript port $Port
    if ($LASTEXITCODE -ne 0) {
        Stop-WithError "127.0.0.1:$Port is already in use, unavailable, or invalid"
    }

    if ($CheckOnly) {
        Write-Host "Check completed successfully. No server or browser was started."
        exit 0
    }

    $StartInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $StartInfo.FileName = (Get-Command $PythonExecutable).Source
    $StartInfo.WorkingDirectory = $RepositoryRoot
    $StartInfo.UseShellExecute = $false
    foreach ($PrefixArgument in $PythonPrefix) {
        [void]$StartInfo.ArgumentList.Add($PrefixArgument)
    }
    [void]$StartInfo.ArgumentList.Add((Join-Path $RepositoryRoot "run_editor.py"))
    [void]$StartInfo.ArgumentList.Add("--port")
    [void]$StartInfo.ArgumentList.Add([string]$Port)

    $ServerProcess = [System.Diagnostics.Process]::Start($StartInfo)
    & $PythonExecutable @PythonPrefix $SupportScript wait $Port
    if ($LASTEXITCODE -ne 0) {
        if (-not $ServerProcess.HasExited) {
            $ServerProcess.Kill($true)
        }
        $ServerProcess.WaitForExit()
        Stop-WithError "the editor did not become available (server exit code $($ServerProcess.ExitCode))"
    }

    if (-not $NoBrowser) {
        Start-Process "http://127.0.0.1:$Port"
    }

    try {
        $ServerProcess.WaitForExit()
        $ExitCode = $ServerProcess.ExitCode
    }
    finally {
        if ($ServerProcess -and -not $ServerProcess.HasExited) {
            $ServerProcess.Kill($true)
            $ServerProcess.WaitForExit()
        }
    }
    exit $ExitCode
}
finally {
    if ($ServerProcess -and -not $ServerProcess.HasExited) {
        $ServerProcess.Kill($true)
        $ServerProcess.WaitForExit()
    }
    Pop-Location
}
