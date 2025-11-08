# Architecture Schema System - Summary

Complete JSON schema system for capturing user-defined system architectures in the Diagram Wizard.

---

## What Was Created

### 1. **ARCHITECTURE_SCHEMA.md** (~1000 lines)
   - Complete JSON schema definition (draft-07)
   - Real-world E-commerce example
   - Simplified form structure for user input
   - Schema transformations (to Mermaid, D2)
   - Validation rules
   - Integration with Diagram Wizard

### 2. **architecture_schema.py** (Python module)
   - `ArchitectureSchema` utility class
   - Validation functions
   - Query/analysis methods
   - Transformation utilities
   - File I/O operations

---

## Core Concepts

### Architecture Definition Sections

1. **Metadata**
   - Name, version, description
   - Author, date, tags, status
   - For tracking and organization

2. **Components**
   - Services, databases, queues, caches
   - API gateways, external services, clients
   - Each with technology, responsibility, security details

3. **Connections**
   - How components communicate
   - Protocol (HTTP, gRPC, Kafka, SQL, etc.)
   - Synchronous/asynchronous patterns

4. **Users/Actors**
   - Who uses the system
   - Web users, mobile users, admins, systems
   - Interaction points

5. **Deployment**
   - Environments (dev, staging, prod)
   - Cloud platforms (AWS, GCP, Azure, Kubernetes)
   - Infrastructure details

6. **Data Flow**
   - Major use case flows
   - Step-by-step transactions
   - Data movement through system

7. **Technologies**
   - Programming languages
   - Frameworks, databases, messaging
   - Caching, external services

---

## Schema Structure

### Minimal Valid Architecture

```json
{
  "metadata": {
    "name": "My System",
    "description": "A description of the system"
  },
  "components": [
    {
      "id": "frontend",
      "name": "Web Frontend",
      "type": "client",
      "technology": "React"
    },
    {
      "id": "backend",
      "name": "API Server",
      "type": "service",
      "technology": "Node.js"
    },
    {
      "id": "database",
      "name": "PostgreSQL",
      "type": "database",
      "technology": "PostgreSQL"
    }
  ]
}
```

### Complete Architecture Example

E-commerce platform with:
- Web & mobile clients
- API gateway
- 3 microservices (users, products, orders)
- 3 databases
- Redis cache
- RabbitMQ message queue
- Stripe payment gateway
- Elasticsearch
- Monitoring stack

See ARCHITECTURE_SCHEMA.md for complete example.

---

## Component Types

```
- service          → Microservice/backend service
- database         → Data storage (SQL, NoSQL)
- queue            → Message queue (RabbitMQ, Kafka)
- cache            → Caching layer (Redis, Memcached)
- api_gateway      → API entry point (Kong, API Gateway)
- load_balancer    → Load balancer (nginx, AWS ELB)
- external_service → Third-party service (Stripe, SendGrid)
- client           → Frontend application (web, mobile)
- container        → Container/pod
- function         → Serverless function (Lambda, Cloud Function)
- storage          → Object/blob storage (S3, GCS)
- monitoring       → Monitoring/logging (Prometheus, ELK)
- other            → Custom/other type
```

---

## Protocol Types

```
- http / https           → Web protocols
- grpc                   → gRPC calls
- websocket              → WebSocket connections
- tcp / udp              → Network protocols
- amqp / kafka           → Message protocols
- rest / graphql         → API styles
- sql                    → Database queries
- redis                  → Cache queries
- other                  → Custom protocols
```

---

## Python Utility Class

### Features

```python
# Validation
valid, errors = ArchitectureSchema.validate(architecture)

# Query components
databases = ArchitectureSchema.get_databases(architecture)
services = ArchitectureSchema.get_services(architecture)
external = ArchitectureSchema.get_external_services(architecture)

# Find connections
conns = ArchitectureSchema.get_connections_for_component(
    architecture,
    "user_service"
)

# Get component
component = ArchitectureSchema.get_component_by_id(
    architecture,
    "user_db"
)

# Extract technologies
techs = ArchitectureSchema.get_technologies(architecture)

# Get statistics
stats = ArchitectureSchema.get_connection_stats(architecture)

# Transform to Mermaid
mermaid_code = ArchitectureSchema.to_mermaid(architecture)

# File operations
ArchitectureSchema.save_to_file(architecture, "arch.json")
architecture = ArchitectureSchema.load_from_file("arch.json")
```

