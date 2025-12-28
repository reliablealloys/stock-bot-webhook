import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
SPREADSHEET_ID = '12O4S5zgXHq63fuTGxLTyAjYiC0lEPHZj8ERCFkbvI8s'
SHEET_NAMES = ['PARTH', 'WADA', 'SRG', 'TALOJA', 'SHEETS', 'RELIABLE ALLOYS']

def connect_to_sheets():
    """Connect to Google Sheets"""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Use service account credentials from environment variable
    creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # Fallback to file-based credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)

def parse_sheet_data(sheet_name, worksheet):
    """Parse data from a worksheet"""
    all_values = worksheet.get_all_values()
    
    inventory = {}
    
    # Find the header row (usually row with SIZE, SHAPE, GRADE, etc.)
    header_row_idx = None
    for idx, row in enumerate(all_values):
        if 'SIZE' in row and 'GRADE' in row and 'SHAPE' in row:
            header_row_idx = idx
            break
    
    if header_row_idx is None:
        print(f"Warning: Could not find header row in {sheet_name}")
        return inventory
    
    headers = all_values[header_row_idx]
    
    # Find column indices
    size_idx = headers.index('SIZE') if 'SIZE' in headers else None
    shape_idx = headers.index('SHAPE') if 'SHAPE' in headers else None
    grade_idx = headers.index('GRADE') if 'GRADE' in headers else None
    quality_idx = headers.index('FINISH') if 'FINISH' in headers else (headers.index('QUALITY') if 'QUALITY' in headers else None)
    weight_idx = headers.index('QUANTITY') if 'QUANTITY' in headers else (headers.index('KGS') if 'KGS' in headers else None)
    
    if None in [size_idx, shape_idx, grade_idx, weight_idx]:
        print(f"Warning: Missing required columns in {sheet_name}")
        return inventory
    
    # Parse data rows
    for row in all_values[header_row_idx + 1:]:
        if len(row) <= max(size_idx, shape_idx, grade_idx, weight_idx):
            continue
        
        size = row[size_idx].strip()
        shape = row[shape_idx].strip()
        grade = row[grade_idx].strip()
        quality = row[quality_idx].strip() if quality_idx and len(row) > quality_idx else ""
        
        try:
            weight = float(row[weight_idx].replace(',', '')) if weight_idx and row[weight_idx] else 0
        except (ValueError, IndexError):
            weight = 0
        
        # Skip invalid rows
        if not size or not grade or not shape or weight <= 0:
            continue
        
        # Skip header-like rows
        if size.upper() in ['SIZE', 'SHEET', 'ROUND']:
            continue
        
        # Normalize grade
        if grade == '304':
            grade = '304L'
        elif grade == '316':
            grade = '316L'
        
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

def sync_inventory():
    """Sync inventory from Google Sheets to inventory.json"""
    print("Connecting to Google Sheets...")
    spreadsheet = connect_to_sheets()
    
    full_inventory = {}
    
    for sheet_name in SHEET_NAMES:
        print(f"Processing {sheet_name}...")
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            inventory = parse_sheet_data(sheet_name, worksheet)
            full_inventory[sheet_name] = inventory
            print(f"  ✓ {sheet_name}: {len(inventory)} sizes found")
        except Exception as e:
            print(f"  ✗ Error processing {sheet_name}: {e}")
    
    # Save to inventory.json
    with open('inventory.json', 'w') as f:
        json.dump(full_inventory, f, indent=2)
    
    print("\n✅ Inventory synced successfully!")
    print(f"Total locations: {len(full_inventory)}")
    for location, data in full_inventory.items():
        print(f"  {location}: {len(data)} sizes")

if __name__ == '__main__':
    sync_inventory()
