import json
import os
import sys

# Add the current directory to the path so we can import the function
sys.path.append('.')

# Import the update function
from extract_product_from_pptx import update_products_json

def check_missing_slides():
    """Check which slides from 100-112 are missing from products.json"""
    
    # Load products.json
    with open('../products.json', 'r') as f:
        products = json.load(f)
    
    # Get all reference strings from products.json
    existing_refs = {p['data']['referenceString'] for p in products}
    
    # Check which slides 100-112 exist in the products folder
    missing_slides = []
    available_slides = []
    
    for slide_num in range(100, 113):
        filename = f'products/slide_{slide_num}_strapi_format.json'
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                payload = json.load(f)
                ref = payload['data']['referenceString']
                if ref not in existing_refs:
                    missing_slides.append((slide_num, ref, payload['data']['name']))
                else:
                    available_slides.append((slide_num, ref, payload['data']['name']))
    
    print(f"Available slides 100-112: {len(available_slides)}")
    for slide_num, ref, name in available_slides:
        print(f"  Slide {slide_num}: {name} (Ref: {ref})")
    
    print(f"\nMissing slides 100-112: {len(missing_slides)}")
    for slide_num, ref, name in missing_slides:
        print(f"  Slide {slide_num}: {name} (Ref: {ref})")
    
    return missing_slides

def update_missing_slides(missing_slides):
    """Update products.json with missing slides"""
    if not missing_slides:
        print("No missing slides to update!")
        return
    
    slide_payloads = []
    
    for slide_num, ref, name in missing_slides:
        filename = f'products/slide_{slide_num}_strapi_format.json'
        with open(filename, 'r') as f:
            payload = json.load(f)
            slide_payloads.append(payload)
            print(f"Loaded slide {slide_num}: {name} (Ref: {ref})")
    
    print(f"\nUpdating {len(slide_payloads)} missing slides...")
    
    # Run the update function
    update_products_json(slide_payloads, products_json_path="../products.json")
    
    print("Update completed!")

if __name__ == "__main__":
    print("Checking for missing slides 100-112...")
    missing_slides = check_missing_slides()
    
    if missing_slides:
        print(f"\nFound {len(missing_slides)} missing slides. Updating...")
        update_missing_slides(missing_slides)
    else:
        print("\nAll slides 100-112 are already in products.json!") 