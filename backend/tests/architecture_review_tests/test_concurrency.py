import asyncio
import uuid
import pytest
from unittest.mock import patch
from app.services.diagram_factory_service import DiagramSessionStore, DiagramFactoryService

# Mock the call_llm function to avoid external API calls


async def mock_call_llm(*args, **kwargs):
    prompt = args[0] if args else kwargs.get("prompt", "")
    # Return different JSON based on the prompt content to simulate workflow
    if "Analyze the following request" in prompt:
        return """
        {
            "analysis_summary": "Analysis complete",
            "assessment_score": 90,
            "clarity_score": 90,
            "json_representation": {"nodes": [], "edges": []},
            "question": null
        }
        """
    elif "Generate Mermaid code" in prompt:
        return """
        graph TD
            A[Start] --> B[End]
        """
    else:
        return "{}"


# Mock get_prompt to return a dummy string


def mock_get_prompt(*args, **kwargs):
    return "Dummy Prompt"


@pytest.mark.asyncio
async def test_concurrent_sessions():
    """
    Test that multiple diagram sessions can run concurrently without state leakage.
    """

    # Clean up any existing sessions
    DiagramSessionStore._sessions = {}

    num_sessions = 5
    sessions = []

    # Patches
    with patch("app.utils.diagram_wizard.nodes.analysis_nodes.call_llm", side_effect=mock_call_llm), patch(
        "app.utils.diagram_wizard.nodes.analysis_nodes.get_prompt", side_effect=mock_get_prompt
    ), patch("app.utils.diagram_wizard.nodes.llm_helpers.call_llm", side_effect=mock_call_llm), patch(
        "app.utils.diagram_wizard.nodes.llm_helpers._get_model_for_id", return_value="gpt-mock"
    ):

        # Create and start 5 sessions
        for i in range(num_sessions):
            session_id = str(uuid.uuid4())
            session = DiagramSessionStore.create_session(session_id)
            service = DiagramFactoryService(session)

            # Start generation (this is async but returns quickly as it spawns a task)
            # We use "auto" to trigger analysis
            prompt = f"System {i}: User logs in and views dashboard."
            await service.start_generation(prompt, diagram_type="auto")
            sessions.append((session, service, prompt))

        # Verify unique session IDs and objects
        assert len(DiagramSessionStore._sessions) == num_sessions
        session_ids = [s.session_id for s, _, _ in sessions]
        assert len(set(session_ids)) == num_sessions

        # Wait for a bit to let the background tasks run
        # The mocked LLM calls are fast, but we need to give the event loop time to process
        await asyncio.sleep(2)

        # Verify state isolation
        for i, (session, _, prompt) in enumerate(sessions):
            # Check history
            assert len(session.history) >= 1
            assert session.history[0] == ("user", prompt)

            # Check internal graph state
            # Ideally, analysis should be complete
            state = session.graph_state
            assert state is not None
            # Check that the prompt in state matches the session's prompt
            assert state.get("design_prompt") == prompt

            # Check that update queue has items (indicating activity)
            assert not session.update_queue.empty()

            # Verify no cross-talk: ensure no other session's prompt is in this session's history
            for other_i, (_, _, other_prompt) in enumerate(sessions):
                if i != other_i:
                    history_text = str(session.history)
                    assert other_prompt not in history_text, f"Session {i} polluted with Session {other_i}'s prompt"

    print(f"Successfully ran {num_sessions} concurrent sessions with verified isolation.")


if __name__ == "__main__":
    # Manually run the test function if executed directly
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_concurrent_sessions())
    loop.close()
