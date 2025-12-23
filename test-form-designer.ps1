# Quick Test Script for Form Designer
Write-Host "========================================"
Write-Host "Form Designer Test - Quick Verification"
Write-Host "========================================"
Write-Host ""

# Check if servers are running
Write-Host "Checking server status..."
$backendStatus = Get-NetTCPConnection -LocalPort 8003 -State Listen -ErrorAction SilentlyContinue
$frontendStatus = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue

if ($backendStatus) {
    Write-Host "✅ Backend server is running on port 8003" -ForegroundColor Green
} else {
    Write-Host "❌ Backend server is NOT running on port 8003" -ForegroundColor Red
}

if ($frontendStatus) {
    Write-Host "✅ Frontend server is running on port 5173" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend server is NOT running on port 5173" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================"
Write-Host "Testing Steps:"
Write-Host "========================================"
Write-Host ""
Write-Host "1. Open your browser and go to: http://localhost:5173"
Write-Host ""
Write-Host "2. Click the 'New Tab' button in the TabManager"
Write-Host ""
Write-Host "3. Select 'Form Designer' from the dropdown menu"
Write-Host ""
Write-Host "4. Verify the FormDesignerView loads with 4 tabs:"
Write-Host "   - Designer (visual form builder)"
Write-Host "   - Preview (live form preview)"
Write-Host "   - JSON Schema (schema editor)"
Write-Host "   - UI Schema (UI schema editor)"
Write-Host ""
Write-Host "5. Test the Designer tab:"
Write-Host "   - Should show the FormBuilder component"
Write-Host "   - Should be interactive"
Write-Host ""
Write-Host "6. Test the Preview tab:"
Write-Host "   - Should show a rendered form"
Write-Host "   - Should update when schema changes"
Write-Host ""
Write-Host "7. Check browser console (F12) for any errors"
Write-Host ""
Write-Host "========================================"
Write-Host "Expected Results:"
Write-Host "========================================"
Write-Host "✅ Form Designer tab creates successfully"
Write-Host "✅ FormBuilder component renders"
Write-Host "✅ All tabs are functional"
Write-Host "✅ No console errors"
Write-Host ""
Write-Host "For detailed testing, see: TEST_FORM_DESIGNER.md"
Write-Host ""

