#!/usr/bin/env python3
"""
Quick test - sends a test message directly to your bot
"""
import requests

BOT_TOKEN = "8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"
CHAT_ID = "YOUR_CHAT_ID"  # Replace with your Telegram chat ID

# Send test message
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {
    "chat_id": CHAT_ID,
    "text": "🤖 Test message from bot! If you see this, the bot API works!"
}

response = requests.post(url, json=data)
print(response.json())
