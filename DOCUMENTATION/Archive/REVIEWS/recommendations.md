# Consolidated Recommendations for Diagram Wizard

This document provides a consolidated and prioritized list of recommendations for improving the `diagram_wizard` feature, based on reviews from ROO, CLAUDE, and Gemini.

## High Priority

1.  **Enforce Refinement Attempt Limit:**
    *   **Issue:** The refinement loop (`validate_code` -> `refine_code` -> `validate_code`) can run indefinitely if the LLM consistently fails to produce valid code.
    *   **Recommendation:** In `nodes.py`, within the `refine_code` function, add a check to limit the number of refinement attempts to a maximum of 3. If the limit is reached, the loop should be terminated, and an error state should be returned.

2.  **Address Unused `user_approved_render` Flag:**
    *   **Issue:** The `route_validation` function in `langgraph_builder.py` checks for a `user_approved_render` flag that is never set. This makes the approval gate non-functional.
    *   **Recommendation:** Either implement the logic to set this flag (e.g., after a user interaction) or remove the check from the `route_validation` function to eliminate the dead code.

3.  **Implement Clarification Timeout:**
    *   **Issue:** The `clarification_timeout` flag in `GraphState` is defined but never used. The clarification loop can continue indefinitely.
    *   **Recommendation:** Implement a timeout mechanism in the `clarify_prompt` node. This could be based on a timer or a maximum number of clarification questions.

## Medium Priority

4.  **Improve State Tracking for Frontend:**
    *   **Issue:** The `current_state` is updated inconsistently across the nodes, making it unreliable for the frontend to track the wizard's state accurately.
    *   **Recommendation:** Standardize the `current_state` updates in all nodes. Ensure that every node returns a `current_state` and that the values used are from the `SessionState` enum.

5.  **Refactor Provider Mapping:**
    *   **Issue:** The dictionary that maps diagram types to provider IDs is duplicated in `validate_code` and `render_diagram` in `nodes.py`.
    *   **Recommendation:** To adhere to the DRY (Don't Repeat Yourself) principle, extract the `provider_map` into a constant at the module level in `nodes.py`.

6.  **Improve Exception Handling:**
    *   **Issue:** The `_call_llm` function in `nodes.py` uses a broad `except Exception` block, which can hide specific errors and make debugging difficult.
    *   **Recommendation:** Refactor the error handling to catch more specific exceptions and provide more detailed logging for each error type.

## Low Priority

7.  **Clarify Routing Function Naming:**
    *   **Issue:** The `route_clarification` function in `langgraph_builder.py` is misleadingly named, as it routes to the `determine_diagram_type` node, not back to clarification.
    *   **Recommendation:** Rename the function to something more descriptive, such as `route_to_diagram_type_determination`, to improve code readability.

8.  **Clean Up `SessionState` Enum:**
    *   **Issue:** The `SessionState` enum in `graph_state.py` contains several unused values.
    *   **Recommendation:** Remove the unused enum values (`INITIALIZED`, `INPUT_PHASE`, `EDIT_MODE`, `COMPLETED`, `VALIDATION_ERROR`) to keep the state definition clean.

9.  **Standardize Diagram Type Conversion:**
    *   **Issue:** The conversion from the `DiagramType` enum to a string is handled inconsistently across different nodes.
    *   **Recommendation:** Create a helper function to handle this conversion to ensure consistency and reduce code duplication.

10. **Update `GraphState` TypedDict:**
    *   **Issue:** The `_update_callback` and `_session_id` fields are used in the nodes but are not defined in the `GraphState` TypedDict.
    *   **Recommendation:** Add these fields to the `GraphState` definition in `graph_state.py` to improve type hinting and code clarity.
