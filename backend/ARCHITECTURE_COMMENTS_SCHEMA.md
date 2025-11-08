# Architecture Comments Schema Extension

Enhanced schema with comprehensive `comment` objects for rich contextual annotations.

---

## Overview

The `comment` object system allows architects to:
- Add rich contextual notes to any architectural element
- Document decisions and trade-offs
- Provide implementation guidance
- Link to external resources
- Tag and categorize information
- Track who said what and when
- Include examples and references

---

## Comment Object Schema

### Core Comment Definition

```json
{
  "comment": {
    "type": "object",
    "description": "Rich contextual annotation",
    "properties": {
      "id": {
        "type": "string",
        "description": "Unique comment identifier",
        "pattern": "^comment_[a-z0-9_-]+$"
      },
      "text": {
        "type": "string",
        "description": "Comment content (markdown supported)"
      },
      "type": {
        "type": "string",
        "enum": [
          "note",
          "rationale",
          "decision",
          "warning",
          "todo",
          "reference",
          "example",
          "constraint",
          "risk",
          "improvement",
          "documentation"
        ],
        "description": "Type of comment"
      },
      "author": {
        "type": "string",
        "description": "Who added this comment"
      },
      "date": {
        "type": "string",
        "format": "date-time",
        "description": "When it was added"
      },
      "tags": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Categorization tags"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high", "critical"],
        "description": "Importance level"
      },
      "related_to": {
        "type": "array",
        "items": { "type": "string" },
        "description": "IDs of related components/connections"
      },
      "references": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string",
              "enum": ["url", "jira", "document", "email", "meeting_note"]
            },
            "identifier": {
              "type": "string",
              "description": "URL, ticket ID, doc name, etc."
            },
            "title": {
              "type": "string",
              "description": "Human-readable reference title"
            }
          }
        },
        "description": "External references"
      },
      "status": {
        "type": "string",
        "enum": ["open", "resolved", "acknowledged", "pending_review"],
        "description": "Comment status"
      },
      "responses": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "author": { "type": "string" },
            "date": { "type": "string", "format": "date-time" },
            "text": { "type": "string" },
            "type": { "type": "string" }
          }
        },
        "description": "Threaded responses to comment"
      },
      "metadata": {
        "type": "object",
        "description": "Custom metadata",
        "additionalProperties": true
      }
    },
    "required": ["id", "text", "type"]
  }
}
```

---

## Comment Types & Use Cases

### 1. **Note** - General observations
```json
{
  "id": "comment_scaling_note",
  "type": "note",
  "text": "This service currently handles 10k RPS but needs to scale to 100k RPS by Q2 2025",
  "author": "Sarah Chen",
  "date": "2024-11-08T10:00:00Z",
  "tags": ["scaling", "performance"]
}
```

### 2. **Rationale** - Why we chose this approach
```json
{
  "id": "comment_kafka_rationale",
  "type": "rationale",
  "text": "Chose Kafka over RabbitMQ because:\n- Higher throughput (1M+ msg/sec)\n- Better for event sourcing\n- Supports message replay\n- Distributed cluster out of box",
  "author": "Michael Ross",
  "date": "2024-11-07T14:30:00Z",
  "tags": ["messaging", "architecture_decision"]
}
```

### 3. **Decision** - Architectural decisions
```json
{
  "id": "comment_db_decision",
  "type": "decision",
  "text": "**DECISION**: Use PostgreSQL for all data storage, not MongoDB\n\n**Rationale**: ACID compliance needed for financial transactions\n**Alternatives Considered**: MongoDB, DynamoDB, Cassandra\n**Trade-offs**: Horizontal scaling harder, but consistency guaranteed\n**Decided By**: Architecture Review Board\n**Date**: 2024-10-15",
  "author": "Architecture Team",
  "date": "2024-10-15T09:00:00Z",
  "priority": "high",
  "references": [
    {
      "type": "jira",
      "identifier": "ARCH-123",
      "title": "Database Technology Selection"
    }
  ]
}
```

