# Diagram Code Refinement Prompts

Prompts for refining and fixing diagram code when validation fails.

---

## Mermaid Refinement Prompt

### Instructions

The previous attempt to generate a Mermaid diagram failed validation. Analyze the error, understand the root cause, and provide corrected code.

**Original Design Summary:**
{final_design_summary}

**Invalid Code (Failed Validation):**
```
{diagram_code}
```

**Validation Error:**
{validation_error}

**Error Type:** {error_type}

### Your Task

1. **Analyze the error** - What syntax issue caused the failure?
2. **Identify the root cause** - Is it a bracket issue? Keyword error? Connection syntax?
3. **Fix the code** - Apply the correction while maintaining the design intent
4. **Validate mentally** - Ensure the corrected code would pass validation

### Error-Specific Guidance

#### Syntax Error
- Check all brackets are properly closed
- Verify keywords are correct (graph, subgraph, etc.)
- Check arrow syntax (-->, --, |text|)
- Ensure all node IDs are valid

#### Missing Element / Invalid Reference
- Ensure all referenced nodes are defined
- Add missing definitions before references
- Check node IDs match exactly (case-sensitive)

#### Tool Timeout
- Simplify the diagram (reduce number of nodes)
- Remove unnecessary details
- Break into smaller subgraphs if too complex

### Mermaid Syntax Reminders

```
# Flowchart
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[Alt Action]

# Sequence
sequenceDiagram
    Actor User
    User->>System: Request
    System->>DB: Query
    DB-->>System: Result

# State
stateDiagram-v2
    [*] --> State1
    State1 --> State2
    State2 --> [*]
```

Return ONLY the corrected Mermaid code (no explanations):

---

## D2 Refinement Prompt

### Instructions

The previous attempt to generate a D2 diagram failed validation. Analyze the error, understand the root cause, and provide corrected code.

**Original Design Summary:**
{final_design_summary}

**Invalid Code (Failed Validation):**
```
{diagram_code}
```

**Validation Error:**
{validation_error}

**Error Type:** {error_type}

### Your Task

1. **Analyze the error** - What syntax issue caused the failure?
2. **Identify the root cause** - Connection syntax? Shape definition? Nesting issue?
3. **Fix the code** - Apply the correction while preserving the design intent
4. **Validate mentally** - Ensure the corrected code would pass validation

### Error-Specific Guidance

#### Syntax Error
- Check all connections use proper syntax (`->`, `<->`, `=>`)
- Verify shape declarations are correct
- Ensure all blocks are properly closed
- Check for mismatched parentheses/brackets

#### Missing Element
- Ensure all referenced objects are defined
- Check that all connections have valid endpoints
- Add missing container definitions

#### Invalid Reference
- Verify object names match exactly
- Check for typos in object IDs
- Ensure nested objects are referenced correctly

### D2 Syntax Reminders

```
# Basic connection
A -> B: Label

# Container grouping
Container {
    A: Item 1
    B: Item 2
    A -> B
}

# Shape definition
Node: {
    shape: rectangle
    label: Description
}

# Complex structure
Web: {
    shape: browser
}
API: {
    shape: container
    label: API Gateway
}
DB: {
    shape: database
}
Web -> API: Request
API -> DB: Query
```

Return ONLY the corrected D2 code (no explanations):

---

## PlantUML Refinement Prompt

### Instructions

The previous attempt to generate a PlantUML diagram failed validation. Analyze the error, understand the root cause, and provide corrected code.

**Original Design Summary:**
{final_design_summary}

**Invalid Code (Failed Validation):**
```
{diagram_code}
```

**Validation Error:**
{validation_error}

**Error Type:** {error_type}

### Your Task

1. **Analyze the error** - What PlantUML syntax issue caused the failure?
2. **Identify the root cause** - Keyword error? Missing declaration? Arrow syntax?
3. **Fix the code** - Apply the correction while maintaining design intent
4. **Validate mentally** - Ensure the corrected code is valid PlantUML

### Error-Specific Guidance

#### Syntax Error
- Verify all arrows are correctly formatted (`->`, `-->`, `--|>`, `*--`, `o--`)
- Check that all objects are properly declared
- Ensure closing keywords exist (end, endnote, etc.)
- Validate quotes and special characters are escaped

#### Missing Element / Invalid Reference
- Ensure all referenced objects are defined
- Define actors/participants before using them
- Check that inheritance/relationship targets exist

#### Invalid Keyword
- Verify actor/participant/class/component keywords are correct
- Check that stereotypes are properly formatted
- Use correct relationship keywords for diagram type

### PlantUML Syntax Reminders

```
# Sequence Diagram
participant A
participant B
A -> B: Message
B --> A: Response

# Class Diagram
class ClassName {
    + publicAttr: Type
    - privateAttr: Type
    + publicMethod()
}

# Component Diagram
component Comp1
component Comp2
Comp1 --> Comp2

# Use Case Diagram
actor User
usecase UC1
User --> UC1
```

Return ONLY the corrected PlantUML code (no explanations, no @startuml/@enduml):

---

## Generic Refinement Strategy

### Step-by-Step Approach

1. **Parse the Error Message**
   - What syntax rule was violated?
   - Where is the error located?
   - What should be there instead?

2. **Review the Original Code**
   - Identify the problematic section
   - Understand what was intended
   - Locate the mistake

3. **Apply Targeted Fixes**
   - Fix ONLY the error
   - Don't over-engineer
   - Keep the rest of the code intact

4. **Mental Validation**
   - Read through the code
   - Check syntax rules apply
   - Ensure design intent is preserved

5. **Return Corrected Code**
   - ONLY raw code, no explanation
   - Ready to validate and render

### Common Issues & Fixes

| Issue | Mermaid | D2 | PlantUML |
|-------|---------|-----|----------|
| **Missing closing bracket** | Add `}` | Add `}` | Check all blocks |
| **Invalid arrow** | Use `-->` or `--` | Use `->` or `<->` | Use `-->` or `--|>` |
| **Undefined node** | Define before reference | Define before reference | Declare first |
| **Special characters** | Quote if needed | Use quotes | Escape or quote |
| **Nesting error** | Check indentation | Fix container scope | Check block closure |

### Error Classification

**Syntax Errors** → Usually easy fixes (brackets, keywords, arrows)

**Missing Elements** → Add required definitions

**Invalid References** → Ensure all targets exist first

**Tool Timeout** → Simplify complexity, break into smaller diagrams

---

## Quality Checklist

Before returning corrected code:

- [ ] Error understood and root cause identified
- [ ] Correction applied cleanly
- [ ] Design intent preserved
- [ ] Syntax is valid for the format
- [ ] All required elements present
- [ ] All references resolved
- [ ] Code is ready to validate and render
- [ ] No explanations or extra text included
