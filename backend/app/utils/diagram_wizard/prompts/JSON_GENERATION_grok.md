# JSON Generation Prompt - Grok Edition

**Model:** Grok (Fast & Deterministic)

**Strength:** Speed, deterministic output, lean efficiency

---

## Mission

Fast analysis and output. Extract architecture facts and generate representations quickly.

## Grok Specific Guidance

### Strategy: Fast, Clean, Deterministic

Grok style: Lean, efficient, no wasted tokens.

1. **Quick Parse**
   - Scan conversation for systems, components, connections
   - Extract key facts only
   - Skip verbose elaboration

2. **Fast Structurizr Build**
   - Generate lean workspace with essentials
   - Include model and basic views
   - No unnecessary detail

3. **Quick Validation**
   - Workspace = clean_d2 architecture
   - All components consistent
   - All connections match

4. **Lean JSON**
   - Required fields only
   - Clean, minimal data
   - Fast to parse and validate

## Output Format

Return single JSON (minimal but complete):

```json
{
  "analysis_summary": "Architecture summary",
  "clarity_score": 8,
  "information_score": {"entities": true, "actions": true, "structure": true, "word_count": 200},
  "structurizr_workspace": "workspace \"System\" \"Desc\" { model { ... } views { systemContext { include * } } }",
  "clean_d2": "model { ... }",
  "json_representation": {"metadata": {"name": "S", "description": "D"}, "components": [], "connections": [], "users": []},
  "assumptions": ["fact1", "fact2"],
  "next_step": "ready_for_generation"
}
```

## Structurizr: Lean Format

```
workspace "System" "Description" {
  model {
    person "User" "Uses system"
    softwareSystem "System" "Main system"
    container "Component" "Does X" "Tech"
    relationship "A" "to" "B" "REST"
  }
  views {
    systemContext { include * }
  }
}
```

clean_d2: Same model block, no views.

## JSON: Minimal Valid Schema

```json
{
  "metadata": {
    "name": "System Name",
    "description": "What it does"
  },
  "components": [
    {"id": "comp", "name": "Component", "type": "service", "description": "Desc"}
  ],
  "connections": [
    {"from": "a", "to": "b", "protocol": "rest"}
  ],
  "users": [
    {"id": "u1", "name": "User", "type": "user"}
  ]
}
```

## Fast Validation

- Workspace valid Structurizr? Yes/No
- clean_d2 matches workspace? Yes/No
- All components in both? Yes/No
- JSON schema valid? Yes/No

If all yes → output
If no → note issue, still output best version

## Speed First

- No verbose descriptions
- No extra metadata
- No redundant detail
- Just essential architecture facts

Return valid JSON now.

---

**Grok style: Fast, deterministic, clean output.**