### 4. **Warning** - Potential issues
```json
{
  "id": "comment_redis_warning",
  "type": "warning",
  "text": "⚠️ Redis is in-memory only. Data loss possible if pod crashes.\nMust implement proper backup strategy (RDB or AOF snapshots).",
  "author": "DevOps Team",
  "date": "2024-11-08T11:00:00Z",
  "priority": "high",
  "related_to": ["cache"],
  "tags": ["reliability", "data_loss_risk"]
}
```

### 5. **TODO** - Action items
```json
{
  "id": "comment_todo_monitoring",
  "type": "todo",
  "text": "TODO: Set up distributed tracing for all microservices\n- Tool: Jaeger or Datadog\n- Owner: Observability Team\n- Deadline: End of Q4 2024",
  "author": "Platform Lead",
  "date": "2024-11-08T08:00:00Z",
  "priority": "high",
  "status": "open",
  "tags": ["monitoring", "observability"]
}
```

### 6. **Reference** - Links to external resources
```json
{
  "id": "comment_ref_docs",
  "type": "reference",
  "text": "For setup and deployment instructions, see the linked documentation",
  "references": [
    {
      "type": "url",
      "identifier": "https://wiki.company.com/kubernetes-setup",
      "title": "Kubernetes Setup Guide"
    },
    {
      "type": "document",
      "identifier": "arch-docs/service-deployment",
      "title": "Service Deployment Standard"
    }
  ]
}
```

### 7. **Example** - Code or configuration examples
```json
{
  "id": "comment_scaling_example",
  "type": "example",
  "text": "Example Kubernetes horizontal pod autoscaler configuration:\n```yaml\napiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\nmetadata:\n  name: user-service-hpa\nspec:\n  scaleTargetRef:\n    apiVersion: apps/v1\n    kind: Deployment\n    name: user-service\n  minReplicas: 3\n  maxReplicas: 50\n  metrics:\n  - type: Resource\n    resource:\n      name: cpu\n      target:\n        type: Utilization\n        averageUtilization: 70\n```",
  "tags": ["kubernetes", "scaling"]
}
```

### 8. **Constraint** - Limitations or restrictions
```json
{
  "id": "comment_constraint_sla",
  "type": "constraint",
  "text": "CONSTRAINT: Must maintain 99.99% uptime (max 52 minutes downtime/year)\n- Requires multi-region deployment\n- Active-active replication mandatory\n- Blue-green deployment strategy required",
  "author": "SRE Team",
  "priority": "critical",
  "tags": ["sla", "reliability"]
}
```

### 9. **Risk** - Potential risks
```json
{
  "id": "comment_risk_vendor_lock",
  "type": "risk",
  "text": "RISK: Vendor lock-in with AWS services\n- Using Kinesis, DynamoDB, Lambda, etc.\n- Migration cost: ~6 months engineering effort\n- Mitigation: Evaluate multi-cloud strategy in 2025",
  "author": "Architecture Review",
  "priority": "medium",
  "tags": ["vendor-lock", "risk-management"]
}
```

### 10. **Improvement** - Future enhancements
```json
{
  "id": "comment_improvement_api_v2",
  "type": "improvement",
  "text": "FUTURE: Plan API v2 to address current limitations:\n- Batch operations support\n- GraphQL support\n- Webhook subscriptions\n- Target: Q2 2025",
  "author": "API Team",
  "priority": "medium",
  "status": "pending_review",
  "tags": ["future-work", "api"]
}
```

### 11. **Documentation** - Technical documentation
```json
{
  "id": "comment_doc_auth_flow",
  "type": "documentation",
  "text": "## Authentication Flow\n\n1. User logs in via web client\n2. Client calls POST /auth/login with credentials\n3. User Service validates credentials against database\n4. JWT token generated with 24-hour expiration\n5. Token returned to client\n6. Client includes token in Authorization header for subsequent requests\n7. API Gateway validates token before routing\n8. Token refresh endpoint available before expiration",
  "tags": ["security", "authentication"]
}
```

---

## Extended Architecture Schema with Comments

### Full Example with Comments

