# Update WADA 304L Export weights from actual stock data
# Run this script to update inventory.json

import json

# Load current inventory
with open('inventory.json', 'r') as f:
    inventory = json.load(f)

# Update WADA 304L Round Export weights
wada_updates = {
    "5": 1011,
    "6": 255,  # THIS IS THE KEY ONE!
    "7.1": 1393,
    "7.13": 937,
    "7.65": 1113,
    "8": 0,  # Negative value, setting to 0
    "9.5": 39,
    "10.76": 1056
}

# Apply updates
for size, weight in wada_updates.items():
    if size in inventory["WADA"] and "304L" in inventory["WADA"][size]:
        for item in inventory["WADA"][size]["304L"]:
            if item["shape"] == "Round" and item["quality"] == "Export":
                item["weight"] = weight
                print(f"Updated WADA {size}mm 304L Export: {weight} kgs")

# Save updated inventory
with open('inventory.json', 'w') as f:
    json.dump(inventory, f, indent=2)

print("\n✅ Inventory updated successfully!")
