#!/usr/bin/env python3
"""
ADD WADA BRIGHT BARS
====================

Adds all bright bar stock from WADA sheet
"""

import json

def add_bright_bars():
    print("🔧 Adding WADA bright bars...")
    
    with open('inventory.json', 'r') as f:
        data = json.load(f)
    
    if 'WADA' not in data:
        data['WADA'] = {}
    
    # 303 Rounds Bright
    bright_303 = {
        '5.1': {'303': [{'shape': 'Round', 'quality': 'DB', 'weight': 478}]},
        '6': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 22}]},
        '6.1': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 1040}]},
        '6.2': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 2078}]},
        '7.12': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 256}]},
        '8.2': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': -535}]},
        '10': {'303': [{'shape': 'Round', 'quality': 'CG', 'weight': 432}, {'shape': 'Round', 'quality': 'Export', 'weight': 93}]},
        '10.15': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 316}]},
        '11.8': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 2124}]},
        '12.7': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 317}]},
        '15': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 1023}]},
        '16': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 252}]},
        '17.2': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 242}]},
        '17.5': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 58}]},
        '19': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 198}]},
        '20': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 353}]},
        '24': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 759}]},
        '25.1': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 386}]},
        '33': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 164}]},
        '41': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 589}]},
        '57': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 721}]},
        '70': {'303': [{'shape': 'Round', 'quality': 'Export', 'weight': 2450}]}
    }
    
    # 316L Rounds Bright
    bright_316l = {
        '5.35': {'316L': [{'shape': 'Round', 'quality': 'Export Coil', 'weight': 300}]},
        '6.75': {'316L': [{'shape': 'Round', 'quality': 'Export Coil', 'weight': 288}]},
        '8': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 1005}]},
        '8.1': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 880}]},
        '10': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 964}]},
        '13': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 113}]},
        '17.35': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 82}]},
        '18': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 465}]},
        '18.2': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 361}]},
        '22.2': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 116}]},
        '22.4': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 219}]},
        '24': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 545}]},
        '29.7': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 465}]},
        '32': {'316L': [{'shape': 'Round', 'quality': 'Export', 'weight': 375}]}
    }
    
    # 304L Hex Bright
    bright_304l_hex = {
        '12.7': {'304L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 739}]},
        '14.3': {'304L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 238}]},
        '16': {'304L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 1826}]},
        '19': {'304L': [{'shape': 'Hex', 'quality': 'Export', 'weight': -154}]},
        '22.2': {'304L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 308}]},
        '24': {'304L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 120}, {'shape': 'Hex', 'quality': 'ALU', 'weight': 288}]}
    }
    
    # 316L Hex Bright
    bright_316l_hex = {
        '9.5': {'316L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 308}]},
        '14': {'316L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 1443}]},
        '19': {'316L': [{'shape': 'Hex', 'quality': 'Export NACE', 'weight': 321}]},
        '22': {'316L': [{'shape': 'Hex', 'quality': 'Export NACE', 'weight': 74}]},
        '22.2': {'316L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 679}]},
        '25.4': {'316L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 54}]},
        '46': {'316L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 138}]},
        '55': {'316L': [{'shape': 'Hex', 'quality': 'Export', 'weight': 634}]}
    }
    
    # 316L Square Bright
    bright_316l_square = {
        '6.1': {'316L': [{'shape': 'Square', 'quality': 'Export', 'weight': 78}]},
        '32': {'316L': [{'shape': 'Square', 'quality': 'Export', 'weight': 870}]}
    }
    
    # Patti
    patti = {
        '12.7x6.35': {'304L': [{'shape': 'Patti', 'quality': 'Export', 'weight': 72}]},
        '13x6': {'304L': [{'shape': 'Patti', 'quality': 'Export', 'weight': 792}]},
        '20x15': {'303': [{'shape': 'Patti', 'quality': 'Export', 'weight': 1195}]},
        '75x35': {'316L': [{'shape': 'Patti', 'quality': 'Export', 'weight': 1248}]}
    }
    
    # Duplex Bright
    duplex_bright = {
        '16': {'DUPLEX': [{'shape': 'Round', 'quality': 'Export', 'weight': -392}]},
        '17.5': {'DUPLEX': [{'shape': 'Round', 'quality': 'Export', 'weight': 1073}]},
        '20': {'DUPLEX': [{'shape': 'Round', 'quality': 'Export', 'weight': -882}]},
        '22': {'DUPLEX': [{'shape': 'Round', 'quality': 'Export', 'weight': 345}]},
        '24': {'DUPLEX': [{'shape': 'Round', 'quality': 'Black Coil Ann', 'weight': 80}]}
    }
    
    # Merge all bright bars
    count = 0
    for items in [bright_303, bright_316l, bright_304l_hex, bright_316l_hex, bright_316l_square, patti, duplex_bright]:
        for size, details in items.items():
            # Check if size already exists
            if size in data['WADA']:
                # Merge grades
                for grade, items_list in details.items():
                    if grade in data['WADA'][size]:
                        data['WADA'][size][grade].extend(items_list)
                    else:
                        data['WADA'][size][grade] = items_list
            else:
                data['WADA'][size] = details
            count += 1
    
    with open('inventory.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Added {count} bright bar items to WADA!")
    print("  • 303 Rounds: 22 sizes")
    print("  • 316L Rounds: 14 sizes")
    print("  • 304L Hex: 6 sizes")
    print("  • 316L Hex: 8 sizes")
    print("  • 316L Square: 2 sizes")
    print("  • Patti: 4 sizes")
    print("  • Duplex: 5 sizes")

if __name__ == '__main__':
    add_bright_bars()
