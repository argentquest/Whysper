# Kill processes on ports 8000-8010

Write-Host "Killing processes on ports 8000-8010..."

# Kill processes on each port
for ($port = 8000; $port -le 8010; $port++) {
    Write-Host "Checking port $port"
    
    # Get processes using the port and kill them
    $connections = netstat -ano | findstr ":$port "
    
    if ($connections) {
        $connections | ForEach-Object {
            $parts = $_.Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
            $processId = $parts[-1]
            
            if ($processId -match '^[0-9]+$') {
                Write-Host "Killing PID $processId on port $port"
                try {
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                    Write-Host "Killed $processId"
                } catch {
                    Write-Host "Failed to kill $processId"
                }
            }
        }
    } else {
        Write-Host "Port $port is free"
    }
}

Write-Host "Done!"