import pytest
from backend.tests_2026.integration.utils import skip_if_no_api_key, api_client

class TestCodeIntegration:

    def test_code_extraction(self, api_client):
        """Test extracting code blocks from content."""
        payload = {
            "messageId": "msg_test_001",
            "content": "Here is some python code:\n```python\nprint('Hello')\n```\nAnd some more:\n```javascript\nconsole.log('Hi');\n```"
        }

        response = api_client.post("/api/v1/code/extract", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        blocks = data["data"]
        assert len(blocks) == 2

        assert blocks[0]["language"] == "python"
        assert "print('Hello')" in blocks[0]["code"]

        assert blocks[1]["language"] == "javascript"
        assert "console.log('Hi')" in blocks[1]["code"]

    # We skip LLM dependent tests if no key, but extraction is pure logic usually?
    # Actually extraction uses `extract_code_blocks_from_content` which is likely regex based.
    # So we don't need API_KEY for this specific test unless it calls LLM.
    # The code says it uses `app.utils.code_extraction`, which is usually regex.
    # So this test should pass without API_KEY.
