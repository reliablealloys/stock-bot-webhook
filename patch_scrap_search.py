#!/usr/bin/env python3
"""
DIRECT PATCH - Add scrap search to main.py
"""

with open('main.py', 'r') as f:
    content = f.read()

# Check if already patched
if 'def search_scrap()' in content:
    print("✅ Already patched!")
    exit(0)

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
    response = "📦 **SCRAP INVENTORY**\\n\\n"
    for loc, items in by_location.items():
        loc_total = sum(i['weight'] for i in items)
        response += f"📍 **{loc}** ({loc_total:,.1f} kgs)\\n"
        for item in items:
            response += f"  • {item['type']} ({item['grade']}): {item['weight']:,.1f} kgs\\n"
        response += "\\n"
    response += f"**TOTAL: {total:,.1f} kgs**"
    return response

'''

# Insert before handle_message
insert_pos = content.find('def handle_message(text):')
if insert_pos == -1:
    print("❌ Could not find handle_message!")
    exit(1)

content = content[:insert_pos] + scrap_code + content[insert_pos:]

# Add scrap check in handle_message
old = "    # Search inventory"
new = '''    # Check for scrap
    if 'scrap' in text_lower:
        scrap_results = search_scrap()
        if scrap_results:
            return format_scrap_response(scrap_results)
    
    # Search inventory'''

content = content.replace(old, new)

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Patched main.py with scrap search!")
