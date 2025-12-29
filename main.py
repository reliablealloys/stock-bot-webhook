import os
import logging
from flask import Flask, request, jsonify
import requests
import re
import json
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs')
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Company information
COMPANY_INFO = {
    'name': 'Reliable Alloys',
    'address': 'Mumbai, India',
    'contact': 'sales@reliablealloys.in',
    'locations': ['PARTH', 'WADA', 'SRG', 'TALOJA', 'SHEETS', 'RELIABLE ALLOYS']
}

# Last updated dates for each location
LAST_UPDATED = {
    'PARTH': '25-12-2025',
    'WADA': '25-12-2025',
    'TALOJA': '20-12-2025',
    'SRG': 'Not specified',
    'SHEETS': '27-12-2025',
    'RELIABLE ALLOYS': '16-9-2025'
}

# Load inventory from JSON file
def load_inventory():
    """Load inventory from inventory.json file"""
    try:
        if not os.path.exists('inventory.json'):
            logger.error("inventory.json not found!")
            return {}
        
        with open('inventory.json', 'r') as f:
            data = json.load(f)
            logger.info(f"Loaded inventory with {len(data)} locations")
            return data
    except Exception as e:
        logger.error(f"Error loading inventory: {e}")
        return {}

INVENTORY = load_inventory()

# Store processed message IDs to prevent duplicates
processed_messages = {}

def is_message_processed(message_id):
    """Check if message was already processed"""
    current_time = datetime.now()
    
    # Clean up old entries (older than 5 minutes)
    to_remove = []
    for msg_id, timestamp in processed_messages.items():
        if current_time - timestamp > timedelta(minutes=5):
            to_remove.append(msg_id)
    
    for msg_id in to_remove:
        del processed_messages[msg_id]
    
    # Check if current message was processed
    if message_id in processed_messages:
        return True
    
    # Mark as processed
    processed_messages[message_id] = current_time
    return False

def search_inventory_flexible(query):
    """Flexible inventory search that extracts size, grade, shape from natural language"""
    if not INVENTORY:
        return []
    
    query_lower = query.lower()
    
    # Extract size
    size_match = re.search(r'(\d+\.?\d*)\s*mm', query_lower)
    size = size_match.group(1) if size_match else None
    
    # Extract grade
    grade_patterns = ['a106', '8620', 'en36c', 'en9', '1117', '321', 'duplex', '316ti', '316l', '316', '304l', '304', '303', '202']
    grade = None
    for pattern in grade_patterns:
        if pattern in query_lower:
            grade = pattern.upper()
            if grade == '304':
                grade = '304L'
            elif grade == '316':
                grade = '316L'
            break
    
    # Extract shape
    shape_match = re.search(r'(round|hex|square|patti|pipe|sheet)', query_lower, re.IGNORECASE)
    shape = shape_match.group(1) if shape_match else None
    
    # If no size, grade, or shape detected, return empty
    if not size and not grade and not shape:
        return []
    
    # Search inventory
    results = []
    try:
        for location, sizes in INVENTORY.items():
            if not isinstance(sizes, dict):
                continue
                
            for inv_size, grades in sizes.items():
                # Match size
                if size and str(inv_size) != str(size):
                    continue
                
                if not isinstance(grades, dict):
                    continue
                
                for inv_grade, items in grades.items():
                    # Match grade
                    if grade and inv_grade != grade:
                        continue
                    
                    if isinstance(items, dict):
                        items = [items]
                    
                    if not isinstance(items, list):
                        continue
                    
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        
                        # Match shape
                        if shape and shape.lower() not in item.get('shape', '').lower():
                            continue
                        
                        if item.get('weight', 0) > 0:
                            results.append({
                                'location': location,
                                'size': inv_size,
                                'grade': inv_grade,
                                'shape': item.get('shape', 'Unknown'),
                                'quality': item.get('quality', 'Unknown'),
                                'weight': item.get('weight', 0),
                                'last_updated': LAST_UPDATED.get(location, 'Unknown')
                            })
    except Exception as e:
        logger.error(f"Error searching inventory: {e}")
    
    return results

