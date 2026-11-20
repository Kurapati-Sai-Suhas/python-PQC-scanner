# PQScan college live demonstration: runs the real pqscan CLI on real third-party Python source and reports what it did.
#
#   powershell -ExecutionPolicy Bypass -File scripts\run_college_live_demo.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\run_college_live_demo.ps1 -Python C:\path\to\venv\Scripts\python.exe
#
# Inputs: the installed pyca/cryptography and PyCryptodome packages (located by importing them; versions recorded and
# checked against the committed source manifest) and the synthetic demonstration fixture docs\demo\demo_repo (always
# labelled synthetic). Never touched: the committed reference outputs (docs\demo\outputs, docs\final\demo\outputs),
# annotation outputs, and the sealed test repositories.
# Outputs: a NEW folder (default %TEMP%\pqscan_live_demo_<timestamp>) with summary, JSON, CycloneDX CBOM and SARIF per
# input, stdout/stderr logs, a transcript, runs.json (exit codes, seconds), SHA256_MANIFEST.txt; and the report
# docs\live_demo\live_demo_report.md + live_demo_metrics.json. Exit code 0 only if every command succeeded and every
# CBOM/SARIF validated.
param(
    [string]$Python = "",
    [string]$OutDir = "",
    [string]$ReportDir = "",
    [switch]$SkipVariants
)
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $Repo ".venv\Scripts\python.exe" }
if (-not $OutDir) { $OutDir = Join-Path $env:TEMP ("pqscan_live_demo_" + (Get-Date -Format "yyyyMMdd_HHmmss")) }
if (-not $ReportDir) { $ReportDir = Join-Path $Repo "docs\live_demo" }
$Bin = Split-Path -Parent $Python
$Pqscan = Join-Path $Bin "pqscan.exe"
$Semgrep = Join-Path $Bin "semgrep.exe"
foreach ($p in @($Python, $Pqscan, $Semgrep)) { if (-not (Test-Path $p)) { throw "required program not found: $p" } }
$OutDir = [System.IO.Path]::GetFullPath($OutDir)
foreach ($protected in @("docs\demo\outputs", "docs\final\demo\outputs")) {
    if ($OutDir.StartsWith((Join-Path $Repo $protected), [StringComparison]::OrdinalIgnoreCase)) { throw "refusing to write into committed reference outputs: $OutDir" }
}
if (Test-Path $OutDir) { throw "output folder already exists (use a new one): $OutDir" }
New-Item -ItemType Directory -Force $OutDir | Out-Null
$env:PYTHONIOENCODING = "utf-8"
Start-Transcript -Path (Join-Path $OutDir "transcript.txt") | Out-Null
$runs = New-Object System.Collections.ArrayList