---

## User Input Flow

### Step 1: Interactive Form
User fills out form with:
- Architecture name & description
- Components (add multiple)
- Connections (define relationships)
- Deployment info
- Technology stack

### Step 2: JSON Generation
System generates JSON architecture definition

### Step 3: Validation
System validates against schema:
- Required fields ✓
- Unique IDs ✓
- Valid connections ✓
- No self-loops ✓
- Correct enum values ✓

### Step 4: LLM Clarification
LLM asks follow-up questions:
- Are all components included?
- Any missing connections?
- Confirm technology choices?
- Performance requirements?

### Step 5: Diagram Generation
Transform to diagram format:
- Mermaid (flowcharts)
- D2 (architecture diagrams)
- PlantUML (UML diagrams)

### Step 6: Output
User gets:
- Architecture JSON (save/reuse)
- Diagram SVG (view/download)
- Documentation

---

## Validation Rules

The schema enforces:

1. **Required Fields**
   - metadata.name ✓
   - metadata.description ✓
   - components (array, min 1) ✓

2. **Component Requirements**
   - Unique IDs (pattern: `^[a-z0-9_-]+$`) ✓
   - Valid type ✓
   - Name ✓

3. **Connection Requirements**
   - Valid source component ✓
   - Valid destination component ✓
   - Valid protocol ✓
   - No self-loops ✓

4. **Custom Rules**
   - All referenced components exist ✓
   - No duplicate IDs ✓
   - Valid enum values ✓

---

## Transform Examples

### Schema to Mermaid

```json
{
  "components": [
    {"id": "client", "name": "Client", "type": "client"},
    {"id": "api", "name": "API", "type": "service"},
    {"id": "db", "name": "Database", "type": "database"}
  ],
  "connections": [
    {"from": "client", "to": "api", "protocol": "https"},
    {"from": "api", "to": "db", "protocol": "sql"}
  ]
}
```

Transforms to:

```
graph TD
    client['👤 Client']
    api['API']
    db[('Database')]
    client -->|https| api
    api -->|sql| db
```

---

## Storage & Versioning

### Save Architecture

```python
architecture = {
    "metadata": {...},
    "components": [...],
    "connections": [...],
    ...
}

ArchitectureSchema.save_to_file(
    architecture,
    "architectures/ecommerce.json"
)
```

### Load Architecture

```python
architecture = ArchitectureSchema.load_from_file(
    "architectures/ecommerce.json"
)

valid, errors = ArchitectureSchema.validate(architecture)
```

### Versioning

```json
{
  "metadata": {
    "name": "E-commerce Platform",
    "version": "2.0.0",
    "previous_versions": [
      {"version": "1.0.0", "date": "2024-10-01"},
      {"version": "1.5.0", "date": "2024-10-15"}
    ]
  }
}
```

---

## Integration Points

### With Diagram Wizard

1. **Architecture Form Endpoint**
   - `POST /api/v1/diagram/architecture/define`
   - Input: Interactive form data
   - Output: JSON schema

2. **Schema Validation Endpoint**
   - `POST /api/v1/diagram/architecture/validate`
   - Input: JSON schema
   - Output: Valid/error messages

3. **Query Endpoint**
   - `POST /api/v1/diagram/architecture/query`
   - Input: Query, schema
   - Output: Filtered results

4. **Diagram Generation**
   - Use validated schema
   - Transform to Mermaid/D2/PlantUML
   - Generate diagram

### With Services

