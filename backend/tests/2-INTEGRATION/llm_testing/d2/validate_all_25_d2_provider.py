"""
Validate all 25 D2 tests using the Provider System (d2v1 provider)

This script:
1. Loads each test case from test.json
2. Gets the D2 code (pre-generated from test.json)
3. Renders with d2v1 provider via /api/v1/diagrams/v2/render
4. Saves validation results and SVG files
