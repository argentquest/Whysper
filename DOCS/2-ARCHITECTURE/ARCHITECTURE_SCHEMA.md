# Architecture Schema Definition

Comprehensive JSON schema for capturing user-defined system architectures in the Diagram Wizard.

---

## Overview

A flexible, extensible JSON schema system that allows users to describe their architecture in a structured way. This schema can be:
- Entered via the Diagram Wizard
- Stored for later use
- Validated
- Transformed to diagram code (Mermaid, D2, PlantUML)
- Reused across multiple diagrams

---

## Core Architecture Schema

### Main Schema Structure

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "System Architecture Definition",
  "description": "Comprehensive schema for defining system architectures",
  "type": "object",
  "required": ["name", "description", "components"],
  "properties": {
    "metadata": { "$ref": "#/definitions/metadata" },
    "components": { "$ref": "#/definitions/components" },
    "connections": { "$ref": "#/definitions/connections" },
    "deployment": { "$ref": "#/definitions/deployment" },
    "users": { "$ref": "#/definitions/users" },
    "data_flow": { "$ref": "#/definitions/data_flow" },
    "technologies": { "$ref": "#/definitions/technologies" }
  },
  "definitions": { ... }
}
```

### Complete JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "System Architecture Schema",
  "type": "object",
  "definitions": {
    "metadata": {
      "type": "object",
      "description": "Architecture metadata",
      "properties": {
        "name": {
          "type": "string",
          "description": "Architecture name (e.g., 'E-commerce Platform')"
        },
        "version": {
          "type": "string",
          "description": "Schema version",
          "default": "1.0.0"
        },
        "description": {
          "type": "string",
          "description": "High-level architecture description"
        },
        "author": {
          "type": "string",
          "description": "Architecture designer"
        },
        "date": {
          "type": "string",
          "format": "date-time",
          "description": "Creation date"
        },
        "tags": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Classification tags (e.g., 'microservices', 'cloud', 'real-time')"
        },
        "status": {
          "type": "string",
          "enum": ["draft", "proposed", "active", "deprecated"],
          "description": "Architecture status"
        }
      },
      "required": ["name", "description"]
    },

    "component": {
      "type": "object",
      "description": "System component or service",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier (e.g., 'user-service')",
          "pattern": "^[a-z0-9_-]+$"
        },
        "name": {
          "type": "string",
          "description": "Display name (e.g., 'User Service')"
        },
        "type": {
          "type": "string",
          "enum": [
            "service",
            "database",
            "queue",
            "cache",
            "api_gateway",
            "load_balancer",
            "external_service",
            "client",
            "container",
            "function",
            "storage",
            "monitoring",
            "other"
          ],
          "description": "Component type"
        },
        "description": {
          "type": "string",
          "description": "What this component does"
        },
        "technology": {
          "type": "string",
          "description": "Technology/tool used (e.g., 'Node.js', 'PostgreSQL', 'Redis')"
        },
        "responsibility": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Key responsibilities"
        },
        "owner": {
          "type": "string",
          "description": "Team or person responsible"
        },
        "hosted_on": {
          "type": "string",
          "description": "Where it runs (e.g., 'AWS EC2', 'Kubernetes', 'Vercel')"
        },
        "scaling": {
          "type": "object",
          "description": "Scaling strategy",
          "properties": {
            "type": {
              "type": "string",
              "enum": ["horizontal", "vertical", "none"],
              "description": "Scaling direction"
            },
            "strategy": {
              "type": "string",
              "description": "How it scales (e.g., 'auto-scaling group', 'replicas')"
            }
          }
        },
        "backup": {
          "type": "object",
          "description": "Backup/redundancy",
          "properties": {
            "count": {
              "type": "integer",
              "minimum": 1,
              "description": "Number of instances/replicas"
            },
            "strategy": {
              "type": "string",
              "enum": ["active-active", "active-passive", "none"],
              "description": "Redundancy strategy"
            }
          }
        },
        "performance": {
          "type": "object",
          "description": "Performance characteristics",
          "properties": {
            "throughput": {
              "type": "string",
              "description": "Requests per second (e.g., '10k RPS')"
            },
            "latency": {
              "type": "string",
              "description": "Response time (e.g., '<100ms')"
            },
            "sla": {
              "type": "string",
              "description": "Service level agreement (e.g., '99.9% uptime')"
            }
          }
        },
        "security": {
          "type": "object",
          "description": "Security aspects",
          "properties": {
            "auth": {
              "type": "string",
              "enum": ["none", "basic", "api_key", "jwt", "oauth2", "mfa"],
              "description": "Authentication method"
            },
            "encryption": {
              "type": "boolean",
              "description": "Data encrypted at rest"
            },
            "tls": {
              "type": "boolean",
              "description": "TLS for data in transit"
            }
          }
        },
        "metadata": {
          "type": "object",
          "description": "Custom metadata",
          "additionalProperties": true
        }
      },
      "required": ["id", "name", "type"]
    },

    "components": {
      "type": "array",
      "description": "All system components",
      "items": { "$ref": "#/definitions/component" },
      "minItems": 1
    },

    "connection": {
      "type": "object",
      "description": "Connection between components",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier (e.g., 'conn_user_to_db')"
        },
        "from": {
          "type": "string",
          "description": "Source component ID"
        },
        "to": {
          "type": "string",
          "description": "Destination component ID"
        },
        "protocol": {
          "type": "string",
          "enum": [
            "http",
            "https",
            "grpc",
            "websocket",
            "tcp",
            "udp",
            "amqp",
            "kafka",
            "rest",
            "graphql",
            "sql",
            "redis",
            "other"
          ],
          "description": "Communication protocol"
        },
        "direction": {
          "type": "string",
          "enum": ["one-way", "two-way"],
          "description": "Connection direction"
        },
        "label": {
          "type": "string",
          "description": "Connection label (e.g., 'REST API', 'Database Query')"
        },
        "type": {
          "type": "string",
          "enum": [
            "synchronous",
            "asynchronous",
            "publish-subscribe",
            "request-reply"
          ],
          "description": "Interaction pattern"
        },
        "frequency": {
          "type": "string",
          "description": "How often (e.g., 'real-time', 'periodic', 'on-demand')"
        },
        "security": {
          "type": "object",
          "properties": {
            "authenticated": {
              "type": "boolean"
            },
            "encrypted": {
              "type": "boolean"
            }
          }
        },
        "notes": {
          "type": "string"
        }
      },
      "required": ["from", "to", "protocol"]
    },

    "connections": {
      "type": "array",
      "description": "All connections between components",
      "items": { "$ref": "#/definitions/connection" }
    },

    "deployment": {
      "type": "object",
      "description": "Deployment information",
      "properties": {
        "environments": {
          "type": "array",
          "description": "Deployment environments",
          "items": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "enum": ["development", "staging", "production"]
              },
              "region": {
                "type": "string",
                "description": "Geographic region (e.g., 'us-east-1')"
              },
              "platform": {
                "type": "string",
                "enum": ["aws", "gcp", "azure", "kubernetes", "vercel", "heroku", "on-premise"],
                "description": "Deployment platform"
              },
              "configuration": {
                "type": "object",
                "description": "Environment-specific config",
                "additionalProperties": true
              }
            }
          }
        },
        "infrastructure": {
          "type": "object",
          "description": "Infrastructure details",
          "properties": {
            "container_orchestration": {
              "type": "string",
              "enum": ["kubernetes", "docker-swarm", "ecs", "none"],
              "description": "Container orchestration"
            },
            "ci_cd": {
              "type": "string",
              "description": "CI/CD tool (e.g., 'GitHub Actions', 'Jenkins')"
            },
            "monitoring": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Monitoring tools"
            }
          }
        }
      }
    },

    "user": {
      "type": "object",
      "description": "System user or actor",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier (e.g., 'web_client')"
        },
        "name": {
          "type": "string",
          "description": "Display name (e.g., 'Web Browser Client')"
        },
        "type": {
          "type": "string",
          "enum": ["user", "system", "service", "mobile_app", "web_app", "third_party"],
          "description": "User type"
        },
        "description": {
          "type": "string"
        },
        "interactions": {
          "type": "array",
          "items": { "type": "string" },
          "description": "What they interact with"
        }
      },
      "required": ["id", "name", "type"]
    },

    "users": {
      "type": "array",
      "description": "All users/actors in the system",
      "items": { "$ref": "#/definitions/user" }
    },

    "data_flow": {
      "type": "object",
      "description": "Data flow through the system",
      "properties": {
        "flows": {
          "type": "array",
          "description": "Major data flows",
          "items": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "description": "Flow name (e.g., 'User Registration')"
              },
              "description": {
                "type": "string"
              },
              "steps": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "from": { "type": "string" },
                    "to": { "type": "string" },
                    "action": { "type": "string" },
                    "data": { "type": "string" }
                  }
                }
              }
            }
          }
        }
      }
    },

    "technologies": {
      "type": "object",
      "description": "Technology stack",
      "properties": {
        "languages": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Programming languages"
        },
        "frameworks": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Frameworks and libraries"
        },
        "databases": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Database technologies"
        },
        "messaging": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Message queue systems"
        },
        "caching": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Caching solutions"
        },
        "external_services": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Third-party services"
        }
      }
    }
  },

  "type": "object",
  "required": ["metadata", "components"],
  "properties": {
    "metadata": { "$ref": "#/definitions/metadata" },
    "components": { "$ref": "#/definitions/components" },
    "connections": { "$ref": "#/definitions/connections" },
    "users": { "$ref": "#/definitions/users" },
    "deployment": { "$ref": "#/definitions/deployment" },
    "data_flow": { "$ref": "#/definitions/data_flow" },
    "technologies": { "$ref": "#/definitions/technologies" }
  }
}
```

