# C4 Diagram Generation - User Guide

**Status**: ✅ Ready to Use
**Last Updated**: November 2, 2025

---

## Quick Start

The system now supports intelligent C4 diagram generation with automatic level detection. Simply request a diagram with any C4-related terminology, and the system will:

1. **Detect** the C4 level (C1, C2, C3, or C4) from your request
2. **Load** the appropriate specialized system prompt
3. **Generate** valid PlantUML C4 code
4. **Render** the diagram in SVG or PNG format

---

## Examples by C4 Level

### C1: System Context Diagram

**What it shows**: Your system and how it interacts with users and external systems at the highest level.

**Example requests**:
- "Create a C1 diagram for an e-commerce platform"
- "Show me the system context for a hospital management system"
- "C1 diagram showing our SaaS analytics platform"

**Result**: PlantUML C4 with `Person`, `System`, `System_Ext`, and `Rel` macros.

```plantuml
@startuml C1_Example
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "User", "End user of the system")
System(mysystem, "My System", "Core application")
System_Ext(external, "External Service", "Third-party API")

Rel(user, mysystem, "Uses")
Rel(mysystem, external, "Integrates with")

SHOW_LEGEND()
@enduml
```

---

### C2: Container Diagram

**What it shows**: Internal structure of your system - the deployable components (APIs, databases, services, etc).

**Example requests**:
- "Create a C2 container diagram for my e-commerce system"
- "Show the containers: web app, API, databases, cache, payment gateway"
- "C2 diagram with microservices architecture"

**Result**: PlantUML C4 with `System_Boundary`, `Container`, `ContainerDb`, `ContainerQueue`, and `Rel` macros.

```plantuml
@startuml C2_Example
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(user, "User", "System user")

System_Boundary(sys, "My System") {
  Container(web, "Web App", "React", "User interface")
  Container(api, "API", "Node.js", "Business logic")
  ContainerDb(db, "Database", "PostgreSQL", "Data storage")
}

System_Ext(payment, "Payment Gateway", "Stripe")

Rel(user, web, "Uses")
Rel(web, api, "Calls")
Rel(api, db, "Queries")
Rel(api, payment, "Integrates")

SHOW_LEGEND()
@enduml
```

---

### C3: Component Diagram

**What it shows**: Internal structure of ONE container, broken down into its components (controllers, services, repositories, etc).

**Example requests**:
- "Create a C3 diagram showing the components inside the API container"
- "C3 for an Order Service with controller, services, repository"
- "Component diagram of the web application"

**Result**: PlantUML C4 with `Container_Boundary`, `Component`, `ContainerDb`, and `Rel` macros.

```plantuml
@startuml C3_Example
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

Container_Boundary(api, "API Service") {
  Component(controller, "Controller", "Express", "Request handler")
  Component(service, "Service", "Business logic")
  Component(repository, "Repository", "Data access")
}

ContainerDb(db, "Database", "PostgreSQL", "Data")

Rel(controller, service, "Uses")
Rel(service, repository, "Uses")
Rel(repository, db, "Queries")

SHOW_LEGEND()
@enduml
```

---

### C4: Code Level Diagram

**What it shows**: Class-level and method-level architecture (rarely used; usually better represented in code).

**Example requests**:
- "Create a C4 diagram showing the class structure for a domain model"
- "Code level diagram for authentication service classes"
- "C4 diagram showing design patterns"

**Result**: PlantUML UML class diagram (not C4 macros).

**Note**: This level is optional and rarely used in practice.

---

## How to Use

### 1. Make a Request

Send a request to the diagram generation endpoint:

```bash
curl -X POST http://localhost:8003/api/v1/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a C2 container diagram for an e-commerce platform with web app, API, databases, and payment gateway",
    "diagram_type": "c4",
    "output_format": "svg"
  }'
```

### 2. Include C4 Level Hints

The system automatically detects C4 levels from your prompt. Use these keywords:

**For C1**: Use "C1", "system context", or "system context diagram"
**For C2**: Use "C2", "container", or "container diagram"
**For C3**: Use "C3", "component", or "component diagram"
**For C4**: Use "C4" or "code level"

Examples:
- "Create a **C1 diagram** showing customers, our platform, and external payment processors"
- "I need a **container diagram** (C2) with web app, API, databases, and cache"
- "Show the **components inside the API service** (C3)"

### 3. (Optional) Specify C4 Level Explicitly

If automatic detection doesn't work, specify the level explicitly:

```bash
curl -X POST http://localhost:8003/api/v1/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "E-commerce system with web, API, databases, cache, payment gateway",
    "diagram_type": "c4",
    "c4_level": "C2",
    "output_format": "svg"
  }'
```

Valid values for `c4_level`: "C1", "C2", "C3", "C4"

### 4. Receive the Diagram

The response contains:
- `image_data`: Base64-encoded SVG or PNG
- `diagram_code`: The PlantUML source code
- `full_response`: The AI's complete response
- `error_info`: Any error details if generation failed

---

## System Prompts Used

The system automatically selects the appropriate prompt based on detected C4 level:

| C4 Level | Prompt File | Includes | Macros |
|----------|-------------|----------|--------|
| C1 | `c1-architecture.md` | C4_Context.puml | Person, System, System_Ext, Rel |
| C2 | `c2-architecture.md` | C4_Container.puml | System_Boundary, Container, ContainerDb, ContainerQueue, System_Ext, Rel |
| C3 | `c3-architecture.md` | C4_Component.puml | Container_Boundary, Component, ContainerDb, System_Ext, Rel |
| C4 | `c4-code-architecture.md` | N/A (UML) | UML class diagram syntax |
| (auto-detect failed) | `c4-architecture.md` | C4_Context.puml | Generic C4 macros |

