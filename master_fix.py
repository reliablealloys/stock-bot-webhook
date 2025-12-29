#!/usr/bin/env python3
"""
MASTER FIX - All inventory updates in one script
Runs faster than multiple sequential scripts
"""

import json

def master_fix():
    print("🚀 MASTER FIX - Loading all inventory updates...")
    
    with open('inventory.json', 'r') as f:
        data = json.load(f)
    
    # Ensure locations exist
    for loc in ['WADA', 'PARTH', 'SRG', 'TALOJA']:
        if loc not in data:
            data[loc] = {}
    
    fixes = 0
    
    # ===== SCRAP =====
    print("\n📦 Adding SCRAP...")
    data['WADA']['MIX HEX'] = {'SCRAP': [{'shape': 'SCRAP', 'quality': 'PICKLED', 'weight': 1350}]}
    data['WADA']['MUDIYA'] = {'SCRAP': [{'shape': 'SCRAP', 'quality': '316', 'weight': 176}]}
    data['WADA']['TURNING 304'] = {'SCRAP': [{'shape': 'SCRAP', 'quality': '304', 'weight': 14559}]}
    data['WADA']['TURNING 316'] = {'SCRAP': [{'shape': 'SCRAP', 'quality': '316', 'weight': 10158.5}]}
    data['SRG']['MS SCRAP'] = {'SCRAP': [{'shape': 'SCRAP', 'quality': 'MS FITTINGS', 'weight': 6640}]}
    data['TALOJA']['ENDCUT 316L'] = {'SCRAP': [{'shape': 'SCRAP', 'quality': '316L', 'weight': 958}]}
    data['TALOJA']['TURNING 316'] = {'SCRAP': [{'shape': 'SCRAP', 'quality': '316', 'weight': 67}]}
    data['TALOJA']['TURNING 304'] = {'SCRAP': [{'shape': 'SCRAP', 'quality': '304', 'weight': 3334}]}
    fixes += 8
    print("  ✅ Added 8 scrap items (37,242.5 kg total)")
    
    # ===== WADA 304L BLACK =====
    print("\n📦 Adding WADA 304L BLACK...")
    wada_304l_black = {
        '25': 3763, '26': 2555, '28.5': 1733, '30': 70, '32': 4460, '34': 1189,
        '36': 3330, '38': 1345, '40': 3612, '42': 167, '45': 725, '50': 2749,
        '56': 3030, '58': 3707, '60': 190, '70': 356, '73': 85, '83': 981,
        '95': 2670, '100': 3160, '110': 414, '115': 496, '125': 5542,
        '130': 627, '145': 1729, '150': 3613
    }
    for size, weight in wada_304l_black.items():
        if size not in data['WADA']:
            data['WADA'][size] = {}
        if '304L' not in data['WADA'][size]:
            data['WADA'][size]['304L'] = []
        data['WADA'][size]['304L'].append({'shape': 'Round', 'quality': 'Black', 'weight': weight})
        fixes += 1
    print(f"  ✅ Added {len(wada_304l_black)} items")
    
    # ===== WADA 304L EXPORT =====
    print("\n📦 Adding WADA 304L EXPORT...")
    wada_304l_export = {
        '5': 1011, '6': 255, '7.1': 1393, '7.13': 937, '7.65': 1113, '9.5': 39,
        '10': 1056, '10.76': 128, '12': 66.8, '12.7': 624, '13': 243, '13.1': 21,
        '14': 1127, '14.58': 141, '16': 374, '19': 95, '20.2': 54, '22': 1305,
        '22.2': 371, '23.85': 119, '24.1': 229, '25': 130, '25.4': 92, '28.1': 26,
        '30.3': 120, '30.4': 176, '31': 102, '35.1': 640, '36': 29, '42.2': 4280,
        '48': 168, '50': 125.2, '53': 99.9, '56': 635.9, '57': 642, '60': 735
    }
    for size, weight in wada_304l_export.items():
        if size not in data['WADA']:
            data['WADA'][size] = {}
        if '304L' not in data['WADA'][size]:
            data['WADA'][size]['304L'] = []
        data['WADA'][size]['304L'].append({'shape': 'Round', 'quality': 'Export', 'weight': weight})
        fixes += 1
    print(f"  ✅ Added {len(wada_304l_export)} items")
    
    # ===== PARTH 28.5mm HEX 316L =====
    print("\n📦 Adding PARTH 28.5mm HEX 316L...")
    if '28.5' not in data['PARTH']:
        data['PARTH']['28.5'] = {}
    if '316L' not in data['PARTH']['28.5']:
        data['PARTH']['28.5']['316L'] = []
    data['PARTH']['28.5']['316L'].append({'shape': 'Hex', 'quality': 'Black Ann', 'weight': 473})
    fixes += 1
    print("  ✅ Added 28.5mm hex 316L: 473 kg")
    
    # Save
    with open('inventory.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ MASTER FIX COMPLETE! Applied {fixes} fixes!")
    return fixes

if __name__ == '__main__':
    master_fix()
