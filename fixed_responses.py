# Fixed response functions with proper newlines

def format_stock_response(results):
    """Format stock results into a nice message"""
    if not results:
        return None
    
    response = f"✅ **Found {len(results)} item(s):**\n\n"
    for item in results[:5]:
        response += f"📍 **{item['location']}**: {item['size']}mm {item['grade']} {item['shape']} - {int(item['weight'])} kgs ({item['quality']})\n"
        response += f"   _Last updated: {item['last_updated']}_\n\n"
    
    if len(results) > 5:
        response += f"_...and {len(results) - 5} more results_\n"
    
    return response

def handle_message(text):
    """Handle regular messages"""
    text_lower = text.lower().strip()
    
    # Greetings
    if text_lower in ['hi', 'hello', 'hey', 'namaste']:
        return "👋 Hello! Welcome to **Reliable Alloys**!\n\nI can help you check stock availability.\n\n**Try:**\n• *50mm 304L*\n• *6mm 304L*\n• *40mm EN36C*\n\nWhat are you looking for?"
    
    # Search inventory
    results = search_inventory_flexible(text)
    
    if results:
        return format_stock_response(results)
    else:
        return f"❌ No exact matches found for '{text}'.\n\nPlease contact us at **{COMPANY_INFO['contact']}** for assistance.\n\nTry searching with: *size + grade* (e.g., '50mm 304L')"

# /start command response
START_MESSAGE = "🏭 **Welcome to Reliable Alloys!**\n\nI can help you check stock availability across all locations.\n\n**Our Locations:**\n• PARTH • WADA • TALOJA\n• SRG • SHEETS • RELIABLE ALLOYS\n\n**Try:**\n• *50mm 304L*\n• *6mm 304L*\n• *40mm EN36C*\n\nWhat can I help you with?"
