import json
import os

# This script updates pipe weights in inventory.json
def update_pipe_weights():
    try:
        with open('inventory.json', 'r') as f:
            data = json.load(f)
        
        # Update SRG pipes
        updates = {
            '114x87': -466.5,  # Negative = credit/return
            '16x11.5': 46.7,
            '33.4x24.5': 38,
            '80x50': 46
        }
        
        for size, weight in updates.items():
            if size in data.get('SRG', {}):
                data['SRG'][size]['304L'][0]['weight'] = weight
                print(f"✅ Updated {size}: {weight} kg")
        
        with open('inventory.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("\n✅ All pipe weights updated successfully!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    update_pipe_weights()
