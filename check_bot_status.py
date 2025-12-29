#!/usr/bin/env python3
"""
Test script to check bot status and webhook
"""
import requests
import os

BOT_TOKEN = '8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs'
RAILWAY_URL = 'https://stock-bot-webhook-production.up.railway.app'

print("🔍 Checking bot status...\n")

# 1. Check if bot is responding
print("1. Checking Telegram Bot API...")
try:
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getMe', timeout=5)
    if response.status_code == 200:
        bot_info = response.json()
        print(f"   ✅ Bot is alive: @{bot_info['result']['username']}")
    else:
        print(f"   ❌ Bot API error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Check webhook status
print("\n2. Checking webhook...")
try:
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo', timeout=5)
    if response.status_code == 200:
        webhook_info = response.json()['result']
        print(f"   URL: {webhook_info.get('url', 'NOT SET')}")
        print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
        print(f"   Last error: {webhook_info.get('last_error_message', 'None')}")
        
        if webhook_info.get('url') != f'{RAILWAY_URL}/{BOT_TOKEN}':
            print(f"\n   ⚠️  WEBHOOK MISMATCH!")
            print(f"   Expected: {RAILWAY_URL}/{BOT_TOKEN}")
            print(f"   Current: {webhook_info.get('url')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Check Railway health
print("\n3. Checking Railway deployment...")
try:
    response = requests.get(f'{RAILWAY_URL}/health', timeout=5)
    if response.status_code == 200:
        health = response.json()
        print(f"   ✅ Status: {health.get('status')}")
        print(f"   Inventory items: {health.get('inventory_items')}")
        print(f"   Inquiry system: {health.get('inquiry_system')}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*50)
print("DIAGNOSIS:")
print("="*50)
print("\nIf webhook URL is wrong, run:")
print(f"curl -X POST https://api.telegram.org/bot{BOT_TOKEN}/setWebhook \\")
print(f"  -d 'url={RAILWAY_URL}/{BOT_TOKEN}'")
