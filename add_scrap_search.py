#!/usr/bin/env python3
"""
AUTO-PATCH MAIN.PY WITH SCRAP SEARCH
=====================================

Run this in Railway: python3 add_scrap_search.py
"""

import re

def add_scrap_search():
    print("🔧 Patching main.py with scrap search...")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check if already patched
    if 'def search_scrap()' in content:
        print("✅ Already patched!")
        return
    
    # Find where to insert scrap functions (after search_inventory_flexible)
    scrap_functions = '''

def search_scrap():
    """Search for all scrap items across locations"""
    if not INVENTORY:
        return []
    
    results = []
    try:
        for location, items in INVENTORY.items():
            if not isinstance(items, dict):
                continue
            
            for item_name, grades in items.items():
                # Check if this is a scrap item
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
                                    'last_updated': LAST_UPDATED.get(location, 'Unknown')
                                })
    except Exception as e:
        logger.error(f"Error searching scrap: {e}")
    
    return results

def format_scrap_response(results):
    """Format scrap search results"""
    if not results:
        return "❌ No scrap found in inventory."
    
    # Group by location
    by_location = {}
    total_weight = 0
    
    for item in results:
        location = item['location']
        if location not in by_location:
            by_location[location] = []
        by_location[location].append(item)
        total_weight += item['weight']
    
    response = "📦 **SCRAP INVENTORY**\\\\n\\\\n"
    
    for location, items in by_location.items():
        location_total = sum(i['weight'] for i in items)
        response += f"📍 **{location}** ({location_total:,.1f} kgs)\\\\n"
        
        for item in items:
            response += f"  • {item['type']} ({item['grade']}): {item['weight']:,.1f} kgs\\\\n"
        
        response += "\\\\n"
    
    response += f"**TOTAL SCRAP: {total_weight:,.1f} kgs**\\\\n"
    response += f"\\\\nLast updated: {LAST_UPDATED.get('WADA', 'Unknown')}"
    
    return response
'''
    
    # Insert after format_stock_response function
    insert_pos = content.find('def handle_message(text):')
    if insert_pos == -1:
        print("❌ Could not find handle_message function!")
        return
    
    content = content[:insert_pos] + scrap_functions + '\n' + content[insert_pos:]
    
    # Now modify handle_message to check for scrap
    # Find the greetings check and add scrap check after it
    old_pattern = r"(# Greetings\s+if text_lower in \['hi'.*?\n.*?return.*?\n)"
    new_code = r"\1\n    # Check if query is for scrap\n    if 'scrap' in text_lower:\n        scrap_results = search_scrap()\n        if scrap_results:\n            return format_scrap_response(scrap_results)\n"
    
    content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
    
    # Write back
    with open('main.py', 'w') as f:
        f.write(content)
    
    print("✅ Patched main.py with scrap search!")
    print("🔄 Restart bot to enable scrap search")

if __name__ == '__main__':
    add_scrap_search()
