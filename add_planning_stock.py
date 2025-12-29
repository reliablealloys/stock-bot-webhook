#!/usr/bin/env python3
"""
ADD PLANNING STOCK TO INVENTORY
================================

This adds PARTH planning stock as a separate searchable location.
Users can search "planning" to see all planning stock.

Run: python3 add_planning_stock.py
"""

import json

def add_planning_stock():
    print("🔧 Adding PARTH planning stock...")
    
    with open('inventory.json', 'r') as f:
        data = json.load(f)
    
    # Add PARTH PLANNING as a new location
    data['PARTH PLANNING'] = {
        # 303 Rounds Planning
        '5.5': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 455}]},
        '7': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1198}]},
        '9': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1500}]},
        '10': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 2500}]},
        '11': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 500}]},
        '16.3': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 701}]},
        '16.4': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 106}]},
        '17.5': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 887}]},
        '19': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 900}]},
        '21': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1500}]},
        '27': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 325}]},
        '75': {'303': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 60}]},
        
        # 304L Rounds Planning
        '5.5': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 259}]},
        '7': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': -710}]},
        '7.1': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 653}]},
        '9': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 2155}]},
        '11': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 7635}]},  # 873 + 6762
        '13': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1480}]},
        '14': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 10692}]},  # 10280 + 412
        '15': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': -195}]},
        '18': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 622}]},
        '19': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1322}]},
        '20': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 2967}]},
        '21': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': -798}]},  # -219 + -579
        '23': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1010}]},
        '24': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 585}]},
        '25': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 2223}]},
        '26': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 5065}]},
        '27': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 995}]},
        '30': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 4311}]},
        '32': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': -93}]},
        '34': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 757}]},
        '45': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 4798}]},
        '50': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 99}]},
        '83': {'304L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1559}]},
        
        # 316L Rounds Planning
        '14': {'316L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1201}]},
        '16.4': {'316L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 994}]},
        '17.5': {'316L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1086}]},
        '23': {'316L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1232}]},  # 492 + 740
        '24': {'316L': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 327}]},  # 300 + 27
        
        # 316L Hex Planning
        '15.88': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': -165}]},
        '15.9': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': -740}]},
        '16': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': 3292}]},
        '18': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': -2015}]},
        '18.5': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': -747}]},
        '19': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': -35}]},
        '20.5': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': -225}]},
        '23.5': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': -802}]},
        '27': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': 398}]},
        '28.5': {'316L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': 10}]},
        
        # 304L Hex Planning
        '16': {'304L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': 2608}]},
        '19': {'304L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': 1291}]},  # 84 + 1207
        '27': {'304L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': 70}]},
        '34': {'304L': [{'shape': 'Hex', 'quality': 'PLANNING', 'weight': 135}]},
        
        # Duplex Rounds Planning
        '17': {'DUPLEX': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 5364}]},
        '17.5': {'DUPLEX': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1048}]},
        '18.3': {'DUPLEX': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 1563}]},
        '19': {'DUPLEX': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 6912}]},
        '21': {'DUPLEX': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 3744}]},
        '22': {'DUPLEX': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 10512}]},
        '23': {'DUPLEX': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 2132}]},  # 472 + 1660
        '24': {'DUPLEX': [{'shape': 'Round', 'quality': 'PLANNING', 'weight': 4115}]},
        
        # 316L Square Planning
        '34': {'316L': [{'shape': 'Square', 'quality': 'PLANNING', 'weight': 813}]}
    }
    
    # Save
    with open('inventory.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Added PARTH PLANNING stock!")
    print("\n📊 Planning Stock Summary:")
    print("  • 303 Rounds: 12 sizes")
    print("  • 304L Rounds: 23 sizes")
    print("  • 316L Rounds: 5 sizes")
    print("  • 316L Hex: 10 sizes")
    print("  • 304L Hex: 4 sizes")
    print("  • Duplex Rounds: 8 sizes")
    print("  • 316L Square: 1 size")
    print("\n🔍 Search 'planning' or specific sizes to see planning stock")

if __name__ == '__main__':
    add_planning_stock()
