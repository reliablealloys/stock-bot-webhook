#!/usr/bin/env python3
"""
Add WADA 304L EXPORT (Bright) bars - COMPLETE LIST
"""

import json

def add_wada_304l_export():
    print("🔧 Adding WADA 304L EXPORT (Bright) bars...")
    
    with open('inventory.json', 'r') as f:
        data = json.load(f)
    
    if 'WADA' not in data:
        data['WADA'] = {}
    
    # WADA 304L Export from sheet (rows 75-113)
    wada_304l_export = {
        '5': 1011,
        '6': 255,
        '7.1': 1393,
        '7.13': 937,
        '7.65': 1113,
        '8': -176,
        '9.5': 39,
        '10': 1056,
        '10.76': 128,
        '12': 66.8,
        '12.7': 624,
        '13': 243,
        '13.1': 21,
        '14': 1127,
        '14.58': 141,
        '16': 374,
        '18': -153,
        '19': 95,
        '20.2': 54,
        '20.35': -151,
        '22': 1305,
        '22.2': 371,
        '23.85': 119,
        '24.1': 229,
        '25': 130,
        '25.4': 92,
        '28.1': 26,
        '30': -1620,
        '30.3': 120,
        '30.4': 176,
        '31': 102,
        '35.1': 640,
        '36': 29,
        '42.2': 4280,
        '48': 168,
        '50': 125.2,
        '53': 99.9,
        '56': 635.9,
        '57': 642,
        '60': 735
    }
    
    count = 0
    for size, weight in wada_304l_export.items():
        # Skip negative weights
        if weight < 0:
            continue
            
        if size not in data['WADA']:
            data['WADA'][size] = {}
        
        if '304L' not in data['WADA'][size]:
            data['WADA'][size]['304L'] = []
        
        # Check if Export quality already exists
        exists = False
        for item in data['WADA'][size]['304L']:
            if item.get('quality') == 'Export':
                item['weight'] = weight
                exists = True
                break
        
        if not exists:
            data['WADA'][size]['304L'].append({
                'shape': 'Round',
                'quality': 'Export',
                'weight': weight
            })
        
        count += 1
        print(f"  ✅ {size}mm 304L Export: {weight} kg")
    
    with open('inventory.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Added {count} WADA 304L EXPORT items!")

if __name__ == '__main__':
    add_wada_304l_export()
