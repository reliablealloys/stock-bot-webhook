import os
import logging
from flask import Flask, request, jsonify
import requests
import re
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs')
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Load inventory from JSON file
def load_inventory():
    """Load inventory from inventory.json file"""
    try:
        with open('inventory.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading inventory: {e}")
        return {}

INVENTORY = load_inventory()

def search_inventory(query):
    """Search inventory based on query"""
    query = query.lower()
    
    # Extract size and grade
    size_match = re.search(r'(\d+\.?\d*)\s*mm', query)
    grade_match = re.search(r'(202|303|304l?|316l?|316ti|duplex|321|1117)', query, re.IGNORECASE)
    shape_match = re.search(r'(round|hex|square|patti|pipe|sheet)', query, re.IGNORECASE)
    
    if not size_match:
        return "Please specify size (e.g., 19mm, 200mm, 6mm, 0.5mm for sheets)"
    
    size = size_match.group(1)
    grade = grade_match.group(1).upper() if grade_match else None
    shape = shape_match.group(1).upper() if shape_match else None
    
    if not grade:
        return f"Please specify grade (e.g., {size}mm 304L, {size}mm 316L, {size}mm 303, {size}mm 202)"
    
    # Normalize grade
    if grade == '304':
        grade = '304L'
    elif grade == '316':
        grade = '316L'
    
    # Search across locations
    results = []
    for location, sizes in INVENTORY.items():
        if size in sizes and grade in sizes[size]:
            items = sizes[size][grade]
            # Handle both single dict and array of dicts
            if isinstance(items, dict):
                items = [items]
            
            for item in items:
                # Skip negative weights
                if item['weight'] <= 0:
                    continue
                    
                # Match shape if specified
                if shape and shape not in item['shape'].upper():
                    continue
                
                results.append({
                    'location': location,
                    'size': size,
                    'grade': grade,
                    'shape': item['shape'],
                    'quality': item['quality'],
                    'weight': item['weight']
                })
    
    if not results:
        # Try to find similar items
        similar = []
        for location, sizes in INVENTORY.items():
            for s, grades in sizes.items():
                if grade in grades:
                    items = grades[grade]
                    if isinstance(items, dict):
                        items = [items]
                    for item in items:
                        if item['weight'] > 0:
                            similar.append(f"{s}mm {item['shape']}")
        
        if similar:
            similar_list = ', '.join(list(set(similar))[:5])
            return f"❌ Sorry, **{size}mm {grade}** is not available in stock.\n\n✅ Similar items available: {similar_list}\n\nContact us for more options!"
        else:
            return f"❌ Sorry, **{size}mm {grade}** is not available in stock.\n\nContact us for availability!"
    
    # Calculate total weight and group by location
    total_weight = sum(r['weight'] for r in results)
    locations = list(set(r['location'] for r in results))
    
    # Always use the same format (Example 2 style)
    response = f"✅ **{size}mm {grade}** available!\n\n"
    response += f"📦 **Total: {int(total_weight)} kgs** across {len(locations)} location(s)\n\n"
    response += "**Breakdown by location:**\n"
    
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
    
    response += f"\n💬 Which location works best for you?"
    return response

def send_message(chat_id, text):
    """Send message via Telegram API"""
    url = f'{TELEGRAM_API}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming webhook updates"""
    try:
        update = request.get_json()
        logger.info(f"Received update: {update}")
        
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text.startswith('/start'):
                response = "🏭 **Welcome to Reliable Alloys Stock Bot!**\n\nI check inventory across all locations:\n✓ PARTH\n✓ WADA\n✓ TALOJA\n✓ SRG\n✓ SHEETS\n\n**Example queries:**\n• 19mm 304L\n• 200mm round 316L\n• 6mm 303\n• 110mm 304L\n• 0.5mm 202 sheet\n\nI'll show you total stock and breakdown by location!"
            elif text.startswith('/refresh'):
                global INVENTORY
                INVENTORY = load_inventory()
                response = "✅ Inventory refreshed!"
            else:
                response = search_inventory(text)
            
            send_message(chat_id, response)
        
        return {'ok': True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {'ok': False, 'error': str(e)}

@app.route('/')
def index():
    """Health check endpoint"""
    return 'Stock Bot is running! 🚀'

@app.route('/health')
def health():
    """Health check for Railway"""
    inventory_count = sum(len(sizes) for sizes in INVENTORY.values())
    return jsonify({
        'status': 'healthy',
        'bot': 'stock-bot-webhook',
        'inventory_items': inventory_count,
        'locations': list(INVENTORY.keys())
    })

@app.route('/inventory')
def get_inventory():
    """API endpoint to get current inventory"""
    return jsonify(INVENTORY)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting bot with {sum(len(sizes) for sizes in INVENTORY.values())} inventory items")
    app.run(host='0.0.0.0', port=port)
