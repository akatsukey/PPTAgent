import json
import os

# Paths
PRODUCTS_JSON = '../products.json'
OUTPUT_DIR = 'products'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load products.json
with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
    products = json.load(f)

# Specific reference strings to extract
target_refs = ['4.3.2', '4.5.1', '4.8.2']

# Filter products with specific reference strings
selected = [p for p in products if p['data']['referenceString'] in target_refs]

print(f"Found {len(selected)} products with specified reference strings")

# Save each as a separate JSON file in the correct format for upload
for p in selected:
    ref = p['data']['referenceString']
    name = p['data']['name'].replace(' ', '_').replace('/', '_')
    filename = f'product_{ref}_{name}.json'
    out_path = os.path.join(OUTPUT_DIR, filename)
    
    # Save in the format expected by upload_product.py: { "data": {...} }
    with open(out_path, 'w', encoding='utf-8') as out:
        json.dump({"data": p['data']}, out, ensure_ascii=False, indent=2)
    print(f"Saved {out_path}")

print("\nProducts ready for upload:")
for p in selected:
    print(f"- {p['data']['name']} (Ref: {p['data']['referenceString']})") 