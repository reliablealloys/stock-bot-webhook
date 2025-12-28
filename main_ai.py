import os
import logging
from flask import Flask, request, jsonify
import requests
import re
import json
import google.generativeai as genai

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
            # Match size if specified
            if size and inv_size != size:
                continue
            
            for inv_grade, items in grades.items():
                # Match grade if specified
                if grade and inv_grade != grade:
                    continue
                
                if isinstance(items, dict):
                    items = [items]
                
                for item in items:
                    if item['weight'] <= 0:
                        continue
                    
                    # Match shape if specified
                    if shape and shape.upper() not in item['shape'].upper():
                        continue
                    
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

def handle_message_with_ai(text, chat_id):
    """Handle messages using Gemini AI for intelligent responses"""
    
    # Get conversation history
    if chat_id not in user_context:
        user_context[chat_id] = {'history': []}
    
    # Search inventory based on query
    inventory_results = search_inventory_flexible(text)
    
    # Prepare context for AI
    system_prompt = f"""You are an intelligent assistant for Reliable Alloys, a steel and alloy supplier in Mumbai, India.

COMPANY INFO:
- Name: {COMPANY_INFO['name']}
- Contact: {COMPANY_INFO['contact']}
- Locations: {', '.join(COMPANY_INFO['locations'])}

YOUR ROLE:
- Help customers find materials in inventory
- Provide detailed, professional responses
- Explain material specifications when asked
- Be conversational and helpful
- Always include relevant stock information when available

RESPONSE STYLE:
- Use emojis appropriately (📍 for locations, ✅ for available, ❌ for unavailable, 📦 for quantities)
- Format with **bold** for emphasis
- Be concise but informative
- Include last updated dates for stock information
- Suggest alternatives if exact match not found

CURRENT QUERY: {text}

INVENTORY SEARCH RESULTS:
{json.dumps(inventory_results, indent=2) if inventory_results else "No exact matches found"}

FULL INVENTORY CONTEXT (for reference):
{json.dumps(get_inventory_summary(), indent=2)}

Respond to the customer's query naturally and helpfully. If they ask about stock, provide detailed information. If they ask general questions about materials, answer knowledgeably."""

    try:
        # Generate response using Gemini
        response = model.generate_content(system_prompt)
        ai_response = response.text
        
        # Store in conversation history
        user_context[chat_id]['history'].append({
            'user': text,
            'bot': ai_response
        })
        
        # Keep only last 5 exchanges
        if len(user_context[chat_id]['history']) > 5:
            user_context[chat_id]['history'] = user_context[chat_id]['history'][-5:]
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Error with Gemini API: {e}")
        # Fallback to basic response
        if inventory_results:
            response = f"✅ Found {len(inventory_results)} item(s):\n\n"
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
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
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
