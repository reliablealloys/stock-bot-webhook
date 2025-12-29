"""
COMPREHENSIVE WEIGHT FIX
========================

This updates ALL known weights from the Google Sheets data.
Fixes hundreds of items across all locations INCLUDING SCRAP.

Run in Railway: python3 comprehensive_fix.py
"""

import json

def comprehensive_fix():
    print("🔧 Starting comprehensive weight fix...")
    
    with open('inventory.json', 'r') as f:
        data = json.load(f)
    
    fixes = 0
    
    # ===== ADD SCRAP ITEMS =====
    print("\n📦 Adding SCRAP items...")
    
    # WADA Scrap
    if 'WADA' not in data:
        data['WADA'] = {}
    
    wada_scrap = {
        'MIX HEX': {'SCRAP': [{'shape': 'SCRAP', 'quality': 'PICKLED', 'weight': 1350}]},
        'MUDIYA': {'SCRAP': [{'shape': 'SCRAP', 'quality': '316', 'weight': 176}]},
        'TURNING 304': {'SCRAP': [{'shape': 'SCRAP', 'quality': '304', 'weight': 14559}]},
        'TURNING 316': {'SCRAP': [{'shape': 'SCRAP', 'quality': '316', 'weight': 10158.5}]}
    }
    
    for item, details in wada_scrap.items():
        data['WADA'][item] = details
        weight = details['SCRAP'][0]['weight']
        print(f"  ✅ WADA {item}: {weight} kg")
        fixes += 1
    
    # SRG Scrap
    if 'SRG' not in data:
        data['SRG'] = {}
    
    data['SRG']['MS SCRAP'] = {'SCRAP': [{'shape': 'SCRAP', 'quality': 'MS FITTINGS', 'weight': 6640}]}
    print(f"  ✅ SRG MS SCRAP: 6640 kg")
    fixes += 1
    
    # TALOJA Scrap
    if 'TALOJA' not in data:
        data['TALOJA'] = {}
    
    taloja_scrap = {
        'ENDCUT 316L': {'SCRAP': [{'shape': 'SCRAP', 'quality': '316L', 'weight': 958}]},
        'TURNING 316': {'SCRAP': [{'shape': 'SCRAP', 'quality': '316', 'weight': 67}]},
        'TURNING 304': {'SCRAP': [{'shape': 'SCRAP', 'quality': '304', 'weight': 3334}]}
    }
    
    for item, details in taloja_scrap.items():
        data['TALOJA'][item] = details
        weight = details['SCRAP'][0]['weight']
        print(f"  ✅ TALOJA {item}: {weight} kg")
        fixes += 1
    
    # ===== SRG PIPES =====
    if 'SRG' in data:
        print("\n📦 Fixing SRG pipes...")
        srg_pipes = {
            '114x87': -466.5,
            '16x11.5': 46.7,
            '33.4x24.5': 38,
            '80x50': 46
        }
        for size, weight in srg_pipes.items():
            size_upper = size.upper()
            size_lower = size.lower()
            for s in [size, size_upper, size_lower]:
                if s in data['SRG'] and '304L' in data['SRG'][s]:
                    data['SRG'][s]['304L'][0]['weight'] = weight
                    print(f"  ✅ {s} pipe: {weight} kg")
                    fixes += 1
                    break
    
    # ===== WADA 304L ROUNDS =====
    if 'WADA' in data:
        print("\n📦 Fixing WADA 304L rounds...")
        wada_304l = {
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
            '22.2': 371
        }
        for size, weight in wada_304l.items():
            if size in data['WADA'] and '304L' in data['WADA'][size]:
                for item in data['WADA'][size]['304L']:
                    if item['shape'] == 'Round' and item['quality'] == 'Export':
                        item['weight'] = weight
                        print(f"  ✅ {size}mm 304L: {weight} kg")
                        fixes += 1
                        break
    
    # ===== PARTH - Update from your notes =====
    if 'PARTH' in data:
        print("\n📦 Fixing PARTH inventory...")
        
        # 303 Rounds
        parth_303 = {
            '7': 6000,
            '8': 2697,
            '8.2': 197,
            '9': 1995,
            '10': 1795,
            '11': 2572,
            '15': 4008,
            '17.5': 2557,
            '21': 1359,
            '22.2': 29,
            '26': 3263,
            '27': 313,
            '32': 1933,
            '33': 201
        }
        for size, weight in parth_303.items():
            if size in data['PARTH'] and '303' in data['PARTH'][size]:
                for item in data['PARTH'][size]['303']:
                    if item['weight'] == 0:
                        item['weight'] = weight
                        print(f"  ✅ {size}mm 303: {weight} kg")
                        fixes += 1
                        break
        
        # 304L Rounds
        parth_304l = {
            '6': 2975,
            '8': 1062,
            '9': 690,
            '10': 303,
            '12': 2230,
            '14': 487,
            '16': 1148,
            '16.4': 1790,
            '17.5': 443,
            '18.3': 326,
            '19': 3906,
            '20': 3288,
            '23': 554,
            '27': 186,
            '30': 90
        }
        for size, weight in parth_304l.items():
            if size in data['PARTH'] and '304L' in data['PARTH'][size]:
                for item in data['PARTH'][size]['304L']:
                    if item['shape'] == 'Round' and item['weight'] == 0:
                        item['weight'] = weight
                        print(f"  ✅ {size}mm 304L: {weight} kg")
                        fixes += 1
                        break
        
        # 316L Rounds
        parth_316l = {
            '6': 1157,
            '7': 2171,
            '9': 1199,
            '10': 2497,
            '11': 2386,
            '14': 2227,
            '16': 198,
            '16.4': 331,
            '17': 1031,
            '19': 3094,
            '20.2': 120,
            '23': 445,
            '24': 1225
        }
        for size, weight in parth_316l.items():
            if size in data['PARTH'] and '316L' in data['PARTH'][size]:
                for item in data['PARTH'][size]['316L']:
                    if item['shape'] == 'Round' and item['weight'] == 0:
                        item['weight'] = weight
                        print(f"  ✅ {size}mm 316L: {weight} kg")
                        fixes += 1
                        break
        
        # 316L Hex
        parth_316l_hex = {
            '15.88': 2027,
            '18': 3146,
            '18.5': 408,
            '20.5': 1719,
            '23.5': 902,
            '25': 90,
            '27': 1576,
            '28.5': 473,
            '34': 415,
            '38': 308
        }
        for size, weight in parth_316l_hex.items():
            if size in data['PARTH'] and '316L' in data['PARTH'][size]:
                for item in data['PARTH'][size]['316L']:
                    if item['shape'] == 'Hex' and item['weight'] == 0:
                        item['weight'] = weight
                        print(f"  ✅ {size}mm 316L Hex: {weight} kg")
                        fixes += 1
                        break
        
        # 304L Hex
        parth_304l_hex = {
            '20.5': 568,
            '23.5': 1024
        }
        for size, weight in parth_304l_hex.items():
            if size in data['PARTH'] and '304L' in data['PARTH'][size]:
                for item in data['PARTH'][size]['304L']:
                    if item['shape'] == 'Hex' and item['weight'] == 0:
                        item['weight'] = weight
                        print(f"  ✅ {size}mm 304L Hex: {weight} kg")
                        fixes += 1
                        break
        
        # Duplex
        parth_duplex = {
            '18': 6373,
            '20': 36
        }
        for size, weight in parth_duplex.items():
            if size in data['PARTH'] and 'DUPLEX' in data['PARTH'][size]:
                for item in data['PARTH'][size]['DUPLEX']:
                    if item['weight'] == 0:
                        item['weight'] = weight
                        print(f"  ✅ {size}mm Duplex: {weight} kg")
                        fixes += 1
                        break
    
    # Save
    with open('inventory.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ COMPLETE! Fixed {fixes} items!")
    print("🔄 Restart bot to load changes")
    
    # Calculate total scrap
    total_scrap = 1350 + 176 + 14559 + 10158.5 + 6640 + 958 + 67 + 3334
    print(f"\n📊 TOTAL SCRAP: {total_scrap} kg")
    
    return fixes

if __name__ == '__main__':
    comprehensive_fix()
