"""
Inquiry Management System
Handles authorized access to inquiry/quotation data from Google Sheets
"""

import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Google Sheets configuration
INQUIRY_SHEET_ID = '1lI9c24H2Jg6DOMAOcJuzYXuTLNjc1FIdOPs507oM5ts'
INQUIRY_SHEET_NAME = 'Sheet1'

def normalize_date(date_str):
    """
    Normalize date string to DD/M/YYYY format
    Handles: 26/5/2025, 26-5-2025, 26.5.2025, etc.
    """
    # Remove extra spaces
    date_str = date_str.strip()
    
    # Replace separators with /
    date_str = date_str.replace('-', '/').replace('.', '/')
    
    # Try to parse and normalize
    try:
        # Handle DD/M/YYYY or D/M/YYYY
        parts = date_str.split('/')
        if len(parts) == 3:
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
            return f"{day}/{month}/{year}"
    except:
        pass
    
    return date_str

def is_inquiry_request(message_text):
    """
    Check if message is requesting inquiries
    Patterns: "inquiries 26/5/2025", "show inquiries for 26-5-2025", "today inquiries"
    """
    message_lower = message_text.lower().strip()
    
    # Keywords that indicate inquiry request
    inquiry_keywords = ['inquiry', 'inquiries', 'quotation', 'quotations', 'quote']
    
    # Check if any keyword is present
    has_keyword = any(keyword in message_lower for keyword in inquiry_keywords)
    
    # Check for date patterns
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',  # 26/5/2025 or 26-5-2025
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2}',   # 26/5/25 or 26-5-25
        r'today',
        r'yesterday'
    ]
    
    has_date = any(re.search(pattern, message_lower) for pattern in date_patterns)
    
    return has_keyword and (has_date or 'list' in message_lower or 'show' in message_lower)

def extract_date_from_message(message_text):
    """
    Extract date from inquiry request message
    Returns normalized date string or None
    """
    message_lower = message_text.lower().strip()
    
    # Handle "today"
    if 'today' in message_lower:
        today = datetime.now()
        return f"{today.day}/{today.month}/{today.year}"
    
    # Handle "yesterday"
    if 'yesterday' in message_lower:
        from datetime import timedelta
        yesterday = datetime.now() - timedelta(days=1)
        return f"{yesterday.day}/{yesterday.month}/{yesterday.year}"
    
    # Extract date pattern
    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # 26/5/2025 or 26-5-2025
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2})',   # 26/5/25 or 26-5-25
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, message_text)
        if match:
            date_str = match.group(1)
            return normalize_date(date_str)
    
    return None

def check_authorization(user_phone, authorized_numbers):
    """
    Check if user's phone number is in the authorized list
    """
    if not user_phone:
        return False
    
    # Normalize phone number (remove +, spaces, etc.)
    user_phone_clean = re.sub(r'[^\d]', '', str(user_phone))
    
    # Check against each authorized number
    for auth_num in authorized_numbers:
        auth_num_clean = re.sub(r'[^\d]', '', str(auth_num))
        if user_phone_clean.endswith(auth_num_clean) or auth_num_clean.endswith(user_phone_clean):
            return True
    
    return False

def fetch_inquiries_by_date(sheets_data, target_date):
    """
    Fetch all inquiries for a specific date from sheets data
    Returns list of inquiry records
    """
    inquiries = []
    
    # Skip header row
    for row in sheets_data[1:]:
        if len(row) < 7:  # Need at least 7 columns
            continue
        
        date_str = row[0] if len(row) > 0 else ''
        status1 = row[1] if len(row) > 1 else ''
        status2 = row[2] if len(row) > 2 else ''
        company = row[3] if len(row) > 3 else ''
        inquiry_link = row[4] if len(row) > 4 else ''
        quotation_link = row[5] if len(row) > 5 else ''
        auth_number = row[6] if len(row) > 6 else ''
        
        # Normalize and compare dates
        if normalize_date(date_str) == target_date:
            inquiries.append({
                'date': date_str,
                'status1': status1,
                'status2': status2,
                'company': company,
                'inquiry': inquiry_link,
                'quotation': quotation_link,
                'authorized': auth_number
            })
    
    return inquiries

def format_inquiry_response(inquiries, date_str):
    """
    Format inquiries into a nice Telegram message
    """
    if not inquiries:
        return f"📭 No inquiries found for **{date_str}**"
    
    message = f"📋 **Inquiries for {date_str}**\n"
    message += f"Total: {len(inquiries)} inquiries\n\n"
    
    for idx, inq in enumerate(inquiries, 1):
        message += f"**{idx}. {inq['company']}**\n"
        
        # Add inquiry link
        if inq['inquiry'] and inq['inquiry'].startswith('http'):
            message += f"   📄 [View Inquiry]({inq['inquiry']})\n"
        
        # Add quotation link or price
        if inq['quotation']:
            if inq['quotation'].startswith('http'):
                message += f"   💰 [View Quotation]({inq['quotation']})\n"
            else:
                message += f"   💰 Quotation: {inq['quotation']}\n"
        
        # Add status if not PENDING
        if inq['status1'] and inq['status1'] != 'PENDING':
            message += f"   ⚡ Status: {inq['status1']}\n"
        
        message += "\n"
    
    return message.strip()

def get_all_authorized_numbers(sheets_data):
    """
    Extract all unique authorized numbers from the sheet
    """
    authorized = set()
    
    # Skip header row
    for row in sheets_data[1:]:
        if len(row) >= 7:
            auth_number = row[6]
            if auth_number:
                authorized.add(str(auth_number).strip())
    
    return list(authorized)
