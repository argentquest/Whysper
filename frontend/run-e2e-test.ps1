# Run the E2E Test for Diagram Wizard
# Tests: GPT-5 → Data Pipeline prompt → D2 diagram generation

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Diagram Wizard E2E Test                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Scenario:" -ForegroundColor Yellow
Write-Host "  1. Select GPT-5 model" -ForegroundColor White
Write-Host "  2. Enter: 'A Data Processing Pipeline, A SQL Server is used," -ForegroundColor White
Write-Host "            A user upload a a file to Incoming Folder'" -ForegroundColor White
Write-Host "  3. Answer clarification questions" -ForegroundColor White
Write-Host "  4. Select D2 diagram type" -ForegroundColor White
Write-Host "  5. Verify D2 diagram is generated" -ForegroundColor White
Write-Host ""
Write-Host "Running test..." -ForegroundColor Green
Write-Host ""

# Run the E2E test with verbose output
npm test -- DiagramWizard.e2e.test.tsx --reporter=verbose

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ TEST PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verified:" -ForegroundColor Yellow
    Write-Host "  ✓ GPT-5 model selected" -ForegroundColor Green
    Write-Host "  ✓ System description entered" -ForegroundColor Green
    Write-Host "  ✓ Clarification questions answered" -ForegroundColor Green
    Write-Host "  ✓ D2 diagram type selected" -ForegroundColor Green
    Write-Host "  ✓ D2 diagram code generated" -ForegroundColor Green
    Write-Host "  ✓ SVG diagram rendered" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "❌ TEST FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the output above for details" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "To run with UI: npm run test:ui" -ForegroundColor Cyan
Write-Host ""
