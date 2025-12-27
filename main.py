import os
import logging
from flask import Flask, request
import requests
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs')
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Google Sheets IDs
PARTH_SHEET_ID = '1inC-m3cFtkGhHJE5I-DYDsDIATsoy-zNtsv5m4lOW7k'
MULTI_SHEET_ID = '12O4S5zgXHq63fuTGxLTyAjYiC0lEPHZj8ERCFkbvI8s'

# Cache for inventory (refresh every 6 hours)
inventory_cache = {}
cache_timestamp = 0

def get_sheets_client():
    """Initialize Google Sheets client"""
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Get credentials from environment
        creds_dict = {
            'type': 'service_account',
            'project_id': os.environ.get('GOOGLE_PROJECT_ID'),
            'private_key_id': os.environ.get('GOOGLE_PRIVATE_KEY_ID'),
            'private_key': os.environ.get('GOOGLE_PRIVATE_KEY', '').replace('\\n', '\n'),
            'client_email': os.environ.get('GOOGLE_CLIENT_EMAIL'),
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': os.environ.get('GOOGLE_CERT_URL')
        }
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Error initializing sheets client: {e}")
        return None

def parse_sheet_data(sheet_data, location):
    """Parse sheet data into inventory items"""
    items = []
    current_grade = None
    current_shape = None
    
    for row in sheet_data:
        if not row or len(row) < 3:
            continue
            
        # Detect grade headers (e.g., "303 / round", "304L / hex")
        if len(row) > 0 and '/' in str(row[0]).lower():
            parts = str(row[0]).lower().split('/')
            if len(parts) >= 2:
                current_grade = parts[0].strip().upper()
                current_shape = parts[1].strip().upper()
            continue
        
        # Skip header rows
        if str(row[0]).upper() in ['SIZE', 'LAST UPDATED']:
            continue
        
        # Parse data rows
        try:
            size = str(row[0]).strip()
            if not size or not size[0].isdigit():
                continue
                
            shape = str(row[1]).strip().upper() if len(row) > 1 else current_shape
            grade = str(row[2]).strip().upper() if len(row) > 2 else current_grade
            quality = str(row[3]).strip() if len(row) > 3 else ''
            weight = str(row[5]).strip() if len(row) > 5 else (str(row[4]).strip() if len(row) > 4 else '0')
            
            # Clean up weight
            try:
                weight = float(weight.replace(',', ''))
                if weight <= 0:
                    continue
            except:
                continue
            
            # Normalize grade
            if grade == '304':
                grade = '304L'
            elif grade == '316':
                grade = '316L'
            
            items.append({
                'location': location,
                'size': size,
                'shape': shape or 'ROUND',
                'grade': grade,
                'quality': quality,
                'weight': weight
            })
        except Exception as e:
            logger.error(f"Error parsing row {row}: {e}")
            continue
    
    return items

def load_inventory():
    """Load inventory from Google Sheets"""
    global inventory_cache, cache_timestamp
    import time
    
    # Use cache if less than 6 hours old
    if inventory_cache and (time.time() - cache_timestamp) < 21600:
        return inventory_cache
    
    logger.info("Loading inventory from Google Sheets...")
    inventory = []
    
    try:
        client = get_sheets_client()
        if not client:
            logger.error("Failed to initialize sheets client")
            return inventory_cache if inventory_cache else []
        
        # Load PARTH sheet
        try:
            parth_sheet = client.open_by_key(PARTH_SHEET_ID).sheet1
            parth_data = parth_sheet.get_all_values()
            inventory.extend(parse_sheet_data(parth_data, 'PARTH'))
            logger.info(f"Loaded {len([i for i in inventory if i['location'] == 'PARTH'])} items from PARTH")
        except Exception as e:
            logger.error(f"Error loading PARTH: {e}")
        
        # Load multi-location sheets
        try:
            multi_workbook = client.open_by_key(MULTI_SHEET_ID)
            for location in ['WADA', 'SRG', 'TALOJA', 'SHEETS', 'RELIABLE ALLOYS']:
                try:
                    sheet = multi_workbook.worksheet(location)
                    data = sheet.get_all_values()
                    items = parse_sheet_data(data, location)
                    inventory.extend(items)
                    logger.info(f"Loaded {len(items)} items from {location}")
                except Exception as e:
                    logger.error(f"Error loading {location}: {e}")
        except Exception as e:
            logger.error(f"Error loading multi-location sheets: {e}")
        
        # Update cache
        if inventory:
            inventory_cache = inventory
            cache_timestamp = time.time()
            logger.info(f"Total inventory items loaded: {len(inventory)}")
        
        return inventory
    except Exception as e:
        logger.error(f"Error loading inventory: {e}")
        return inventory_cache if inventory_cache else []

