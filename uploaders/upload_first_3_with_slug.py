#!/usr/bin/env python3
"""
Upload the first 3 products with a slug from products.json to Strapi API
"""
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")
STRAPI_URL = "http://localhost:1337/api/medical-products"


def upload_product_directly(product_data):
    """Upload a product data directly to Strapi"""
    product_name = product_data['data']['name']
    print(f"\U0001F4E4 Uploading {product_name}...")
    headers = {
        "Authorization": f"Bearer {STRAPI_TOKEN}",
        "Content-Type": "application/json"
    }
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
    # Load products.json (adjust path if needed)
    with open('../products.json', 'r', encoding='utf-8') as f:
        all_products = json.load(f)
    # Filter for products with a slug
    products_with_slug = [p for p in all_products if p.get('data', {}).get('slug')]
    # Take the first 3
    selected_products = products_with_slug[:3]
    print(f"Found {len(selected_products)} products with a slug. Uploading...")
    for i, product in enumerate(selected_products, 1):
        print(f"\nUploading product {i}/{len(selected_products)}:")
        upload_product_directly(product)

if __name__ == "__main__":
    main() 