"""
Integration tests for LLM Correction Service
"""

from diagrams.llm_correction_service import LLMCorrectionService, get_llm_correction_service
import sys
from pathlib import Path
from unittest.mock import Mock

# Add backend to path for importing local modules
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


def test_llm_service_singleton():
    # Verify that the LLM service returns the same instance every time
    service1 = get_llm_correction_service()
    service2 = get_llm_correction_service()

    assert service1 is service2, "Should return same instance"
    print("[OK] LLM service singleton test passed")


def test_llm_service_availability_without_processor():
    # Ensure service is not available when no AI processor is configured
    service = LLMCorrectionService()

    assert not service.is_available(), "Should not be available without AI processor"
    print("[OK] LLM service availability test (no processor) passed")


def test_llm_service_availability_with_processor():
    # Confirm service becomes available when an AI processor is set
    mock_processor = Mock()
    service = LLMCorrectionService(ai_processor=mock_processor)

    assert service.is_available(), "Should be available with AI processor"
    print("[OK] LLM service availability test (with processor) passed")


def test_correction_prompt_building():
    # Test that correction prompts are constructed with all necessary components
    mock_processor = Mock()
    service = LLMCorrectionService(ai_processor=mock_processor)

    diagram_type = "mermaid"
    invalid_code = "graph TD\n  A -> B"
    error_message = "Syntax error on line 2"
    provider_rules = "Always use proper arrow syntax"

    # Construct correction prompt using internal method
    prompt = service._build_correction_prompt(
        diagram_type=diagram_type,
        invalid_code=invalid_code,
        error_message=error_message,
        provider_specific_rules=provider_rules,
    )

    # Verify all key elements are included in the prompt
    assert "mermaid" in prompt.lower(), "Prompt should mention diagram type"
    assert invalid_code in prompt, "Prompt should include invalid code"
    assert error_message in prompt, "Prompt should include error message"
    assert provider_rules in prompt, "Prompt should include provider rules"

    print("[OK] Correction prompt building test passed")


def test_code_extraction_from_llm_response():
    # Test extracting corrected code from different LLM response formats
    mock_processor = Mock()
    service = LLMCorrectionService(ai_processor=mock_processor)

    # Test extraction from code block response
    response_with_block = """Here's the corrected code:

```mermaid
graph TD
  A --> B
  B --> C
```
This should work now!"""

    extracted = service._extract_code_from_response(response_with_block, "mermaid")
    assert extracted.strip() == "graph TD\n  A --> B\n  B --> C", f"Should extract code from block, got: {extracted}"

    # Test extraction from plain text response (if supported, or fail gracefully)
    # The implementation might look for backticks. If not found, it returns the whole string or tries to clean it.
    response_plain = "graph TD\n  A --> B\n  B --> C"
    extracted_plain = service._extract_code_from_response(response_plain, "mermaid")
    # If it returns the whole string when no backticks
    assert "graph TD" in extracted_plain, "Should handle plain response"

    print("[OK] Code extraction test passed")


def test_mocked_correction_workflow():
    # Simulate a complete correction workflow using a mocked AI processor
    mock_processor = Mock()
    # Set up mock to return a corrected code response
    mock_processor.process_question.return_value = """Here's the corrected code:

```mermaid
graph TD
  A --> B
  B --> C
```"""

    service = LLMCorrectionService(ai_processor=mock_processor)

    # Attempt diagram code correction
    success, corrected_code, message = service.correct_diagram_code(
        diagram_type="mermaid",
        invalid_code="graph TD\n  A -> B\n  B -> C",
        error_message="Invalid arrow syntax",
        provider_specific_rules="Use --> for arrows",
        max_tokens=2000,
        temperature=0.2,
    )

    # Verify correction results and processor interactions
    assert success, "Correction should succeed"
    assert "graph TD" in corrected_code, "Should return corrected code"
    assert "-->" in corrected_code, "Should have correct arrow syntax"

    assert mock_processor.process_question.called, "Should call AI processor"
    call_args = mock_processor.process_question.call_args
    assert call_args[1]["max_tokens"] == 2000, "Should use specified max_tokens"
    assert call_args[1]["temperature"] == 0.2, "Should use specified temperature"

    print("[OK] Mocked correction workflow test passed")


def test_correction_failure_handling():
    # Test service behavior when AI processor fails to provide a correction
    mock_processor = Mock()
    # Configure mock to return an empty response
    mock_processor.process_question.return_value = ""

    service = LLMCorrectionService(ai_processor=mock_processor)

    # Attempt correction with expectation of failure
    success, corrected_code, message = service.correct_diagram_code(
        diagram_type="mermaid", invalid_code="invalid code", error_message="Some error"
    )

    # Verify failure handling mechanisms
    assert not success, "Should report failure"
    assert (
        "Could not extract" in message or "Failed" in message or "Empty response" in message
    ), "Should provide error message"
    assert corrected_code == "invalid code", "Should return original code on failure"

    print("[OK] Correction failure handling test passed")


def test_provider_specific_rules():
    # Ensure provider-specific rules are incorporated into correction prompts
    mock_processor = Mock()
    mock_processor.process_question.return_value = "```mermaid\ngraph TD\n```"

    service = LLMCorrectionService(ai_processor=mock_processor)

    provider_rules = "Always use subgraphs for complex diagrams"

    # Trigger correction to check rule inclusion
    service.correct_diagram_code(
        diagram_type="mermaid",
        invalid_code="test code",
        error_message="test error",
        provider_specific_rules=provider_rules,
    )

    # Verify provider rules are in the prompt
    call_args = mock_processor.process_question.call_args
    prompt = call_args[1]["question"]
    assert provider_rules in prompt, "Provider rules should be in prompt"

    print("[OK] Provider-specific rules test passed")


def run_all_tests():
    # Orchestrate and run the entire test suite
    print("\n" + "=" * 60)
    print("Testing LLM Correction Service")
    print("=" * 60 + "\n")

    test_llm_service_singleton()
    test_llm_service_availability_without_processor()
    test_llm_service_availability_with_processor()
    test_correction_prompt_building()
    test_code_extraction_from_llm_response()
    test_mocked_correction_workflow()
    test_correction_failure_handling()
    test_provider_specific_rules()

    print("\n" + "=" * 60)
    print("[OK] All LLM correction service tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
