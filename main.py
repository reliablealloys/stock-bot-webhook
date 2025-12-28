import os
import logging
from flask import Flask, request, jsonify
import requests
import re
import json
import google.generativeai as genai
from datetime import datetime, timedelta

# Import inquiry handler
from inquiry_handler import (
    is_inquiry_request, 
    extract_date_from_message,
    check_authorization,
    fetch_inquiries_by_date,
    format_inquiry_response,
    get_all_authorized_numbers
)
from sheets_helper import fetch_sheet_data

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

# Inquiry sheet configuration
INQUIRY_SHEET_ID = '1lI9c24H2Jg6DOMAOcJuzYXuTLNjc1FIdOPs507oM5ts'

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

def get_user_phone(user_data):
    """Extract phone number from Telegram user data"""
    # Try to get phone from contact
    if 'contact' in user_data and 'phone_number' in user_data['contact']:
        return user_data['contact']['phone_number']
    
    # Try username (if it's a phone number)
    if 'username' in user_data:
        username = user_data['username']
        # Check if username looks like a phone number
        phone_match = re.search(r'\d{10,}', username)
        if phone_match:
            return phone_match.group(0)
    
    return None

def handle_inquiry_request(message_text, user_data):
    """Handle inquiry request from authorized users"""
    try:
        # Extract date from message
        target_date = extract_date_from_message(message_text)
        
        if not target_date:
            return "❌ Please specify a date. Example: 'inquiries 26/5/2025' or 'show inquiries for 28-5-2025'"
        
        # Fetch sheet data
        logger.info(f"Fetching inquiry data for date: {target_date}")
        sheets_data = fetch_sheet_data(INQUIRY_SHEET_ID)
        
        if not sheets_data:
            return "❌ Unable to fetch inquiry data. Please make sure the Google Sheet is publicly accessible."
        
        # Get all authorized numbers from sheet
        authorized_numbers = get_all_authorized_numbers(sheets_data)
        logger.info(f"Authorized numbers: {authorized_numbers}")
        
        # Get user's phone number
        user_phone = get_user_phone(user_data)
        logger.info(f"User phone: {user_phone}")
        
        # Check authorization
        if not check_authorization(user_phone, authorized_numbers):
            return "🔒 **Access Denied**\n\nYou are not authorized to view inquiry data. Please contact the administrator."
        
        # Fetch inquiries for the date
        inquiries = fetch_inquiries_by_date(sheets_data, target_date)
        
        # Format and return response
        return format_inquiry_response(inquiries, target_date)
        
    except Exception as e:
        logger.error(f"Error handling inquiry request: {e}")
        return f"❌ Error processing inquiry request: {str(e)}"

def search_inventory_flexible(query):
    """Flexible inventory search that extracts size, grade, shape from natural language"""
    query_lower = query.lower()
    
    # Extract size - support both "17.5mm" and "17.5 mm" formats
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
    
    # If no size, grade, or shape detected, return empty (not all items)
    if not size and not grade and not shape:
        return []
    
    # Search inventory
    results = []
    for location, sizes in INVENTORY.items():
        for inv_size, grades in sizes.items():
            # Match size - exact match
            if size and str(inv_size) != str(size):
                continue
            
            for inv_grade, items in grades.items():
                # Match grade - exact match
                if grade and inv_grade != grade:
                    continue
                
                if isinstance(items, dict):
                    items = [items]
                
                for item in items:
                    # Match shape - flexible match
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
        
        logger.info(f"Query: {user_message}, Found: {len(inventory_results)} results")
        
        # Create prompt
        if inventory_results:
            prompt = f"""You are an intelligent assistant for Reliable Alloys, a steel and alloy supplier in Mumbai, India.

Company Information:
- Name: {COMPANY_INFO['name']}
- Contact: {COMPANY_INFO['contact']}
- Locations: {', '.join(COMPANY_INFO['locations'])}

User Query: {user_message}

Inventory Search Results (Found {len(inventory_results)} items):
{json.dumps(inventory_results[:10], indent=2)}

Instructions:
1. Provide a clear, friendly response confirming availability
2. List the top 5 results with location, size, grade, shape, quantity, and quality
3. Mention the last updated date
4. Keep response concise and professional
5. Use emojis appropriately (✅, 📍, etc.)

Respond naturally:"""
        else:
            prompt = f"""You are an intelligent assistant for Reliable Alloys, a steel and alloy supplier in Mumbai, India.

Company Information:
- Name: {COMPANY_INFO['name']}
- Contact: {COMPANY_INFO['contact']}
- Locations: {', '.join(COMPANY_INFO['locations'])}

User Query: {user_message}

No inventory matches found for this query.

Instructions:
1. If it's a greeting (hi, hello, hey), respond warmly and ask how you can help
2. If it's a stock query, politely say you couldn't find exact matches
3. Suggest they contact {COMPANY_INFO['contact']} for assistance
4. Ask if they'd like to search for something else
5. Keep response friendly and helpful

Respond naturally:"""

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
            response = f"✅ **Found {len(inventory_results)} item(s):**\n\n"
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
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
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
            user_data = message.get('from', {})
            
            # Check if message was already processed
            if is_message_processed(message_id):
                logger.info(f"Message {message_id} already processed, skipping")
                return {'ok': True}
            
            # Check if it's an inquiry request
            if is_inquiry_request(text):
                logger.info(f"Inquiry request detected: {text}")
                response = handle_inquiry_request(text, user_data)
                send_message(chat_id, response)
                return {'ok': True}
            
            # Handle commands
            if text.startswith('/start'):
                response = "🏭 **Welcome to Reliable Alloys AI Assistant!**\n\nI'm an intelligent bot powered by AI. I can help you with:\n\n✅ Stock availability across all locations\n✅ Material specifications and details\n✅ General questions about alloys and steel\n✅ Recommendations and alternatives\n✅ Inquiry and quotation tracking (authorized users)\n\n**Our Locations:**\n• PARTH\n• WADA\n• TALOJA\n• SRG\n• SHEETS\n• RELIABLE ALLOYS\n\n**Try asking:**\n• *Do you have 50mm 304L?*\n• *What is A106 Grade B pipe?*\n• *Show inquiries for 26/5/2025* (authorized only)\n• *Tell me about EN36C material*\n\nWhat can I help you with?"
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
    return 'Stock Bot AI with Inquiry System is running! 🚀'

@app.route('/health')
def health():
    """Health check for Railway"""
    inventory_count = sum(len(sizes) for sizes in INVENTORY.values())
    return jsonify({
        'status': 'healthy',
        'bot': 'stock-bot-ai-inquiry',
        'inventory_items': inventory_count,
        'locations': list(INVENTORY.keys()),
        'ai_enabled': bool(GEMINI_API_KEY),
        'inquiry_system': True
    })

@app.route('/inventory')
def get_inventory():
    """API endpoint to get current inventory"""
    return jsonify(INVENTORY)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting AI bot with {sum(len(sizes) for sizes in INVENTORY.values())} inventory items")
    logger.info("Inquiry system enabled")
    app.run(host='0.0.0.0', port=port)
