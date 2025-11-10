#!/usr/bin/env python3
"""
SVG Validation and Testing Script

This script focuses specifically on SVG generation and validation.
It can be used to test SVG generation in isolation and validate
existing SVG outputs from the diagram wizard.
"""

import asyncio
import sys
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from app.services.diagram_factory_service import DiagramFactoryService


class SVGValidator:
    """Comprehensive SVG validation and testing."""
    
    def validate_svg_structure(self, svg_content: str) -> dict:
        """Perform comprehensive SVG validation."""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "info": {},
            "structure": {}
        }
        
        if not svg_content or not svg_content.strip():
            result["errors"].append("No SVG content provided")
            return result
        
        result["info"]["length"] = len(svg_content)
        result["info"]["lines"] = svg_content.count('\n')
        
        # Basic structure checks
        svg_lower = svg_content.lower()
        
        # Check for essential SVG elements
        if "<svg" not in svg_lower:
            result["errors"].append("Missing <svg> opening tag")
        else:
            result["structure"]["has_svg_tag"] = True
            
        if "</svg>" not in svg_lower:
            result["errors"].append("Missing </svg> closing tag")
        else:
            result["structure"]["has_closing_tag"] = True
        
        # Check for attributes
        if "viewbox" in svg_lower:
            result["structure"]["has_viewbox"] = True
        else:
            result["warnings"].append("Missing viewBox attribute (recommended)")
        
        if any(attr in svg_lower for attr in ["width=", "height="]):
            result["structure"]["has_dimensions"] = True
        else:
            result["warnings"].append("Missing width/height attributes")
        
        # Check for drawing elements
        drawing_elements = ["path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "g"]
        found_elements = []
        for element in drawing_elements:
            if f"<{element}" in svg_lower:
                found_elements.append(element)
        
        result["structure"]["drawing_elements"] = found_elements
        
        if not found_elements:
            result["errors"].append("No drawing elements found (empty diagram)")
        else:
            result["info"]["element_types"] = len(found_elements)
            result["info"]["element_list"] = found_elements
        
        # Try XML parsing
        try:
            # Clean up the SVG for XML parsing
            clean_svg = svg_content.strip()
            if not clean_svg.startswith('<?xml'):
                # Add XML declaration if missing
                clean_svg = '<?xml version="1.0" encoding="UTF-8"?>\n' + clean_svg
            
            root = ET.fromstring(clean_svg)
            result["structure"]["xml_valid"] = True
            result["info"]["root_tag"] = root.tag
            result["info"]["total_elements"] = len(list(root.iter()))
            
        except ET.ParseError as e:
            result["errors"].append(f"Invalid XML structure: {e}")
            result["structure"]["xml_valid"] = False
        
        # Extract dimensions if possible
        try:
            width_match = re.search(r'width=["\']([^"\']+)["\']', svg_content, re.IGNORECASE)
            height_match = re.search(r'height=["\']([^"\']+)["\']', svg_content, re.IGNORECASE)
            viewbox_match = re.search(r'viewbox=["\']([^"\']+)["\']', svg_content, re.IGNORECASE)
            
            if width_match:
                result["info"]["width"] = width_match.group(1)
            if height_match:
                result["info"]["height"] = height_match.group(1)
            if viewbox_match:
                result["info"]["viewbox"] = viewbox_match.group(1)
                
        except Exception as e:
            result["warnings"].append(f"Could not extract dimensions: {e}")
        
        # Determine overall validity
        result["valid"] = len(result["errors"]) == 0 and len(found_elements) > 0
        
        return result
    
    def save_svg_file(self, svg_content: str, filename: str = None) -> str:
        """Save SVG to file with validation."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_diagram_{timestamp}.svg"
        
        try:
            # Ensure proper SVG format
            if not svg_content.strip().startswith('<?xml'):
                svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            print(f"[SAVE] SVG saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"[ERROR] Failed to save SVG: {e}")
            return None
    
    def print_validation_report(self, validation: dict):
        """Print detailed validation report."""
        print("\n" + "="*60)
        print("[CHECK] SVG VALIDATION REPORT")
        print("="*60)
        
        # Overall status
        status = "[OK] VALID" if validation["valid"] else "[ERROR] INVALID"
        print(f"Overall Status: {status}")
        
        # Basic info
        info = validation["info"]
        print(f"\n[CHART] Basic Information:")
        print(f"  Content Length: {info.get('length', 0)} characters")
        print(f"  Number of Lines: {info.get('lines', 0)}")
        print(f"  Width: {info.get('width', 'not specified')}")
        print(f"  Height: {info.get('height', 'not specified')}")
        print(f"  ViewBox: {info.get('viewbox', 'not specified')}")
        print(f"  XML Valid: {validation['structure'].get('xml_valid', False)}")
        
        # Structure analysis
        structure = validation["structure"]
        print(f"\n[STRUCTURE] Structure Analysis:")
        print(f"  Has <svg> tag: {structure.get('has_svg_tag', False)}")
        print(f"  Has closing tag: {structure.get('has_closing_tag', False)}")
        print(f"  Has viewBox: {structure.get('has_viewbox', False)}")
        print(f"  Has dimensions: {structure.get('has_dimensions', False)}")
        
        # Drawing elements
        elements = structure.get('drawing_elements', [])
        print(f"\n[RENDER] Drawing Elements Found: {len(elements)}")
        if elements:
            for element in elements:
                print(f"    - <{element}>")
        else:
            print("    No drawing elements found!")
        
        # Errors
        errors = validation["errors"]
        if errors:
            print(f"\n[ERROR] Errors ({len(errors)}):")
            for error in errors:
                print(f"    - {error}")
        
        # Warnings
        warnings = validation["warnings"]
        if warnings:
            print(f"\n[WARNING]  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"    - {warning}")
        
        if validation["valid"]:
            print(f"\n[OK] SVG appears to be valid and renderable!")
        else:
            print(f"\n[ERROR] SVG has issues that may prevent proper rendering.")
        
        print("="*60)


async def test_svg_generation_only():
    """Test just the SVG generation part of the workflow."""
    print("[TEST] Testing SVG Generation in Isolation")
    print("-" * 50)
    
    validator = SVGValidator()
    
    # Sample D2 diagram code that should work
    test_d2_code = """
direction: right

# Web Application Architecture

frontend: React Frontend {
  shape: rectangle
  style: {
    fill: "#e1f5fe"
    stroke: "#0277bd"
  }
}

backend: Node.js Backend {
  shape: rectangle
  style: {
    fill: "#e8f5e8"
    stroke: "#2e7d32"
  }
}

database: PostgreSQL {
  shape: cylinder
  style: {
    fill: "#fff3e0"
    stroke: "#ef6c00"
  }
}

auth: Auth Service {
  shape: rectangle
  style: {
    fill: "#fce4ec"
    stroke: "#c2185b"
  }
}

# Connections
frontend -> backend: API Calls
backend -> database: SQL Queries  
backend -> auth: Authentication
auth -> database: User Data
"""

    try:
        # Initialize service
        from app.services.diagram_factory_service import DiagramSession
        session = DiagramSession("test-session")
        service = DiagramFactoryService(session)
        print("[OK] Service initialized")
        
        # Set up a mock session with the test code
        service.session.diagram_code = test_d2_code.strip()
        print(f"[OK] Test D2 code set ({len(test_d2_code)} chars)")
        
        # Test rendering
        print("\n[RENDER] Attempting to render D2 diagram...")
        await service.render_diagram()
        
        if service.session.svg_output:
            print(f"[OK] SVG generated ({len(service.session.svg_output)} chars)")
            
            # Validate the SVG
            validation = validator.validate_svg_structure(service.session.svg_output)
            validator.print_validation_report(validation)
            
            # Save the SVG
            filename = validator.save_svg_file(service.session.svg_output, "test_d2_diagram.svg")
            
            if validation["valid"]:
                print(f"\n[SUCCESS] SUCCESS: Valid SVG generated and saved!")
                return True
            else:
                print(f"\n[WARNING]  SVG generated but has validation issues")
                return False
                
        else:
            print("[ERROR] No SVG output generated")
            return False
            
    except Exception as e:
        print(f"[ERROR] SVG generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_minimal_workflow():
    """Test a minimal workflow to ensure SVG generation works."""
    print("\n[TEST] Testing Minimal Workflow for SVG")
    print("-" * 50)
    
    validator = SVGValidator()
    
    try:
        # Initialize service
        from app.services.diagram_factory_service import DiagramSession
        session = DiagramSession("test-session")
        service = DiagramFactoryService(session)
        
        # Use a very simple, direct prompt
        simple_prompt = "Create a simple diagram showing a user connecting to a database through an API"
        
        print(f"[NOTE] Starting with simple prompt: {simple_prompt}")
        await service.start_generation(simple_prompt)
        
        # Give a very direct clarification
        await asyncio.sleep(3)
        clarification = "Show three boxes: User, API, Database. User connects to API, API connects to Database. Use D2 diagram format."
        
        print(f"[NOTE] Providing direct clarification...")
        await service.handle_clarification(clarification)
        
        # Request D2 specifically
        await asyncio.sleep(3)
        print(f"[NOTE] Selecting D2 diagram type...")
        await service.handle_clarification("Create a D2 diagram")
        
        # Wait for generation
        print(f"[WAIT] Waiting for generation...")
        max_wait = 60
        wait_time = 0
        
        while wait_time < max_wait:
            if service.session.diagram_code:
                print(f"[OK] Diagram code generated!")
                break
            await asyncio.sleep(3)
            wait_time += 3
            
        if service.session.diagram_code:
            print(f"[RENDER] Rendering SVG...")
            await service.render_diagram()
            
            if service.session.svg_output:
                validation = validator.validate_svg_structure(service.session.svg_output)
                validator.print_validation_report(validation)
                
                filename = validator.save_svg_file(service.session.svg_output, "minimal_test_diagram.svg")
                
                return validation["valid"]
            else:
                print("[ERROR] No SVG generated")
                return False
        else:
            print("[ERROR] No diagram code generated")
            return False
            
    except Exception as e:
        print(f"[ERROR] Minimal workflow test failed: {e}")
        return False


def test_existing_svg(filename: str):
    """Test validation of an existing SVG file."""
    print(f"\n[CHECK] Validating Existing SVG: {filename}")
    print("-" * 50)
    
    validator = SVGValidator()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        validation = validator.validate_svg_structure(svg_content)
        validator.print_validation_report(validation)
        
        return validation["valid"]
        
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filename}")
        return False
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return False


async def main():
    """Run SVG validation tests."""
    print("SVG Validation and Generation Tests")
    print("="*60)
    
    tests = []
    
    # Test 1: SVG generation in isolation
    print("\n1. Testing SVG Generation in Isolation")
    result1 = await test_svg_generation_only()
    tests.append(("SVG Generation", result1))
    
    # Test 2: Minimal workflow
    print("\n2. Testing Minimal Workflow")
    result2 = await test_minimal_workflow()
    tests.append(("Minimal Workflow", result2))
    
    # Test 3: Validate any existing SVG files
    existing_files = [f for f in os.listdir('.') if f.endswith('.svg')]
    if existing_files:
        print(f"\n3. Validating Existing SVG Files")
        for svg_file in existing_files:
            result = test_existing_svg(svg_file)
            tests.append((f"Existing: {svg_file}", result))
    
    # Summary
    print(f"\n[CHART] TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "[OK] PASSED" if result else "[ERROR] FAILED"
        print(f"{test_name}: {status}")
    
    overall = passed == total
    print(f"\nOverall: {passed}/{total} tests passed")
    print(f"Result: {'[OK] ALL PASSED' if overall else '[ERROR] SOME FAILED'}")
    
    if overall:
        print("\n[SUCCESS] SVG generation is working correctly!")
    else:
        print("\n[WARNING]  Some SVG issues detected. Check individual test results.")
    
    return overall


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)