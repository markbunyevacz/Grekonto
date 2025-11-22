# Helper script to open Playwright report, handling port conflicts
$port = 9323
$processes = netstat -ano | findstr ":$port" | findstr LISTENING

if ($processes) {
    Write-Host "Found process using port $port, stopping it..." -ForegroundColor Yellow
    $pids = $processes | ForEach-Object { ($_ -split '\s+')[-1] } | Select-Object -Unique
    foreach ($pid in $pids) {
        if ($pid -and $pid -ne "0") {
            try {
                taskkill /PID $pid /F 2>$null
                Write-Host "Stopped process $pid" -ForegroundColor Green
            } catch {
                Write-Host "Could not stop process $pid" -ForegroundColor Red
            }
        }
    }
    Start-Sleep -Seconds 1
}

# Open the report
Write-Host "Opening Playwright report..." -ForegroundColor Cyan
npx playwright show-report

