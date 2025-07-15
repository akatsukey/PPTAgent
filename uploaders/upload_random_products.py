#!/usr/bin/env python3
"""
Upload 5 random products to Strapi API
"""
import json
import os
import requests
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")
STRAPI_URL = "http://localhost:1337/api/medical-products"

def upload_product_directly(product_data):
    """Upload a product data directly to Strapi"""
    
    product_name = product_data['data']['name']
    print(f"📤 Uploading {product_name}...")
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {STRAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Make the POST request
    try:
        response = requests.post(STRAPI_URL, json=product_data, headers=headers)
        
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
    print("🎲 Random Product Uploader (5 Products)")
    print("=" * 50)
    
    # Check if token is available
    if not STRAPI_TOKEN:
        print("❌ STRAPI_TOKEN not found in .env file")
        print("Please make sure you have a valid API token with write permissions")
        return
    
    # Load products.json
    try:
        with open('../products.json', 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except Exception as e:
        print(f"❌ Error reading products.json: {e}")
        return
    
    # Randomly select 5 products
    selected_products = random.sample(all_products, 5)
    
    print(f"🎯 Randomly selected {len(selected_products)} products:")
    for i, product in enumerate(selected_products, 1):
        name = product['data']['name']
        ref = product['data']['referenceString']
        print(f"  {i}. {name} (Ref: {ref})")
    
    print("\n" + "=" * 50)
    
    # Upload each product
    success_count = 0
    for i, product in enumerate(selected_products, 1):
        print(f"\n📦 Uploading product {i}/5...")
        success = upload_product_directly(product)
        if success:
            success_count += 1
        else:
            print(f"⚠️  Skipping due to upload error (likely missing category/division)")
    
    print(f"\n🎉 Upload complete! {success_count}/{len(selected_products)} products uploaded successfully.")
    
    if success_count < len(selected_products):
        print(f"⚠️  {len(selected_products) - success_count} products failed to upload.")
        print("   This is usually due to missing category or division mappings in Strapi.")

if __name__ == "__main__":
    main() 