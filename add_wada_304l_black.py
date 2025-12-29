#!/usr/bin/env python3
"""
Add WADA 304L BLACK bars
"""

import json

def add_wada_304l_black():
    print("🔧 Adding WADA 304L BLACK bars...")
    
    with open('inventory.json', 'r') as f:
        data = json.load(f)
    
    if 'WADA' not in data:
        data['WADA'] = {}
    
    # WADA 304L Black from sheet
    wada_304l_black = {
        '25': 3763,
        '26': 2555,
        '28.5': 1733,
        '30': 70,
        '32': 4460,
        '34': 1189,
        '36': 3330,
        '38': 1345,
        '40': 3612,
        '42': 167,
        '45': 725,
        '50': 2749,
        '56': 3030,
        '58': 3707,
        '60': 190,
        '70': 356,
        '73': 85,
        '83': 981,
        '95': 2670,
        '100': 3160,
        '110': 414,
        '115': 496,
        '125': 5542,
        '130': 627,
        '145': 1729,
        '150': 3613
    }
    
    count = 0
    for size, weight in wada_304l_black.items():
        if size not in data['WADA']:
            data['WADA'][size] = {}
        
        if '304L' not in data['WADA'][size]:
            data['WADA'][size]['304L'] = []
        
        # Check if already exists
        exists = False
        for item in data['WADA'][size]['304L']:
            if item.get('quality') == 'Black':
                item['weight'] = weight
                exists = True
                break
        
        if not exists:
            data['WADA'][size]['304L'].append({
                'shape': 'Round',
                'quality': 'Black',
                'weight': weight
            })
        
        count += 1
        print(f"  ✅ {size}mm 304L Black: {weight} kg")
    
    with open('inventory.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Added {count} WADA 304L BLACK items!")

if __name__ == '__main__':
    add_wada_304l_black()
