# Stock Bot Webhook

Multi-location inventory Telegram bot with instant responses.

## Features
- Instant webhook-based responses
- Multi-location inventory search
- Supports 303, 304L, 316L, 316TI grades
- Shows location, quality, and quantity

## Deployment

### Railway (Recommended)
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select this repository
4. Add environment variable: `BOT_TOKEN` = `8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs`
5. Deploy!
6. Copy your Railway URL (e.g., https://stock-bot-webhook-production.up.railway.app)
7. Set webhook: 
```bash
curl -X POST https://api.telegram.org/bot8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs/setWebhook \
  -d url=https://YOUR-RAILWAY-URL.railway.app/8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs
```

## Usage
Message @Reliablealloys on Telegram:
- "19mm 304L"
- "200mm round 316L"
- "110mm 304L"

Bot responds instantly with location and quantity!
