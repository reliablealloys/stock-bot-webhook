"""
Google Sheets helper for inquiry system
Fetches data from Google Sheets without authentication (public sheets)
"""

import requests
import logging

logger = logging.getLogger(__name__)

def fetch_sheet_data(sheet_id, range_name='Sheet1!A:Z'):
    """
    Fetch data from Google Sheets using public API
    Note: Sheet must be publicly accessible
    """
    try:
        # Use Google Sheets API v4 public endpoint
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json&sheet={range_name.split("!")[0]}'
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch sheet data: {response.status_code}")
            return None
        
        # Parse the response (it's JSONP, need to extract JSON)
        content = response.text
        
        # Remove JSONP wrapper
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]
        
        import json
        data = json.loads(json_str)
        
        # Extract rows
        rows = []
        if 'table' in data and 'rows' in data['table']:
            for row in data['table']['rows']:
                row_data = []
                if 'c' in row:
                    for cell in row['c']:
                        if cell is None:
                            row_data.append('')
                        elif 'v' in cell:
                            row_data.append(str(cell['v']))
                        else:
                            row_data.append('')
                rows.append(row_data)
        
        return rows
        
    except Exception as e:
        logger.error(f"Error fetching sheet data: {e}")
        return None
