sequenceDiagram
    participant User
    participant Frontend as DiagramWizard<br/>(React Component)
    participant API as Backend API<br/>(FastAPI)
    participant DFS as DiagramFactoryService<br/>(Python)
    participant LG as LangGraph<br/>Workflow Engine
    participant AI as AI Provider<br/>(OpenRouter)
    participant SSE as Server-Sent Events

    Note over User,SSE: Phase 1: Model Selection & Initial Setup

    User->>Frontend: Select AI Model (gpt5/grok/claude/gemini)
    Frontend->>Frontend: Store selectedModel in localStorage
    Frontend->>Frontend: Navigate to SystemDescriptionScreen

    Note over User,SSE: Phase 2: System Description & Analysis

    User->>Frontend: Enter system description
    Frontend->>API: POST /api/v1/diagram/start<br/>{"prompt": "...", "diagram_type": "Mermaid", "model_id": "claude"}
    API->>DFS: start_generation(initial_prompt, model_id)
    DFS->>DFS: Initialize GraphState with user prompt
    DFS->>LG: graph.ainvoke(initial_state)

    Note over LG,AI: LangGraph Node Execution - ANALYZE_REQUEST

    LG->>LG: analyze_request node
    LG->>AI: Call LLM with analyze_request prompt<br/>Analyze user requirements
    AI-->>LG: Return analysis + assessment_score + json_representation
    LG->>DFS: Push SSE update: "analyzing" -> "analysis_complete"
    DFS->>SSE: Send real-time status update
    SSE-->>Frontend: Update UI with analysis results

    Note over LG,AI: LangGraph Node Execution - CLARIFY_PROMPT Loop

    LG->>LG: clarify_prompt node (iterative)
    LG->>AI: Call LLM with clarify_universal prompt<br/>Ask clarifying questions
    AI-->>LG: Return question + clarity_score + updated json_representation
    LG->>DFS: Push SSE update: "clarifying"
    DFS->>SSE: Send clarification question
    SSE-->>Frontend: Show question to user

    User->>Frontend: Provide clarification response
    Frontend->>API: POST /api/v1/diagram/{session_id}/clarify<br/>{"response": "..."}
    API->>DFS: handle_clarification(response)
    DFS->>LG: Resume graph with updated clarification_history

    Note over LG,AI: Continue clarification loop until ready

    LG->>AI: LLM determines clarity_score >= 8
    AI-->>LG: Return ready=true + final_design_summary
    LG->>DFS: Push SSE update: "clarification_ready"
    DFS->>SSE: Send ready status
    SSE-->>Frontend: Show "Ready to proceed" UI

    User->>Frontend: Click "Confirm Ready"
    Frontend->>API: POST /api/v1/diagram/{session_id}/confirm-ready
    API->>DFS: confirm_ready()
    DFS->>LG: Set user_confirmed_ready=true, resume graph

    Note over LG,AI: Phase 3: Diagram Generation Pipeline

    LG->>LG: generate_json_representation node
    LG->>AI: Call LLM with json_generation prompt<br/>Create structured JSON + Structurizr DSL
    AI-->>LG: Return structurizr_workspace + clean_d2 + json_representation
    LG->>DFS: Push SSE update: "generating_json"
    DFS->>SSE: Send JSON generation status

    LG->>LG: determine_diagram_type node
    LG->>LG: Analyze keywords in final_design_summary
    LG->>LG: Select Mermaid/D2/PlantUML based on scoring
    LG->>DFS: Push SSE update: "diagram_type_determined"
    DFS->>SSE: Send selected diagram type

    LG->>LG: generate_code node
    LG->>AI: Call LLM with generate_{type} prompt<br/>Generate diagram syntax code
    AI-->>LG: Return diagram_code
    LG->>DFS: Push SSE update: "generating" -> "code_generated"
    DFS->>SSE: Send generated code

    Note over LG,SSE: Phase 4: Validation & Refinement Loop

    LG->>LG: validate_code node
    LG->>LG: Call provider.validate_code(diagram_code)
    alt Code is valid
        LG->>DFS: Push SSE update: "validating" -> valid
    else Code has errors
        LG->>LG: refine_code node (up to 3 attempts)
        LG->>AI: Call LLM with refine_{type} prompt<br/>Fix syntax errors
        AI-->>LG: Return refined_code
        LG->>LG: validate_code again
        LG->>DFS: Push SSE update: "refining" -> "code_refined"
        DFS->>SSE: Send refined code
    end

    Note over LG,SSE: Phase 5: Rendering & Completion

    LG->>LG: render_diagram node
    LG->>LG: Call provider.render_with_validation()<br/>Convert code to SVG
    LG->>DFS: Push SSE update: "rendering" -> "rendered" -> "completed"
    DFS->>SSE: Send final SVG output
    SSE-->>Frontend: Update to GenerationScreen with diagram

    Frontend->>Frontend: Navigate to GenerationScreen
    Frontend->>Frontend: Display diagram code + SVG preview
    Frontend->>Frontend: Enable export options

    Note over User,Frontend: User can export diagram or start new one