"""
Google Sheets Sync Module for Stock Bot
Uses Bhindi API to fetch data from Google Sheets
"""

import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

SPREADSHEET_ID = '12O4S5zgXHq63fuTGxLTyAjYiC0lEPHZj8ERCFkbvI8s'
BHINDI_API_KEY = os.environ.get('BHINDI_API_KEY', '')
SHEET_NAMES = ['PARTH', 'WADA', 'SRG', 'TALOJA', 'SHEETS', 'RELIABLE ALLOYS']

def parse_sheet_data(sheet_name, raw_data):
    """Parse raw sheet data into inventory format"""
    inventory = {}
    
    if not raw_data or len(raw_data) < 3:
        return inventory
    
    # Find header row
    header_row_idx = None
    for idx, row in enumerate(raw_data):
        if len(row) > 2 and 'SIZE' in str(row).upper() and 'GRADE' in str(row).upper():
            header_row_idx = idx
            break
    
    if header_row_idx is None:
        logger.warning(f"No header row found in {sheet_name}")
        return inventory
    
    headers = [str(h).strip().upper() for h in raw_data[header_row_idx]]
    
    # Find column indices
    try:
        size_idx = headers.index('SIZE')
        shape_idx = headers.index('SHAPE')
        grade_idx = headers.index('GRADE')
    except ValueError as e:
        logger.error(f"Missing required columns in {sheet_name}: {e}")
        return inventory
    
    # Find weight column
    weight_idx = None
    for col_name in ['QUANTITY', 'WEIGHT', 'KGS']:
        try:
            weight_idx = headers.index(col_name)
            break
        except ValueError:
            continue
    
    if weight_idx is None:
        logger.warning(f"No weight column found in {sheet_name}")
        return inventory
    
    # Find quality column
    quality_idx = None
    for col_name in ['FINISH', 'QUALITY']:
        try:
            quality_idx = headers.index(col_name)
            break
        except ValueError:
            continue
    
    # Parse data rows
    for row in raw_data[header_row_idx + 1:]:
        if len(row) <= max(size_idx, shape_idx, grade_idx, weight_idx):
            continue
        
        try:
            size = str(row[size_idx]).strip()
            shape = str(row[shape_idx]).strip()
            grade = str(row[grade_idx]).strip()
            quality = str(row[quality_idx]).strip() if quality_idx and len(row) > quality_idx else ""
            
            # Parse weight - handle negative values and convert to 0
            weight_str = str(row[weight_idx]).strip() if len(row) > weight_idx else "0"
            weight_str = weight_str.replace(',', '').replace(' ', '')
            
            # Remove negative sign
            if weight_str.startswith('-'):
                weight = 0
            else:
                try:
                    weight = float(weight_str) if weight_str else 0
                except ValueError:
                    weight = 0
            
            # Skip invalid rows
            if not size or not grade or not shape or weight <= 0:
                continue
            
            # Skip header-like rows
            if size.upper() in ['SIZE', 'SHEET', 'ROUND', 'HEX', 'SQUARE', 'PIPE', 'PATTI']:
                continue
            
            # Skip rows with non-numeric sizes (except for pipes like "96X86")
            if 'X' not in size.upper():
                try:
                    float(size)
                except ValueError:
                    continue
            
            # Normalize grade
            grade = grade.upper()
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
                'weight': round(weight, 2)
            })
        
        except (ValueError, IndexError) as e:
            continue
    
    return inventory

def sync_from_google_sheets():
    """
    Sync inventory from Google Sheets
    Returns: (success: bool, inventory: dict, message: str)
    """
    try:
        # This will be called by the bot using Bhindi's Google Sheets integration
        # For now, return empty dict - the actual implementation will be in main.py
        return True, {}, "Sync function ready"
    except Exception as e:
        logger.error(f"Error syncing from Google Sheets: {e}")
        return False, {}, str(e)
