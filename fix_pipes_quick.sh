#!/bin/bash
# Quick fix for pipe weights - run this on Railway

cd /app

# Backup current inventory
cp inventory.json inventory.json.backup

# Update pipe weights using Python
python3 << 'EOF'
import json

with open('inventory.json', 'r') as f:
    data = json.load(f)

# Update SRG pipes with correct weights
if 'SRG' in data:
    updates = {
        '114x87': -466.5,  # Negative weight (credit/return)
        '16x11.5': 46.7,
        '33.4x24.5': 38,
        '80x50': 46
    }
    
    for size, weight in updates.items():
        if size in data['SRG'] and '304L' in data['SRG'][size]:
            data['SRG'][size]['304L'][0]['weight'] = weight
            print(f"✅ Updated {size}: {weight} kg")

with open('inventory.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\n✅ Pipe weights updated!")
EOF

echo "Done! Restart the bot to load new inventory."
