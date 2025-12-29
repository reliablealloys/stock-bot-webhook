#!/usr/bin/env python3
"""
Check webhook status and recent errors
"""
import requests
import json
from datetime import datetime

BOT_TOKEN = "8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"

print("🔍 Checking webhook status...\n")

response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
data = response.json()

if data['ok']:
    info = data['result']
    
    print(f"📍 Webhook URL: {info.get('url', 'NOT SET')}")
    print(f"📬 Pending updates: {info.get('pending_update_count', 0)}")
    print(f"🔢 Max connections: {info.get('max_connections', 40)}")
    
    if info.get('last_error_date'):
        error_time = datetime.fromtimestamp(info['last_error_date'])
        print(f"\n⚠️  LAST ERROR:")
        print(f"   Time: {error_time}")
        print(f"   Message: {info.get('last_error_message', 'Unknown')}")
    
    if info.get('last_synchronization_error_date'):
        sync_time = datetime.fromtimestamp(info['last_synchronization_error_date'])
        print(f"\n⚠️  LAST SYNC ERROR:")
        print(f"   Time: {sync_time}")
    
    if info.get('ip_address'):
        print(f"\n🌐 IP Address: {info['ip_address']}")
    
    # Check if there are pending updates
    if info.get('pending_update_count', 0) > 0:
        print(f"\n⚠️  WARNING: {info['pending_update_count']} pending updates!")
        print("   This means Telegram sent messages but Railway didn't respond properly")
        print("   The bot might be crashing or returning errors")
        
        # Get updates to see what's pending
        print("\n📥 Fetching pending updates...")
        updates_response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
        if updates_response.json()['ok']:
            updates = updates_response.json()['result']
            print(f"   Found {len(updates)} updates:")
            for update in updates[:3]:
                if 'message' in update:
                    msg = update['message']
                    print(f"   - Message {msg['message_id']}: {msg.get('text', 'No text')}")
    else:
        print("\n✅ No pending updates - webhook is processing messages")
    
    print("\n" + "="*60)
    print("Full webhook info:")
    print(json.dumps(info, indent=2))
    
else:
    print(f"❌ Error: {data.get('description')}")
