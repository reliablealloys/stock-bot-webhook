#!/usr/bin/env python3
"""
Temporary polling bot - bypasses webhook issues
Run this locally to test if the bot logic works
"""
import requests
import json
import time
from datetime import datetime

BOT_TOKEN = "8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'

# Load inventory
import sys
sys.path.insert(0, '.')

print("🤖 Starting polling bot (temporary test mode)...")
print("This will fetch messages directly from Telegram")
print("Press Ctrl+C to stop\n")

# First, delete webhook to enable polling
print("1. Removing webhook...")
requests.get(f"{TELEGRAM_API}/deleteWebhook")
print("   ✅ Webhook removed\n")

offset = None

try:
    while True:
        # Get updates
        params = {'timeout': 30}
        if offset:
            params['offset'] = offset
        
        response = requests.get(f"{TELEGRAM_API}/getUpdates", params=params, timeout=35)
        data = response.json()
        
        if not data['ok']:
            print(f"❌ Error: {data.get('description')}")
            time.sleep(5)
            continue
        
        updates = data['result']
        
        for update in updates:
            offset = update['update_id'] + 1
            
            if 'message' not in update:
                continue
            
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            print(f"📨 Received: {text} from {chat_id}")
            
            # Simple response
            if text.lower() in ['hi', 'hello', 'hey']:
                response_text = "👋 Hello! Bot is working in polling mode!"
            elif '304l' in text.lower():
                response_text = "✅ Found 304L items! (This is a test response)"
            else:
                response_text = f"Got your message: {text}"
            
            # Send response
            send_data = {
                'chat_id': chat_id,
                'text': response_text
            }
            
            send_response = requests.post(f"{TELEGRAM_API}/sendMessage", json=send_data)
            
            if send_response.json()['ok']:
                print(f"✅ Sent: {response_text[:50]}...\n")
            else:
                print(f"❌ Failed to send: {send_response.text}\n")
        
        if not updates:
            print(".", end="", flush=True)
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\n🛑 Stopping polling bot...")
    print("Remember to set webhook back!")
    print(f"Run: curl 'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=https://stock-bot-webhook-production.up.railway.app/{BOT_TOKEN}'")
