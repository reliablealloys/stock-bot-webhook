#!/usr/bin/env python3
"""
Quick webhook setup script
Run this to connect your bot to Railway
"""
import requests

BOT_TOKEN = "8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"
RAILWAY_URL = "https://stock-bot-webhook-production.up.railway.app"

print("🔄 Setting up Telegram webhook...\n")

# Step 1: Delete old webhook
print("1. Deleting old webhook...")
delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
response = requests.get(delete_url)
print(f"   Response: {response.json()}\n")

# Step 2: Set new webhook
print("2. Setting new webhook...")
webhook_url = f"{RAILWAY_URL}/{BOT_TOKEN}"
set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
response = requests.post(set_url, json={"url": webhook_url})
result = response.json()
print(f"   Response: {result}\n")

if result.get('ok'):
    print("✅ SUCCESS! Webhook set successfully!")
else:
    print(f"❌ FAILED: {result.get('description')}")

# Step 3: Check webhook info
print("\n3. Checking webhook status...")
info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
response = requests.get(info_url)
info = response.json()['result']

print(f"   URL: {info.get('url')}")
print(f"   Pending updates: {info.get('pending_update_count', 0)}")
if info.get('last_error_message'):
    print(f"   Last error: {info.get('last_error_message')}")

print("\n" + "="*60)
print("✅ Setup complete! Try sending a message to your bot now.")
print("="*60)
