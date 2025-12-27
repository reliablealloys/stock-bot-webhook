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
                        similar.append(f"{s}mm {item['shape']}")
        
        if similar:
            similar_list = ', '.join(list(set(similar))[:5])
            return f"Sorry, **{size}mm {grade}** is not available in stock.\n\nSimilar items available: {similar_list}\n\nPlease contact us for more options."
        else:
            return f"Sorry, **{size}mm {grade}** is not available in stock.\n\nPlease contact us for availability."
    
    # Format response
    if len(results) == 1:
        r = results[0]
        quality_text = f" in **{r['quality']}**" if r['quality'] else ""
        return f"✅ Yes, **{r['size']}mm {r['shape']} {r['grade']}** is available at **{r['location']}**{quality_text} - **{int(r['weight'])} kgs** in stock.\n\nHow many kgs do you need?"
    else:
        # Group by location
        response = f"✅ Yes, **{size}mm {grade}** is available at multiple locations:\n\n"
        for r in results:
            quality_text = f" ({r['quality']})" if r['quality'] else ""
            response += f"📍 **{r['location']}**: {int(r['weight'])} kgs - {r['shape']}{quality_text}\n"
        response += "\nWhich location do you prefer?"
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
                response = "Welcome to Reliable Alloys Stock Bot! 🏭\n\nI can check inventory across all our locations:\n• PARTH\n• WADA\n• TALOJA\n• SRG\n• SHEETS\n\nSend me a query like:\n• 19mm 304L\n• 200mm round 316L\n• 6mm 303\n• 110mm 304L\n• 0.5mm 202 sheet\n\nI'll check all locations instantly!"
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
