# =========================
# WJA Lightweight Scheduler
# =========================

$rootPath = "C:\Users\shridhar.dt\Downloads\WJA_QE_AUTOMATION\WJA_QE_Automation-main"
$batFile = "$rootPath\run_tests_scheduled.bat"

# ---- First run time: TODAY at 2:32 PM ----
$firstRun = (Get-Date).Date.AddHours(13).AddMinutes(09)

# If current time already passed 2:32 PM, schedule for tomorrow
if (Get-Date -gt $firstRun) {
    $firstRun = $firstRun.AddDays(1)
}

$waitSeconds = ($firstRun - (Get-Date)).TotalSeconds

Write-Host "First run scheduled at $firstRun"
Write-Host "Waiting $([int]$waitSeconds) seconds..."

Start-Sleep -Seconds $waitSeconds

while ($true) {

    Write-Host "Starting WJA Automation at $(Get-Date)"

    Set-Location $rootPath
    cmd /c $batFile

    Write-Host "Run completed at $(Get-Date)"
    Write-Host "Sleeping for 24 hours..."

    # 24 hours
    Start-Sleep -Seconds 86400
}
