# DiagramWizard Model Selection Implementation Checklist

## Phase 1: Prompt Files ✅ COMPLETE

- [x] Create ANALYSE_CONFIRM for GPT-5 → `diagram-wizard-gpt5.md`
- [x] Create ANALYSE_CONFIRM for Grok → `diagram-wizard-grok.md`
- [x] Create ANALYSE_CONFIRM for Claude → `diagram-wizard-sonet45.md`
- [x] Create ANALYSE_CONFIRM for Gemini → `diagram-wizardgemini25pro.md`
- [x] Create CLARIFY_UNIVERSAL for GPT-5 → `clarify-universal-gpt5.md`
- [x] Create CLARIFY_UNIVERSAL for Grok → `clarify-universal-grok.md`
- [x] Create CLARIFY_UNIVERSAL for Claude → `clarify-universal-sonet45.md`
- [x] Create CLARIFY_UNIVERSAL for Gemini → `clarify-universal-gemini25pro.md`

**All 8 prompt files ready in:** `prompts/coding/agent/`

---

## Phase 2: Backend Infrastructure

### GraphState Updates
- [ ] Add `model_id: str` field
- [ ] Add `provider: str` field
- [ ] Add `model: str` field (full model name)
- [ ] Add `prompt_version: str` field
- [ ] File: `backend/app/utils/diagram_wizard/graph_state.py`

### MODEL_MAPPING Dictionary
- [ ] Create mapping in `backend/app/utils/diagram_wizard/main.py`
- [ ] Maps: model_id → (provider, model, prompt_files)
- [ ] Entries:
  - `'gpt5'` → GPT-5 files + provider
  - `'grok'` → Grok files + provider
  - `'claude'` → Claude files + provider
  - `'gemini'` → Gemini files + provider

### Prompt Loader Updates
- [ ] File: `backend/app/utils/diagram_wizard/prompt_loader.py`
- [ ] Update `get_prompt()` signature to accept optional `model_id`
- [ ] Implement model-specific lookup logic
- [ ] Fallback to generic prompt if model-specific not found
- [ ] Cache both generic and model-specific prompts

### API Endpoint: Start Session
- [ ] File: `backend/app/routes/diagram_wizard.py` (or similar)
- [ ] New POST `/api/diagram-wizard/start-session`
- [ ] Request body:
  ```json
  {
    "initial_prompt": "string - user's system description",
    "model_id": "gpt5|grok|claude|gemini"
  }
  ```
- [ ] Response includes: `session_id`, `status`, `model_id`
- [ ] Validate `model_id` exists in MODEL_MAPPING
- [ ] Store session with selected model_id

### Session Storage
- [ ] Update `session_store.py` to save `model_id`
- [ ] Session TTL: 1 hour (existing)
- [ ] Cleanup: Expired sessions auto-deleted

### Node: analyze_request
- [ ] File: `backend/app/utils/diagram_wizard/nodes.py`
- [ ] Get `model_id` from state
- [ ] Pass to `get_prompt()` for model-specific ANALYSE_CONFIRM
- [ ] Load model-specific prompt: `diagram-wizard-{model_id}.md`
- [ ] Use selected model's provider/model for LLM call

### Node: clarify_prompt
- [ ] File: `backend/app/utils/diagram_wizard/nodes.py`
- [ ] Get `model_id` from state
- [ ] Pass to `get_prompt()` for model-specific CLARIFY_UNIVERSAL
- [ ] Load model-specific prompt: `clarify-universal-{model_id}.md`
- [ ] Use selected model's provider/model for LLM call
- [ ] Pass `model_id` to `_call_llm()`

### Node: generate_json_representation (CRITICAL)
- [ ] File: `backend/app/utils/diagram_wizard/nodes.py`
- [ ] Update function signature to accept `model_id` from state
- [ ] Load model-specific JSON_GENERATION prompt: `JSON_GENERATION_{model_id}.md`
- [ ] Update prompt output to include:
  - `structurizr_workspace` (Full Structurizr DSL)
  - `clean_d2` (Normalized Structurizr)
  - `json_representation` (Legacy schema for backward compatibility)
- [ ] Parse response and validate both Structurizr and legacy schema
- [ ] Return updated state with all three representations
- [ ] Handle sync validation (workspace ↔ clean_d2)

