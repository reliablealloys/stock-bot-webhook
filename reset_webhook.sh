#!/bin/bash
# Reset webhook for Telegram bot

BOT_TOKEN="8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"
RAILWAY_URL="https://stock-bot-webhook-production.up.railway.app"

echo "🔄 Resetting Telegram webhook..."
echo ""

# Delete existing webhook
echo "1. Deleting old webhook..."
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook"
echo ""
echo ""

# Set new webhook
echo "2. Setting new webhook..."
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -d "url=${RAILWAY_URL}/${BOT_TOKEN}")
echo "$RESPONSE"
echo ""

# Check webhook status
echo "3. Checking webhook status..."
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | python3 -m json.tool
echo ""

echo "✅ Done! Try sending a message to the bot now."
