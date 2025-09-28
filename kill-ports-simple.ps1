# Simple PowerShell script to kill processes on ports 8000-8010
# Uses netstat and taskkill for broader compatibility

Write-Host "Killing all processes on ports 8000-8010..." -ForegroundColor Yellow

# Function to kill processes on a specific port using netstat
function Kill-ProcessOnPortSimple {
    param (
        [int]$Port
    )
    
    Write-Host "Checking port $Port..." -ForegroundColor Cyan
    
    # Get PIDs using the port
    $netstatOutput = netstat -ano | Select-String ":$Port "
    
    if ($netstatOutput) {
        foreach ($line in $netstatOutput) {
            # Extract PID from netstat output (last column)
            $parts = $line.ToString().Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
            $pid = $parts[-1]
            
            if ($pid -match '^\d+$') {
                try {
                    # Get process name for display
                    $processName = (Get-Process -Id $pid -ErrorAction SilentlyContinue).ProcessName
                    if ($processName) {
                        Write-Host "Killing process '$processName' (PID: $pid) on port $Port" -ForegroundColor Red
                        taskkill /PID $pid /F | Out-Null
                        Write-Host "✓ Successfully killed process $pid on port $Port" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "✗ Failed to kill process $pid on port $Port" -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host "No processes found on port $Port" -ForegroundColor Gray
    }
}

# Kill processes on each port from 8000 to 8010
for ($port = 8000; $port -le 8010; $port++) {
    Kill-ProcessOnPortSimple -Port $port
}

Write-Host "`nCompleted! All processes on ports 8000-8010 have been terminated." -ForegroundColor Green

# Show final status
Write-Host "`nFinal port status:" -ForegroundColor Cyan
for ($port = 8000; $port -le 8010; $port++) {
    $result = netstat -ano | Select-String ":$Port " | Measure-Object
    if ($result.Count -eq 0) {
        Write-Host "Port $port`: Clear ✓" -ForegroundColor Green
    } else {
        Write-Host "Port $port`: Still in use ⚠️" -ForegroundColor Yellow
    }
}