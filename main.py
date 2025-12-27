import os
import logging
from flask import Flask, request
import requests
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs')
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Inventory data - simplified version
INVENTORY = {
    'PARTH': {
        '19': {'304L': {'shape': 'Round', 'quality': 'Black Coil', 'weight': 3906}},
        '6': {'316L': {'shape': 'Round', 'quality': 'Black Coil', 'weight': 1157}},
        '9': {'316L': {'shape': 'Round', 'quality': 'Black Coil', 'weight': 1199}},
    },
    'WADA': {
        '100': {'304L': {'shape': 'Round', 'quality': 'Black', 'weight': 3160}},
        '110': {'304L': {'shape': 'Round', 'quality': 'Black', 'weight': 414}},
        '150': {'304L': {'shape': 'Round', 'quality': 'Black', 'weight': 3613}},
    },
    'TALOJA': {
        '100': {'304L': {'shape': 'Round', 'quality': 'Black', 'weight': 1201}},
        '110': {'304L': {'shape': 'Round', 'quality': 'Black', 'weight': 4435}},
        '200': {'316L': {'shape': 'Round', 'quality': 'Black', 'weight': 1312}},
    }
}

def search_inventory(query):
    """Search inventory based on query"""
    query = query.lower()
    
    # Extract size and grade
    size_match = re.search(r'(\d+\.?\d*)\s*mm', query)
    grade_match = re.search(r'(303|304l?|316l?|316ti|duplex|321)', query, re.IGNORECASE)
    
    if not size_match:
        return "Please specify size (e.g., 19mm, 200mm, 6mm)"
    
    size = size_match.group(1)
    grade = grade_match.group(1).upper() if grade_match else None
    
    if not grade:
        return f"Please specify grade (e.g., {size}mm 304L, {size}mm 316L)"
    
    # Normalize grade
    if grade == '304':
        grade = '304L'
    elif grade == '316':
        grade = '316L'
    
    # Search across locations
    results = []
    for location, sizes in INVENTORY.items():
        if size in sizes and grade in sizes[size]:
            item = sizes[size][grade]
            results.append({
                'location': location,
                'size': size,
                'grade': grade,
                'shape': item['shape'],
                'quality': item['quality'],
                'weight': item['weight']
            })
    
    if not results:
        return f"Sorry, **{size}mm {grade}** is not available in stock.\n\nPlease check our inventory or contact us for alternatives."
    
    # Format response
    if len(results) == 1:
        r = results[0]
        return f"Yes, **{r['size']}mm {r['shape']} {r['grade']}** is available at **{r['location']}** in **{r['quality']}** - **{r['weight']} kgs** in stock.\n\nHow many kgs do you need?"
    else:
        response = f"Yes, **{size}mm {grade}** is available at multiple locations:\n\n"
        for r in results:
            response += f"**{r['location']}**: {r['weight']} kgs ({r['quality']})\n"
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
                response = "Welcome to Reliable Alloys Stock Bot! 🏭\n\nSend me a query like:\n• 19mm 304L\n• 200mm round 316L\n• 6mm 316L\n\nI'll check all our locations instantly!"
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
    return {'status': 'healthy', 'bot': 'stock-bot-webhook'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