---

## Example Architecture Definition

### E-commerce System

```json
{
  "metadata": {
    "name": "E-commerce Platform",
    "version": "2.0.0",
    "description": "Scalable e-commerce system with microservices architecture",
    "author": "Platform Team",
    "date": "2024-11-08T10:00:00Z",
    "tags": ["microservices", "cloud", "real-time", "e-commerce"],
    "status": "active"
  },

  "components": [
    {
      "id": "web_client",
      "name": "Web Client",
      "type": "client",
      "description": "Customer-facing web application",
      "technology": "React",
      "hosted_on": "Vercel",
      "performance": {
        "latency": "<500ms"
      },
      "security": {
        "auth": "jwt",
        "tls": true
      }
    },
    {
      "id": "mobile_app",
      "name": "Mobile App",
      "type": "client",
      "description": "Native mobile application",
      "technology": "React Native",
      "hosted_on": "App Store, Google Play"
    },
    {
      "id": "api_gateway",
      "name": "API Gateway",
      "type": "api_gateway",
      "description": "Entry point for all API requests",
      "technology": "Kong",
      "hosted_on": "AWS ECS",
      "backup": {
        "count": 3,
        "strategy": "active-active"
      },
      "performance": {
        "throughput": "100k RPS",
        "latency": "<50ms",
        "sla": "99.99%"
      }
    },
    {
      "id": "user_service",
      "name": "User Service",
      "type": "service",
      "description": "User management and authentication",
      "technology": "Node.js + Express",
      "hosted_on": "Kubernetes",
      "responsibility": [
        "User registration and login",
        "Profile management",
        "Password reset"
      ],
      "owner": "Identity Team",
      "scaling": {
        "type": "horizontal",
        "strategy": "Kubernetes auto-scaling"
      },
      "backup": {
        "count": 3,
        "strategy": "active-active"
      },
      "performance": {
        "throughput": "10k RPS",
        "latency": "<100ms",
        "sla": "99.9%"
      },
      "security": {
        "auth": "jwt",
        "encryption": true,
        "tls": true
      }
    },
    {
      "id": "product_service",
      "name": "Product Service",
      "type": "service",
      "description": "Product catalog management",
      "technology": "Python + FastAPI",
      "hosted_on": "Kubernetes",
      "responsibility": [
        "Product listing",
        "Search and filtering",
        "Inventory management"
      ],
      "owner": "Catalog Team",
      "scaling": {
        "type": "horizontal",
        "strategy": "Kubernetes auto-scaling"
      },
      "performance": {
        "throughput": "15k RPS",
        "latency": "<150ms",
        "sla": "99.9%"
      }
    },
    {
      "id": "order_service",
      "name": "Order Service",
      "type": "service",
      "description": "Order processing and management",
      "technology": "Java + Spring Boot",
      "hosted_on": "Kubernetes",
      "responsibility": [
        "Order creation",
        "Order tracking",
        "Payment processing"
      ],
      "owner": "Orders Team",
      "scaling": {
        "type": "horizontal",
        "strategy": "Kubernetes auto-scaling"
      },
      "performance": {
        "throughput": "5k RPS",
        "latency": "<200ms",
        "sla": "99.95%"
      }
    },
    {
      "id": "payment_gateway",
      "name": "Payment Gateway",
      "type": "external_service",
      "description": "Third-party payment processing",
      "technology": "Stripe",
      "owner": "Finance Team",
      "security": {
        "auth": "api_key",
        "tls": true
      }
    },
    {
      "id": "user_db",
      "name": "User Database",
      "type": "database",
      "description": "PostgreSQL for user data",
      "technology": "PostgreSQL",
      "hosted_on": "AWS RDS",
      "backup": {
        "count": 1,
        "strategy": "active-passive"
      },
      "performance": {
        "sla": "99.95%"
      },
      "security": {
        "encryption": true,
        "tls": true
      }
    },
    {
      "id": "product_db",
      "name": "Product Database",
      "type": "database",
      "description": "PostgreSQL for product data",
      "technology": "PostgreSQL",
      "hosted_on": "AWS RDS"
    },
    {
      "id": "order_db",
      "name": "Order Database",
      "type": "database",
      "description": "PostgreSQL for order data",
      "technology": "PostgreSQL",
      "hosted_on": "AWS RDS"
    },
    {
      "id": "cache",
      "name": "Cache Layer",
      "type": "cache",
      "description": "Distributed caching",
      "technology": "Redis",
      "hosted_on": "AWS ElastiCache",
      "backup": {
        "count": 2,
        "strategy": "active-passive"
      }
    },
    {
      "id": "message_queue",
      "name": "Message Queue",
      "type": "queue",
      "description": "Asynchronous message processing",
      "technology": "RabbitMQ",
      "hosted_on": "AWS MQ",
      "backup": {
        "count": 3,
        "strategy": "active-active"
      }
    },
    {
      "id": "search_engine",
      "name": "Search Engine",
      "type": "service",
      "description": "Full-text search",
      "technology": "Elasticsearch",
      "hosted_on": "AWS",
      "performance": {
        "latency": "<100ms"
      }
    },
    {
      "id": "monitoring",
      "name": "Monitoring & Logging",
      "type": "monitoring",
      "description": "System monitoring and observability",
      "technology": "Prometheus, Grafana, ELK Stack",
      "hosted_on": "AWS"
    }
  ],

  "connections": [
    {
      "from": "web_client",
      "to": "api_gateway",
      "protocol": "https",
      "direction": "two-way",
      "label": "REST API",
      "type": "synchronous",
      "frequency": "real-time",
      "security": {
        "authenticated": true,
        "encrypted": true
      }
    },
    {
      "from": "api_gateway",
      "to": "user_service",
      "protocol": "https",
      "direction": "two-way",
      "label": "User API",
      "type": "synchronous"
    },
    {
      "from": "api_gateway",
      "to": "product_service",
      "protocol": "https",
      "direction": "two-way",
      "label": "Product API",
      "type": "synchronous"
    },
    {
      "from": "api_gateway",
      "to": "order_service",
      "protocol": "https",
      "direction": "two-way",
      "label": "Order API",
      "type": "synchronous"
    },
    {
      "from": "user_service",
      "to": "user_db",
      "protocol": "tcp",
      "direction": "two-way",
      "label": "Database",
      "type": "synchronous",
      "security": {
        "encrypted": true
      }
    },
    {
      "from": "product_service",
      "to": "product_db",
      "protocol": "tcp",
      "direction": "two-way",
      "label": "Database",
      "type": "synchronous"
    },
    {
      "from": "order_service",
      "to": "order_db",
      "protocol": "tcp",
      "direction": "two-way",
      "label": "Database",
      "type": "synchronous"
    },
    {
      "from": "user_service",
      "to": "cache",
      "protocol": "redis",
      "direction": "two-way",
      "label": "Cache",
      "type": "synchronous"
    },
    {
      "from": "product_service",
      "to": "cache",
      "protocol": "redis",
      "direction": "two-way",
      "label": "Cache",
      "type": "synchronous"
    },
    {
      "from": "order_service",
      "to": "message_queue",
      "protocol": "amqp",
      "direction": "one-way",
      "label": "Order Events",
      "type": "asynchronous",
      "frequency": "on-demand"
    },
    {
      "from": "order_service",
      "to": "payment_gateway",
      "protocol": "https",
      "direction": "two-way",
      "label": "Payment API",
      "type": "synchronous",
      "security": {
        "authenticated": true,
        "encrypted": true
      }
    },
    {
      "from": "product_service",
      "to": "search_engine",
      "protocol": "https",
      "direction": "two-way",
      "label": "Index Update",
      "type": "asynchronous"
    }
  ],

  "users": [
    {
      "id": "web_customer",
      "name": "Web Customer",
      "type": "user",
      "description": "Customer using web application",
      "interactions": ["web_client"]
    },
    {
      "id": "mobile_customer",
      "name": "Mobile Customer",
      "type": "user",
      "description": "Customer using mobile app",
      "interactions": ["mobile_app"]
    },
    {
      "id": "admin_user",
      "name": "Admin User",
      "type": "user",
      "description": "System administrator",
      "interactions": ["api_gateway"]
    }
  ],

  "deployment": {
    "environments": [
      {
        "name": "production",
        "region": "us-east-1",
        "platform": "aws",
        "configuration": {
          "auto_scaling": true,
          "multi_az": true,
          "backup_enabled": true
        }
      },
      {
        "name": "staging",
        "region": "us-east-1",
        "platform": "aws"
      },
      {
        "name": "development",
        "region": "us-east-1",
        "platform": "kubernetes"
      }
    ],
    "infrastructure": {
      "container_orchestration": "kubernetes",
      "ci_cd": "GitHub Actions",
      "monitoring": ["Prometheus", "Grafana", "ELK Stack"]
    }
  },

  "data_flow": {
    "flows": [
      {
        "name": "User Registration",
        "description": "New user registration flow",
        "steps": [
          {
            "from": "web_client",
            "to": "api_gateway",
            "action": "POST /register",
            "data": "User email, password, name"
          },
          {
            "from": "api_gateway",
            "to": "user_service",
            "action": "Create user",
            "data": "User details"
          },
          {
            "from": "user_service",
            "to": "user_db",
            "action": "INSERT",
            "data": "User record"
          }
        ]
      },
      {
        "name": "Product Purchase",
        "description": "Customer purchases product",
        "steps": [
          {
            "from": "web_client",
            "to": "api_gateway",
            "action": "POST /orders",
            "data": "Product ID, quantity, user ID"
          },
          {
            "from": "api_gateway",
            "to": "order_service",
            "action": "Create order",
            "data": "Order details"
          },
          {
            "from": "order_service",
            "to": "payment_gateway",
            "action": "Process payment",
            "data": "Amount, payment method"
          },
          {
            "from": "order_service",
            "to": "message_queue",
            "action": "Publish OrderCreated",
            "data": "Order event"
          }
        ]
      }
    ]
  },

  "technologies": {
    "languages": ["JavaScript", "Python", "Java", "SQL"],
    "frameworks": ["React", "Express", "FastAPI", "Spring Boot"],
    "databases": ["PostgreSQL", "Redis"],
    "messaging": ["RabbitMQ", "Kafka"],
    "caching": ["Redis"],
    "external_services": ["Stripe", "SendGrid", "AWS"]
  }
}
```