function Invoke-Step([string]$Label, [string]$Exe, [string[]]$ArgList, [string]$Dir, [string]$StdoutName) {
    New-Item -ItemType Directory -Force $Dir | Out-Null
    $out = Join-Path $Dir $StdoutName
    $err = Join-Path $Dir ($StdoutName + ".stderr.txt")
    $quoted = ($ArgList | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join " "
    Write-Host ">>> $Label"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $proc = Start-Process -FilePath $Exe -ArgumentList $quoted -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $out -RedirectStandardError $err
    $sw.Stop()
    $secs = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    [void]$runs.Add([ordered]@{ label = $Label; exit_code = $proc.ExitCode; seconds = $secs; stdout = $out; stderr = $err })
    Write-Host ("    exit {0}, {1} s" -f $proc.ExitCode, $secs)
    if ($proc.ExitCode -ne 0) {
        Get-Content $err -Tail 20 | Write-Host
        ($runs | ConvertTo-Json -Depth 4) | Set-Content -Encoding utf8 (Join-Path $OutDir "runs.json")
        Stop-Transcript | Out-Null
        throw "FAILED: $Label (exit $($proc.ExitCode)); see $err"
    }
}

try {
    # 1. environment and exact revision
    $commit = "unknown"; $same = "unknown"
    Push-Location $Repo
    try {
        $commit = (git rev-parse HEAD).Trim()
        git diff --quiet f69d81b HEAD -- pqscan pyproject.toml; $a = $LASTEXITCODE
        git diff --quiet -- pqscan pyproject.toml; $b = $LASTEXITCODE
        $same = (($a -eq 0) -and ($b -eq 0))
    } catch { } finally { Pop-Location }
    $info = & $Python -I -c "import json,sys,pqscan,cryptography;from importlib.metadata import version as v;print(json.dumps({'python':sys.version.split()[0],'pqscan_version':v('pqscan'),'pqscan_module':pqscan.__file__,'cryptography':v('cryptography'),'pycryptodome':v('pycryptodome')}))"
    $envObj = $info | ConvertFrom-Json
    $sgv = (& $Semgrep --version).Trim()
    $environment = [ordered]@{
        started_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"); git_commit = $commit
        scanner_code_matches_f69d81b = $same; python = $envObj.python; pqscan_version = $envObj.pqscan_version
        pqscan_module = $envObj.pqscan_module; semgrep = $sgv; cryptography = $envObj.cryptography
        pycryptodome = $envObj.pycryptodome; out_dir = $OutDir; python_exe = $Python
    }
    $environment | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $OutDir "environment.json")
    Write-Host "commit $commit | pqscan $($envObj.pqscan_version) | Python $($envObj.python) | Semgrep $sgv"
    Write-Host "cryptography $($envObj.cryptography) | PyCryptodome $($envObj.pycryptodome)"
    if ($envObj.cryptography -ne "47.0.0" -or $envObj.pycryptodome -ne "4.4.0") { throw "expected cryptography 47.0.0 and PyCryptodome 4.4.0" }

    # 2. locate the installed library sources and copy them (read-only use of site-packages)
    Invoke-Step "locate and copy installed library sources" $Python @("-I", (Join-Path $Repo "scripts\live_demo_metrics.py"), "prepare", $OutDir) $OutDir "prepare.txt"
    Get-Content (Join-Path $OutDir "prepare.txt") | Where-Object { $_ -notmatch "^SCANROOT" -and $_ -notmatch "^[A-Z]:\\" } | Write-Host

    # 3. scans
    $targets = @(
        @{ name = "cryptography-47.0.0"; root = (Join-Path $OutDir "sources\cryptography-47.0.0") },
        @{ name = "pycryptodome-4.4.0"; root = (Join-Path $OutDir "sources\pycryptodome-4.4.0") },
        @{ name = "demo-fixture-synthetic"; root = (Join-Path $Repo "docs\demo\demo_repo") }
    )
    foreach ($t in $targets) {
        $d = Join-Path $OutDir $t.name
        Invoke-Step "pqscan scan $($t.name) --format summary" $Pqscan @("scan", $t.root) $d "summary.txt"
        Invoke-Step "pqscan scan $($t.name) --format json" $Pqscan @("scan", $t.root, "--format", "json", "-o", (Join-Path $d "scan.json")) $d "json.log"
        Invoke-Step "pqscan scan $($t.name) --format cbom" $Pqscan @("scan", $t.root, "--format", "cbom", "-o", (Join-Path $d "cbom.json")) $d "cbom.log"
        Invoke-Step "pqscan scan $($t.name) --format sarif" $Pqscan @("scan", $t.root, "--format", "sarif", "-o", (Join-Path $d "scan.sarif")) $d "sarif.log"
        if (-not $SkipVariants) {
            Invoke-Step "pqscan scan $($t.name) --format json --tier-threshold T3" $Pqscan @("scan", $t.root, "--format", "json", "--tier-threshold", "T3", "-o", (Join-Path $d "scan_T3.json")) $d "json_T3.log"
            if ($t.name -ne "demo-fixture-synthetic") {
                Invoke-Step "pqscan scan $($t.name) --format json --exclude-tests" $Pqscan @("scan", $t.root, "--format", "json", "--exclude-tests", "-o", (Join-Path $d "scan_exclude-tests.json")) $d "json_exclude_tests.log"
            }
        }
    }
    ($runs | ConvertTo-Json -Depth 4) | Set-Content -Encoding utf8 (Join-Path $OutDir "runs.json")

    # 4. metrics, schema validation, reference comparison, manifest
    & $Python -I (Join-Path $Repo "scripts\live_demo_metrics.py") report $OutDir $ReportDir
    $rc = $LASTEXITCODE
    Write-Host ""
    Write-Host "Outputs:  $OutDir"
    Write-Host "Report:   $(Join-Path $ReportDir 'live_demo_report.md')"
    if ($rc -ne 0) { throw "metrics/validation reported problems (exit $rc)" }
    Write-Host "LIVE DEMO COMPLETED: every command exited 0 and every CBOM/SARIF validated."
} finally {
    try { Stop-Transcript | Out-Null } catch { }
}
