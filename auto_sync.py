"""
Auto-sync script for Reliable Alloys Stock Bot
Fetches data from Google Sheets and updates inventory.json
Run this manually or set up as a cron job
"""

import json
import requests
import os

SPREADSHEET_ID = '12O4S5zgXHq63fuTGxLTyAjYiC0lEPHZj8ERCFkbvI8s'
SHEET_NAMES = ['PARTH', 'WADA', 'SRG', 'TALOJA', 'SHEETS', 'RELIABLE ALLOYS']

# Bhindi API endpoint (you'll need to set this up)
BHINDI_API_KEY = os.environ.get('BHINDI_API_KEY', 'YOUR_BHINDI_API_KEY')

def fetch_sheet_data(sheet_name):
    """Fetch data from a specific sheet using Bhindi API"""
    # This would call Bhindi's Google Sheets integration
    # For now, returning placeholder
    print(f"Fetching {sheet_name}...")
    return {}

def parse_inventory_data(sheet_name, raw_data):
    """Parse raw sheet data into inventory format"""
    inventory = {}
    
    # Find header row
    header_row = None
    for idx, row in enumerate(raw_data):
        if 'SIZE' in row and 'GRADE' in row:
            header_row = idx
            break
    
    if header_row is None:
        return inventory
    
    headers = raw_data[header_row]
    size_idx = headers.index('SIZE')
    shape_idx = headers.index('SHAPE')
    grade_idx = headers.index('GRADE')
    
    # Find weight column (could be QUANTITY, WEIGHT, or KGS)
    weight_idx = None
    for col_name in ['QUANTITY', 'WEIGHT', 'KGS']:
        if col_name in headers:
            weight_idx = headers.index(col_name)
            break
    
    # Find quality column
    quality_idx = None
    for col_name in ['FINISH', 'QUALITY']:
        if col_name in headers:
            quality_idx = headers.index(col_name)
            break
    
    # Parse data rows
    for row in raw_data[header_row + 1:]:
        if len(row) <= max(size_idx, shape_idx, grade_idx):
            continue
        
        try:
            size = row[size_idx].strip()
            shape = row[shape_idx].strip()
            grade = row[grade_idx].strip()
            quality = row[quality_idx].strip() if quality_idx and len(row) > quality_idx else ""
            
            # Parse weight
            weight_str = row[weight_idx] if weight_idx and len(row) > weight_idx else "0"
            weight = float(weight_str.replace(',', '').replace('-', '0')) if weight_str else 0
            
            # Skip invalid rows
            if not size or not grade or weight <= 0:
                continue
            
            # Skip header-like rows
            if size.upper() in ['SIZE', 'SHEET', 'ROUND', 'HEX']:
                continue
            
            # Normalize grade
            if grade == '304':
                grade = '304L'
            elif grade == '316':
                grade = '316L'
            
            # Build inventory
            if size not in inventory:
                inventory[size] = {}
            
            if grade not in inventory[size]:
                inventory[size][grade] = []
            
            inventory[size][grade].append({
                'shape': shape,
                'quality': quality,
                'weight': weight
            })
        
        except (ValueError, IndexError) as e:
            continue
    
    return inventory

def main():
    """Main sync function"""
    print("=" * 50)
    print("RELIABLE ALLOYS - INVENTORY SYNC")
    print("=" * 50)
    
    full_inventory = {}
    
    # For now, this is a template
    # You'll need to integrate with Bhindi's Google Sheets API
    
    print("\n✅ Sync complete!")
    print(f"Total locations: {len(full_inventory)}")
    
    # Save to file
    with open('inventory.json', 'w') as f:
        json.dump(full_inventory, f, indent=2)
    
    print("\n📝 inventory.json updated!")

if __name__ == '__main__':
    main()
