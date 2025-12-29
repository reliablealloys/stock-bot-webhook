"""
Patch to add /fix command to main.py
Run this to add the command
"""

with open('main.py', 'r') as f:
    content = f.read()

# Find the /refresh command and add /fix after it
old_code = '''            elif text.startswith('/refresh'):
                global INVENTORY
                INVENTORY = load_inventory()
                response = f"✅ Inventory refreshed! Loaded {len(INVENTORY)} locations."
            else:'''

new_code = '''            elif text.startswith('/refresh'):
                global INVENTORY
                INVENTORY = load_inventory()
                response = f"✅ Inventory refreshed! Loaded {len(INVENTORY)} locations."
            elif text.startswith('/fix'):
                try:
                    import subprocess
                    result = subprocess.run(['python3', 'one_click_fix.py'], 
                                          capture_output=True, text=True, timeout=30)
                    global INVENTORY
                    INVENTORY = load_inventory()
                    response = f"✅ FIX APPLIED!\\\\n\\\\nLoaded {len(INVENTORY)} locations\\\\n\\\\nTest: scrap, 8mm 304l"
                    logger.info(f"Fix output: {result.stdout}")
                except Exception as e:
                    response = f"❌ Error: {str(e)}"
                    logger.error(f"Fix error: {e}")
            else:'''

content = content.replace(old_code, new_code)

with open('main.py', 'w') as f:
    f.write(content)

print("✅ Added /fix command to main.py!")
