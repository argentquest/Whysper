"""
Architecture Schema utilities for validating and working with architecture definitions.

Provides validation, querying, transformation functions, and comment management
for architecture JSON schemas.
"""

import json
import jsonschema
import uuid
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum


# Component types
class ComponentType(str, Enum):
    """Valid component types."""

    SERVICE = "service"
    DATABASE = "database"
    QUEUE = "queue"
    CACHE = "cache"
    API_GATEWAY = "api_gateway"
    LOAD_BALANCER = "load_balancer"
    EXTERNAL_SERVICE = "external_service"
    CLIENT = "client"
    CONTAINER = "container"
    FUNCTION = "function"
    STORAGE = "storage"
    MONITORING = "monitoring"
    OTHER = "other"


# Protocol types
class ProtocolType(str, Enum):
    """Valid protocol types."""

    HTTP = "http"
    HTTPS = "https"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    TCP = "tcp"
    UDP = "udp"
    AMQP = "amqp"
    KAFKA = "kafka"
    REST = "rest"
    GRAPHQL = "graphql"
    SQL = "sql"
    REDIS = "redis"
    OTHER = "other"


class ArchitectureSchema:
    """
    Architecture Schema validator and query tool.

    Validates architecture definitions against JSON schema
    and provides utility methods for querying and analyzing.
    """

    # Minimal JSON schema for architecture
    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "System Architecture Schema",
        "type": "object",
        "required": ["metadata", "components"],
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                    "description": {"type": "string"},
                    "author": {"type": "string"},
                    "date": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "status": {
                        "type": "string",
                        "enum": ["draft", "proposed", "active", "deprecated"],
                    },
                },
                "required": ["name", "description"],
            },
            "components": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["id", "name", "type"],
                    "properties": {
                        "id": {"type": "string", "pattern": "^[a-z0-9_-]+$"},
                        "name": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": [e.value for e in ComponentType],
                        },
                        "description": {"type": "string"},
                        "technology": {"type": "string"},
                        "responsibility": {"type": "array", "items": {"type": "string"}},
                        "owner": {"type": "string"},
                        "hosted_on": {"type": "string"},
                    },
                },
            },
            "connections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["from", "to", "protocol"],
                    "properties": {
                        "id": {"type": "string"},
                        "from": {"type": "string"},
                        "to": {"type": "string"},
                        "protocol": {
                            "type": "string",
                            "enum": [e.value for e in ProtocolType],
                        },
                        "direction": {
                            "type": "string",
                            "enum": ["one-way", "two-way"],
                        },
                        "label": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": [
                                "synchronous",
                                "asynchronous",
                                "publish-subscribe",
                                "request-reply",
                            ],
                        },
                    },
                },
            },
            "users": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "name", "type"],
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": [
                                "user",
                                "system",
                                "service",
                                "mobile_app",
                                "web_app",
                                "third_party",
                            ],
                        },
                        "description": {"type": "string"},
                    },
                },
            },
            "deployment": {"type": "object"},
            "data_flow": {"type": "object"},
            "technologies": {"type": "object"},
        },
    }

    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate architecture definition against schema.

        Args:
            data: Architecture definition dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Schema validation
        try:
            jsonschema.validate(instance=data, schema=ArchitectureSchema.SCHEMA)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation: {e.message}")

        # Additional business logic validation
        if "components" in data:
            # Check for duplicate component IDs
            ids = [c.get("id") for c in data["components"]]
            duplicates = [id for id in ids if ids.count(id) > 1]
            if duplicates:
                errors.append(f"Duplicate component IDs: {duplicates}")

            # Check connections reference valid components
            component_ids = {c.get("id") for c in data["components"]}
            for conn in data.get("connections", []):
                if conn.get("from") not in component_ids:
                    errors.append(f"Connection references unknown component: {conn['from']}")
                if conn.get("to") not in component_ids:
                    errors.append(f"Connection references unknown component: {conn['to']}")

                # Check no self-loops
                if conn.get("from") == conn.get("to"):
                    errors.append(f"Self-loop not allowed: {conn['from']} -> {conn['to']}")

        return len(errors) == 0, errors

    @staticmethod
    def get_components_by_type(schema: Dict[str, Any], component_type: str) -> List[Dict[str, Any]]:
        """
        Get all components of a specific type.

        Args:
            schema: Architecture definition
            component_type: Type to filter by

        Returns:
            List of matching components
        """
        return [c for c in schema.get("components", []) if c.get("type") == component_type]

    @staticmethod
    def get_connections_for_component(schema: Dict[str, Any], component_id: str) -> List[Dict[str, Any]]:
        """
        Get all connections involving a component.

        Args:
            schema: Architecture definition
            component_id: Component to find connections for

        Returns:
            List of connections (incoming and outgoing)
        """
        conns = schema.get("connections", [])
        return [c for c in conns if c.get("from") == component_id or c.get("to") == component_id]

    @staticmethod
    def get_component_by_id(schema: Dict[str, Any], component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a component by ID.

        Args:
            schema: Architecture definition
            component_id: Component ID to find

        Returns:
            Component definition or None if not found
        """
        for c in schema.get("components", []):
            if c.get("id") == component_id:
                return c
        return None

    @staticmethod
    def get_external_services(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all external services.

        Args:
            schema: Architecture definition

        Returns:
            List of external service components
        """
        return ArchitectureSchema.get_components_by_type(schema, "external_service")

    @staticmethod
    def get_databases(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all databases.

        Args:
            schema: Architecture definition

        Returns:
            List of database components
        """
        return ArchitectureSchema.get_components_by_type(schema, "database")

    @staticmethod
    def get_services(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all microservices.

        Args:
            schema: Architecture definition

        Returns:
            List of service components
        """
        return ArchitectureSchema.get_components_by_type(schema, "service")

    @staticmethod
    def get_clients(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all client components.

        Args:
            schema: Architecture definition

        Returns:
            List of client components
        """
        return ArchitectureSchema.get_components_by_type(schema, "client")

    @staticmethod
    def get_technologies(schema: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract technology stack from architecture.

        Args:
            schema: Architecture definition

        Returns:
            Dictionary of technologies by category
        """
        techs = schema.get("technologies", {})
        return {
            "languages": techs.get("languages", []),
            "frameworks": techs.get("frameworks", []),
            "databases": techs.get("databases", []),
            "messaging": techs.get("messaging", []),
            "caching": techs.get("caching", []),
            "external_services": techs.get("external_services", []),
        }

    @staticmethod
    def get_connection_stats(schema: Dict[str, Any]) -> Dict[str, int]:
        """
        Get statistics about connections.

        Args:
            schema: Architecture definition

        Returns:
            Dictionary of connection statistics
        """
        conns = schema.get("connections", [])
        protocols = {}
        types = {}

        for conn in conns:
            protocol = conn.get("protocol")
            conn_type = conn.get("type")

            protocols[protocol] = protocols.get(protocol, 0) + 1
            types[conn_type] = types.get(conn_type, 0) + 1

        return {
            "total_connections": len(conns),
            "protocols": protocols,
            "types": types,
        }

    @staticmethod
    def to_mermaid(schema: Dict[str, Any]) -> str:
        """
        Transform architecture schema to Mermaid diagram code.

        Args:
            schema: Architecture definition

        Returns:
            Mermaid diagram code
        """
        lines = ["graph TD"]

        # Add components
        for component in schema.get("components", []):
            component_id = component.get("id")
            name = component.get("name")
            comp_type = component.get("type")

            # Style based on type
            if comp_type == "database":
                lines.append(f"    {component_id}[('{name}')]")
            elif comp_type == "queue":
                lines.append(f"    {component_id}['⚙️ {name}']")
            elif comp_type == "client":
                lines.append(f"    {component_id}['👤 {name}']")
            elif comp_type == "external_service":
                lines.append(f"    {component_id}['🔗 {name}']")
            else:
                lines.append(f"    {component_id}['{name}']")

        # Add connections
        lines.append("")
        for conn in schema.get("connections", []):
            from_id = conn.get("from")
            to_id = conn.get("to")
            label = conn.get("label", conn.get("protocol", ""))

            if label:
                lines.append(f"    {from_id} -->|{label}| {to_id}")
            else:
                lines.append(f"    {from_id} --> {to_id}")

        return "\n".join(lines)

    @staticmethod
    def save_to_file(schema: Dict[str, Any], filepath: str) -> bool:
        """
        Save architecture schema to JSON file.

        Args:
            schema: Architecture definition
            filepath: Path to save to

        Returns:
            True if successful
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(schema, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving architecture: {e}")
            return False

    @staticmethod
    def load_from_file(filepath: str) -> Optional[Dict[str, Any]]:
        """
        Load architecture schema from JSON file.

        Args:
            filepath: Path to load from

        Returns:
            Architecture definition or None if error
        """
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading architecture: {e}")
            return None


class CommentType(str, Enum):
    """Valid comment types."""

    NOTE = "note"
    RATIONALE = "rationale"
    DECISION = "decision"
    WARNING = "warning"
    TODO = "todo"
    REFERENCE = "reference"
    EXAMPLE = "example"
    CONSTRAINT = "constraint"
    RISK = "risk"
    IMPROVEMENT = "improvement"
    DOCUMENTATION = "documentation"


class CommentPriority(str, Enum):
    """Comment priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CommentStatus(str, Enum):
    """Comment status."""

    OPEN = "open"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    PENDING_REVIEW = "pending_review"


class ArchitectureComments:
    """
    Comment management for architecture schemas.

    Allows adding, querying, and managing contextual comments
    throughout the architecture definition.
    """

    @staticmethod
    def add_global_comment(
        schema: Dict[str, Any],
        text: str,
        comment_type: str,
        author: str,
        tags: List[str] = None,
        priority: str = "medium",
        references: List[Dict] = None,
    ) -> str:
        """
        Add a global comment to the architecture.

        Args:
            schema: Architecture definition
            text: Comment text (markdown supported)
            comment_type: Type of comment
            author: Who added the comment
            tags: Categorization tags
            priority: Importance level
            references: External references

        Returns:
            Comment ID
        """
        comment_id = f"comment_{uuid.uuid4().hex[:8]}"

        comment = {
            "id": comment_id,
            "text": text,
            "type": comment_type,
            "author": author,
            "date": datetime.utcnow().isoformat(),
            "tags": tags or [],
            "priority": priority,
            "status": "open",
        }

        if references:
            comment["references"] = references

        if "comments" not in schema:
            schema["comments"] = []

        schema["comments"].append(comment)
        return comment_id

    @staticmethod
    def add_component_comment(
        schema: Dict[str, Any],
        component_id: str,
        text: str,
        comment_type: str,
        author: str,
        tags: List[str] = None,
        priority: str = "medium",
    ) -> str:
        """
        Add a comment to a specific component.

        Args:
            schema: Architecture definition
            component_id: Component to comment on
            text: Comment text
            comment_type: Type of comment
            author: Who added the comment
            tags: Categorization tags
            priority: Importance level

        Returns:
            Comment ID
        """
        component = ArchitectureSchema.get_component_by_id(schema, component_id)
        if not component:
            raise ValueError(f"Component not found: {component_id}")

        comment_id = f"comment_{uuid.uuid4().hex[:8]}"

        comment = {
            "id": comment_id,
            "text": text,
            "type": comment_type,
            "author": author,
            "date": datetime.utcnow().isoformat(),
            "tags": tags or [],
            "priority": priority,
            "status": "open",
        }

        if "comments" not in component:
            component["comments"] = []

        component["comments"].append(comment)
        return comment_id

    @staticmethod
    def get_all_comments(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all comments in the architecture.

        Args:
            schema: Architecture definition

        Returns:
            List of all comments
        """
        comments = schema.get("comments", [])

        # Add component comments with context
        for component in schema.get("components", []):
            for comment in component.get("comments", []):
                comment_with_context = comment.copy()
                comment_with_context["component_id"] = component["id"]
                comments.append(comment_with_context)

        return comments

    @staticmethod
    def get_comments_by_type(schema: Dict[str, Any], comment_type: str) -> List[Dict[str, Any]]:
        """
        Get all comments of a specific type.

        Args:
            schema: Architecture definition
            comment_type: Type to filter by

        Returns:
            List of matching comments
        """
        return [c for c in ArchitectureComments.get_all_comments(schema) if c.get("type") == comment_type]

    @staticmethod
    def get_comments_by_priority(schema: Dict[str, Any], priorities: List[str]) -> List[Dict[str, Any]]:
        """
        Get comments with specific priorities.

        Args:
            schema: Architecture definition
            priorities: List of priorities to filter by

        Returns:
            List of matching comments
        """
        return [c for c in ArchitectureComments.get_all_comments(schema) if c.get("priority") in priorities]

    @staticmethod
    def get_comments_by_tag(schema: Dict[str, Any], tag: str) -> List[Dict[str, Any]]:
        """
        Get comments with a specific tag.

        Args:
            schema: Architecture definition
            tag: Tag to filter by

        Returns:
            List of matching comments
        """
        return [c for c in ArchitectureComments.get_all_comments(schema) if tag in c.get("tags", [])]

    @staticmethod
    def get_open_todos(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all open TODO items.

        Args:
            schema: Architecture definition

        Returns:
            List of open TODOs
        """
        return [
            c
            for c in ArchitectureComments.get_all_comments(schema)
            if c.get("type") == "todo" and c.get("status") == "open"
        ]

    @staticmethod
    def get_component_comments(schema: Dict[str, Any], component_id: str) -> List[Dict[str, Any]]:
        """
        Get all comments for a specific component.

        Args:
            schema: Architecture definition
            component_id: Component to get comments for

        Returns:
            List of comments for the component
        """
        component = ArchitectureSchema.get_component_by_id(schema, component_id)
        if not component:
            return []

        return component.get("comments", [])

    @staticmethod
    def add_response(
        schema: Dict[str, Any],
        comment_id: str,
        author: str,
        text: str,
    ) -> bool:
        """
        Add a response to a comment (threaded discussion).

        Args:
            schema: Architecture definition
            comment_id: Comment to respond to
            author: Who is responding
            text: Response text

        Returns:
            True if successful
        """
        all_comments = ArchitectureComments.get_all_comments(schema)

        for comment in all_comments:
            if comment.get("id") == comment_id:
                if "responses" not in comment:
                    comment["responses"] = []

                response = {
                    "author": author,
                    "date": datetime.utcnow().isoformat(),
                    "text": text,
                }

                comment["responses"].append(response)
                return True

        return False

    @staticmethod
    def get_comment_statistics(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about comments in the architecture.

        Args:
            schema: Architecture definition

        Returns:
            Dictionary of comment statistics
        """
        all_comments = ArchitectureComments.get_all_comments(schema)

        stats = {
            "total_comments": len(all_comments),
            "by_type": {},
            "by_priority": {},
            "by_status": {},
            "by_tag": {},
            "total_responses": 0,
        }

        for comment in all_comments:
            # Count by type
            ctype = comment.get("type", "unknown")
            stats["by_type"][ctype] = stats["by_type"].get(ctype, 0) + 1

            # Count by priority
            priority = comment.get("priority", "medium")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

            # Count by status
            status = comment.get("status", "open")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Count by tag
            for tag in comment.get("tags", []):
                stats["by_tag"][tag] = stats["by_tag"].get(tag, 0) + 1

            # Count responses
            stats["total_responses"] += len(comment.get("responses", []))

        return stats

    @staticmethod
    def generate_decision_log(schema: Dict[str, Any]) -> str:
        """
        Generate architectural decision log from decision comments.

        Args:
            schema: Architecture definition

        Returns:
            Formatted decision log in markdown
        """
        decisions = ArchitectureComments.get_comments_by_type(schema, "decision")
        decisions_sorted = sorted(decisions, key=lambda x: x.get("date", ""))

        log = "# Architectural Decision Log\n\n"

        for decision in decisions_sorted:
            log += f"## {decision.get('text', '')}\n"
            log += f"**Author**: {decision.get('author')}\n"
            log += f"**Date**: {decision.get('date')}\n\n"

        return log

    @staticmethod
    def generate_risk_report(schema: Dict[str, Any]) -> str:
        """
        Generate risk assessment report from risk comments.

        Args:
            schema: Architecture definition

        Returns:
            Formatted risk report in markdown
        """
        risks = ArchitectureComments.get_comments_by_type(schema, "risk")

        report = "# Risk Assessment Report\n\n"

        for risk in sorted(risks, key=lambda x: x.get("priority", "medium")):
            priority = risk.get("priority", "medium").upper()
            report += f"## [{priority}] {risk.get('text', '')}\n"
            report += f"**Identified by**: {risk.get('author')}\n"
            report += f"**Date**: {risk.get('date')}\n\n"

        return report

    @staticmethod
    def generate_action_items_report(schema: Dict[str, Any]) -> str:
        """
        Generate action items report from TODO comments.

        Args:
            schema: Architecture definition

        Returns:
            Formatted action items report in markdown
        """
        todos = ArchitectureComments.get_open_todos(schema)

        report = "# Action Items\n\n"

        for item in sorted(todos, key=lambda x: x.get("priority", "medium")):
            priority = item.get("priority", "medium").upper()
            report += f"- [{priority}] {item.get('text', '')}\n"
            report += f"  - Owner: {item.get('author')}\n\n"

        return report
