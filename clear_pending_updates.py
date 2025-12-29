#!/usr/bin/env python3
"""
Clear all pending updates - forces Telegram to start fresh
"""
import requests

BOT_TOKEN = "8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"

print("🧹 Clearing all pending updates...\n")

# Get all pending updates
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
data = response.json()

if data['ok']:
    updates = data['result']
    print(f"Found {len(updates)} pending updates")
    
    if len(updates) > 0:
        # Get the last update_id
        last_update_id = updates[-1]['update_id']
        
        # Clear by acknowledging all updates
        clear_response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            params={'offset': last_update_id + 1}
        )
        
        if clear_response.json()['ok']:
            print(f"✅ Cleared all {len(updates)} pending updates!")
            print("\n📝 Cleared messages:")
            for update in updates:
                if 'message' in update:
                    msg = update['message']
                    print(f"   - {msg.get('text', 'No text')}")
        else:
            print("❌ Failed to clear updates")
    else:
        print("✅ No pending updates to clear")
    
    print("\n🎉 Done! Now send a new message to your bot.")
else:
    print(f"❌ Error: {data.get('description')}")
