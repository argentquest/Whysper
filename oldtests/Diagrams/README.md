# MCP Diagram Test Script

This directory contains a test script that processes diagram test prompts through the MCP endpoints.

## Files

- `test.json` - Contains test prompts for D2, Mermaid, and C4 diagrams
- `test_mcp_diagrams.py` - Python script that calls MCP endpoints for each test entry
- `history/` - Folder where request/response JSON files and generated SVG files are saved

## Prerequisites

1. Make sure the backend server is running on port 8003:
   ```bash
   python backend/main.py
   ```

2. Ensure all required dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the API key in the backend/.env file:
   - Copy backend/.envTemplate to backend/.env if it doesn't exist
   - Add your API key (e.g., OpenRouter) to the API_KEY variable
   - Example: `API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Running the Test Script

To run the test script and process all diagram test entries:

```bash
cd backend
python test_mcp_diagrams.py
```

## What the Script Does

1. Reads test data from `backend/tests/Diagrams/test.json`
2. For each test entry:
   - Calls the MCP endpoint `/mcp/tools/generate_and_render`
   - Sends the description as a prompt with the appropriate diagram type
   - Saves the request and response as a JSON file in the history folder
   - Extracts and saves any generated SVG files to the history folder
3. Uses the test ID as the root of the filename for all generated files

## Output Files

The script creates files in the `backend/tests/Diagrams/history/` folder:

- JSON files: `{id:02d}_{diagram_type}_{test_name}.json`
  - Contains the request data, response data, and metadata
- SVG files: `{id:02d}_{diagram_type}_{test_name}.svg`
  - Contains the generated diagram in SVG format

## Example

For a test entry with:
- id: 1
- name: "Basic Hierarchy and Flow"
- diagram_type: "d2"

The script will generate:
- `01_d2_Basic_Hierarchy_and_Flow.json`
- `01_d2_Basic_Hierarchy_and_Flow.svg` (if SVG is generated)

## Troubleshooting

1. **Connection Error**: Make sure the backend server is running on port 8003
2. **Import Error**: Ensure all dependencies are installed from requirements.txt
3. **Permission Error**: Make sure the script has write access to the history folder
4. **API Key Error**: If you see "API key is not configured" in the logs:
   - Check that backend/.env exists and contains a valid API_KEY
   - Ensure the API key is for the correct provider (default is OpenRouter)
5. **Playwright Error**: If you see NotImplementedError for Playwright:
   - This is a known issue on Windows with certain asyncio configurations
   - The script will automatically fall back to static HTML rendering