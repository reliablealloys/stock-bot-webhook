"""
Gemini-powered Stock Bot for Bhindi Scheduler
This version works with your existing 5-minute schedule automation
No deployment needed - runs directly in Bhindi
"""

import json
import re

# This will be populated by Bhindi from your inventory note
INVENTORY = {}

# Company info
COMPANY_INFO = {
    'name': 'Reliable Alloys',
    'contact': 'sales@reliablealloys.in',
    'locations': ['PARTH', 'WADA', 'SRG', 'TALOJA', 'SHEETS', 'RELIABLE ALLOYS']
}

def search_inventory(size, grade, shape=None):
    """Search inventory based on size, grade, and optional shape"""
    size = str(size).strip()
    grade = grade.upper().strip()
    
    # Auto-correct
    if grade == '304':
        grade = '304L'
    elif grade == '316':
        grade = '316L'
    
    results = []
    for location, sizes in INVENTORY.items():
        if size in sizes and grade in sizes[size]:
            items = sizes[size][grade]
            if isinstance(items, dict):
                items = [items]
            
            for item in items:
                if item['weight'] <= 0:
                    continue
                if shape and shape.upper() not in item['shape'].upper():
                    continue
                
                results.append({
                    'location': location,
                    'size': size,
                    'grade': grade,
                    'shape': item['shape'],
                    'quality': item['quality'],
                    'weight': item['weight']
                })
    
    return results

def format_results(results, size, grade):
    """Format search results"""
    if not results:
        return None
    
    total_weight = sum(r['weight'] for r in results)
    locations = list(set(r['location'] for r in results))
    
    response = f"✅ **{size}mm {grade}** available!\n\n"
    response += f"📦 **Total: {int(total_weight)} kgs** across {len(locations)} location(s)\n\n"
    
    # Group by location
    location_data = {}
    for r in results:
        if r['location'] not in location_data:
            location_data[r['location']] = []
        location_data[r['location']].append(r)
    
    for location, items in location_data.items():
        location_total = sum(item['weight'] for item in items)
        response += f"\n📍 **{location}**: {int(location_total)} kgs\n"
        for item in items:
            quality_text = f" - {item['quality']}" if item['quality'] else ""
            response += f"   • {item['shape']}: {int(item['weight'])} kgs{quality_text}\n"
    
    return response

def handle_message(user_message, inventory_data):
    """
    Main handler for customer messages
    Uses Gemini-like intelligence through pattern matching and context
    """
    global INVENTORY
    INVENTORY = inventory_data
    
    text = user_message.lower().strip()
    
    # Greetings
    if any(word in text for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return "Hello! 👋 Welcome to Reliable Alloys!\n\nI'm here to help you check stock availability. What material are you looking for?\n\n**Example:** *110mm 304L* or *50mm EN36C*"
    
    # Contact queries
    if any(word in text for word in ['address', 'location', 'contact', 'email', 'phone']):
        return f"📍 **{COMPANY_INFO['name']}**\n\n📧 Email: {COMPANY_INFO['contact']}\n\nWe have multiple locations:\n" + "\n".join([f"• {loc}" for loc in COMPANY_INFO['locations']]) + "\n\nWhat material can I help you find?"
    
    # Delivery queries
    if any(word in text for word in ['deliver', 'delivery', 'shipping']):
        return "🚚 **Yes, we deliver across India!**\n\nDelivery depends on:\n• Your location\n• Quantity needed\n• Material type\n\nWhat material are you looking for? I'll check availability first!"
    
    # Price queries
    if any(word in text for word in ['price', 'cost', 'rate', 'how much']):
        return f"💰 **Pricing varies based on:**\n• Material grade & quantity\n• Current market rates\n• Delivery location\n\nPlease tell me what you need (e.g., *110mm 304L*) and I'll check stock. For pricing, contact: {COMPANY_INFO['contact']}"
    
    # Thank you
    if any(word in text for word in ['thank', 'thanks']):
        return "You're welcome! 😊\n\nNeed anything else? I'm here to help!"
    
    # Extract size and grade for stock queries
    size_match = re.search(r'(\d+\.?\d*)\s*mm', text)
    grade_match = re.search(r'(202|303|304l?|316l?|316ti|duplex|321|1117|en9|en36c|8620|a106)', text, re.IGNORECASE)
    shape_match = re.search(r'(round|hex|square|patti|pipe|sheet)', text, re.IGNORECASE)
    
    if not size_match:
        return "I'd love to help! Could you tell me the **size** and **grade** you need?\n\n**Example:** *110mm 304L* or *50mm EN36C*"
    
    size = size_match.group(1)
    
    if not grade_match:
        return f"What **grade** do you need for {size}mm?\n\n**Example:** *{size}mm 304L* or *{size}mm 316L*"
    
    grade = grade_match.group(1).upper()
    shape = shape_match.group(1) if shape_match else None
    
    # Normalize grade
    if grade == '304':
        grade = '304L'
    elif grade == '316':
        grade = '316L'
    
    # Search inventory
    results = search_inventory(size, grade, shape)
    
    if results:
        response = format_results(results, size, grade)
        response += "\n\n💬 How many kgs do you need? Which location works for you?"
        return response
    else:
        return f"❌ We don't have **{size}mm {grade}** in stock right now.\n\n📧 Contact us for availability: {COMPANY_INFO['contact']}\n\nWould you like to check a different size or grade?"

# Example usage for Bhindi scheduler:
# response = handle_message(customer_message, inventory_from_note)
