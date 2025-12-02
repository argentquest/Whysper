# Diagram Wizard Test Runner
# Runs all tests related to the recent changes

Write-Host "🧪 Running Diagram Wizard Tests..." -ForegroundColor Cyan
Write-Host ""

# Run all DiagramWizard tests
Write-Host "📦 Running main DiagramWizard tests..." -ForegroundColor Yellow
npm test -- DiagramWizard.test.tsx --reporter=verbose

Write-Host ""
Write-Host "🔄 Running state management tests..." -ForegroundColor Yellow
npm test -- DiagramWizard.stateManagement.test.tsx --reporter=verbose

Write-Host ""
Write-Host "🔗 Running integration tests..." -ForegroundColor Yellow
npm test -- DiagramWizard.integration.test.tsx --reporter=verbose

Write-Host ""
Write-Host "✅ All tests complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 To view coverage, run: npm run test:coverage" -ForegroundColor Cyan
Write-Host "🎨 To view UI, run: npm run test:ui" -ForegroundColor Cyan
