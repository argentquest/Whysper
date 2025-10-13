#!/usr/bin/env python3
"""
Test script to validate C4 to D2 conversion issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mvp_diagram_generator.c4_to_d2 import convert_c4_to_d2

# Sample C4 code from test data
C4_SAMPLE = """
C4Context
Person(user, "User", "A user of the system")
System(app, "Application", "The main application")
Rel(user, app, "Uses")
"""

def test_current_implementation():
    """Test the current (broken) implementation"""
    print("=" * 60)
    print("Testing Current C4 to D2 Implementation")
    print("=" * 60)
    
    print("\nInput C4 Code:")
    print("-" * 40)
    print(C4_SAMPLE)
    
    print("\nConverted D2 Code:")
    print("-" * 40)
    result = convert_c4_to_d2(C4_SAMPLE)
    print(result)
    
    # Check if entities were converted
    has_person = "Person(" in result
    has_system = "System(" in result
    has_rel = "Rel(" in result
    
    print("\nAnalysis:")
    print("-" * 40)
    print(f"Person entity preserved: {has_person}")
    print(f"System entity preserved: {has_system}")
    print(f"Relationship preserved: {has_rel}")
    
    if has_person or has_system or has_rel:
        print("\n❌ ISSUE CONFIRMED: Entities are not being converted to D2 syntax")
        print("   The converter only changes C4 diagram declarations to comments")
    else:
        print("\n✅ Entities were converted (or removed)")
        
    return result

def compare_with_expected():
    """Show what the expected D2 output should look like"""
    print("\n" + "=" * 60)
    print("Expected D2 Output (from frontend implementation)")
    print("=" * 60)
    
    expected = """# C4 Context Diagram

direction: down

user: {
  label: "User"
  shape: person
}

app: {
  label: "Application"
  shape: rectangle
}

user -> app: "Uses"
"""
    print(expected)
    
    return expected

if __name__ == "__main__":
    actual = test_current_implementation()
    expected = compare_with_expected()
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("The backend C4 to D2 converter is incomplete.")
    print("It only converts diagram declarations to comments.")
    print("The frontend has a full implementation that should be ported.")