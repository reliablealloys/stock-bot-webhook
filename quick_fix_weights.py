"""
QUICK FIX - Update known zero-weight items
===========================================

This fixes the most common search queries by updating weights
from the Google Sheet data we know is correct.

Run in Railway: python3 quick_fix_weights.py
"""

import json

def quick_fix():
    print("🔧 Quick fix starting...")
    
    with open('inventory.json', 'r') as f:
        data = json.load(f)
    
    fixes = 0
    
    # Fix SRG pipes
    if 'SRG' in data:
        srg_pipes = {
            '114x87': -466.5,
            '16x11.5': 46.7,
            '33.4x24.5': 38,
            '80x50': 46
        }
        for size, weight in srg_pipes.items():
            if size in data['SRG'] and '304L' in data['SRG'][size]:
                data['SRG'][size]['304L'][0]['weight'] = weight
                print(f"✅ SRG {size} pipe: {weight} kg")
                fixes += 1
    
    # Fix WADA 304L rounds (from actual Google Sheet)
    if 'WADA' in data:
        wada_304l = {
            '5': 1011,
            '6': 255,
            '7.1': 1393,
            '7.13': 937,
            '7.65': 1113,
            '8': -176,  # negative = credit/return
            '9.5': 39,
            '10': 1056,
            '10.76': 128,
            '12': 66.8,
            '12.7': 624,
            '13': 243,
            '13.1': 21
        }
        for size, weight in wada_304l.items():
            if size in data['WADA'] and '304L' in data['WADA'][size]:
                for item in data['WADA'][size]['304L']:
                    if item['shape'] == 'Round' and item['quality'] == 'Export':
                        item['weight'] = weight
                        print(f"✅ WADA {size}mm 304L: {weight} kg")
                        fixes += 1
                        break
    
    # Save
    with open('inventory.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Fixed {fixes} items!")
    print("🔄 Restart bot to load changes")

if __name__ == '__main__':
    quick_fix()
