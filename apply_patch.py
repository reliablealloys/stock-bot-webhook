#!/usr/bin/env python3
"""
Quick fix script to update 6mm 304L weights in WADA and SRG
Run this on Railway to fix the inventory immediately
"""

import json

print("🔧 Applying inventory patch...")

# Load current inventory
with open('inventory.json', 'r') as f:
    inventory = json.load(f)

# Update WADA 6mm 304L
if "WADA" in inventory:
    if "6" not in inventory["WADA"]:
        inventory["WADA"]["6"] = {}
    inventory["WADA"]["6"]["304L"] = [{"shape": "Round", "quality": "Export", "weight": 255}]
    print("✅ Updated WADA 6mm 304L Export: 255 kgs")

# Update SRG 6mm 304L  
if "SRG" in inventory:
    if "6" not in inventory["SRG"]:
        inventory["SRG"]["6"] = {}
    inventory["SRG"]["6"]["304L"] = [{"shape": "Round", "quality": "Export", "weight": 1434.4}]
    print("✅ Updated SRG 6mm 304L Export: 1434.4 kgs")

# Save
with open('inventory.json', 'w') as f:
    json.dump(inventory, f, indent=2)

print("\n🎉 Patch applied! Now searching '6mm 304L' will show:")
print("   📍 PARTH: 2975 kgs (Black Coil)")
print("   📍 WADA: 255 kgs (Export)")
print("   📍 SRG: 1434.4 kgs (Export)")
