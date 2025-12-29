web: python3 generate_fixed_inventory.py && cp inventory_FIXED.json inventory.json && python3 add_scrap_search.py && gunicorn main:app --workers 1 --timeout 120 --log-level debug
