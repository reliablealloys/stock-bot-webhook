web: cp inventory_working.json inventory.json && python3 patch_scrap_search.py && gunicorn main:app --workers 1 --timeout 120 --log-level debug
