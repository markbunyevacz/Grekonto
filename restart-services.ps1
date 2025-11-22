# Restart Services for E2E Testing
# This script stops and restarts all required services for end-to-end testing

Write-Host "=== Restarting Services for E2E Testing ===" -ForegroundColor Cyan
Write-Host ""

# Function to stop processes on specific ports
function Stop-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    
    $connections = netstat -ano | findstr ":$Port" | findstr "LISTENING"
    if ($connections) {
        $processId = ($connections -split '\s+')[-1]
        if ($processId) {
            Write-Host "Stopping $ServiceName on port $Port (PID: $processId)..." -ForegroundColor Yellow
            try {
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
                Write-Host "  [OK] Stopped $ServiceName" -ForegroundColor Green
            } catch {
                Write-Host "  [WARN] Could not stop process $processId : $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "  [INFO] $ServiceName is not running on port $Port" -ForegroundColor Gray
    }
}

# Function to check if a port is listening
function Test-PortListening {
    param([int]$Port, [int]$TimeoutSeconds = 10)
    
    $endTime = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $endTime) {
        $result = netstat -ano | findstr ":$Port" | findstr "LISTENING"
        if ($result) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

# Step 1: Stop existing services
Write-Host "Step 1: Stopping existing services..." -ForegroundColor Cyan
Stop-ProcessOnPort -Port 10000 -ServiceName "Azurite (Blob)"
Stop-ProcessOnPort -Port 10001 -ServiceName "Azurite (Queue)"
Stop-ProcessOnPort -Port 10002 -ServiceName "Azurite (Table)"
Stop-ProcessOnPort -Port 7071 -ServiceName "Azure Functions"
Stop-ProcessOnPort -Port 5173 -ServiceName "Frontend (Vite)"

# Also kill any remaining azurite or func processes
Write-Host ""
Write-Host "Cleaning up remaining processes..." -ForegroundColor Cyan
Get-Process | Where-Object {$_.ProcessName -eq "azurite"} | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process | Where-Object {$_.ProcessName -eq "func"} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2
Write-Host ""

# Step 2: Start Azurite
Write-Host "Step 2: Starting Azurite (Azure Storage Emulator)..." -ForegroundColor Cyan
$currentDir = Get-Location
$azuriteJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    azurite --silent --location . --debug azurite.log
} -ArgumentList $currentDir

Start-Sleep -Seconds 3

if (Test-PortListening -Port 10000 -TimeoutSeconds 10) {
    Write-Host "  [OK] Azurite started successfully" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Azurite failed to start" -ForegroundColor Red
    Receive-Job $azuriteJob
    exit 1
}

# Step 3: Start Azure Functions Backend
Write-Host ""
Write-Host "Step 3: Starting Azure Functions Backend..." -ForegroundColor Cyan
$backendDir = Join-Path $currentDir "backend"
$funcJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    func start --port 7071
} -ArgumentList $backendDir

Start-Sleep -Seconds 5

if (Test-PortListening -Port 7071 -TimeoutSeconds 30) {
    Write-Host "  [OK] Azure Functions started successfully on port 7071" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Azure Functions may still be starting. Check logs if tests fail." -ForegroundColor Yellow
    Write-Host "  You can check status with: netstat -ano | findstr ':7071'" -ForegroundColor Gray
}

# Step 4: Frontend info
Write-Host ""
Write-Host "Step 4: Frontend Dev Server" -ForegroundColor Cyan
Write-Host "  [INFO] Frontend will be auto-started by Playwright when running E2E tests" -ForegroundColor Gray
Write-Host "  To start manually: cd frontend; npm run dev" -ForegroundColor Gray

# Summary
Write-Host ""
Write-Host "=== Service Status ===" -ForegroundColor Cyan
Write-Host "Azurite:        " -NoNewline
if (Test-PortListening -Port 10000 -TimeoutSeconds 2) {
    Write-Host "[OK] Running (ports 10000-10002)" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Not running" -ForegroundColor Red
}

Write-Host "Azure Functions: " -NoNewline
if (Test-PortListening -Port 7071 -TimeoutSeconds 2) {
    Write-Host "[OK] Running (port 7071)" -ForegroundColor Green
} else {
    Write-Host "[WARN] Starting or not running" -ForegroundColor Yellow
}

Write-Host "Frontend:        " -NoNewline
if (Test-PortListening -Port 5173 -TimeoutSeconds 2) {
    Write-Host "[OK] Running (port 5173)" -ForegroundColor Green
} else {
    Write-Host "[INFO] Will start with E2E tests" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Ready for E2E Testing ===" -ForegroundColor Green
Write-Host "To run E2E tests:" -ForegroundColor Cyan
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm run e2e" -ForegroundColor White
Write-Host ""
Write-Host "Note: Jobs are running in background. To stop them:" -ForegroundColor Yellow
Write-Host '  Stop-Job $azuriteJob, $funcJob' -ForegroundColor White
Write-Host '  Remove-Job $azuriteJob, $funcJob' -ForegroundColor White
