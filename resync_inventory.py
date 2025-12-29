"""
COMPLETE INVENTORY RESYNC FROM GOOGLE SHEETS
=============================================

This script fetches fresh data from Google Sheets and rebuilds inventory.json

Run in Railway terminal:
python3 resync_inventory.py
"""

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SHEET_ID = '12O4S5zgXHq63fuTGxLTyAjYiC0lEPHZj8ERCFkbvI8s'

def get_sheets_service():
    """Initialize Google Sheets API service"""
    creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    if not creds_json:
        raise Exception("GOOGLE_SHEETS_CREDENTIALS not found!")
    
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    return build('sheets', 'v4', credentials=creds)

def parse_sheet_data(sheet_name, range_name):
    """Parse data from a specific sheet"""
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!{range_name}'
    ).execute()
    
    values = result.get('values', [])
    inventory = {}
    
    for row in values:
        if len(row) < 6:
            continue
        
        size = row[0].strip().upper()
        shape = row[1].strip().upper() if len(row) > 1 else ''
        grade = row[2].strip().upper() if len(row) > 2 else ''
        quality = row[3].strip() if len(row) > 3 else ''
        weight_str = row[5].strip() if len(row) > 5 else '0'
        
        # Skip headers and empty rows
        if not size or size == 'SIZE' or not grade:
            continue
        
        try:
            weight = float(weight_str)
        except:
            continue
        
        # Build inventory structure
        if size not in inventory:
            inventory[size] = {}
        
        if grade not in inventory[size]:
            inventory[size][grade] = []
        
        inventory[size][grade].append({
            'shape': shape,
            'quality': quality,
            'weight': weight
        })
    
    return inventory

def resync_all():
    """Resync all locations"""
    print("🔄 Starting complete inventory resync...")
    
    locations = {
        'SRG': 'A1:F500',
        'WADA': 'A1:F500',
        'PARTH': 'A1:F500',
        'TALOJA': 'A1:F500',
        'SHEETS': 'A1:F500',
        'RELIABLE ALLOYS': 'A1:F500'
    }
    
    full_inventory = {}
    
    for location, range_name in locations.items():
        print(f"📥 Syncing {location}...")
        try:
            data = parse_sheet_data(location, range_name)
            full_inventory[location] = data
            print(f"✅ {location}: {len(data)} items")
        except Exception as e:
            print(f"⚠️  {location} failed: {e}")
    
    # Save to inventory.json
    with open('inventory.json', 'w') as f:
        json.dump(full_inventory, f, indent=2)
    
    print("\n✅ RESYNC COMPLETE!")
    print("🔄 Restart the bot to load new data.")

if __name__ == '__main__':
    resync_all()
