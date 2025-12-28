import os
import logging
from flask import Flask, request, jsonify
import requests
import re
import json
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs')
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Inquiry system configuration
INQUIRY_SHEET_ID = '1lI9c24H2Jg6DOMAOcJuzYXuTLNjc1FIdOPs507oM5ts'
INQUIRY_SHEET_NAME = 'DEMO LINKS'
AUTHORIZED_NUMBERS = ['9831935522']  # Add more authorized numbers here

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

def get_google_sheets_client():
    """Initialize Google Sheets client"""
    try:
        # Get credentials from environment variable
        creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        if not creds_json:
            logger.error("GOOGLE_SHEETS_CREDENTIALS not found")
            return None
        
        creds_dict = json.loads(creds_json)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Error initializing Google Sheets: {e}")
        return None

def is_authorized(phone_number):
    """Check if phone number is authorized"""
    # Remove any formatting from phone number
    clean_number = re.sub(r'[^\d]', '', str(phone_number))
    
    for auth_number in AUTHORIZED_NUMBERS:
        clean_auth = re.sub(r'[^\d]', '', str(auth_number))
        if clean_number.endswith(clean_auth) or clean_auth.endswith(clean_number):
            return True
    return False

def parse_date(date_str):
    """Parse date from various formats"""
    # Try different date formats
    formats = ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%d/%m/%Y')
        except:
            continue
    
    return None

def fetch_inquiries(date_str, phone_number):
    """Fetch inquiries for a specific date"""
    try:
        # Check authorization
        if not is_authorized(phone_number):
            return "🚫 **Access Denied**\\n\\nYou are not authorized to view inquiries."
        
        # Parse date
        target_date = parse_date(date_str)
        if not target_date:
            return f"❌ Invalid date format. Please use: DD/MM/YYYY or DD-MM-YYYY"
        
        # Get Google Sheets client
        client = get_google_sheets_client()
        if not client:
            return "❌ Unable to connect to inquiry system. Please try again later."
        
        # Open sheet
        sheet = client.open_by_key(INQUIRY_SHEET_ID).worksheet(INQUIRY_SHEET_NAME)
        all_data = sheet.get_all_values()
        
        # Find inquiries for the date
        inquiries = []
        for row in all_data[1:]:  # Skip header
            if len(row) >= 5 and row[0] == target_date:
                inquiries.append({
                    'company': row[3] if len(row) > 3 else 'N/A',
                    'inquiry_link': row[4] if len(row) > 4 else 'N/A',
                    'quotation': row[5] if len(row) > 5 else 'N/A'
                })
        
        if not inquiries:
            return f"📭 No inquiries found for **{target_date}**"
        
        # Format response
        response = f"📋 **Inquiries for {target_date}**\\n\\n"
        for i, inq in enumerate(inquiries, 1):
            response += f"{i}. **{inq['company']}**\\n"
            if inq['inquiry_link'] != 'N/A':
                response += f"   📄 [Inquiry]({inq['inquiry_link']})\\n"
            if inq['quotation'] != 'N/A':
                response += f"   💰 [Quotation]({inq['quotation']})\\n"
            response += "\\n"
        
        return response
    
    except Exception as e:
        logger.error(f"Error fetching inquiries: {e}")
        return f"❌ Error fetching inquiries: {str(e)}"

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
    
    # If no size, grade, or shape detected, return empty
    if not size and not grade and not shape:
        return []
    
    # Search inventory
    results = []
    for location, sizes in INVENTORY.items():
        for inv_size, grades in sizes.items():
            # Match size
            if size and str(inv_size) != str(size):
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

def handle_message(text, phone_number=None):
    """Handle regular messages"""
    text_lower = text.lower().strip()
    
    # Check for inquiry commands
    inquiry_match = re.search(r'inquir(?:y|ies).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text_lower)
    if inquiry_match:
        date_str = inquiry_match.group(1)
        return fetch_inquiries(date_str, phone_number)
    
    # Check for "today inquiries"
    if 'today' in text_lower and 'inquir' in text_lower:
        today = datetime.now().strftime('%d/%m/%Y')
        return fetch_inquiries(today, phone_number)
    
    # Greetings
    if text_lower in ['hi', 'hello', 'hey', 'namaste']:
        return "👋 Hello! Welcome to **Reliable Alloys**!\\n\\nI can help you with:\\n\\n✅ Stock availability\\n✅ Inquiries (authorized users)\\n\\n**Try:**\\n• *50mm 304L*\\n• *inquiries 28/12/2025*\\n• *today inquiries*\\n\\nWhat can I help you with?"
    
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
            
            # Get phone number if available
            phone_number = None
            if 'from' in message and 'phone_number' in message['from']:
                phone_number = message['from']['phone_number']
            elif 'contact' in message:
                phone_number = message['contact']['phone_number']
            
            # Check if message was already processed
            if is_message_processed(message_id):
                logger.info(f"Message {message_id} already processed, skipping")
                return {'ok': True}
            
            # Handle commands
            if text.startswith('/start'):
                response = "🏭 **Welcome to Reliable Alloys!**\\n\\nI can help you with:\\n\\n✅ Stock availability across all locations\\n✅ Inquiries & Quotations (authorized users)\\n\\n**Our Locations:**\\n• PARTH • WADA • TALOJA\\n• SRG • SHEETS • RELIABLE ALLOYS\\n\\n**Try:**\\n• *50mm 304L*\\n• *inquiries 28/12/2025*\\n• *today inquiries*\\n\\nWhat can I help you with?"
            elif text.startswith('/refresh'):
                global INVENTORY
                INVENTORY = load_inventory()
                response = "✅ Inventory refreshed!"
            else:
                response = handle_message(text, phone_number)
            
            send_message(chat_id, response)
        
        return {'ok': True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {'ok': False, 'error': str(e)}

@app.route('/')
def index():
    """Health check endpoint"""
    return 'Stock Bot with Inquiry System is running! 🚀'

@app.route('/health')
def health():
    """Health check for Railway"""
    inventory_count = sum(len(sizes) for sizes in INVENTORY.values())
    return jsonify({
        'status': 'healthy',
        'bot': 'stock-bot',
        'inventory_items': inventory_count,
        'locations': list(INVENTORY.keys()),
        'inquiry_system': 'enabled'
    })

@app.route('/inventory')
def get_inventory():
    """API endpoint to get current inventory"""
    return jsonify(INVENTORY)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting bot with {sum(len(sizes) for sizes in INVENTORY.values())} inventory items")
    logger.info(f"Inquiry system enabled for {len(AUTHORIZED_NUMBERS)} authorized numbers")
    app.run(host='0.0.0.0', port=port)