---

## Tips for Better Results

### 1. Be Specific About What Goes Where

**Good**:
- "C2 diagram showing the web app, API, user database, product database, and cache inside the system boundary, with Stripe payment gateway as external"

**Vague**:
- "C2 diagram of our system"

### 2. Use Domain-Specific Terminology

The system recognizes business terms:
- Instead of just "C1", say "**system context diagram**"
- Instead of just "C2", say "**container diagram**" or "**internal structure**"
- Instead of just "C3", say "**component diagram**" or "**show the parts inside the API**"

### 3. Mention Technology Stacks

This helps the AI provide more realistic examples:
- "C2 diagram for a microservices architecture with Node.js API, PostgreSQL databases, and RabbitMQ"
- "C3 diagram of a Spring Boot API service"
- "C2 diagram for a React web app with Express backend"

### 4. Specify External Dependencies

Make it clear what's inside vs outside your system:
- Inside: Your containers, services, databases
- Outside: Third-party services, payment gateways, cloud providers

---

## Common Patterns

### E-commerce Platform
```
"Create a C2 diagram for an e-commerce system showing:
- Customer (actor)
- Web application (React)
- API server (Node.js)
- User database
- Product database
- Cache (Redis)
- Payment gateway (Stripe) - external
- Shipping provider (FedEx) - external"
```

### Microservices Architecture
```
"C2 container diagram for a microservices platform with:
- API Gateway
- User Service
- Order Service
- Payment Service
- Databases (one per service)
- Message Queue (RabbitMQ)
- External: Stripe, Slack"
```

### SaaS Application
```
"System context (C1) diagram showing:
- Data analysts (users)
- Analytics platform (our system)
- Data warehouse (Snowflake) - external
- Email service (SendGrid) - external
- Slack (notifications) - external"
```

---

## Troubleshooting

### Issue: Wrong C4 Level Selected

**Symptom**: You requested C2 but got C1-like diagram

**Solution**:
1. Check your prompt wording - make sure it includes "container" or "C2"
2. Or explicitly specify: `"c4_level": "C2"` in request
3. Use clearer keywords: "internal structure", "deployable units", "system boundary"

### Issue: Diagram Code Looks Incomplete

**Symptom**: Generated code cuts off mid-sentence

**Solution**: This was fixed! Token budget increased from 4096 to 16000. If still occurring, check:
1. Your prompt isn't extremely long
2. You're requesting a single diagram, not multiple

### Issue: Kroki Rendering Fails

**Symptom**: SVG generation fails even though PlantUML code looks valid

**Solution**:
1. Check the `diagram_code` in response - look for malformed syntax
2. Try validating manually on plantuml.com
3. Ensure the `!include` line matches the C4 level (C4_Context, C4_Container, C4_Component)

---

## Examples That Work Well

### C1 - Healthcare System
```
"Create a C1 system context diagram for a hospital management system.
Show: Patients, Doctors, Hospital System, Insurance provider (external), Pharmacy network (external)"
```

### C2 - Fitness App
```
"C2 container diagram for a mobile fitness tracking platform:
- Mobile app (iOS/Android)
- REST API (Node.js)
- User database (PostgreSQL)
- Workout database
- Push notification service (Firebase)
- External integrations: Fitbit API, Apple HealthKit"
```

### C3 - Order Processing Service
```
"C3 component diagram showing the internals of an Order Service:
- Order Controller (handles HTTP requests)
- Order Processor (core logic)
- Order Validator (data validation)
- Payment Handler (integrates with Stripe)
- Notification Service (sends emails)
- Order Repository (database access)
- External: Order database, Payment gateway, Email service"
```

---

## API Reference

### Request
```json
{
  "prompt": "Your diagram description with C4 level hints",
  "diagram_type": "c4",
  "c4_level": "C2",  // Optional: "C1", "C2", "C3", or "C4"
  "output_format": "svg"  // or "png"
}
```

### Response
```json
{
  "image_data": "base64-encoded SVG or PNG",
  "image_format": "svg",
  "initial_prompt": "Your original prompt",
  "full_response": "AI's complete response",
  "diagram_code": "PlantUML C4 source code",
  "error_info": {
    "has_error": false,
    "error_message": ""
  }
}
```

---

## Key Points to Remember

✅ **Automatic Detection**: Mention C1/C2/C3/C4 or use terms like "system context", "container", "component"

✅ **Flexible Syntax**: You can be casual in your prompt; the system understands business language

✅ **PlantUML C4 Standard**: All generated code uses official C4 extensions via plantuml-stdlib

✅ **Plenty of Examples**: Each prompt includes 3 complete working examples you can reference

✅ **Token Budget**: Sufficient tokens (16000) for complete diagram generation

✅ **Fallback Support**: If C4 level detection fails, system uses generic C4 prompt

---

## Next Steps

1. **Try generating a C1 diagram** - Start with the simplest level
2. **Graduate to C2** - Add internal containers
3. **Deep dive with C3** - Show component details
4. **Share with team** - Use generated diagrams in documentation

---

**Happy diagramming! 🎨**

For questions or issues, check the implementation summary document or the system prompt files in `prompts/coding/agent/`.

