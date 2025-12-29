#!/usr/bin/env python3
"""
Manual webhook test - simulates Telegram sending an update
"""
import requests
import json

RAILWAY_URL = "https://stock-bot-webhook-production.up.railway.app"
BOT_TOKEN = "8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"

# Simulate a Telegram update
test_update = {
    "update_id": 123456789,
    "message": {
        "message_id": 1,
        "from": {
            "id": 123456,
            "is_bot": False,
            "first_name": "Test User"
        },
        "chat": {
            "id": 123456,
            "first_name": "Test User",
            "type": "private"
        },
        "date": 1640000000,
        "text": "6mm 304L"
    }
}

print("🧪 Testing webhook endpoint...")
print(f"URL: {RAILWAY_URL}/{BOT_TOKEN}")
print(f"Payload: {json.dumps(test_update, indent=2)}\n")

try:
    response = requests.post(
        f"{RAILWAY_URL}/{BOT_TOKEN}",
        json=test_update,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}\n")
    
    if response.status_code == 200:
        print("✅ Webhook is working!")
        print("If bot didn't respond, check Railway logs for errors")
    else:
        print("❌ Webhook returned an error")
        
except Exception as e:
    print(f"❌ Error: {e}")
