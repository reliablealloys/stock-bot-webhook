#!/usr/bin/env python3
"""
EMERGENCY FIX - Add 28.5mm hex 316L immediately
"""

import json

with open('inventory.json', 'r') as f:
    data = json.load(f)

if 'PARTH' not in data:
    data['PARTH'] = {}

# Add 28.5mm hex 316L
data['PARTH']['28.5'] = {
    '316L': [
        {'shape': 'Hex', 'quality': 'Black Ann', 'weight': 473}
    ]
}

with open('inventory.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Added 28.5mm hex 316L: 473 kg (PARTH)")
