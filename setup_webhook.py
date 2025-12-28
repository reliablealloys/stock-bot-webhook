import requests
import sys

BOT_TOKEN = "8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"
WEBHOOK_URL = "https://web-production-9d147.up.railway.app/webhook"

# Delete existing webhook
delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
response = requests.get(delete_url)
print(f"Delete webhook: {response.json()}")

# Set new webhook
set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
data = {"url": WEBHOOK_URL}
response = requests.post(set_url, json=data)
print(f"Set webhook: {response.json()}")

# Get webhook info
info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
response = requests.get(info_url)
print(f"Webhook info: {response.json()}")
