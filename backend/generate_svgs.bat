@echo off
echo Generating SVGs for all valid D2 files...

cd backend\backend\test_results_50\temp_0.1\d2_code

for %%f in (*.d2) do (
    echo Processing %%f...
    d2 "%%f" "%%~nf.svg"
)

echo SVG generation complete!
pause