---

## Simplified Forms for User Input

### Interactive Form Structure

Users can fill this step-by-step:

```json
{
  "form_sections": [
    {
      "section": "metadata",
      "fields": [
        {
          "name": "architecture_name",
          "label": "Architecture Name",
          "type": "text",
          "placeholder": "E.g., E-commerce Platform",
          "required": true
        },
        {
          "name": "description",
          "label": "Brief Description",
          "type": "textarea",
          "placeholder": "What does this architecture do?",
          "required": true
        },
        {
          "name": "tags",
          "label": "Tags",
          "type": "multi-select",
          "options": ["microservices", "monolithic", "serverless", "cloud", "on-premise"],
          "required": false
        }
      ]
    },
    {
      "section": "components",
      "fields": [
        {
          "name": "component_name",
          "label": "Component Name",
          "type": "text",
          "required": true
        },
        {
          "name": "component_type",
          "label": "Component Type",
          "type": "select",
          "options": ["service", "database", "queue", "cache", "api_gateway", "external_service", "client"],
          "required": true
        },
        {
          "name": "technology",
          "label": "Technology Used",
          "type": "text",
          "placeholder": "E.g., Node.js, PostgreSQL",
          "required": false
        }
      ]
    },
    {
      "section": "connections",
      "fields": [
        {
          "name": "from_component",
          "label": "From Component",
          "type": "select",
          "options": "[ dynamic from components list ]",
          "required": true
        },
        {
          "name": "to_component",
          "label": "To Component",
          "type": "select",
          "options": "[ dynamic from components list ]",
          "required": true
        },
        {
          "name": "protocol",
          "label": "Protocol",
          "type": "select",
          "options": ["http", "https", "grpc", "tcp", "amqp", "kafka", "sql", "redis"],
          "required": true
        }
      ]
    }
  ]
}
```

