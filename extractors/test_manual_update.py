import json
import sys
import os

# Add the current directory to the path so we can import the function
sys.path.append('.')

# Import the update function
from extract_product_from_pptx import update_products_json

# Load the extracted data from slides 100-112
slide_payloads = []

# Load all the slide files from 100-112
for slide_num in range(100, 113):
    filename = f'products/slide_{slide_num}_strapi_format.json'
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            payload = json.load(f)
            slide_payloads.append(payload)
            print(f"Loaded slide {slide_num}: {payload['data']['name']} (Ref: {payload['data']['referenceString']})")

print(f"\nLoaded {len(slide_payloads)} slide payloads")

# Run the update function
update_products_json(slide_payloads, products_json_path="../products.json")

print("\nUpdate completed!") 