```python
from app.utils.architecture_schema import ArchitectureSchema

# In diagram_factory_service.py
def generate_diagram_from_architecture(schema):
    # Validate
    valid, errors = ArchitectureSchema.validate(schema)
    if not valid:
        raise ValueError(f"Invalid schema: {errors}")

    # Get components by type
    services = ArchitectureSchema.get_services(schema)
    databases = ArchitectureSchema.get_databases(schema)

    # Generate diagram
    mermaid_code = ArchitectureSchema.to_mermaid(schema)

    return mermaid_code
```

---

## API Usage Examples

### Create Architecture Interactively

```bash
curl -X POST http://localhost:8003/api/v1/diagram/architecture/define \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My E-commerce Platform",
    "description": "Online shopping system",
    "components": [
      {"id": "web", "name": "Web App", "type": "client"},
      {"id": "api", "name": "API", "type": "service"},
      {"id": "db", "name": "DB", "type": "database"}
    ]
  }'
```

### Validate Architecture

```bash
curl -X POST http://localhost:8003/api/v1/diagram/architecture/validate \
  -H "Content-Type: application/json" \
  -d @architecture.json
```

### Query Databases

```bash
curl -X POST http://localhost:8003/api/v1/diagram/architecture/query \
  -H "Content-Type: application/json" \
  -d '{
    "type": "component_by_type",
    "component_type": "database"
  }'
```

### Generate Diagram

```bash
curl -X POST http://localhost:8003/api/v1/diagram/architecture/to_diagram \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {...},
    "format": "mermaid"
  }'
```

---

## Benefits

### For Architecture Definition

✓ **Structured** - Unambiguous, machine-readable definition
✓ **Validated** - JSON schema ensures correctness
✓ **Queryable** - Easy to analyze and extract information
✓ **Transformable** - Single source to multiple diagram types
✓ **Versionable** - Track architecture evolution
✓ **Shareable** - JSON files easy to share/store

### For Diagram Wizard

✓ **Clarity** - Ask specific follow-up questions
✓ **Completeness** - Identify missing components
✓ **Consistency** - Validate relationships
✓ **Quality** - Better diagrams from structured input
✓ **Reusability** - Save and reuse architectures

### For Users

✓ **Easy Input** - Fill form or paste JSON
✓ **Flexible** - Add as much detail as needed
✓ **Clear Output** - Multiple diagram formats
✓ **Documentation** - JSON serves as documentation
✓ **Accuracy** - No ambiguity in definitions

---

## Files Created

```
backend/
├── ARCHITECTURE_SCHEMA.md          ← Complete schema documentation
└── app/utils/
    └── architecture_schema.py      ← Python utility class
```

---

## Next Steps

### Implementation Tasks

1. **Create API Endpoints**
   - `POST /diagram/architecture/define`
   - `POST /diagram/architecture/validate`
   - `POST /diagram/architecture/query`
   - `POST /diagram/architecture/to_diagram`

2. **Add to Diagram Wizard**
   - Architecture form in Panel 1
   - Schema generation
   - Validation feedback
   - Query/refine loop

3. **Enhance LLM Prompts**
   - Ask schema-specific questions
   - Fill gaps in definition
   - Suggest improvements

4. **Create UI Form**
   - Component add/edit
   - Connection builder
   - Technology selector
   - Review & validate

---

## Examples Provided

1. **E-commerce System** (full example)
   - 13 components
   - 11 connections
   - 3 databases
   - Complete technology stack

2. **Minimal System** (3 components)
   - Frontend, Backend, Database
   - Shows minimum valid schema

3. **Form Structure** (for UI implementation)
   - Metadata form
   - Component form
   - Connection form
   - Deployment form

---

## Status

✓ Schema designed and documented
✓ Python utility class created
✓ Examples provided
✓ Validation rules specified
✓ Integration points identified

**Ready for:** API endpoint implementation & UI form creation

---

**Location:** `c:\Code2025\Whysper\backend\ARCHITECTURE_SCHEMA.md`
**Utility Class:** `c:\Code2025\Whysper\backend\app\utils\architecture_schema.py`
