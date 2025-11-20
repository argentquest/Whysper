#!/usr/bin/env python3
"""
Test script to verify the JSON extraction function handles both wrapped and unwrapped JSON responses.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.diagram_wizard.nodes.llm_helpers import extract_json_from_response

def test_unwrapped_json():
    """Test parsing plain JSON string"""
    test_response = '{"question": "What are the main components?", "clarity_score": 75}'
    result = extract_json_from_response(test_response)
    assert result == {"question": "What are the main components?", "clarity_score": 75}
    print("✓ Unwrapped JSON test passed")

def test_wrapped_json_with_json_tag():
    """Test parsing JSON wrapped in ```json ... ``` blocks"""
    test_response = '```json\n{"question": "What are the main components?", "clarity_score": 75}\n```'
    result = extract_json_from_response(test_response)
    assert result == {"question": "What are the main components?", "clarity_score": 75}
    print("✓ Wrapped JSON with json tag test passed")

def test_wrapped_json_without_tag():
    """Test parsing JSON wrapped in ``` ... ``` blocks without json tag"""
    test_response = '```\n{"question": "What are the main components?", "clarity_score": 75}\n```'
    result = extract_json_from_response(test_response)
    assert result == {"question": "What are the main components?", "clarity_score": 75}
    print("✓ Wrapped JSON without tag test passed")

def test_nested_json_in_text():
    """Test parsing JSON embedded in larger text"""
    test_response = 'Here is the analysis:\n```json\n{"question": "What are the main components?", "clarity_score": 75}\n```\nLet me know if you need more details.'
    result = extract_json_from_response(test_response)
    assert result == {"question": "What are the main components?", "clarity_score": 75}
    print("✓ Nested JSON in text test passed")

def test_invalid_json():
    """Test handling of invalid JSON"""
    test_response = 'This is not JSON at all'
    try:
        extract_json_from_response(test_response)
        assert False, "Should have raised JSONDecodeError"
    except Exception as e:
        assert "JSON" in str(type(e).__name__) or "parse" in str(e).lower()
        print("✓ Invalid JSON handling test passed")

def test_complex_nested_json():
    """Test parsing complex nested JSON structures"""
    test_response = '''```json
{
    "question": "What are the main components?",
    "clarity_score": 75,
    "suggested_components": ["input", "processor", "output"],
    "metadata": {
        "confidence": 0.8,
        "model": "gpt-4"
    }
}
```'''
    result = extract_json_from_response(test_response)
    expected = {
        "question": "What are the main components?",
        "clarity_score": 75,
        "suggested_components": ["input", "processor", "output"],
        "metadata": {
            "confidence": 0.8,
            "model": "gpt-4"
        }
    }
    assert result == expected
    print("✓ Complex nested JSON test passed")

def run_all_tests():
    """Run all test cases"""
    print("Testing JSON extraction function...")
    print("=" * 50)
    
    try:
        test_unwrapped_json()
        test_wrapped_json_with_json_tag()
        test_wrapped_json_without_tag()
        test_nested_json_in_text()
        test_invalid_json()
        test_complex_nested_json()
        
        print("=" * 50)
        print("🎉 All tests passed! The JSON extraction function works correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)