# Run Azure Document Intelligence Benchmark on SROIE Dataset

$env:DOCUMENT_INTELLIGENCE_ENDPOINT = "https://grekonto.cognitiveservices.azure.com/"
$env:DOCUMENT_INTELLIGENCE_KEY = "YOUR_KEY_HERE"

# Get sample size from argument or default to 5
$sampleSize = if ($args.Count -gt 0) { $args[0] } else { 5 }

Write-Host "Running benchmark with $sampleSize images..." -ForegroundColor Green

# Run from project root
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot

# Use backend's virtual environment
$pythonExe = Join-Path $projectRoot "backend\.venv\Scripts\python.exe"
& $pythonExe benchmark\test_azure_on_sroie.py $sampleSize

