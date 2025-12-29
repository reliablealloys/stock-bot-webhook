#!/usr/bin/env python3
"""
ONE-CLICK FIX - RUN THIS MANUALLY IN RAILWAY TERMINAL
======================================================

This single script does EVERYTHING:
1. Generates complete inventory with scrap
2. Adds planning stock
3. Patches main.py with scrap search
4. Ready to use!

Run in Railway terminal: python3 one_click_fix.py
Then restart the bot
"""

import json
import re

print("🚀 ONE-CLICK FIX STARTING...")
print("=" * 50)

# STEP 1: Generate complete inventory
print("\n📦 STEP 1: Generating inventory with scrap...")

inventory = {
    "WADA": {
        # Scrap
        "MIX HEX": {"SCRAP": [{"shape": "SCRAP", "quality": "PICKLED", "weight": 1350}]},
        "MUDIYA": {"SCRAP": [{"shape": "SCRAP", "quality": "316", "weight": 176}]},
        "TURNING 304": {"SCRAP": [{"shape": "SCRAP", "quality": "304", "weight": 14559}]},
        "TURNING 316": {"SCRAP": [{"shape": "SCRAP", "quality": "316", "weight": 10158.5}]},
        
        # 304L Rounds
        "8": {"304L": [{"shape": "Round", "quality": "Export", "weight": -176}]},
        "9.5": {"304L": [{"shape": "Round", "quality": "Export", "weight": 39}]},
    },
    
    "SRG": {
        "MS SCRAP": {"SCRAP": [{"shape": "SCRAP", "quality": "MS FITTINGS", "weight": 6640}]},
        "16x11.5": {"304L": [{"shape": "Pipe", "quality": "Export", "weight": 46.7}]},
    },
    
    "TALOJA": {
        "ENDCUT 316L": {"SCRAP": [{"shape": "SCRAP", "quality": "316L", "weight": 958}]},
        "TURNING 316": {"SCRAP": [{"shape": "SCRAP", "quality": "316", "weight": 67}]},
        "TURNING 304": {"SCRAP": [{"shape": "SCRAP", "quality": "304", "weight": 3334}]},
    },
    
    "PARTH": {
        "7": {"303": [{"shape": "Round", "quality": "Black Coil Ann", "weight": 6000}]},
        "14": {"304L": [{"shape": "Round", "quality": "Black Coil", "weight": 487}]},
    },
    
    "PARTH PLANNING": {
        # Planning stock
        "14": {"304L": [{"shape": "Round", "quality": "PLANNING", "weight": 10692}]},
        "28.5": {"316L": [{"shape": "Hex", "quality": "PLANNING", "weight": 10}]},
    }
}

with open('inventory.json', 'w') as f:
    json.dump(inventory, f, indent=2)

print("✅ Inventory created with scrap + planning")

# STEP 2: Patch main.py with scrap search
print("\n🔧 STEP 2: Patching main.py with scrap search...")

try:
    with open('main.py', 'r') as f:
        content = f.read()
    
    if 'def search_scrap()' in content:
        print("✅ Already patched!")
    else:
        # Add scrap functions before handle_message
        scrap_code = '''

def search_scrap():
    """Search for all scrap items"""
    if not INVENTORY:
        return []
    results = []
    try:
        for location, items in INVENTORY.items():
            if not isinstance(items, dict):
                continue
            for item_name, grades in items.items():
                if 'scrap' in item_name.lower() or (isinstance(grades, dict) and 'SCRAP' in grades):
                    if isinstance(grades, dict) and 'SCRAP' in grades:
                        scrap_items = grades['SCRAP']
                        if isinstance(scrap_items, dict):
                            scrap_items = [scrap_items]
                        for scrap in scrap_items:
                            if isinstance(scrap, dict):
                                results.append({
                                    'location': location,
                                    'type': item_name,
                                    'grade': scrap.get('quality', 'Unknown'),
                                    'weight': scrap.get('weight', 0),
                                })
    except Exception as e:
        logger.error(f"Error: {e}")
    return results

def format_scrap_response(results):
    """Format scrap results"""
    if not results:
        return "❌ No scrap found"
    by_location = {}
    total = 0
    for item in results:
        loc = item['location']
        if loc not in by_location:
            by_location[loc] = []
        by_location[loc].append(item)
        total += item['weight']
    response = "📦 **SCRAP INVENTORY**\\\\n\\\\n"
    for loc, items in by_location.items():
        loc_total = sum(i['weight'] for i in items)
        response += f"📍 **{loc}** ({loc_total:,.1f} kgs)\\\\n"
        for item in items:
            response += f"  • {item['type']} ({item['grade']}): {item['weight']:,.1f} kgs\\\\n"
        response += "\\\\n"
    response += f"**TOTAL: {total:,.1f} kgs**"
    return response

'''
        
        # Insert before handle_message
        insert_pos = content.find('def handle_message(text):')
        if insert_pos != -1:
            content = content[:insert_pos] + scrap_code + content[insert_pos:]
            
            # Add scrap check in handle_message
            old = "# Search inventory"
            new = '''# Check for scrap
    if 'scrap' in text_lower:
        scrap_results = search_scrap()
        if scrap_results:
            return format_scrap_response(scrap_results)
    
    # Search inventory'''
            content = content.replace(old, new)
            
            with open('main.py', 'w') as f:
                f.write(content)
            
            print("✅ Patched main.py!")
        else:
            print("⚠️ Could not find handle_message")
            
except Exception as e:
    print(f"⚠️ Error patching: {e}")

print("\n" + "=" * 50)
print("✅ ONE-CLICK FIX COMPLETE!")
print("\n📊 What's included:")
print("  • Scrap: 37,242.5 kg (WADA, SRG, TALOJA)")
print("  • Planning: PARTH PLANNING location")
print("  • Fixed weights: 8mm, 9.5mm, pipes, etc.")
print("\n🔄 NOW RESTART THE BOT!")
print("=" * 50)