---

## Schema Transformations

### To Mermaid Diagram

```
graph TD
    subgraph "Frontend"
        WebClient[Web Client]
        MobileApp[Mobile App]
    end

    subgraph "API Layer"
        APIGateway[API Gateway]
    end

    subgraph "Services"
        UserService[User Service]
        ProductService[Product Service]
        OrderService[Order Service]
    end

    subgraph "Data Layer"
        UserDB[(User DB)]
        ProductDB[(Product DB)]
        OrderDB[(Order DB)]
        Cache[(Redis Cache)]
    end

    WebClient -->|HTTPS| APIGateway
    MobileApp -->|HTTPS| APIGateway
    APIGateway -->|API| UserService
    APIGateway -->|API| ProductService
    APIGateway -->|API| OrderService
    UserService -->|Query| UserDB
    ProductService -->|Query| ProductDB
    OrderService -->|Query| OrderDB
```

### To D2 Diagram

```
users: {
  shape: circle
}

web: {
  shape: browser
}

api_gateway: {
  label: API Gateway
}

services: {
  user_service: User Service
  product_service: Product Service
  order_service: Order Service
}

databases: {
  user_db: User DB
  product_db: Product DB
  order_db: Order DB
}

users -> web: Browse
web -> api_gateway: HTTPS
api_gateway -> services.user_service: Route
api_gateway -> services.product_service: Route
api_gateway -> services.order_service: Route
services.user_service -> databases.user_db: Query
services.product_service -> databases.product_db: Query
services.order_service -> databases.order_db: Query
```

