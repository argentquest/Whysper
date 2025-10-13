#!/usr/bin/env python3
"""
Diagnostic script to identify C4 diagram rendering issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvp_diagram_generator.c4_to_d2 import convert_c4_to_d2

def test_boundary_relationships():
    """Test boundary relationship handling"""
    print("=" * 60)
    print("DIAGNOSTIC: Boundary Relationship Handling")
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
    
    print("\nRelationship Analysis:")
    print("-" * 40)
    for line in result.split('\n'):
        if '->' in line:
            print(f"  {line.strip()}")
    
    # Check if relationships are properly qualified
    has_qualified = "web.webapp -> web.database" in result
    has_flat = "webapp -> database" in result
    
    print(f"\nQualified relationships (web.webapp -> web.database): {has_qualified}")
    print(f"Flat relationships (webapp -> database): {has_flat}")
    
    return has_qualified, has_flat

def test_none_input():
    """Test None input handling"""
    print("\n" + "=" * 60)
    print("DIAGNOSTIC: None Input Handling")
    print("=" * 60)
    
    try:
        result = convert_c4_to_d2(None)
        print(f"Result: '{result}'")
        print("✅ None input handled gracefully")
        return True
    except Exception as e:
        print(f"❌ Error with None input: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_complex_relationships():
    """Test complex diagram relationships"""
    print("\n" + "=" * 60)
    print("DIAGNOSTIC: Complex Relationship Handling")
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
    
    print("Analyzing relationships in complex diagram...")
    result = convert_c4_to_d2(c4_input)
    
    print("\nRelationship Analysis:")
    print("-" * 40)
    
    relationships = []
    for line in result.split('\n'):
        if '->' in line and line.strip():
            relationships.append(line.strip())
            print(f"  {line.strip()}")
    
    # Check specific expected relationships
    expected = [
        ("customer -> api", any("customer ->" in r and "api" in r for r in relationships)),
        ("api -> db", any("api ->" in r and "db" in r for r in relationships)),
        ("api -> queue", any("api ->" in r and "queue" in r for r in relationships)),
        ("queue -> external", any("queue ->" in r and "external" in r for r in relationships)),
        ("external -> bank", any("external ->" in r and "bank" in r for r in relationships)),
    ]
    
    print(f"\nExpected Relationships Found:")
    print("-" * 40)
    all_found = True
    for name, found in expected:
        status = "✅" if found else "❌"
        print(f"  {status} {name}")
        if not found:
            all_found = False
    
    return all_found, relationships

def main():
    """Run all diagnostics"""
    print("🔍 C4 DIAGRAM RENDERING DIAGNOSTICS")
    print("=" * 60)
    
    # Test 1: Boundary relationships
    qualified, flat = test_boundary_relationships()
    
    # Test 2: None input
    none_handled = test_none_input()
    
    # Test 3: Complex relationships
    complex_ok, relationships = test_complex_relationships()
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    issues = []
    
    if not qualified and flat:
        issues.append("❌ Boundary relationships are not properly qualified (missing container prefix)")
    elif qualified and not flat:
        print("✅ Boundary relationships are properly qualified")
    elif qualified and flat:
        print("⚠️ Mixed relationship formats found")
    
    if not none_handled:
        issues.append("❌ None input not handled gracefully (crashes)")
    else:
        print("✅ None input handled gracefully")
    
    if not complex_ok:
        issues.append("❌ Complex diagram relationships not handled correctly")
    else:
        print("✅ Complex diagram relationships handled correctly")
    
    if issues:
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n🎉 No issues found!")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)