"""
MANUAL FIX INSTRUCTIONS
=======================

Run this command in Railway terminal:

python3 manual_fix_pipes.py

This will update the pipe weights in inventory.json
"""

import json
import sys

def fix_pipe_weights():
    print("🔧 Starting pipe weight fix...")
    
    try:
        # Read inventory
        with open('inventory.json', 'r') as f:
            data = json.load(f)
        
        print("✅ Loaded inventory.json")
        
        # Update SRG pipes
        updates = {
            '114x87': -466.5,
            '16x11.5': 46.7,
            '33.4x24.5': 38,
            '80x50': 46
        }
        
        if 'SRG' not in data:
            print("❌ SRG location not found!")
            return False
        
        for size, weight in updates.items():
            if size in data['SRG']:
                old_weight = data['SRG'][size]['304L'][0]['weight']
                data['SRG'][size]['304L'][0]['weight'] = weight
                print(f"✅ {size}: {old_weight} → {weight} kg")
            else:
                print(f"⚠️  {size} not found in SRG")
        
        # Write back
        with open('inventory.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("\n✅ SUCCESS! Pipe weights updated.")
        print("🔄 Restart the bot to load new data.")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    success = fix_pipe_weights()
    sys.exit(0 if success else 1)
