# Stock Bot Webhook - Gemini AI Powered

Multi-location inventory Telegram bot with **instant responses** powered by Google Gemini AI + **Inquiry Management System** for authorized users.

## 🚀 One-Click Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/stock-bot?referralCode=bhindi)

**OR manually deploy:**

### Railway Deployment (Recommended)

1. **Fork this repo** or use directly
2. Go to [Railway.app](https://railway.app)
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select: `reliablealloys/stock-bot-webhook`
5. **Add Environment Variables:**
   - `BOT_TOKEN` = `8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs`
   - `GEMINI_API_KEY` = Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
6. Click **"Deploy"**
7. Wait 2-3 minutes for deployment
8. Copy your Railway URL (e.g., `https://reliable-alloys-stock-bot-production.up.railway.app`)

### Set Telegram Webhook

After deployment, set the webhook (replace `YOUR-RAILWAY-URL`):

```bash
curl "https://api.telegram.org/bot8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs/setWebhook?url=https://YOUR-RAILWAY-URL.railway.app/8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"
```

**Or visit in browser:**
```
https://api.telegram.org/bot8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs/setWebhook?url=https://YOUR-RAILWAY-URL.railway.app/8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs
```

## ✨ Features

### Stock Management
- **Instant Responses** - No delays, webhook-based
- **Gemini AI Powered** - Natural, intelligent conversations
- **Multi-Location Search** - PARTH, WADA, SRG, TALOJA, SHEETS, RELIABLE ALLOYS
- **Smart Understanding** - Handles greetings, questions, stock queries
- **Auto-Correction** - 304→304L, 316→316L
- **Conversational** - Not robotic, friendly responses

### Inquiry Management System 🆕
- **Authorized Access** - Only authorized phone numbers can view inquiries
- **Date-Based Search** - "Show inquiries for 26/5/2025"
- **Google Sheets Integration** - Fetches data from public Google Sheets
- **PDF Links** - Direct links to inquiry and quotation PDFs
- **Secure** - Phone number verification before showing data

## 📦 Supported Materials

- **Grades:** 303, 304L, 316L, 316TI, DUPLEX, 321, 1117, EN9, EN36C, 8620, A106
- **Shapes:** Round, Hex, Square, Patti, Pipe, Sheet
- **Sizes:** 4mm - 200mm+

## 💬 Example Conversations

### Stock Queries

**Customer:** "Hi"
**Bot:** "Hello! 👋 Welcome to Reliable Alloys! What material are you looking for?"

**Customer:** "50mm EN36C"
**Bot:** "Yes, **50mm EN36C** available at **RELIABLE ALLOYS** - **2,146 kgs** (BLACK). How many kgs do you need?"

**Customer:** "What's your address?"
**Bot:** "📍 Reliable Alloys - Email: sales@reliablealloys.in, Mumbai. We have 6 locations..."

### Inquiry Requests (Authorized Users Only)

**Authorized User:** "Show inquiries for 26/5/2025"
**Bot:** 
```
📋 Inquiries for 26/5/2025
Total: 6 inquiries

1. ACHME WATER
   📄 View Inquiry
   💰 View Quotation

2. AK AUTOPUMP
   📄 View Inquiry
   💰 View Quotation
...
```

**Unauthorized User:** "Show inquiries for 26/5/2025"
**Bot:** "🔒 Access Denied - You are not authorized to view inquiry data."

## 🔐 Inquiry System Setup

### 1. Prepare Google Sheet

Your Google Sheet should have this structure:

| DATE | STATUS | STATUS | COMPANY NAME | INQUIRY | QUOTATION | AUTHORISED NUMBERS |
|------|--------|--------|--------------|---------|-----------|-------------------|
| 26/5/2025 | PENDING | PENDING | ACHME WATER | [PDF Link] | [PDF Link] | 9831935522 |

**Important:** Make the sheet **publicly accessible** (Anyone with link can view)

### 2. Update Sheet ID

In `main.py`, update:
```python
INQUIRY_SHEET_ID = 'YOUR_SHEET_ID_HERE'
```

### 3. Add Authorized Numbers

Add phone numbers in the last column (AUTHORISED NUMBERS) of your sheet. Format: `9831935522`

### 4. User Commands

Authorized users can request inquiries using:
- `inquiries 26/5/2025`
- `show inquiries for 26-5-2025`
- `quotations 28/5/2025`
- `today inquiries`

## 🔧 Manual Setup (Alternative)

### Render.com
1. Go to [Render.com](https://render.com)
2. New Web Service → Connect GitHub
3. Select this repo
4. Add environment variables (same as above)
5. Deploy

### Local Testing
```bash
pip install -r requirements.txt
export BOT_TOKEN="8023224003:AAHNGp6QxZRfawYQn75Ww4_9OORFJhAJeCs"
export GEMINI_API_KEY="your-key-here"
python main.py
```

## 📊 Inventory Management

Inventory is stored in `inventory.json` and auto-synced from Google Sheets every 6 hours.

## 🛠️ Tech Stack

- **Python 3.11** - Flask web framework
- **Google Gemini AI** - Natural language understanding
- **Telegram Bot API** - Instant messaging
- **Google Sheets API** - Inquiry data source
- **Railway/Render** - Cloud hosting
- **Gunicorn** - Production server

## 📞 Contact

- **Email:** sales@reliablealloys.in
- **Telegram:** [@Reliablealloys](https://t.me/Reliablealloys)

## 🔒 Security Notes

- Phone numbers are verified before showing inquiry data
- Only users with phone numbers in the AUTHORISED NUMBERS column can access inquiries
- Google Sheet must be public for the bot to fetch data
- No authentication credentials are stored

---

**Made with ❤️ for Reliable Alloys**