### JSON Generation Prompts
- [ ] Update: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_PROMPT.md`
  - [ ] Add Structurizr output requirements
  - [ ] Add dual representation rules
  - [ ] Specify unified output schema
- [ ] Create: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_gpt5.md`
  - [ ] Model-specific guidance for GPT-5
- [ ] Create: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_grok.md`
  - [ ] Model-specific guidance for Grok
- [ ] Create: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_sonet45.md`
  - [ ] Model-specific guidance for Claude
- [ ] Create: `backend/app/utils/diagram_wizard/prompts/JSON_GENERATION_gemini25pro.md`
  - [ ] Model-specific guidance for Gemini

### Graph Integration: Add JSON Node
- [ ] File: `backend/app/utils/diagram_wizard/langgraph_builder.py`
- [ ] Import `generate_json_representation` from nodes
- [ ] Add node to workflow: `workflow.add_node("generate_json_representation", ...)`
- [ ] Update edge from clarify_prompt:
  - [ ] Old: clarify_prompt → determine_diagram_type
  - [ ] New: clarify_prompt → generate_json_representation → determine_diagram_type
- [ ] Update conditional routing if needed
- [ ] Test that graph compiles and runs

### LLM Processor: _call_llm()
- [ ] File: `backend/app/utils/diagram_wizard/nodes.py`
- [ ] Update signature to accept `model_id`
- [ ] Look up provider/model from MODEL_MAPPING
- [ ] Create AI processor with correct provider/model
- [ ] Make LLM call with selected model

### Error Handling
- [ ] Invalid `model_id` → HTTP 400 with clear message
- [ ] Model unavailable → HTTP 503 with fallback suggestion
- [ ] Session without model_id → default to Claude (backward compatible)

---

## Phase 3: Frontend Implementation

### ModelSelector Component
- [ ] Create: `frontend/src/components/DiagramWizard/ModelSelector.tsx`
- [ ] Display 4 cards with model options
- [ ] Each card shows:
  - Model name (GPT-5, Grok, Claude, Gemini)
  - Description
  - 3-4 key strengths
  - Select button
- [ ] Styling: Card layout, hover effects, responsive
- [ ] Callback: `onSelect(modelId: string)`

### DiagramWizard Component Update
- [ ] File: `frontend/src/components/DiagramWizard/DiagramWizard.tsx`
- [ ] Add state: `selectedModel: string | null`
- [ ] Conditional rendering:
  - If no model selected: show ModelSelector
  - If model selected: show wizard UI
- [ ] Pass `selectedModel` to all API calls

### API Call Updates
- [ ] File: `frontend/src/services/diagram/diagramApi.ts`
- [ ] Update `startDiagramSession()` to accept `modelId`
- [ ] POST to `/api/diagram-wizard/start-session`
- [ ] Include `model_id` in request body
- [ ] Store `modelId` in session state for subsequent calls

### Hook: useDiagramSession
- [ ] File: `frontend/src/components/DiagramWizard/hooks/useDiagramSession.ts`
- [ ] Update `startSession()` to accept `modelId`
- [ ] Pass through to API call
- [ ] Store `modelId` in local state for all subsequent calls

### UI Indicators (Optional)
- [ ] Display selected model name somewhere in wizard (top-right/breadcrumb)
- [ ] Show model badge during processing
- [ ] Helpful: "Running with GPT-5 (long-context analysis)"

---

## Phase 4: Testing

### Unit Tests
- [ ] Test MODEL_MAPPING lookup logic
- [ ] Test prompt_loader with model_id parameter
- [ ] Test session storage/retrieval with model_id
- [ ] Test invalid model_id handling

### Integration Tests
- [ ] Test full flow with GPT-5
  - [ ] StartSession with model_id='gpt5'
  - [ ] Verify correct prompt loaded
  - [ ] Verify LLM call uses GPT-5
  - [ ] Verify response handling
- [ ] Test full flow with Grok
- [ ] Test full flow with Claude
- [ ] Test full flow with Gemini

