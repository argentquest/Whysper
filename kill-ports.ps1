# Simple PowerShell script to kill processes on ports 8000-8010

Write-Host "Killing processes on ports 8000-8010..." -ForegroundColor Yellow

# Get all processes on ports 8000-8010 and kill them
$ports = 8000..8010

foreach ($port in $ports) {
    Write-Host "Checking port $port..." -ForegroundColor Cyan
    
    # Get PIDs using netstat
    $pids = netstat -ano | Where-Object { $_ -match ":$port " } | ForEach-Object {
        ($_ -split '\s+')[-1]
    } | Where-Object { $_ -match '^\d+$' } | Sort-Object -Unique
    
    if ($pids) {
        foreach ($pid in $pids) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Killing $($process.ProcessName) (PID: $pid) on port $port" -ForegroundColor Red
                    Stop-Process -Id $pid -Force
                    Write-Host "✓ Killed process $pid" -ForegroundColor Green
                }
            } catch {
                Write-Host "✗ Failed to kill PID $pid" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "Port $port is free" -ForegroundColor Gray
    }
}

Write-Host "`nDone!" -ForegroundColor Green