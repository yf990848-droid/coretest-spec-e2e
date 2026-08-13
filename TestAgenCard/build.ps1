# build.ps1 - Build all cards (parallel)
# Usage:
#   .\build.ps1 gamma
#   .\build.ps1 prod

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("gamma", "prod")]
    [string]$BuildEnv
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$ConfigFile = Join-Path $ScriptDir "codeagent-extension.json"
if (Test-Path $ConfigFile) {
    $PkgName = (Select-String '"name"\s*:\s*"([^"]*)"' $ConfigFile).Matches.Groups[1].Value
    $PkgVersion = (Select-String '"version"\s*:\s*"([^"]*)"' $ConfigFile).Matches.Groups[1].Value
    if ($PkgName -and $PkgVersion) {
        $Package = "${PkgName}@${PkgVersion}"
        Write-Host "Package from codeagent-extension.json: $Package"
    }
} else {
    Write-Host "WARN: codeagent-extension.json not found, skip VITE_APP_AGENT_MODEL replace"
}

Write-Host "Build env: $BuildEnv"
Write-Host "=========================================="

$Dirs = @("requirementDetails", "testCase", "testSpecification", "testSpot")

$EnvMap = @{
    "gamma" = ".env.gamma"
    "prod"  = ".env.production"
}

$EnvFileName = $EnvMap[$BuildEnv]

$BuildJob = {
    param($Dir, $FullPath, $BuildEnv, $Package, $EnvFileName)

    Set-Location $FullPath
    $log = @()
    $log += "========== $Dir =========="

    if ($Package) {
        $EnvFile = Join-Path $FullPath $EnvFileName
        if (Test-Path $EnvFile) {
            $AgentModel = "/$Package/webapps/$Dir"
            $lines = Get-Content $EnvFile
            $lines = $lines -replace "^VITE_APP_AGENT_MODEL=.*", "VITE_APP_AGENT_MODEL=$AgentModel"
            Set-Content $EnvFile $lines
            $log += "VITE_APP_AGENT_MODEL => $AgentModel"
        } else {
            $log += "WARN: $EnvFileName not found, skip replace"
        }
    }

    if (-not (Test-Path (Join-Path $FullPath "package.json"))) {
        $log += "WARN: package.json not found in $Dir"
        return $log
    }

    $log += "Running: npm install"
    npm install --legacy-peer-deps 2>&1 | ForEach-Object { $log += $_ }
    if ($LASTEXITCODE -ne 0) {
        $log += "[FAIL] $Dir npm install failed"
        return $log
    }

    $log += "Running: npm run build:$BuildEnv"
    npm run "build:$BuildEnv" 2>&1 | ForEach-Object { $log += $_ }
    if ($LASTEXITCODE -eq 0) {
        $log += "[OK] $Dir build success"
    } else {
        $log += "[FAIL] $Dir build failed"
    }

    return $log
}

$Jobs = @()

foreach ($Dir in $Dirs) {
    $FullPath = Join-Path $ScriptDir $Dir

    if (-not (Test-Path $FullPath -PathType Container)) {
        Write-Host "WARN: $Dir not found"
        continue
    }

    $Jobs += Start-Job -ScriptBlock $BuildJob -ArgumentList $Dir, $FullPath, $BuildEnv, $Package, $EnvFileName
    Write-Host "Started job for $Dir"
}

Write-Host ""
Write-Host "Waiting for all builds to complete..."
Write-Host ""

$FailedDirs = @()

foreach ($Job in $Jobs) {
    $output = Receive-Job -Job $Job -Wait
    $output | ForEach-Object { Write-Host $_ }

    $jobInfo = Get-Job -Id $Job.Id
    if ($output -match "\[FAIL\]") {
        $FailedDirs += ($output | Select-String "========== (.+) ==========")[0].Matches.Groups[1].Value
    }

    Write-Host ""
    Remove-Job -Job $Job -Force
}

Write-Host "=========================================="
if ($FailedDirs.Count -gt 0) {
    Write-Host "Build done with failures: $($FailedDirs -join ', ')"
    exit 1
} else {
    Write-Host "Build done - all succeeded"
}