def format_stock_response(results):
    """Format stock results into a nice message"""
    if not results:
        return None
    
    response = f"✅ **Found {len(results)} item(s):**\\n\\n"
    for item in results[:5]:
        response += f"📍 **{item['location']}**: {item['size']}mm {item['grade']} {item['shape']} - {int(item['weight'])} kgs ({item['quality']})\\n"
        response += f"   _Last updated: {item['last_updated']}_\\n\\n"
    
    if len(results) > 5:
        response += f"_...and {len(results) - 5} more results_\\n"
    
    return response

def handle_message(text):
    """Handle regular messages"""
    text_lower = text.lower().strip()
    
    # Greetings
    if text_lower in ['hi', 'hello', 'hey', 'namaste']:
        return "👋 Hello! Welcome to **Reliable Alloys**!\\n\\nI can help you check stock availability.\\n\\n**Try:**\\n• *50mm 304L*\\n• *6mm 304L*\\n• *40mm EN36C*\\n\\nWhat are you looking for?"
    
    # Search inventory
    results = search_inventory_flexible(text)
    
    if results:
        return format_stock_response(results)
    else:
        return f"❌ No exact matches found for '{text}'.\\n\\nPlease contact us at **{COMPANY_INFO['contact']}** for assistance.\\n\\nTry searching with: *size + grade* (e.g., '50mm 304L')"

def send_message(chat_id, text):
    """Send message via Telegram API"""
    url = f'{TELEGRAM_API}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        logger.info(f"Sent message to {chat_id}: {response.status_code}")
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

def process_update(update):
    """Process incoming update"""
    try:
        logger.info(f"Processing update: {json.dumps(update)}")
        
        if 'message' in update:
            message = update['message']
            message_id = message['message_id']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            logger.info(f"Message {message_id} from {chat_id}: {text}")
            
            # Check if message was already processed
            if is_message_processed(message_id):
                logger.info(f"Message {message_id} already processed, skipping")
                return {'ok': True}
            
            # Handle commands
            if text.startswith('/start'):
                response = "🏭 **Welcome to Reliable Alloys!**\\n\\nI can help you check stock availability across all locations.\\n\\n**Our Locations:**\\n• PARTH • WADA • TALOJA\\n• SRG • SHEETS • RELIABLE ALLOYS\\n\\n**Try:**\\n• *50mm 304L*\\n• *6mm 304L*\\n• *40mm EN36C*\\n\\nWhat can I help you with?"
            elif text.startswith('/refresh'):
                global INVENTORY
                INVENTORY = load_inventory()
                response = f"✅ Inventory refreshed! Loaded {len(INVENTORY)} locations."
            else:
                response = handle_message(text)
            
            logger.info(f"Sending response: {response[:100]}...")
            send_message(chat_id, response)
        
        return {'ok': True}
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        return {'ok': False, 'error': str(e)}

# Webhook endpoint - catch all POST requests
@app.route('/', methods=['POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['POST'])
def webhook(path):
    """Handle incoming webhook updates - accepts any path"""
    try:
        logger.info(f"Webhook called with path: /{path}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        update = request.get_json()
        if not update:
            logger.error("No JSON data received")
            return jsonify({'ok': False, 'error': 'No data'}), 400
        
        result = process_update(update)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Health check endpoint"""
    return f'Stock Bot is running! 🚀<br>Inventory locations: {len(INVENTORY)}<br>Bot token configured: {BOT_TOKEN[:20]}...'

@app.route('/health', methods=['GET'])
def health():
    """Health check for Railway"""
    inventory_count = sum(len(sizes) for sizes in INVENTORY.values()) if INVENTORY else 0
    return jsonify({
        'status': 'healthy',
        'bot': 'stock-bot',
        'inventory_items': inventory_count,
        'locations': list(INVENTORY.keys()) if INVENTORY else [],
        'inventory_loaded': len(INVENTORY) > 0,
        'bot_token_set': bool(BOT_TOKEN)
    })

@app.route('/inventory', methods=['GET'])
def get_inventory():
    """API endpoint to get current inventory"""
    return jsonify(INVENTORY)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info("="*60)
    logger.info("STARTING STOCK BOT")
    logger.info("="*60)
    logger.info(f"Bot token: {BOT_TOKEN[:20]}...")
    logger.info(f"Inventory loaded: {len(INVENTORY)} locations")
    if INVENTORY:
        logger.info(f"Total items: {sum(len(sizes) for sizes in INVENTORY.values())}")
    else:
        logger.warning("No inventory loaded - check inventory.json file")
    logger.info(f"Starting server on port {port}")
    logger.info("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)