```json
{
  "metadata": {
    "name": "E-commerce Platform",
    "description": "Scalable e-commerce system",
    "version": "2.0.0"
  },

  "comments": [
    {
      "id": "comment_arch_overview",
      "type": "documentation",
      "text": "## Architecture Overview\n\nThis is a microservices architecture with:\n- Independent deployment per service\n- Event-driven async communication\n- Multi-region failover\n- API Gateway as single entry point\n\nDesigned for 100k concurrent users and 1M transactions/day",
      "author": "Architecture Team"
    },
    {
      "id": "comment_tech_stack_rationale",
      "type": "decision",
      "text": "Selected tech stack based on:\n1. PostgreSQL - ACID compliance required for financial data\n2. Kafka - High throughput event streaming\n3. Kubernetes - Standard container orchestration\n4. Node.js/Python - Polyglot services for team skill match",
      "author": "CTO",
      "priority": "high"
    }
  ],

  "components": [
    {
      "id": "api_gateway",
      "name": "API Gateway",
      "type": "api_gateway",
      "technology": "Kong",
      "description": "Single entry point for all API requests",
      "comments": [
        {
          "id": "comment_kong_choice",
          "type": "rationale",
          "text": "Chose Kong over nginx because:\n- Plugin ecosystem for auth, rate limiting, logging\n- Manages API versioning natively\n- Kong Enterprise for advanced features\n- Community is active and mature",
          "author": "Platform Team"
        },
        {
          "id": "comment_kong_scaling",
          "type": "note",
          "text": "Currently handles 50k RPS with 5 nodes. Scaling plan:\n- Add nodes to 10 for 100k RPS\n- Database cluster for state management\n- Multi-region active-active by Q2 2025",
          "priority": "medium",
          "tags": ["scaling"]
        }
      ]
    },

    {
      "id": "user_service",
      "name": "User Service",
      "type": "service",
      "technology": "Node.js + Express",
      "description": "User authentication and profile management",
      "comments": [
        {
          "id": "comment_jwt_decision",
          "type": "decision",
          "text": "Using JWT tokens instead of session-based auth:\n- Stateless - scales horizontally\n- No server-side session storage needed\n- Standard for microservices\n- 24-hour expiration with refresh tokens",
          "author": "Security Team",
          "priority": "high"
        },
        {
          "id": "comment_user_svc_performance",
          "type": "note",
          "text": "Performance baseline:\n- Auth endpoint: <50ms (p95)\n- Profile update: <100ms (p95)\n- Cache hit rate: 85% for popular profiles",
          "tags": ["performance"]
        }
      ]
    },

    {
      "id": "user_db",
      "name": "User Database",
      "type": "database",
      "technology": "PostgreSQL",
      "comments": [
        {
          "id": "comment_db_security",
          "type": "constraint",
          "text": "Database security requirements:\n- All data at rest encryption (AES-256)\n- TLS for all connections\n- Rows-level security for multi-tenant data\n- Regular security audits (quarterly)",
          "priority": "critical",
          "tags": ["security", "compliance"]
        },
        {
          "id": "comment_db_backup",
          "type": "todo",
          "text": "TODO: Implement automated backup strategy\n- Daily snapshots (7-day retention)\n- Weekly snapshots (30-day retention)\n- Monthly snapshots (1-year retention)\n- Cross-region replication",
          "status": "open",
          "priority": "high"
        }
      ]
    }
  ],

  "connections": [
    {
      "id": "conn_client_to_gateway",
      "from": "web_client",
      "to": "api_gateway",
      "protocol": "https",
      "type": "synchronous",
      "comments": [
        {
          "id": "comment_tls_requirement",
          "type": "constraint",
          "text": "Must use TLS 1.3 minimum. No unencrypted HTTP allowed.",
          "priority": "critical"
        },
        {
          "id": "comment_rate_limiting",
          "type": "note",
          "text": "Rate limiting configured:\n- 1000 req/min per IP\n- 10000 req/min per authenticated user\n- Returns 429 Too Many Requests when exceeded",
          "tags": ["security"]
        }
      ]
    },

    {
      "id": "conn_gateway_to_user_svc",
      "from": "api_gateway",
      "to": "user_service",
      "protocol": "https",
      "type": "synchronous",
      "comments": [
        {
          "id": "comment_circuit_breaker",
          "type": "note",
          "text": "Circuit breaker pattern implemented:\n- Opens after 5 consecutive failures\n- Half-open state after 30s\n- Full reset on success\n- Fallback returns cached response",
          "tags": ["resilience"]
        }
      ]
    }
  ]
}
```

