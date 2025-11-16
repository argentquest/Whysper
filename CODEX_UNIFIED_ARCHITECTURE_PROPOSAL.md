# CODEX Unified Architecture Proposal

## 1. Vision: The Best of Both Worlds

The separate `DiagramWizard` and `ArchitectureGenStudio` modules serve two distinct but valuable use cases: the former offers a guided, conversational experience ideal for discovery and refinement, while the latter provides a powerful, agent-driven studio for expert users.

The CODEX proposal is to evolve these two separate modules into a single, unified application called **Whysper Studio**. This new application will preserve the unique strengths of both original modules by offering two distinct but complementary user workflows:

*   **Wizard Mode:** An evolution of `DiagramWizard`, this mode will guide users through a stateful, conversational process to generate diagrams. It remains the ideal entry point for new users or those exploring complex ideas.
*   **Expert Mode:** An evolution of `ArchitectureGenStudio`, this mode will provide a direct, template-driven interface for power users who know exactly what they want to create, leveraging a rich set of agents and providers.

This unified approach eliminates redundancy, consolidates development effort, and creates a more powerful and flexible tool that can grow with the user, from novice to expert.

## 2. Guiding Principles

1.  **Unified Backend:** We will consolidate all diagram generation logic onto the robust, extensible provider-based backend from `ArchitectureGenStudio`. The `/diagrams/v2` API will become the single source of truth.
2.  **Modular Frontend:** We will create a shared library of core frontend components, including hooks for API communication, real-time updates, and state management, which will be used by both modes.
3.  **User-Centric Workflows:** The application shell will allow users to seamlessly switch between "Wizard Mode" and "Expert Mode," using the best tool for the task at hand.
4.  **Single Source of Truth:** One backend API, one set of core frontend components, and one unified application entry point.

## 3. Proposed Architecture Blueprint

### Backend Evolution: Unifying on the Provider Model

The core of this proposal is to refactor the `DiagramWizard`'s LangGraph-based conversational logic to fit within the `ArchitectureGenStudio`'s superior provider model.

1.  **Deprecate the `/diagram` API:** The legacy, session-based API for the wizard will be retired. All frontend interactions will target the `/diagrams/v2` endpoints.
2.  **Integrate LangGraph as a "Conversational Provider":**
    *   The logic from `backend/app/services/diagram_factory_service.py` will be encapsulated into a new provider, `ConversationalProvider`.
    *   This provider will conform to the `BaseDiagram` interface, just like the Mermaid, D2, and Kroki providers.
    *   It will be invoked via the standard, stateless `POST /api/v1/diagrams/v2/generate` endpoint.
    *   The provider itself will manage the state of the conversation (history, clarifications, scores) internally, using a request ID to handle multi-turn interactions. This gives us the stateful magic of the wizard within the clean, stateless architecture of the provider system.

This change centralizes all diagram generation logic, allowing any part of the application to access the conversational workflow, and enables the wizard to benefit from the provider model's built-in validation, error correction, and telemetry.

### Frontend Evolution: A Shared Component Library

The frontend will be refactored to eliminate duplicate code and establish a clear, modular structure.

1.  **Create a Shared Core Library (`frontend/src/core`):**
    *   **Hooks:** `ArchitectureGenStudio`'s resilient `useSSE`, `useAPIClient`, and `useLocalStorage` hooks will be moved here to be used by the entire application.
    *   **Components:** UI elements like zoom controls, export buttons, and status footers will be made generic and placed in the shared library.
2.  **Refactor `DiagramWizard`:**
    *   The wizard will be updated to use the shared hooks (`useAPIClient`, `useSSE`) instead of its bespoke API service.
    *   It will now call the `/diagrams/v2/generate` endpoint, specifically requesting the `conversational` provider.
    *   It will be enhanced with high-value features from the shared library, such as `localStorage` persistence and improved UI controls.
3.  **Build the Unified "Whysper Studio" Shell:**
    *   A new top-level component will serve as the application's main layout.
    *   This shell will feature a mode-switcher to toggle between "Wizard Mode" and "Expert Mode."
    *   "Wizard Mode" will render the refactored `DiagramWizard` component.
    *   "Expert Mode" will render the three-column `ArchitectureGenStudio` interface.

## 4. Phased Implementation Roadmap

This roadmap breaks the migration into manageable phases, delivering value at each step.

### Phase 1: Foundation & Backend Unification
*Goal: Consolidate the backend and create a shared frontend infrastructure.*
1.  **Establish Shared Frontend Library:** Create `frontend/src/core` and migrate `useSSE`, `useAPIClient`, and `useLocalStorage` from `ArchitectureGenStudio`.
2.  **Refactor LangGraph into a Provider:** Rework the `DiagramFactoryService` into the `ConversationalProvider` within the existing provider registry. This is the most critical task.
3.  **Align API Usage:** Update `DiagramWizard` to use the new shared hooks and target the `/diagrams/v2` endpoint. At this point, the old `/diagram` API can be deprecated.
4.  **Unify Environment:** Align both frontends to use a single `VITE_API_URL` and port.

### Phase 2: Enhancing the Wizard Experience
*Goal: Bring high-impact features from the studio into the wizard, leveraging the new shared architecture.*
1.  **Add Persistence:** Use the shared `useLocalStorage` hook to persist `DiagramWizard`'s session history and user input across page reloads.
2.  **Improve UI Controls:** Integrate shared components for zoom/pan functionality in the preview panel and add enhanced export options (e.g., PDF).
3.  **Enhance Accessibility:** Apply WCAG 2.1 AA standards to the wizard, focusing on ARIA labels and focus management.
4.  **Add Real-time Validation:** Leverage the provider backend's validation capabilities to provide real-time feedback in the wizard's code editor.

### Phase 3: The Unified Studio Shell
*Goal: Launch the unified application that seamlessly integrates both workflows.*
1.  **Build the Application Shell:** Create the main `WhysperStudio` component that includes the mode-switcher.
2.  **Integrate Modes:** Render the enhanced `DiagramWizard` in "Wizard Mode" and the `ArchitectureGenStudio` UI in "Expert Mode."
3.  **Finalize Integration:** Ensure smooth state transitions between modes and deprecate the old, separate application entry points.

By following this plan, we can strategically merge the best of both modules, creating a superior, unified diagramming tool that is both powerful and easy to use.
