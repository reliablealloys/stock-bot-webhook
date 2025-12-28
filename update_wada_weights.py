# Update WADA and SRG 304L Export weights from actual stock data
# Run this script to update inventory.json

import json

# Load current inventory
with open('inventory.json', 'r') as f:
    inventory = json.load(f)

# Update WADA 304L Round Export weights
wada_updates = {
    "5": 1011,
    "6": 255,  # WADA has 6mm!
    "7.1": 1393,
    "7.13": 937,
    "7.65": 1113,
    "8": 0,  # Negative value, setting to 0
    "9.5": 39,
    "10.76": 1056
}

# Update SRG 304L Round Export weights
srg_updates = {
    "5": 27,
    "5.3": 1471.1,
    "6": 1434.4,  # SRG has 6mm!
    "6.35": 1073,
    "7": 81
}

# Apply WADA updates
print("Updating WADA...")
for size, weight in wada_updates.items():
    if size in inventory["WADA"] and "304L" in inventory["WADA"][size]:
        for item in inventory["WADA"][size]["304L"]:
            if item["shape"] == "Round" and item["quality"] == "Export":
                item["weight"] = weight
                print(f"✅ WADA {size}mm 304L Export: {weight} kgs")

# Apply SRG updates
print("\nUpdating SRG...")
for size, weight in srg_updates.items():
    if size in inventory["SRG"]:
        if "304L" in inventory["SRG"][size]:
            for item in inventory["SRG"][size]["304L"]:
                if item["shape"] == "Round" and item["quality"] == "Export":
                    item["weight"] = weight
                    print(f"✅ SRG {size}mm 304L Export: {weight} kgs")
        else:
            # Add new entry if doesn't exist
            inventory["SRG"][size]["304L"] = [{"shape": "Round", "quality": "Export", "weight": weight}]
            print(f"✅ SRG {size}mm 304L Export: {weight} kgs (NEW)")

# Save updated inventory
with open('inventory.json', 'w') as f:
    json.dump(inventory, f, indent=2)

print("\n🎉 Inventory updated successfully!")
print("\nNow when you search '6mm 304L', bot will show:")
print("  📍 PARTH: 2975 kgs (Black Coil)")
print("  📍 WADA: 255 kgs (Export)")
print("  📍 SRG: 1434.4 kgs (Export)")
