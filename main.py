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
    'specialties': ['Stainless Steel', '303', '304L', '316L', 'Duplex', 'Sheets'],
    'services': ['Stock availability', 'Custom cutting', 'Delivery across India']
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

def handle_general_query(text):
    """Handle general questions and conversational queries"""
    text_lower = text.lower()
    
    # Greetings
    if any(word in text_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return "Hello! 👋 Welcome to Reliable Alloys!\n\nI can help you check stock availability across all our locations. Just tell me what you're looking for!\n\nExample: *110mm 304L* or *6mm 303 round*"
    
    # Contact/Address queries
    if any(word in text_lower for word in ['address', 'location', 'where are you', 'contact', 'phone', 'email']):
        return f"📍 **{COMPANY_INFO['name']}**\n\n📧 Email: {COMPANY_INFO['contact']}\n📞 Contact us for phone details\n\nWe have multiple godowns:\n• PARTH\n• WADA\n• TALOJA\n• SRG\n• SHEETS\n\nWhat material are you looking for?"
    
    # Working hours
    if any(word in text_lower for word in ['hours', 'timing', 'open', 'close', 'when']):
        return "⏰ **Working Hours:**\nMonday - Saturday: 9:00 AM - 6:00 PM\nSunday: Closed\n\nWhat can I help you find today?"
    
    # Delivery queries
    if any(word in text_lower for word in ['deliver', 'delivery', 'shipping', 'transport']):
        return "🚚 **Delivery Available!**\n\nWe deliver across India. Delivery time and charges depend on:\n• Location\n• Quantity\n• Material type\n\nPlease share your requirement and location for a quote!\n\nWhat material do you need?"
    
    # Price queries
    if any(word in text_lower for word in ['price', 'cost', 'rate', 'how much']):
        return "💰 **Pricing Information:**\n\nPrices vary based on:\n• Material grade\n• Quantity\n• Current market rates\n• Delivery location\n\nPlease tell me what you need (e.g., *110mm 304L*) and I'll check availability. For pricing, contact: {}\n\nWhat are you looking for?".format(COMPANY_INFO['contact'])
    
    # Thank you
    if any(word in text_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're welcome! 😊\n\nNeed anything else? Just ask!"
    
    # Help
    if 'help' in text_lower:
        return "🏭 **How I Can Help:**\n\n✅ Check stock availability\n✅ Show quantities at each location\n✅ Answer general questions\n\n**Example queries:**\n• *110mm 304L*\n• *6mm 303 round*\n• *0.5mm 202 sheet*\n• *What's your address?*\n• *Do you deliver?*\n\nWhat would you like to know?"
    
    return None

def search_inventory(query):
    """Search inventory based on query"""
    query_lower = query.lower()
    
    # Extract size and grade
    size_match = re.search(r'(\d+\.?\d*)\s*mm', query_lower)
    grade_match = re.search(r'(202|303|304l?|316l?|316ti|duplex|321|1117)', query_lower, re.IGNORECASE)
    shape_match = re.search(r'(round|hex|square|patti|pipe|sheet)', query_lower, re.IGNORECASE)
    
    # Auto-correct common mistakes
    corrections = []
    if '304 ' in query_lower and '304l' not in query_lower:
        query_lower = query_lower.replace('304 ', '304l ')
        corrections.append("(Assuming you meant 304L)")
    if '316 ' in query_lower and '316l' not in query_lower:
        query_lower = query_lower.replace('316 ', '316l ')
        corrections.append("(Assuming you meant 316L)")
    
    if not size_match:
        return "Please specify the size you need.\n\n**Example:** *19mm 304L* or *110mm 316L round*"
    
    size = size_match.group(1)
    grade = grade_match.group(1).upper() if grade_match else None
    shape = shape_match.group(1).upper() if shape_match else None
    
    if not grade:
        return f"Please specify the grade for {size}mm.\n\n**Example:** *{size}mm 304L* or *{size}mm 316L* or *{size}mm 303*"
    
    # Normalize grade
    if grade == '304':
        grade = '304L'
        corrections.append("(Corrected to 304L)")
    elif grade == '316':
        grade = '316L'
        corrections.append("(Corrected to 316L)")
    
    correction_text = " " + " ".join(corrections) if corrections else ""
    
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
            return f"❌ Sorry, **{size}mm {grade}**{correction_text} is not available in stock.\n\n✅ **Similar items available:** {similar_list}\n\n💬 Want to check any of these? Or contact us at {COMPANY_INFO['contact']}"
        else:
            return f"❌ Sorry, **{size}mm {grade}**{correction_text} is not available in stock.\n\n📧 Contact us for availability: {COMPANY_INFO['contact']}"
    
    # Calculate total weight and group by location
    total_weight = sum(r['weight'] for r in results)
    locations = list(set(r['location'] for r in results))
    
    # Format response
    response = f"✅ **{size}mm {grade}**{correction_text} available!\n\n"
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
    
    response += f"\n💬 How many kgs do you need? Which location works for you?"
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
                response = "🏭 **Welcome to Reliable Alloys Stock Bot!**\n\nI'm here to help you with:\n✅ Stock availability across all locations\n✅ Material specifications\n✅ General inquiries\n\n**Our Locations:**\n• PARTH\n• WADA\n• TALOJA\n• SRG\n• SHEETS\n\n**Try asking:**\n• *110mm 304L*\n• *What's your address?*\n• *Do you deliver?*\n\nWhat can I help you with?"
            elif text.startswith('/refresh'):
                global INVENTORY
                INVENTORY = load_inventory()
                response = "✅ Inventory refreshed!"
            else:
                # First check if it's a general query
                response = handle_general_query(text)
                
                # If not a general query, search inventory
                if response is None:
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