---

## Comment Operations

### Adding Comments

```python
def add_comment(component_id, comment):
    """Add comment to a component."""
    comment = {
        "id": f"comment_{uuid.uuid4()}",
        "type": "note",
        "text": "User's comment text",
        "author": "User Name",
        "date": datetime.utcnow().isoformat(),
        "tags": ["tag1", "tag2"]
    }

    if "comments" not in architecture[component_id]:
        architecture[component_id]["comments"] = []

    architecture[component_id]["comments"].append(comment)
```

### Querying Comments

```python
# Get all comments of a type
def get_comments_by_type(architecture, comment_type):
    """Get all comments of a specific type."""
    all_comments = []

    # Global comments
    for comment in architecture.get("comments", []):
        if comment["type"] == comment_type:
            all_comments.append(comment)

    # Component comments
    for component in architecture.get("components", []):
        for comment in component.get("comments", []):
            if comment["type"] == comment_type:
                all_comments.append(comment)

    return all_comments

# Get high-priority comments
def get_high_priority_comments(architecture):
    """Get all critical/high priority comments."""
    all_comments = []

    for component in architecture.get("components", []):
        for comment in component.get("comments", []):
            if comment.get("priority") in ["high", "critical"]:
                all_comments.append({
                    "component": component["id"],
                    "comment": comment
                })

    return all_comments

# Get TODO items
def get_open_todos(architecture):
    """Get all open TODO items."""
    todos = []

    for component in architecture.get("components", []):
        for comment in component.get("comments", []):
            if (comment["type"] == "todo" and
                comment.get("status") == "open"):
                todos.append({
                    "component": component["id"],
                    "comment": comment
                })

    return todos

# Get comments with tags
def get_comments_by_tag(architecture, tag):
    """Get all comments with a specific tag."""
    matching = []

    for component in architecture.get("components", []):
        for comment in component.get("comments", []):
            if tag in comment.get("tags", []):
                matching.append(comment)

    return matching
```

### Generating Reports from Comments

```python
def generate_risk_report(architecture):
    """Generate risk assessment report from risk comments."""
    risks = get_comments_by_type(architecture, "risk")

    report = "# Risk Assessment Report\n\n"

    for risk in risks:
        priority = risk.get("priority", "medium").upper()
        report += f"## [{priority}] {risk.get('text', '')}\n"
        report += f"**Identified by**: {risk.get('author')}\n"
        report += f"**Date**: {risk.get('date')}\n\n"

    return report

def generate_decision_log(architecture):
    """Generate architectural decision log."""
    decisions = get_comments_by_type(architecture, "decision")

    log = "# Architectural Decision Log\n\n"

    for decision in sorted(decisions, key=lambda x: x.get("date", "")):
        log += f"## {decision.get('text', '')}\n"
        log += f"**By**: {decision.get('author')}\n"
        log += f"**Date**: {decision.get('date')}\n\n"

    return log

def generate_todo_report(architecture):
    """Generate action items report."""
    todos = get_open_todos(architecture)

    report = "# Action Items\n\n"

    for item in todos:
        comment = item["comment"]
        priority = comment.get("priority", "medium")
        report += f"- [{priority.upper()}] {comment.get('text')}\n"

    return report
```

---

## Comment Threads (Responses)

Comments can have responses for discussions:

