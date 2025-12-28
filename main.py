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

# Store conversation context per user (simple memory)
user_context = {}

def search_inventory(size, grade, shape=None):
    """Search inventory based on size, grade, and optional shape"""
    size = str(size).strip()
    grade = grade.upper().strip()
    
    # Auto-correct common mistakes
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

def format_inventory_results(results, size, grade):
    """Format inventory search results"""
    if not results:
        return None
    
    total_weight = sum(r['weight'] for r in results)
    locations = list(set(r['location'] for r in results))
    
    response = f"✅ **{size}mm {grade}** available!\n\n"
    response += f"📦 **Total: {int(total_weight)} kgs** across {len(locations)} location(s)\n\n"
    response += "**Breakdown by location:**\n"
    
    location_data = {}
    for r in results:
        if r['location'] not in location_data:
            location_data[r['location']] = []
        location_data[r['location']].append(r)
    
    for location, items in location_data.items():
        location_total = sum(item['weight'] for item in items)
        last_updated = LAST_UPDATED.get(location, 'Unknown')
        response += f"\n📍 **{location}**: {int(location_total)} kgs\n"
        for item in items:
            quality_text = f" - {item['quality']}" if item['quality'] else ""
            response += f"   • {item['shape']}: {int(item['weight'])} kgs{quality_text}\n"
        response += f"   📅 *Last updated: {last_updated}*\n"
    
    return response

def get_available_grades():
    """Get list of all available grades"""
    grades = set()
    for location, sizes in INVENTORY.items():
        for size, grade_dict in sizes.items():
            grades.update(grade_dict.keys())
    return sorted(list(grades))

def get_available_sizes_for_grade(grade):
    """Get available sizes for a grade"""
    sizes = set()
    for location, size_dict in INVENTORY.items():
        for size, grade_dict in size_dict.items():
            if grade.upper() in grade_dict:
                sizes.add(size)
    return sorted(list(sizes), key=lambda x: float(x))

def handle_message(text, chat_id):
    """Handle incoming messages with intelligent responses"""
    text_lower = text.lower().strip()
    
    # Store context
    if chat_id not in user_context:
        user_context[chat_id] = {'last_query': None, 'conversation_count': 0}
    
    user_context[chat_id]['conversation_count'] += 1
    
    # Greetings
    if any(word in text_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'namaste']):
        return "Hello! 👋 Welcome to Reliable Alloys!\n\nI can help you check stock availability across all our locations. What material are you looking for?\n\n**Example:** *110mm 304L* or *50mm EN36C*"
    
    # Contact/Address queries
    if any(word in text_lower for word in ['address', 'location', 'where are you', 'contact', 'phone', 'email', 'reach']):
        return f"📍 **{COMPANY_INFO['name']}**\n\n📧 Email: {COMPANY_INFO['contact']}\n📞 Contact us for phone details\n\nWe have multiple locations:\n" + "\n".join([f"• {loc}" for loc in COMPANY_INFO['locations']]) + "\n\nWhat material can I help you find?"
    
    # Delivery queries
    if any(word in text_lower for word in ['deliver', 'delivery', 'shipping', 'transport', 'courier']):
        return "🚚 **Yes, we deliver across India!**\n\nDelivery depends on:\n• Your location\n• Quantity needed\n• Material type\n\nWhat material are you looking for? I'll check availability first!"
    
    # Price queries
    if any(word in text_lower for word in ['price', 'cost', 'rate', 'how much', 'pricing']):
        return f"💰 **Pricing varies based on:**\n• Material grade & quantity\n• Current market rates\n• Delivery location\n\nPlease tell me what you need (e.g., *110mm 304L*) and I'll check stock. For pricing, contact: {COMPANY_INFO['contact']}"
    
    # Thank you
    if any(word in text_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're welcome! 😊\n\nNeed anything else? I'm here to help!"
    
    # Help
    if 'help' in text_lower:
        return "🏭 **How I Can Help:**\n\n✅ Check stock availability\n✅ Show quantities at each location\n✅ Answer general questions\n\n**Example queries:**\n• *110mm 304L*\n• *50mm EN36C*\n• *What's your address?*\n• *Do you deliver?*\n\nWhat would you like to know?"
    
    # Extract size and grade for stock queries
    size_match = re.search(r'(\\d+\\.?\\d*)\\s*mm', text_lower)
    grade_match = re.search(r'(202|303|304l?|316l?|316ti|duplex|321|1117|en9|en36c|8620|a106)', text_lower, re.IGNORECASE)
    shape_match = re.search(r'(round|hex|square|patti|pipe|sheet)', text_lower, re.IGNORECASE)
    
    # Check if user is asking about availability
    is_stock_query = any(word in text_lower for word in ['have', 'available', 'stock', 'need', 'want', 'looking for', 'require'])
    
    if not size_match and not is_stock_query:
        return "I'd love to help! Could you tell me the **size** and **grade** you need?\n\n**Example:** *110mm 304L* or *50mm EN36C*"
    
    if size_match and not grade_match:
        size = size_match.group(1)
        user_context[chat_id]['last_query'] = {'size': size}
        return f"What **grade** do you need for {size}mm?\n\n**Example:** *{size}mm 304L* or *{size}mm 316L*"
    
    if not size_match and grade_match:
        grade = grade_match.group(1).upper()
        if grade == '304':
            grade = '304L'
        elif grade == '316':
            grade = '316L'
        user_context[chat_id]['last_query'] = {'grade': grade}
        return f"What **size** do you need in {grade}?\n\n**Example:** *110mm {grade}* or *50mm {grade}*"
    
    if not size_match and not grade_match:
        return "I'd love to help! Could you tell me the **size** and **grade** you need?\n\n**Example:** *110mm 304L* or *50mm EN36C*"
    
    # We have both size and grade
    size = size_match.group(1)
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
        response = format_inventory_results(results, size, grade)
        response += "\n\n💬 How many kgs do you need? Which location works for you?"
        user_context[chat_id]['last_query'] = {'size': size, 'grade': grade, 'found': True}
        return response
    else:
        # Try to find similar items
        similar_sizes = get_available_sizes_for_grade(grade)
        if similar_sizes:
            similar_list = ', '.join([f"{s}mm" for s in similar_sizes[:5]])
            return f"❌ We don't have **{size}mm {grade}** in stock right now.\n\n✅ **Available sizes in {grade}:** {similar_list}\n\n💬 Would you like to check any of these? Or contact us at {COMPANY_INFO['contact']}"
        else:
            available_grades = get_available_grades()
            grades_list = ', '.join(available_grades[:8])
            return f"❌ We don't have **{size}mm {grade}** in stock right now.\n\n✅ **Available grades:** {grades_list}\n\n📧 Contact us for availability: {COMPANY_INFO['contact']}"

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
                response = "🏭 **Welcome to Reliable Alloys Stock Bot!**\n\nI'm here to help you with instant stock availability across all our locations!\n\n**Our Locations:**\n• PARTH\n• WADA\n• TALOJA\n• SRG\n• SHEETS\n• RELIABLE ALLOYS\n\n**Try asking:**\n• *110mm 304L*\n• *50mm EN36C*\n• *What's your address?*\n• *Do you deliver?*\n\nWhat can I help you with?"
            elif text.startswith('/refresh'):
                global INVENTORY
                INVENTORY = load_inventory()
                response = "✅ Inventory refreshed!"
            elif text.startswith('/clear'):
                if chat_id in user_context:
                    user_context[chat_id] = {'last_query': None, 'conversation_count': 0}
                response = "✅ Conversation cleared!"
            else:
                response = handle_message(text, chat_id)
            
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