### Prompt Output Tests
- [ ] Verify ANALYSE_CONFIRM output JSON schema
- [ ] Verify CLARIFY_UNIVERSAL output JSON schema
- [ ] Validate Structurizr syntax for each model
- [ ] Test clarity_score progression (5→6→7→8)
- [ ] Test question generation (one per turn)
- [ ] Test ready flag behavior

### E2E Tests
- [ ] User selects GPT-5 → system uses it throughout
- [ ] User selects Grok → system uses it throughout
- [ ] User selects Claude → system uses it throughout
- [ ] User selects Gemini → system uses it throughout
- [ ] Complete diagram generation with each model
- [ ] Verify final SVG output

### Backward Compatibility Tests
- [ ] Old sessions without model_id still work
- [ ] Falls back to Claude if no model specified
- [ ] Environment variables still honored if no model selected

---

## Phase 5: Documentation

- [ ] Update API documentation
  - [ ] `POST /api/diagram-wizard/start-session` with model_id
  - [ ] Request/response examples
  - [ ] Error codes and messages
- [ ] Update README with model selection info
- [ ] Document MODEL_MAPPING
- [ ] Document prompt file naming convention
- [ ] Create user guide for selecting models
  - [ ] When to use each model
  - [ ] Performance vs. quality tradeoffs
  - [ ] Cost implications (if applicable)

---

## Phase 6: Deployment

- [ ] Deploy backend changes (graph_state, routes, nodes, prompt_loader)
- [ ] Deploy 8 new prompt files to prompts/coding/agent/
- [ ] Deploy frontend ModelSelector component
- [ ] Deploy API client updates
- [ ] Update frontend hook implementations
- [ ] Verify all environment variables set
- [ ] Smoke test with all 4 models

---

## Phase 7: Monitoring

- [ ] Track which models users select (analytics)
- [ ] Monitor success rates by model
- [ ] Alert on model unavailability
- [ ] Log clarity_score progression per session
- [ ] Monitor token usage per model
- [ ] Track refinement iterations per model

---

## Definitions of Done

### For each Phase:
- ✅ All tasks completed
- ✅ Unit tests passing
- ✅ Code reviewed
- ✅ Documentation updated
- ✅ No breaking changes
- ✅ Backward compatible (where applicable)

### For Full Feature:
- ✅ User can select model at start
- ✅ Selected model used throughout session
- ✅ All 4 models work correctly
- ✅ Proper error handling
- ✅ Tests covering all scenarios
- ✅ Documentation complete
- ✅ Deployed to production
- ✅ Monitoring in place

---

## Priority Order

**High Priority (Do First):**
1. Phase 1: Prompt files (✅ DONE)
2. GraphState updates + MODEL_MAPPING
3. Prompt loader updates
4. Backend node updates (analyze_request, clarify_prompt)
5. API endpoint for start-session

**Medium Priority:**
6. Frontend ModelSelector component
7. Frontend hook/API client updates
8. Integration tests
9. E2E tests

**Lower Priority:**
10. Documentation
11. Monitoring/analytics
12. Performance optimization

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Prompt quality varies by model | High | Medium | Extensive testing with all 4 models |
| User confusion about model differences | Medium | Low | Clear UI descriptions, help text |
| Backward compatibility issues | Low | High | Thorough compatibility testing |
| Performance issues with large models | Low | Medium | Token limits in prompts, timeouts |
| Model API key/access issues | Low | High | Proper error handling, fallbacks |

---

## Timeline Estimate

- **Phase 1 (Prompts):** ✅ Complete
- **Phase 2 (Backend):** 2-3 days
- **Phase 3 (Frontend):** 1-2 days
- **Phase 4 (Testing):** 2-3 days
- **Phase 5 (Documentation):** 1 day
- **Phase 6 (Deployment):** 1 day
- **Phase 7 (Monitoring):** 1 day

**Total:** ~10 days from this point

---

## Success Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All 4 models can be selected and used
- [ ] Clarity score progresses correctly
- [ ] Final SVG diagrams are generated successfully
- [ ] No performance degradation
- [ ] Zero breaking changes to existing functionality
- [ ] User documentation clear
- [ ] Analytics showing usage by model type

---

**Last Updated:** 2025-11-16
**Status:** Phase 1 ✅ Complete | Phase 2-7 📋 Ready to Begin
