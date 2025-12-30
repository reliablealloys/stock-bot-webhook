#!/usr/bin/env python3
"""
TEST: Verify 28.5mm hex 316L is in inventory
"""

import json

# Load inventory
with open('inventory.json', 'r') as f:
    inventory = json.load(f)

print("🔍 Checking for 28.5mm hex 316L...")

# Check PARTH
if 'PARTH' in inventory:
    print(f"✅ PARTH location exists")
    
    if '28.5' in inventory['PARTH']:
        print(f"✅ Size 28.5 exists in PARTH")
        
        if '316L' in inventory['PARTH']['28.5']:
            print(f"✅ Grade 316L exists in PARTH 28.5")
            
            items = inventory['PARTH']['28.5']['316L']
            print(f"✅ Found {len(items)} item(s):")
            for item in items:
                print(f"   - Shape: {item.get('shape')}, Quality: {item.get('quality')}, Weight: {item.get('weight')} kg")
                
                if 'hex' in item.get('shape', '').lower():
                    print(f"   ✅ HEX SHAPE CONFIRMED!")
        else:
            print(f"❌ Grade 316L NOT FOUND in PARTH 28.5")
            print(f"   Available grades: {list(inventory['PARTH']['28.5'].keys())}")
    else:
        print(f"❌ Size 28.5 NOT FOUND in PARTH")
        print(f"   Available sizes: {list(inventory['PARTH'].keys())}")
else:
    print(f"❌ PARTH location NOT FOUND")
    print(f"   Available locations: {list(inventory.keys())}")

print("\n" + "="*50)
print("FULL PARTH INVENTORY:")
print(json.dumps(inventory.get('PARTH', {}), indent=2))
