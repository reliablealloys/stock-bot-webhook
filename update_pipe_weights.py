#!/usr/bin/env python3
"""
Update SRG pipe weights in inventory.json
"""
import json

# Read current inventory
with open('inventory.json', 'r') as f:
    inventory = json.load(f)

# Update SRG pipe weights
if 'SRG' in inventory:
    # Update 114x87 pipe (negative weight means it's a credit/return)
    if '114x87' in inventory['SRG']:
        inventory['SRG']['114x87']['304L'][0]['weight'] = -466.5
    
    # Update 16x11.5 pipe
    if '16x11.5' in inventory['SRG']:
        inventory['SRG']['16x11.5']['304L'][0]['weight'] = 46.7
    
    # Update 33.4x24.5 pipe
    if '33.4x24.5' in inventory['SRG']:
        inventory['SRG']['33.4x24.5']['304L'][0]['weight'] = 38
    
    # Update 80x50 pipe
    if '80x50' in inventory['SRG']:
        inventory['SRG']['80x50']['304L'][0]['weight'] = 46

# Write updated inventory
with open('inventory.json', 'w') as f:
    json.dump(inventory, f, indent=2)

print("✅ Updated SRG pipe weights successfully!")
print("Updated pipes:")
print("  - 114x87mm 304L Pipe: -466.5 kg (credit)")
print("  - 16x11.5mm 304L Pipe: 46.7 kg")
print("  - 33.4x24.5mm 304L Pipe: 38 kg")
print("  - 80x50mm 304L Pipe: 46 kg")
