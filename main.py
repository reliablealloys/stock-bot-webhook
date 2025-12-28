import os
import logging
from flask import Flask, request, jsonify
import requests
import re
import json
import google.generativeai as genai
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs')
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

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
        with open('inventory.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading inventory: {e}")
        return {}

INVENTORY = load_inventory()

# Store conversation context per user
user_context = {}

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

def get_inventory_summary():
    """Get a summary of all inventory for AI context"""
    summary = []
    for location, sizes in INVENTORY.items():
        for size, grades in sizes.items():
            for grade, items in grades.items():
                if isinstance(items, dict):
                    items = [items]
                for item in items:
                    if item['weight'] > 0:
                        summary.append({
                            'location': location,
                            'size': size,
                            'grade': grade,
                            'shape': item['shape'],
                            'quality': item['quality'],
                            'weight': item['weight'],
                            'last_updated': LAST_UPDATED.get(location, 'Unknown')
                        })
    return summary

def search_inventory_flexible(query):
    """Flexible inventory search that extracts size, grade, shape from natural language"""
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
    
    # Search inventory
    results = []
    for location, sizes in INVENTORY.items():
        for inv_size, grades in sizes.items():
            # Match size
            if size and inv_size != size:
                continue
            
            for inv_grade, items in grades.items():
                # Match grade
                if grade and inv_grade != grade:
                    continue
                
                if isinstance(items, dict):
                    items = [items]
                
                for item in items:
                    # Match shape
                    if shape and shape.lower() not in item['shape'].lower():
                        continue
                    
                    if item['weight'] > 0:
                        results.append({
                            'location': location,
                            'size': inv_size,
                            'grade': inv_grade,
                            'shape': item['shape'],
                            'quality': item['quality'],
                            'weight': item['weight'],
                            'last_updated': LAST_UPDATED.get(location, 'Unknown')
                        })
    
    return results

def handle_message_with_ai(user_message, chat_id):
    """Handle message using Gemini AI"""
    try:
        # Initialize context for new users
        if chat_id not in user_context:
            user_context[chat_id] = {'history': []}
        
        # Search inventory first
        inventory_results = search_inventory_flexible(user_message)
        
        # Build context for AI
        inventory_summary = get_inventory_summary()
        
        # Create prompt
        prompt = f"""You are an intelligent assistant for Reliable Alloys, a steel and alloy supplier in Mumbai, India.

Company Information:
- Name: {COMPANY_INFO['name']}
- Contact: {COMPANY_INFO['contact']}
- Locations: {', '.join(COMPANY_INFO['locations'])}

User Query: {user_message}

Inventory Search Results:
{json.dumps(inventory_results, indent=2) if inventory_results else "No exact matches found"}

Instructions:
1. If inventory results are found, provide a clear, friendly response with:
   - Availability confirmation
   - Quantities and locations
   - Quality/finish details
   - Last updated date
2. If no results, suggest alternatives or ask for clarification
3. For general questions about materials, provide helpful information
4. Always be professional and helpful
5. Keep responses concise but informative

Respond naturally and professionally:"""

        # Get AI response
        response = model.generate_content(prompt)
        ai_response = response.text
        
        # Store in context
        user_context[chat_id]['history'].append({
            'user': user_message,
            'bot': ai_response
        })
        
        # Keep only last 5 exchanges
        if len(user_context[chat_id]['history']) > 5:
            user_context[chat_id]['history'] = user_context[chat_id]['history'][-5:]
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Error in AI handler: {e}")
        # Fallback to simple response
        if inventory_results:
            response = f"✅ **Found {len(inventory_results)} items:**\n\n"
            for item in inventory_results[:5]:
                response += f"📍 **{item['location']}**: {item['size']}mm {item['grade']} {item['shape']} - {int(item['weight'])} kgs ({item['quality']})\n"
            return response
        else:
            return f"I couldn't find exact matches. Please contact us at {COMPANY_INFO['contact']} for assistance."

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
            message_id = message['message_id']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # Check if message was already processed
            if is_message_processed(message_id):
                logger.info(f"Message {message_id} already processed, skipping")
                return {'ok': True}
            
            if text.startswith('/start'):
                response = "🏭 **Welcome to Reliable Alloys AI Assistant!**\n\nI'm an intelligent bot powered by AI. I can help you with:\n\n✅ Stock availability across all locations\n✅ Material specifications and details\n✅ General questions about alloys and steel\n✅ Recommendations and alternatives\n\n**Our Locations:**\n• PARTH\n• WADA\n• TALOJA\n• SRG\n• SHEETS\n• RELIABLE ALLOYS\n\n**Try asking:**\n• *Do you have 50mm 304L?*\n• *What is A106 Grade B pipe?*\n• *How much scrap is in stock?*\n• *Tell me about EN36C material*\n\nWhat can I help you with?"
            elif text.startswith('/refresh'):
                global INVENTORY
                INVENTORY = load_inventory()
                response = "✅ Inventory refreshed!"
            elif text.startswith('/clear'):
                if chat_id in user_context:
                    user_context[chat_id] = {'history': []}
                response = "✅ Conversation cleared!"
            else:
                response = handle_message_with_ai(text, chat_id)
            
            send_message(chat_id, response)
        
        return {'ok': True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {'ok': False, 'error': str(e)}

@app.route('/')
def index():
    """Health check endpoint"""
    return 'Stock Bot AI is running! 🚀'

@app.route('/health')
def health():
    """Health check for Railway"""
    inventory_count = sum(len(sizes) for sizes in INVENTORY.values())
    return jsonify({
        'status': 'healthy',
        'bot': 'stock-bot-ai',
        'inventory_items': inventory_count,
        'locations': list(INVENTORY.keys()),
        'ai_enabled': bool(GEMINI_API_KEY)
    })

@app.route('/inventory')
def get_inventory():
    """API endpoint to get current inventory"""
    return jsonify(INVENTORY)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting AI bot with {sum(len(sizes) for sizes in INVENTORY.values())} inventory items")
    app.run(host='0.0.0.0', port=port)
