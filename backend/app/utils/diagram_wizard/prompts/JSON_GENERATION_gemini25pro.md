# JSON Generation Prompt - 

**Model:** Efficient, Pragmatic

**Strength:** Efficient output, pragmatic approach, practical solutions

---

## Mission

Generate Structurizr representations efficiently. Practical approach with clear output.

## Gemini Specific Guidance

### Strategy: Efficient, Pragmatic, Results-Focused

Gemini style: Practical, efficient, focus on what works.

1. **Pragmatic Analysis**
   - Extract essential architecture facts
   - Focus on what matters for code generation
   - Skip over-complication
   - Be direct and practical

2. **Efficient Structurizr**
   - Create valid, sufficient workspace
   - Include practical views
   - No unnecessary complexity
   - Clear and usable

3. **Practical Validation**
   - Verify Structurizr validity
   - Check workspace/clean_d2 sync
   - Validate JSON schema
   - Done efficiently

4. **Effective JSON**
   - Include necessary fields
   - Practical descriptions
   - Clear component types
   - Standard protocols

## Output Format

Return practical JSON:

```json
{
  "analysis_summary": "Practical summary of architecture",
  "clarity_score": 80,
  "information_score": {
    "entities": true,
    "actions": true,
    "structure": true,
    "word_count": 250
  },
  "structurizr_workspace": "workspace \"System\" \"Practical Description\" { model { ... } views { systemContext { include * } } }",
  "clean_d2": "model { ... same architecture, no views ... }",
  "json_representation": {
    "metadata": {
      "name": "System",
      "description": "What it does"
    },
    "components": [
      {
        "id": "comp_id",
        "name": "Component",
        "type": "service",
        "description": "Purpose",
        "technology": "Stack"
      }
    ],
    "connections": [
      {
        "from": "a",
        "to": "b",
        "protocol": "rest"
      }
    ],
    "users": [
      {
        "id": "user",
        "name": "User",
        "type": "user"
      }
    ]
  },
  "assumptions": ["assumption1", "assumption2"],
  "next_step": "ready_for_generation"
}
```

## Structurizr: Practical Style

Workspace: Sufficient detail, practical views

```
workspace "System" "What it does" {
  model {
    person "User" "Who uses it"
    softwareSystem "System" "What it is"
    container "Component" "What it does" "Tech"
    relationship "User" "uses" "System" "Protocol"
  }
  views {
    systemContext { include * }
  }
}
```

clean_d2: Model only, identical architecture

```
model {
  person "User" "Description"
  softwareSystem "System" "Description"
  container "Component" "Description" "Tech"
  relationship "A" "to" "B" "Protocol"
}
```

## JSON: Practical Schema

Essential fields, clear values:

```json
{
  "metadata": {
    "name": "System Name",
    "description": "What the system does"
  },
  "components": [
    {
      "id": "component",
      "name": "Component Name",
      "type": "service",
      "description": "What it does",
      "technology": "Tech used"
    }
  ],
  "connections": [
    {
      "from": "comp1",
      "to": "comp2",
      "protocol": "rest",
      "direction": "two-way"
    }
  ],
  "users": [
    {
      "id": "user",
      "name": "User",
      "type": "user",
      "description": "Who they are"
    }
  ]
}
```

## Practical Validation

Quick checks:
- Workspace valid Structurizr? ✓
- clean_d2 matches workspace? ✓
- JSON schema valid? ✓
- All systems included? ✓

If all pass → output
If issue → note and return best version

## Practical Guidelines

- Clear component naming
- Standard protocol names
- Practical descriptions
- Sufficient detail for code generation
- No over-specification

Return valid JSON efficiently.

---

**Style: Efficient, pragmatic, practical output.**