```json
{
  "id": "comment_scaling_discussion",
  "type": "note",
  "text": "We need better horizontal scaling for the user service",
  "author": "Sarah",
  "date": "2024-11-08T10:00:00Z",
  "responses": [
    {
      "author": "Michael",
      "date": "2024-11-08T10:30:00Z",
      "text": "Agreed. Should we add Kubernetes HPA?"
    },
    {
      "author": "Sarah",
      "date": "2024-11-08T11:00:00Z",
      "text": "Yes, exactly. With CPU target at 70%"
    },
    {
      "author": "DevOps",
      "date": "2024-11-08T14:00:00Z",
      "text": "Implemented. Live in staging now."
    }
  ],
  "status": "resolved"
}
```

---

## Comment Analytics

### Statistics

```python
def get_comment_statistics(architecture):
    """Get statistics about comments."""
    stats = {
        "total_comments": 0,
        "by_type": {},
        "by_priority": {},
        "by_status": {},
        "by_tag": {}
    }

    all_comments = get_all_comments(architecture)

    for comment in all_comments:
        stats["total_comments"] += 1

        ctype = comment.get("type", "unknown")
        stats["by_type"][ctype] = stats["by_type"].get(ctype, 0) + 1

        priority = comment.get("priority", "medium")
        stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

        status = comment.get("status", "open")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        for tag in comment.get("tags", []):
            stats["by_tag"][tag] = stats["by_tag"].get(tag, 0) + 1

    return stats
```

---

## Integration with LLM Clarification

### Questions Based on Comments

The LLM can ask clarification questions based on missing/incomplete comments:

```python
def generate_clarification_questions(architecture):
    """Generate questions based on missing information."""
    questions = []

    # Check for missing rationale
    services = get_components_by_type(architecture, "service")
    for service in services:
        rationale_comments = [
            c for c in service.get("comments", [])
            if c["type"] == "rationale"
        ]
        if not rationale_comments:
            questions.append(
                f"Why did you choose {service['technology']} for {service['name']}?"
            )

    # Check for unaddressed risks
    high_risks = get_comments_by_priority(architecture, ["critical", "high"])
    for risk in high_risks:
        if risk.get("status") != "resolved":
            questions.append(
                f"How will you mitigate: {risk['text'][:50]}...?"
            )

    # Check for open TODOs
    open_todos = get_open_todos(architecture)
    if len(open_todos) > 0:
        questions.append(
            f"You have {len(open_todos)} open action items. "
            f"What's the timeline for completion?"
        )

    return questions
```

---

## Comment-Based Documentation

### Auto-generated Documentation

```python
def generate_architecture_document(architecture):
    """Generate complete documentation from comments."""
    doc = "# System Architecture Documentation\n\n"

    # Overview from global comments
    overview_comments = get_comments_by_type(architecture, "documentation")
    for comment in overview_comments:
        doc += comment["text"] + "\n\n"

    # Decision log
    doc += generate_decision_log(architecture)

    # Risk assessment
    doc += generate_risk_report(architecture)

    # Action items
    doc += generate_todo_report(architecture)

    # Component-specific documentation
    for component in architecture.get("components", []):
        doc += f"\n## {component['name']}\n\n"
        doc += f"{component.get('description', '')}\n\n"

        comp_comments = component.get("comments", [])
        for comment in comp_comments:
            doc += f"**{comment['type']}**: {comment['text']}\n\n"

    return doc
```

---

## Benefits of Comment System

1. **Rich Context** - Multiple perspectives captured
2. **Decision Tracking** - Why decisions were made
3. **Risk Management** - Identified and tracked risks
4. **Action Items** - Clear TODOs and ownership
5. **Documentation** - Auto-generated from comments
6. **Discussions** - Threaded responses for collaboration
7. **Queries** - Easy to find information by type/tag/priority
8. **Versioning** - Tracks evolution of thinking
9. **Accountability** - Who said what and when
10. **Reporting** - Analytics and summaries

---

## Files Created

1. **ARCHITECTURE_COMMENTS_SCHEMA.md** - This document
2. **Updated architecture_schema.py** - Add comment utilities (next)

---

**Status:** Comment system design complete
**Ready for:** Implementation in architecture schema module
