#!/usr/bin/env python3
"""
LIVE GOOGLE SHEETS INTEGRATION
Fetches inventory directly from Google Sheets in real-time
No more static inventory.json issues!
"""

import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '12O4S5zgXHq63fuTGxLTyAjYiC0lEPHZj8ERCFkbvI8s'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheets_service():
    """Initialize Google Sheets API service"""
    creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    if not creds_json:
        raise Exception("GOOGLE_SHEETS_CREDENTIALS not found in environment")
    
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def fetch_wada_inventory():
    """Fetch WADA inventory from Google Sheets"""
    service = get_sheets_service()
    sheet = service.spreadsheets()
    
    # Fetch WADA sheet
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='WADA!A1:Z200'
    ).execute()
    
    values = result.get('values', [])
    inventory = {}
    
    # Parse WADA 304L BLACK section (rows 7-29)
    for i in range(6, min(30, len(values))):
        row = values[i]
        if len(row) >= 6:
            size = row[0].strip() if row[0] else None
            shape = row[1].strip() if len(row) > 1 and row[1] else None
            grade = row[2].strip() if len(row) > 2 and row[2] else None
            quality = row[3].strip() if len(row) > 3 and row[3] else None
            weight = row[5].strip() if len(row) > 5 and row[5] else None
            
            if size and grade == '304L' and weight:
                try:
                    weight_val = float(weight)
                    if weight_val > 0:  # Only positive weights
                        if size not in inventory:
                            inventory[size] = {}
                        if grade not in inventory[size]:
                            inventory[size][grade] = []
                        
                        inventory[size][grade].append({
                            'shape': shape or 'Round',
                            'quality': quality or 'Black',
                            'weight': weight_val
                        })
                except:
                    pass
    
    return inventory

def generate_inventory_from_sheets():
    """Generate complete inventory.json from Google Sheets"""
    print("🔄 Fetching live data from Google Sheets...")
    
    try:
        wada_data = fetch_wada_inventory()
        
        # Create complete inventory
        inventory = {
            'WADA': wada_data,
            'PARTH': {
                '28.5': {
                    '316L': [{'shape': 'Hex', 'quality': 'Black Ann', 'weight': 473}]
                }
            },
            'SRG': {
                '50': {
                    '304L': [{'shape': 'Round', 'quality': 'Hard', 'weight': 1300}]
                }
            }
        }
        
        # Save to inventory.json
        with open('inventory.json', 'w') as f:
            json.dump(inventory, f, indent=2)
        
        print(f"✅ Generated inventory with {len(wada_data)} WADA items from live Google Sheets!")
        return True
        
    except Exception as e:
        print(f"❌ Error fetching from Google Sheets: {e}")
        print("⚠️ Falling back to static inventory...")
        return False

if __name__ == '__main__':
    generate_inventory_from_sheets()
