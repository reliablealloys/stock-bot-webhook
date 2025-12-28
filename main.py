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
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    logger.warning("GEMINI_API_KEY not set - AI features will be disabled")
    model = None

# Company information
COMPANY_INFO = {
    'name': 'Reliable Alloys',
    'address': 'Mumbai, India',
    'contact': 'sales@reliablealloys.in',
    'specialties': ['Stainless Steel', '303', '304L', '316L', 'Duplex', 'Sheets'],
    'services': ['Stock availability', 'Custom cutting', 'Delivery across India']
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

# Store conversation history per user
conversation_history = {}

def search_inventory(size, grade, shape=None):
    """Search inventory based on size, grade, and optional shape"""
    # Normalize inputs
    size = str(size).strip()
    grade = grade.upper().strip()
    
    # Auto-correct common mistakes
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
                # Skip negative weights
                if item['weight'] <= 0:
                    continue
                    
                # Match shape if specified
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
    """Format inventory search results into a readable message"""
    if not results:
        return None
    
    # Calculate total weight and group by location
    total_weight = sum(r['weight'] for r in results)
    locations = list(set(r['location'] for r in results))
    
    # Format response
    response = f"✅ **{size}mm {grade}** available!\\n\\n"
    response += f"📦 **Total: {int(total_weight)} kgs** across {len(locations)} location(s)\\n\\n"
    response += "**Breakdown by location:**\\n"
    
    # Group by location
    location_data = {}
    for r in results:
        if r['location'] not in location_data:
            location_data[r['location']] = []
        location_data[r['location']].append(r)
    
    for location, items in location_data.items():
        location_total = sum(item['weight'] for item in items)
        last_updated = LAST_UPDATED.get(location, 'Unknown')
        response += f"\\n📍 **{location}**: {int(location_total)} kgs\\n"
        for item in items:
            quality_text = f" - {item['quality']}" if item['quality'] else ""
            response += f"   • {item['shape']}: {int(item['weight'])} kgs{quality_text}\\n"
        response += f"   📅 *Last updated: {last_updated}*\\n"
    
    return response

def get_available_grades():
    """Get list of all available grades in inventory"""
    grades = set()
    for location, sizes in INVENTORY.items():
        for size, grade_dict in sizes.items():
            grades.update(grade_dict.keys())
    return sorted(list(grades))

def get_available_sizes_for_grade(grade):
    """Get list of all available sizes for a specific grade"""
    sizes = set()
    for location, size_dict in INVENTORY.items():
        for size, grade_dict in size_dict.items():
            if grade.upper() in grade_dict:
                sizes.add(size)
    return sorted(list(sizes), key=lambda x: float(x))

def create_system_prompt():
    """Create system prompt for Gemini with inventory context"""
    available_grades = get_available_grades()
    
    return f"""You are a helpful customer service assistant for Reliable Alloys, a stainless steel supplier in Mumbai, India.

COMPANY INFORMATION:
- Name: {COMPANY_INFO['name']}
- Contact: {COMPANY_INFO['contact']}
- Specialties: {', '.join(COMPANY_INFO['specialties'])}
- Services: {', '.join(COMPANY_INFO['services'])}

AVAILABLE GRADES IN INVENTORY:
{', '.join(available_grades)}

LOCATIONS:
{', '.join(INVENTORY.keys())}

YOUR ROLE:
1. Be friendly, professional, and helpful
2. When customers ask about stock, extract the SIZE and GRADE from their message
3. If they mention a size without grade, ask which grade they need
4. If they mention a grade without size, ask which size they need
5. Answer general questions about the company, delivery, pricing, etc.
6. Be conversational and natural - don't sound robotic
7. If you're not sure what they're asking, politely ask for clarification

IMPORTANT RULES:
- Always extract size (in mm) and grade from customer queries
- Common grades: 303, 304L, 316L, 316TI, DUPLEX, 321, 1117, EN9, EN36C, 8620
- If customer says "304" assume they mean "304L"
- If customer says "316" assume they mean "316L"
- Be brief and to the point
- Don't make up stock information - only I will provide actual stock data

RESPONSE FORMAT:
When you identify a stock query, respond with:
STOCK_QUERY: size=<size>, grade=<grade>, shape=<shape if mentioned>

For general queries, just respond naturally without the STOCK_QUERY prefix.

Examples:
Customer: "Do you have 50mm en36c?"
You: STOCK_QUERY: size=50, grade=EN36C

Customer: "I need 110mm 304L"
You: STOCK_QUERY: size=110, grade=304L

Customer: "What's your address?"
You: We're located in Mumbai, India. You can reach us at sales@reliablealloys.in for detailed address and directions!

Customer: "Do you deliver?"
You: Yes, we deliver across India! Delivery time and charges depend on your location and quantity. What material are you looking for?"""

def chat_with_gemini(user_message, chat_id):
    """Chat with Gemini AI and handle stock queries"""
    if not model:
        return "AI features are currently unavailable. Please contact us at sales@reliablealloys.in"
    
    try:
        # Get or create conversation history for this user
        if chat_id not in conversation_history:
            conversation_history[chat_id] = []
        
        # Add system prompt context
        system_prompt = create_system_prompt()
        
        # Build conversation context
        conversation_context = system_prompt + "\\n\\nCONVERSATION HISTORY:\\n"
        for msg in conversation_history[chat_id][-5:]:  # Last 5 messages for context
            conversation_context += f"{msg['role']}: {msg['content']}\\n"
        conversation_context += f"Customer: {user_message}\\nYou: "
        
        # Generate response
        response = model.generate_content(conversation_context)
        ai_response = response.text.strip()
        
        # Store in conversation history
        conversation_history[chat_id].append({'role': 'Customer', 'content': user_message})
        conversation_history[chat_id].append({'role': 'Assistant', 'content': ai_response})
        
        # Keep only last 10 messages to avoid token limits
        if len(conversation_history[chat_id]) > 10:
            conversation_history[chat_id] = conversation_history[chat_id][-10:]
        
        # Check if this is a stock query
        if ai_response.startswith('STOCK_QUERY:'):
            # Parse the stock query
            query_part = ai_response.replace('STOCK_QUERY:', '').strip()
            params = {}
            for param in query_part.split(','):
                key, value = param.split('=')
                params[key.strip()] = value.strip()
            
            size = params.get('size')
            grade = params.get('grade')
            shape = params.get('shape')
            
            # Search inventory
            results = search_inventory(size, grade, shape)
            
            if results:
                return format_inventory_results(results, size, grade)
            else:
                # Try to find similar items
                similar_sizes = get_available_sizes_for_grade(grade)
                if similar_sizes:
                    similar_list = ', '.join([f"{s}mm" for s in similar_sizes[:5]])
                    return f"❌ We don't have **{size}mm {grade}** in stock right now.\\n\\n✅ **Available sizes in {grade}:** {similar_list}\\n\\n💬 Would you like to check any of these? Or contact us at {COMPANY_INFO['contact']}"
                else:
                    return f"❌ We don't have **{size}mm {grade}** in stock right now.\\n\\n📧 Contact us for availability: {COMPANY_INFO['contact']}"
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Error in Gemini chat: {e}")
        return "I'm having trouble processing your request. Please contact us at sales@reliablealloys.in or try again."

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
                response = "🏭 **Welcome to Reliable Alloys Stock Bot!**\\n\\nI'm your AI assistant powered by Gemini! I can help you with:\\n✅ Stock availability across all locations\\n✅ Material specifications\\n✅ General inquiries\\n\\n**Our Locations:**\\n• PARTH\\n• WADA\\n• TALOJA\\n• SRG\\n• SHEETS\\n• RELIABLE ALLOYS\\n\\n**Try asking:**\\n• *Do you have 110mm 304L?*\\n• *I need 50mm EN36C*\\n• *What's your address?*\\n• *Do you deliver to Bangalore?*\\n\\nWhat can I help you with?"
            elif text.startswith('/refresh'):
                global INVENTORY
                INVENTORY = load_inventory()
                response = "✅ Inventory refreshed!"
            elif text.startswith('/clear'):
                if chat_id in conversation_history:
                    conversation_history[chat_id] = []
                response = "✅ Conversation history cleared!"
            else:
                # Use Gemini AI for all other messages
                response = chat_with_gemini(text, chat_id)
            
            send_message(chat_id, response)
        
        return {'ok': True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {'ok': False, 'error': str(e)}

@app.route('/')
def index():
    """Health check endpoint"""
    return 'Stock Bot with Gemini AI is running! 🚀'

@app.route('/health')
def health():
    """Health check for Railway"""
    inventory_count = sum(len(sizes) for sizes in INVENTORY.values())
    return jsonify({
        'status': 'healthy',
        'bot': 'stock-bot-webhook-gemini',
        'ai_enabled': model is not None,
        'inventory_items': inventory_count,
        'locations': list(INVENTORY.keys())
    })

@app.route('/inventory')
def get_inventory():
    """API endpoint to get current inventory"""
    return jsonify(INVENTORY)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting bot with Gemini AI and {sum(len(sizes) for sizes in INVENTORY.values())} inventory items")
    app.run(host='0.0.0.0', port=port)
