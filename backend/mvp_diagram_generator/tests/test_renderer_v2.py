"""
Tests for the new renderer_v2.py using Playwright + frontend HTML page
"""

import pytest
import asyncio
import sys
import os

# Add parent directory to path so we can import renderer_v2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from renderer_v2 import render_diagram


# Test fixtures
FRONTEND_URL = "http://localhost:5173"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Simple Diagram Tests (Direct rendering without AI)
# ============================================================================

@pytest.mark.asyncio
async def test_mermaid_simple_flowchart():
    """Test rendering a simple Mermaid flowchart."""
    code = """
    flowchart TD
        A[Start] --> B{Decision}
        B -->|Yes| C[Success]
        B -->|No| D[Failure]
        C --> E[End]
        D --> E
    """

    svg = await render_diagram(code, "mermaid", "svg", FRONTEND_URL)

    assert svg is not None
    assert len(svg) > 0
    assert "<svg" in svg
    print(f"[PASS] Mermaid flowchart rendered: {len(svg)} chars")


@pytest.mark.asyncio
async def test_mermaid_sequence_diagram():
    """Test rendering a Mermaid sequence diagram."""
    code = """
    sequenceDiagram
        participant User
        participant App
        participant DB

        User->>App: Login Request
        App->>DB: Validate Credentials
        DB-->>App: User Data
        App-->>User: Login Success
    """

    svg = await render_diagram(code, "mermaid", "svg", FRONTEND_URL)

    assert svg is not None
    assert "<svg" in svg
    print(f"[PASS] Mermaid sequence diagram rendered: {len(svg)} chars")


@pytest.mark.asyncio
async def test_d2_simple_diagram():
    """Test rendering a simple D2 diagram."""
    code = """
    frontend: Frontend App {
        shape: rectangle
    }

    backend: Backend API {
        shape: rectangle
    }

    database: Database {
        shape: cylinder
    }

    frontend -> backend: HTTP Request
    backend -> database: Query
    database -> backend: Results
    backend -> frontend: Response
    """

    svg = await render_diagram(code, "d2", "svg", FRONTEND_URL)

    assert svg is not None
    assert "<svg" in svg
    print(f"[PASS] D2 diagram rendered: {len(svg)} chars")


@pytest.mark.asyncio
async def test_c4_context_diagram():
    """Test rendering a C4 context diagram."""
    code = """
    C4Context

    Person(user, "User", "A user of the system")
    System(app, "Application", "The main application")
    System_Ext(external, "External API", "Third-party service")

    Rel(user, app, "Uses")
    Rel(app, external, "Calls API")
    """

    svg = await render_diagram(code, "c4", "svg", FRONTEND_URL)

    assert svg is not None
    assert "<svg" in svg
    print(f"[PASS] C4 context diagram rendered: {len(svg)} chars")


@pytest.mark.asyncio
async def test_png_output():
    """Test rendering to PNG format."""
    code = """
    flowchart LR
        A[Input] --> B[Process]
        B --> C[Output]
    """

    png_base64 = await render_diagram(code, "mermaid", "png", FRONTEND_URL)

    assert png_base64 is not None
    assert len(png_base64) > 0
    # PNG base64 should not contain SVG tags
    assert "<svg" not in png_base64
    print(f"[PASS] PNG output rendered: {len(png_base64)} chars (base64)")


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_mermaid_syntax():
    """Test handling of invalid Mermaid syntax."""
    code = "this is not valid mermaid syntax at all"

    with pytest.raises(Exception):
        await render_diagram(code, "mermaid", "svg", FRONTEND_URL)


@pytest.mark.asyncio
async def test_invalid_diagram_type():
    """Test handling of invalid diagram type."""
    code = "graph TD; A-->B"

    with pytest.raises(Exception):
        await render_diagram(code, "invalid_type", "svg", FRONTEND_URL)


@pytest.mark.asyncio
async def test_empty_code():
    """Test handling of empty diagram code."""
    code = ""

    with pytest.raises(Exception):
        await render_diagram(code, "mermaid", "svg", FRONTEND_URL)


# ============================================================================
# Complex Diagram Tests
# ============================================================================

@pytest.mark.asyncio
async def test_complex_mermaid_class_diagram():
    """Test rendering a complex Mermaid class diagram."""
    code = """
    classDiagram
        class Animal {
            +String name
            +int age
            +makeSound()
        }

        class Dog {
            +String breed
            +bark()
        }

        class Cat {
            +String color
            +meow()
        }

        Animal <|-- Dog
        Animal <|-- Cat
    """

    svg = await render_diagram(code, "mermaid", "svg", FRONTEND_URL)

    assert svg is not None
    assert "<svg" in svg
    print(f"[PASS] Complex Mermaid class diagram rendered: {len(svg)} chars")


@pytest.mark.asyncio
async def test_complex_d2_with_containers():
    """Test rendering a complex D2 diagram with containers."""
    code = """
    direction: right

    web_tier: Web Tier {
        nginx: NGINX {
            shape: rectangle
        }

        app1: App Server 1
        app2: App Server 2
    }

    data_tier: Data Tier {
        primary: Primary DB {
            shape: cylinder
        }

        backup: Backup DB {
            shape: cylinder
        }
    }

    user: User {
        shape: person
    }

    user -> web_tier.nginx: HTTPS
    web_tier.nginx -> web_tier.app1: Route
    web_tier.nginx -> web_tier.app2: Route
    web_tier.app1 -> data_tier.primary: Query
    web_tier.app2 -> data_tier.primary: Query
    data_tier.primary -> data_tier.backup: Replicate
    """

    svg = await render_diagram(code, "d2", "svg", FRONTEND_URL)

    assert svg is not None
    assert "<svg" in svg
    print(f"[PASS] Complex D2 diagram with containers rendered: {len(svg)} chars")


@pytest.mark.asyncio
async def test_c4_container_diagram():
    """Test rendering a C4 container diagram."""
    code = """
    C4Container

    Person(user, "Customer", "A customer of the bank")

    System_Boundary(banking, "Banking System") {
        Container(web, "Web Application", "Java, Spring", "Delivers banking UI")
        Container(mobile, "Mobile App", "React Native", "Mobile banking")
        ContainerDb(db, "Database", "PostgreSQL", "Stores user data")
    }

    System_Ext(email, "Email System", "Sends notifications")

    Rel(user, web, "Uses", "HTTPS")
    Rel(user, mobile, "Uses")
    Rel(web, db, "Reads/Writes")
    Rel(mobile, db, "Reads/Writes")
    Rel(web, email, "Sends email")
    """

    svg = await render_diagram(code, "c4", "svg", FRONTEND_URL)

    assert svg is not None
    assert "<svg" in svg
    print(f"[PASS] C4 container diagram rendered: {len(svg)} chars")


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.asyncio
async def test_multiple_renders_in_sequence():
    """Test rendering multiple diagrams in sequence."""
    diagrams = [
        ("flowchart TD; A-->B", "mermaid"),
        ("a -> b", "d2"),
        ("C4Context\nPerson(u, 'User')", "c4"),
    ]

    for code, diagram_type in diagrams:
        svg = await render_diagram(code, diagram_type, "svg", FRONTEND_URL)
        assert svg is not None
        assert "<svg" in svg

    print(f"[PASS] Rendered {len(diagrams)} diagrams in sequence")


# ============================================================================
# Run all tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
