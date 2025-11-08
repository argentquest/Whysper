# Diagram Code Generation Prompts

Prompts for generating actual diagram code from finalized design specifications.

---

## Mermaid Generation Prompt

### Instructions

You are a Mermaid diagram expert. Convert the following design specification into clean, valid Mermaid code.

**Design Specification:**
{final_design_summary}

**Requirements:**
1. Return ONLY the raw Mermaid code block
2. Do NOT include markdown backticks or explanations
3. Ensure the syntax is 100% valid for Mermaid
4. Use proper formatting and indentation
5. Include appropriate labels and descriptions
6. Match the diagram type implied by the design

**Mermaid Best Practices:**
- Use clear, descriptive labels
- Avoid circular references where possible
- Use appropriate diagram keywords
- For flowcharts: use `graph TD` for top-down
- For sequences: properly define actors and messages
- For state: clearly define states and transitions

**Example Output:**
```
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process A]
    B -->|No| D[Process B]
    C --> E[End]
    D --> E
```

Return your Mermaid code now (no explanations, just code):

---

## D2 Generation Prompt

### Instructions

You are a D2 architecture diagram expert. Convert the following design specification into clean, valid D2 code.

**Design Specification:**
{final_design_summary}

**Requirements:**
1. Return ONLY the raw D2 code block
2. Do NOT include markdown backticks or explanations
3. Ensure the syntax is 100% valid for D2
4. Use proper connections and labels
5. Group related components logically
6. Include styling for clarity where appropriate

**D2 Best Practices:**
- Use containers (`shape: container`) for grouping
- Use appropriate shapes for different component types
- Use arrows with labels for connections
- Style text for emphasis: `text: {underline: true}`
- Use colors for different layers/roles
- Keep layout logical (left-to-right or top-down)

**Common D2 Shapes:**
- `shape: circle` for endpoints/users
- `shape: rectangle` for services/databases
- `shape: container` for grouping
- `shape: queue` for message queues
- `shape: database` for databases

**Example Output:**
```
A: Client
B: API Gateway
C: Service 1
D: Database

A -> B: HTTP Request
B -> C: Route to Service
C -> D: Query
D -> C: Result
C -> B: Response
B -> A: JSON Response
```

Return your D2 code now (no explanations, just code):

---

## PlantUML Generation Prompt

### Instructions

You are a PlantUML diagram expert. Convert the following design specification into clean, valid PlantUML code.

**Design Specification:**
{final_design_summary}

**Requirements:**
1. Return ONLY the raw PlantUML code block
2. Do NOT include @startuml/@enduml markers
3. Ensure the syntax is 100% valid for PlantUML
4. Use appropriate diagram keywords (actor, participant, class, component, usecase)
5. Include clear relationships and interactions
6. Match the diagram type (sequence, class, component, usecase)

**PlantUML Best Practices:**

#### For Sequence Diagrams:
- Define actors/participants first
- Show interactions with `->`, `-->` arrows
- Use activation boxes for active periods
- Include note blocks for clarification
- Use `alt/else` for alternatives

#### For Class Diagrams:
- Define classes with attributes and methods
- Use relationships: inheritance `--|>`, composition `*--`, aggregation `o--`
- Include visibility markers: `+` public, `-` private, `#` protected
- Add cardinality where relevant

#### For Component Diagrams:
- Group related components
- Use interfaces for connections
- Show dependencies clearly
- Use appropriate stereotypes

#### For Use Case Diagrams:
- Define actors
- Show use cases as ovals
- Use extends/includes relationships
- Group related use cases

**Example Output (Sequence):**
```
actor User
participant Client
participant API
database DB

User -> Client: Click Button
Client -> API: POST /data
API -> DB: Query
DB --> API: Result
API --> Client: JSON Response
Client --> User: Show Result
```

Return your PlantUML code now (no explanations, just code):

---

## General Guidelines for All Formats

### Code Quality Standards

1. **Readability**
   - Use meaningful names and labels
   - Proper spacing and indentation
   - Clear hierarchy and grouping

2. **Completeness**
   - All entities from design summary included
   - All relationships shown
   - No missing components

3. **Syntax Validity**
   - 100% valid for the target format
   - No warnings or errors
   - Ready to render immediately

4. **Adherence to Design**
   - Matches the provided design specification exactly
   - Uses correct terminology
   - Represents all interactions/relationships

### Common Pitfalls to Avoid

1. **Don't** include:
   - Markdown backticks
   - Code block markers
   - Explanatory text
   - Comments (unless required by format)

2. **Do**:
   - Return ONLY the diagram code
   - Use proper syntax
   - Include all details from design
   - Use clear labels

3. **Format-Specific**:
   - Mermaid: Use graph keywords correctly
   - D2: Proper connection syntax
   - PlantUML: Proper stereotypes and keywords

---

## Diagram-Type-Specific Hints

### Mermaid
- Best for: Flowcharts, sequence diagrams, state diagrams, Gantt charts
- Syntax: Use `--` for longer connections, `-->` for arrows
- Labels: Put descriptive text in `|text|` format after arrow

### D2
- Best for: Architecture and system design diagrams
- Syntax: Use `->` for simple connections, `<->` for bidirectional
- Styling: Use `style:` block for formatting
- Grouping: Use containers to group related items

### PlantUML
- Best for: UML diagrams (class, sequence, component, usecase)
- Syntax: Use `-->`, `--|>` (inheritance), `*--` (composition)
- Participants: Define in order of appearance
- Messages: Use `->` for synchronous, `-->` for asynchronous