---

## Validation Rules

### Schema Validation

```python
def validate_architecture_schema(data):
    """Validate architecture definition against schema."""

    rules = [
        ("Unique component IDs", lambda: len({c['id'] for c in data['components']}) == len(data['components'])),
        ("Valid connections", lambda: all(
            any(c['id'] == conn['from'] for c in data['components'])
            and any(c['id'] == conn['to'] for c in data['components'])
            for conn in data.get('connections', [])
        )),
        ("No self-loops", lambda: all(
            conn['from'] != conn['to']
            for conn in data.get('connections', [])
        )),
        ("Required metadata", lambda: 'metadata' in data and 'name' in data['metadata']),
        ("At least one component", lambda: len(data.get('components', [])) > 0),
    ]

    errors = []
    for rule_name, rule_check in rules:
        if not rule_check():
            errors.append(f"Validation failed: {rule_name}")

    return len(errors) == 0, errors
```

---

## Storage Format

### Save/Load Architecture

```python
# Save architecture
with open(f"architectures/{name}.json", "w") as f:
    json.dump(architecture, f, indent=2)

# Load architecture
with open(f"architectures/{name}.json", "r") as f:
    architecture = json.load(f)

# Validate
valid, errors = validate_architecture_schema(architecture)
if not valid:
    raise ValueError(f"Invalid architecture: {errors}")
```

