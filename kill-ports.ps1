# Define the port range
$StartPort = 8000
$EndPort = 8010

Write-Host "Searching for processes using ports $StartPort to $EndPort..."

# Get all listening TCP ports and associated PIDs within the specified range
$Processes = Get-NetTCPConnection | Where-Object {
    $_.State -eq "Listen" -and $_.LocalPort -ge $StartPort -and $_.LocalPort -le $EndPort
} | Select-Object -Unique LocalPort, OwningProcess

if ($Processes.Count -eq 0) {
    Write-Host "No services found listening on ports $StartPort through $EndPort."
} else {
    Write-Host "--- Found Services ---"
    $Processes | ForEach-Object {
        $Port = $_.LocalPort
        $PID = $_.OwningProcess
        
        # Get the process name using the PID
        $ProcessInfo = Get-Process -Id $PID -ErrorAction SilentlyContinue
        $ProcessName = if ($ProcessInfo) { $ProcessInfo.ProcessName } else { "Unknown Process" }
        
        Write-Host "Stopping Process: [$ProcessName] (PID: $PID) on Port: $Port"
        
        # Stop the process
        Stop-Process -Id $PID -Force -ErrorAction SilentlyContinue
    }
    Write-Host "----------------------"
    Write-Host "All processes in the range 8000-8010 have been terminated."
}
