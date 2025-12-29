#!/usr/bin/env python3
"""
Complete bot diagnostic - checks everything
"""
import requests
import json

BOT_TOKEN = "8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"
RAILWAY_URL = "https://stock-bot-webhook-production.up.railway.app"

print("="*70)
print("TELEGRAM BOT DIAGNOSTIC TOOL")
print("="*70)

# 1. Check if Railway is responding
print("\n1️⃣ CHECKING RAILWAY DEPLOYMENT...")
try:
    response = requests.get(f"{RAILWAY_URL}/health", timeout=5)
    if response.status_code == 200:
        health = response.json()
        print(f"   ✅ Railway is ONLINE")
        print(f"   📊 Status: {health.get('status')}")
        print(f"   📦 Inventory: {health.get('inventory_items')} items")
        print(f"   📍 Locations: {', '.join(health.get('locations', []))}")
    else:
        print(f"   ❌ Railway returned status {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print(f"   Railway might be down or URL is wrong")

# 2. Check bot API
print("\n2️⃣ CHECKING TELEGRAM BOT API...")
try:
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=5)
    if response.status_code == 200:
        bot = response.json()['result']
        print(f"   ✅ Bot is ALIVE")
        print(f"   🤖 Username: @{bot['username']}")
        print(f"   📝 Name: {bot['first_name']}")
    else:
        print(f"   ❌ Bot API error: {response.status_code}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 3. Check webhook status
print("\n3️⃣ CHECKING WEBHOOK STATUS...")
try:
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo", timeout=5)
    if response.status_code == 200:
        webhook = response.json()['result']
        current_url = webhook.get('url', 'NOT SET')
        expected_url = f"{RAILWAY_URL}/{BOT_TOKEN}"
        
        print(f"   Current URL: {current_url}")
        print(f"   Expected URL: {expected_url}")
        
        if current_url == expected_url:
            print(f"   ✅ Webhook is CORRECTLY SET")
        elif current_url == '':
            print(f"   ❌ Webhook is NOT SET")
        else:
            print(f"   ⚠️  Webhook is set to WRONG URL")
        
        print(f"   📬 Pending updates: {webhook.get('pending_update_count', 0)}")
        
        if webhook.get('last_error_message'):
            print(f"   ⚠️  Last error: {webhook.get('last_error_message')}")
            print(f"   🕐 Error time: {webhook.get('last_error_date')}")
        
        if webhook.get('last_synchronization_error_date'):
            print(f"   ⚠️  Last sync error: {webhook.get('last_synchronization_error_date')}")
            
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 4. Test webhook endpoint
print("\n4️⃣ TESTING WEBHOOK ENDPOINT...")
try:
    test_update = {
        "update_id": 999999999,
        "message": {
            "message_id": 999,
            "from": {"id": 123456, "first_name": "Test"},
            "chat": {"id": 123456, "type": "private"},
            "date": 1234567890,
            "text": "/start"
        }
    }
    
    response = requests.post(
        f"{RAILWAY_URL}/{BOT_TOKEN}",
        json=test_update,
        timeout=5
    )
    
    if response.status_code == 200:
        print(f"   ✅ Webhook endpoint is RESPONDING")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ❌ Webhook returned status {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "="*70)
print("DIAGNOSIS COMPLETE")
print("="*70)

# Provide fix suggestions
print("\n💡 NEXT STEPS:")
print("   1. If Railway is down → Check Railway dashboard")
print("   2. If webhook is not set → Run: python3 setup_webhook_simple.py")
print("   3. If webhook has wrong URL → Run: python3 setup_webhook_simple.py")
print("   4. If webhook endpoint fails → Check Railway logs")
print("\n   Try sending a message to the bot after fixing!")
