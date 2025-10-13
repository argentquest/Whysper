#!/usr/bin/env python3
"""
Test different C4 boundary relationship patterns to understand expected behavior
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvp_diagram_generator.c4_to_d2 import convert_c4_to_d2

def test_relationship_inside_boundary():
    """Test relationship defined INSIDE boundary"""
    print("=" * 60)
    print("TEST: Relationship INSIDE Boundary")
    print("=" * 60)
    
    c4_input = """C4Container
System_Boundary(web, "Web Application") {
    Container(webapp, "Web App", "Spring Boot application")
    ContainerDb(database, "Database", "PostgreSQL")
    Rel(webapp, database, "Reads from")
}
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
    
    return result

def test_relationship_outside_boundary():
    """Test relationship defined OUTSIDE boundary (current failing test)"""
    print("\n" + "=" * 60)
    print("TEST: Relationship OUTSIDE Boundary")
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
    
    return result

def test_qualified_relationship_outside():
    """Test fully qualified relationship outside boundary"""
    print("\n" + "=" * 60)
    print("TEST: Qualified Relationship OUTSIDE Boundary")
    print("=" * 60)
    
    c4_input = """C4Container
System_Boundary(web, "Web Application") {
    Container(webapp, "Web App", "Spring Boot application")
    ContainerDb(database, "Database", "PostgreSQL")
}
Rel(web.webapp, web.database, "Reads from")
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
    
    return result

def main():
    """Run all boundary relationship tests"""
    print("🔍 BOUNDARY RELATIONSHIP BEHAVIOR ANALYSIS")
    print("=" * 60)
    
    # Test 1: Relationship inside boundary
    inside_result = test_relationship_inside_boundary()
    
    # Test 2: Relationship outside boundary (current issue)
    outside_result = test_relationship_outside_boundary()
    
    # Test 3: Qualified relationship outside boundary
    qualified_result = test_qualified_relationship_outside()
    
    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    
    print("1. Relationship INSIDE boundary:")
    if "web.webapp -> web.database" in inside_result:
        print("   ✅ Properly qualified with container prefix")
    else:
        print("   ❌ Not properly qualified")
    
    print("\n2. Relationship OUTSIDE boundary (unqualified):")
    if "webapp -> database" in outside_result:
        print("   ❌ Not qualified (this is the current issue)")
    else:
        print("   ✅ Unexpected behavior")
    
    print("\n3. Relationship OUTSIDE boundary (pre-qualified):")
    if "web.webapp -> web.database" in qualified_result:
        print("   ✅ Preserves qualification")
    else:
        print("   ❌ Doesn't preserve qualification")
    
    print("\nCONCLUSION:")
    print("-" * 40)
    print("The issue occurs when relationships are defined outside")
    print("boundaries but reference entities inside boundaries.")
    print("The converter should automatically qualify these relationships.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())