def search_inventory(query):
    """Search inventory based on query"""
    query = query.lower()
    
    # Extract size and grade
    size_match = re.search(r'(\d+\.?\d*)\s*mm', query)
    grade_match = re.search(r'(303|304l?|316l?|316ti|duplex|321)', query, re.IGNORECASE)
    shape_match = re.search(r'(round|hex|square|patti|pipe)', query, re.IGNORECASE)
    
    if not size_match:
        return "Please specify size (e.g., 19mm, 200mm, 6mm)"
    
    size = size_match.group(1)
    grade = grade_match.group(1).upper() if grade_match else None
    shape = shape_match.group(1).upper() if shape_match else None
    
    if not grade:
        return f"Please specify grade (e.g., {size}mm 304L, {size}mm 316L, {size}mm 303)"
    
    # Normalize grade
    if grade == '304':
        grade = '304L'
    elif grade == '316':
        grade = '316L'
    
    # Load inventory
    inventory = load_inventory()
    
    if not inventory:
        return "Sorry, inventory data is currently unavailable. Please try again later or contact us directly."
    
    # Search for matching items
    results = []
    for item in inventory:
        # Match size (exact or close)
        item_size = float(item['size'])
        query_size = float(size)
        
        # Allow 0.5mm tolerance
        if abs(item_size - query_size) > 0.5:
            continue
        
        # Match grade
        if item['grade'] != grade:
            continue
        
        # Match shape if specified
        if shape and item['shape'] != shape:
            continue
        
        results.append(item)
    
    if not results:
        # Try to find similar items
        similar = []
        for item in inventory:
            if item['grade'] == grade:
                similar.append(f"{item['size']}mm {item['shape']}")
        
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
            response += f"📍 **{r['location']}**: {int(r['weight'])} kgs{quality_text}\n"
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
                response = "Welcome to Reliable Alloys Stock Bot! 🏭\n\nI can check inventory across all our locations:\n• PARTH\n• WADA\n• TALOJA\n• SRG\n• SHEETS\n• RELIABLE ALLOYS\n\nSend me a query like:\n• 19mm 304L\n• 200mm round 316L\n• 6mm 303\n• 110mm 304L\n\nI'll check all locations instantly!"
            elif text.startswith('/refresh'):
                global inventory_cache, cache_timestamp
                inventory_cache = {}
                cache_timestamp = 0
                load_inventory()
                response = "✅ Inventory refreshed from Google Sheets!"
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
    inventory_count = len(inventory_cache) if inventory_cache else 0
    return {
        'status': 'healthy',
        'bot': 'stock-bot-webhook',
        'inventory_items': inventory_count,
        'cache_age_hours': round((time.time() - cache_timestamp) / 3600, 2) if cache_timestamp else 0
    }

if __name__ == '__main__':
    import time
    port = int(os.environ.get('PORT', 8080))
    
    # Pre-load inventory on startup
    logger.info("Pre-loading inventory...")
    load_inventory()
    
    app.run(host='0.0.0.0', port=port)
