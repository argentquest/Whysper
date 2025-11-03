#!/usr/bin/env python3
"""Manual test of C4 rendering with provider system"""

import requests
import json

# Simple C4 diagram code (PlantUML format)
c4_code = """
@startuml C1
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "User", "A user of the system")
System(web, "Web System", "The main web system")
System(db, "Database", "Data storage")

Rel(user, web, "Uses")
Rel(web, db, "Reads/Writes")

@enduml
"""

print("Testing C4 diagram rendering with MVP endpoint...")
print("=" * 60)

try:
    response = requests.post(
        "http://localhost:8003/api/v1/diagrams/generate",
        json={
            "prompt": "Create a simple C4 System Context diagram with a user, web system, and database",
            "diagram_type": "c4",
            "output_format": "svg"
        },
        timeout=30
    )

    print(f"Response Status: {response.status_code}")
    data = response.json()

    print(f"Success: {not data.get('error_info', {}).get('has_error', True)}")

    error_info = data.get('error_info', {})
    if error_info.get('has_error'):
        print(f"Error: {error_info.get('error_message', 'Unknown error')}")
    else:
        image_data = data.get('image_data', '')
        if image_data:
            print(f"SVG generated successfully ({len(image_data)} bytes)")
            if '<svg' in str(image_data)[:100]:
                print("✓ Valid SVG content")
            else:
                print("✗ Invalid SVG content")
        else:
            print("No image data in response")

    # Print the diagram code generated
    print(f"\nGenerated diagram code:")
    print(data.get('diagram_code', 'N/A'))

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
