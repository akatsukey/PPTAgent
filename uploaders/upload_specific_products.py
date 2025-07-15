#!/usr/bin/env python3
"""
Upload specific products directly to Strapi API
"""
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")
STRAPI_URL = "http://localhost:1337/api/medical-products"

def upload_product_directly(json_file_path):
    """Upload a single product JSON file to Strapi"""
    
    print(f"📤 Uploading {json_file_path}...")
    
    # Read the JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {json_file_path}: {e}")
        return False
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {STRAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Make the POST request
    try:
        response = requests.post(STRAPI_URL, json=payload, headers=headers)
        
        if response.status_code in (200, 201):
            result = response.json()
            product_id = result["data"]["id"]
            product_name = result["data"]["attributes"]["name"]
            print(f"✅ Successfully created product: {product_name} (ID: {product_id})")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def main():
    print("🚀 Direct Product Uploader")
    print("=" * 40)
    
    # Check if token is available
    if not STRAPI_TOKEN:
        print("❌ STRAPI_TOKEN not found in .env file")
        print("Please make sure you have a valid API token with write permissions")
        return
    
    # List of specific products to upload
    products_to_upload = [
        "products/product_4.3.2_SAFETY_SCALP_VEIN_SETS.json",
        "products/product_4.5.1_INFUSION_SETS.json", 
        "products/product_4.8.2_UV-LIGHT_PROOF_CONVENTIONAL_EXTENSION_TUBES.json"
    ]
    
    print(f"📁 Uploading {len(products_to_upload)} specific products:")
    for product in products_to_upload:
        print(f"  - {product}")
    
    print("\n" + "=" * 40)
    
    # Upload each product
    success_count = 0
    for product_file in products_to_upload:
        if os.path.exists(product_file):
            success = upload_product_directly(product_file)
            if success:
                success_count += 1
        else:
            print(f"❌ File not found: {product_file}")
    
    print(f"\n🎉 Upload complete! {success_count}/{len(products_to_upload)} products uploaded successfully.")

if __name__ == "__main__":
    main() 