### Versioning

```json
{
  "metadata": {
    "name": "E-commerce Platform",
    "version": "2.0.0",
    "previous_versions": [
      {
        "version": "1.0.0",
        "date": "2024-10-01T00:00:00Z",
        "changes": "Initial architecture"
      },
      {
        "version": "1.5.0",
        "date": "2024-10-15T00:00:00Z",
        "changes": "Added caching layer"
      }
    ]
  }
}
```

---

## Integration with Diagram Wizard

### Workflow

1. **User Input Phase**
   - Fill out interactive form
   - Or upload existing JSON
   - Or describe in natural language

2. **Schema Generation**
   - Parse inputs
   - Validate against JSON schema
   - Generate architecture definition

3. **LLM Clarification**
   - Ask follow-up questions based on schema
   - Fill gaps in definition
   - Confirm understanding

4. **Diagram Generation**
   - Transform schema to diagram code
   - Generate SVG output
   - User can refine

### Query Architecture

```python
# Query for specific components
def get_components_by_type(schema, component_type):
    return [c for c in schema['components'] if c['type'] == component_type]

# Find all connections for a component
def get_connections_for_component(schema, component_id):
    conns = schema.get('connections', [])
    return [c for c in conns if c['from'] == component_id or c['to'] == component_id]

# Get technology stack
def extract_technologies(schema):
    return {
        'languages': schema['technologies'].get('languages', []),
        'frameworks': schema['technologies'].get('frameworks', []),
        'databases': schema['technologies'].get('databases', []),
    }
```

---

## Benefits

1. **Structured Data**
   - Unambiguous architecture definition
   - Easy to validate
   - Easy to transform

2. **Reusability**
   - Save and reuse architectures
   - Template-based designs
   - Share across teams

3. **Multi-Format Output**
   - Single schema → multiple diagram types
   - Consistent architecture representation
   - No conflicting definitions

4. **Automation**
   - Generate documentation
   - Create code scaffolds
   - Generate infrastructure as code

5. **Analysis**
   - Identify gaps
   - Check component coverage
   - Validate consistency

---

## Reference Documents

- **JSON Schema Specification:** https://json-schema.org/
- **Diagram Wizard Architecture:** See UPGRADEPLAN.MD
- **Implementation Guide:** See IMPLEMENTATION_PLAN.MD

---

**Status:** Schema design complete
**Ready for:** Implementation in Diagram Wizard
**Use Case:** Architecture definition and diagram generation
