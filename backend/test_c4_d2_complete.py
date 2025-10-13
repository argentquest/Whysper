#!/usr/bin/env python3
"""
Comprehensive test for C4 to D2 conversion
Tests the complete implementation with various C4 patterns
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvp_diagram_generator.c4_to_d2 import convert_c4_to_d2, looks_like_c4, extract_c4_level

def test_basic_conversion():
    """Test basic C4 to D2 conversion"""
    print("=" * 60)
    print("Test 1: Basic C4 to D2 Conversion")
    print("=" * 60)
    
    c4_input = """C4Context
Person(user, "User", "A user of the system")
System(app, "Application", "The main application")
Rel(user, app, "Uses")
"""
    
    print("Input C4:")
    print("-" * 40)
    print(c4_input)
    
    result = convert_c4_to_d2(c4_input)
    
    print("\nOutput D2:")
    print("-" * 40)
    print(result)
    
    # Validate key elements
    assert "direction: down" in result
    assert "user: {" in result
    assert "shape: person" in result
    assert "app: {" in result
    assert "shape: rectangle" in result
    assert "user -> app: \"Uses\"" in result
    
    print("\n✅ Test 1 PASSED: Basic conversion works correctly")
    return True

def test_container_boundaries():
    """Test C4 with container boundaries"""
    print("\n" + "=" * 60)
    print("Test 2: Container Boundaries")
    print("=" * 60)
    
    c4_input = """C4Container
System_Boundary(web, "Web Application") {
    Container(webapp, "Web App", "Spring Boot application")
    ContainerDb(database, "Database", "PostgreSQL")
}
Rel(webapp, database, "Reads from")
"""
    
    print("Input C4:")
    print("-" * 40)
    print(c4_input)
    
    result = convert_c4_to_d2(c4_input)
    
    print("\nOutput D2:")
    print("-" * 40)
    print(result)
    
    # Validate boundary handling
    assert "web: {" in result
    assert "label: \"Web Application\"" in result
    assert "webapp: {" in result
    assert "database: {" in result
    assert "web.webapp -> web.database: \"Reads from\"" in result
    
    print("\n✅ Test 2 PASSED: Container boundaries work correctly")
    return True

def test_technology_styling():
    """Test technology information and styling"""
    print("\n" + "=" * 60)
    print("Test 3: Technology and Styling")
    print("=" * 60)
    
    c4_input = """C4Component
ComponentDb(db, "Database", "Stores data", "PostgreSQL")
Container(app, "Application", "Main app", "Spring Boot")
Rel(app, db, "Queries", "JDBC")
"""
    
    print("Input C4:")
    print("-" * 40)
    print(c4_input)
    
    result = convert_c4_to_d2(c4_input)
    
    print("\nOutput D2:")
    print("-" * 40)
    print(result)
    
    # Validate technology handling
    assert "tooltip: \"Stores data\\n[PostgreSQL]\"" in result
    assert "tooltip: \"Main app\\n[Spring Boot]\"" in result
    assert "app -> db: \"Queries\\n[JDBC]\"" in result
    
    print("\n✅ Test 3 PASSED: Technology and styling work correctly")
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 60)
    print("Test 4: Edge Cases")
    print("=" * 60)
    
    # Test empty input
    result = convert_c4_to_d2("")
    assert result == ""
    print("✅ Empty input handled correctly")
    
    # Test None input
    result = convert_c4_to_d2(None)
    assert result == ""
    print("✅ None input handled correctly")
    
    # Test invalid input type
    result = convert_c4_to_d2(123)
    assert result == ""
    print("✅ Invalid input type handled correctly")
    
    # Test C4 detection
    assert looks_like_c4("Person(user, \"User\")")
    assert looks_like_c4("System(app, \"App\")")
    assert looks_like_c4("Rel(a, b, \"uses\")")
    assert not looks_like_c4("flowchart TD\nA-->B")
    print("✅ C4 detection works correctly")
    
    # Test C4 level extraction
    assert extract_c4_level("C4Context") == "Context"
    assert extract_c4_level("C4Container") == "Container"
    assert extract_c4_level("C4Component") == "Component"
    assert extract_c4_level("Random text") == "Unknown"
    print("✅ C4 level extraction works correctly")
    
    print("\n✅ Test 4 PASSED: Edge cases handled correctly")
    return True

def test_complex_diagram():
    """Test a complex C4 diagram with multiple elements"""
    print("\n" + "=" * 60)
    print("Test 5: Complex Diagram")
    print("=" * 60)
    
    c4_input = """title Payment System Architecture

C4Context
Person(customer, "Customer", "Makes payments")
Person_Ext(bank, "Bank", "External bank system")

System_Boundary(payment_system, "Payment System") {
    Container(api, "API Gateway", "REST API", "Spring Boot")
    ContainerDb(db, "Database", "Transaction storage", "PostgreSQL")
    Container(queue, "Message Queue", "Async processing", "RabbitMQ")
}

System_Ext(external, "External Service", "Third-party payment")

Rel(customer, api, "Submits payment", "HTTPS")
Rel(api, db, "Stores transaction", "JDBC")
Rel(api, queue, "Sends message", "AMQP")
Rel(queue, external, "Processes payment", "HTTP")
Rel(external, bank, "Charges card", "HTTPS")
"""
    
    print("Input C4:")
    print("-" * 40)
    print(c4_input)
    
    result = convert_c4_to_d2(c4_input)
    
    print("\nOutput D2:")
    print("-" * 40)
    print(result)
    
    # Validate complex elements
    assert "# Payment System Architecture" in result
    assert "customer: {" in result
    assert "shape: person" in result
    assert "bank: {" in result
    assert "payment_system: {" in result
    assert "api: {" in result
    assert "db: {" in result
    assert "queue: {" in result
    assert "external: {" in result
    assert "customer -> payment_system.api: \"Submits payment\\n[HTTPS]\"" in result
    assert "payment_system.api -> payment_system.db: \"Stores transaction\\n[JDBC]\"" in result
    
    print("\n✅ Test 5 PASSED: Complex diagram conversion works correctly")
    return True

def main():
    """Run all tests"""
    print("🧪 Running C4 to D2 Conversion Tests")
    print("=" * 60)
    
    tests = [
        test_basic_conversion,
        test_container_boundaries,
        test_technology_styling,
        test_edge_cases,
        test_complex_diagram
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! C4 to D2 conversion is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())