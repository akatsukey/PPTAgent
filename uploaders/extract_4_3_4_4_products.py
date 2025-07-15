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

# Filter products with referenceString starting with 4.3 or 4.4
selected = [p for p in products if p['data']['referenceString'].startswith('4.3') or p['data']['referenceString'].startswith('4.4')]

print(f"Found {len(selected)} products with referenceString 4.3* or 4.4*")

# Save each as a separate JSON file
for p in selected:
    ref = p['data']['referenceString'].replace('.', '_')
    name = p['data']['name'].replace(' ', '_').replace('/', '_')
    filename = f'strapi_{ref}_{name}.json'
    out_path = os.path.join(OUTPUT_DIR, filename)
    with open(out_path, 'w', encoding='utf-8') as out:
        json.dump(p['data'], out, ensure_ascii=False, indent=2)
    print(f"Saved {out_path}") 