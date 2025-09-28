# PowerShell script to kill all processes using ports 8000-8010
# Usage: .\kill-ports-8000-8010.ps1

Write-Host "Killing processes on ports 8000-8010..." -ForegroundColor Yellow

# Kill processes on each port from 8000 to 8010
for ($port = 8000; $port -le 8010; $port++) {
    Write-Host "Checking port $port..." -ForegroundColor Cyan
    
    # Get processes using the port
    $netstatOutput = netstat -ano | Select-String ":$port "
    
    if ($netstatOutput) {
        foreach ($line in $netstatOutput) {
            # Extract PID from netstat output (last column)
            $parts = $line.ToString().Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
            $pid = $parts[-1]
            
            if ($pid -match '^\d+$') {
                try {
                    # Get process name for display
                    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($process) {
                        $processName = $process.ProcessName
                        Write-Host "Killing process '$processName' (PID: $pid) on port $port" -ForegroundColor Red
                        Stop-Process -Id $pid -Force
                        Write-Host "✓ Successfully killed process $pid on port $port" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "✗ Failed to kill process $pid on port $port" -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host "No processes found on port $port" -ForegroundColor Gray
    }
}

Write-Host "`nCompleted! All processes on ports 8000-8010 have been terminated." -ForegroundColor Green

# Show final status
Write-Host "`nFinal port status:" -ForegroundColor Cyan
for ($port = 8000; $port -le 8010; $port++) {
    $connections = netstat -ano | Select-String ":$port "
    if ($connections) {
        Write-Host "Port $port`: Still in use ⚠️" -ForegroundColor Yellow
    } else {
        Write-Host "Port $port`: Clear ✓" -ForegroundColor Green
    }
}

Write-Host "`nDone!" -ForegroundColor Green