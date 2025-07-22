#!/usr/bin/env python3
"""
Test uploading one product to production Strapi
"""
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")
PRODUCTION_URL = "https://adminpanel.lets-med.com/api/medical-products"

def upload_product_to_production(product_data):
    """Upload a product to production Strapi"""
    
    product_name = product_data['data']['name']
    print(f"📤 Uploading {product_name} to production...")
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {STRAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Make the POST request
    try:
        response = requests.post(PRODUCTION_URL, json=product_data, headers=headers)
        
        if response.status_code in (200, 201):
            result = response.json()
            product_id = result["data"]["id"]
            product_name = result["data"]["attributes"]["name"]
            print(f"✅ Successfully created product: {product_name} (ID: {product_id})")
            print(f"🌐 View in admin: https://adminpanel.lets-med.com/admin/content-manager/collectionType/api::medical-product.medical-product/{product_id}")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def main():
    print("🚀 Production Upload Test")
    print("=" * 50)
    
    # Check if token is available
    if not STRAPI_TOKEN:
        print("❌ STRAPI_TOKEN not found in .env file")
        return
    
    # Load products.json
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            all_products = json.load(f)
    except Exception as e:
        print(f"❌ Error reading products.json: {e}")
        return
    
    # Find a product with valid category mapping
    test_product = None
    for product in all_products:
        product_data = product.get('data', {})
        category_name = product_data.get('categoryName', '')
        
        # Skip products with missing or problematic category names
        if category_name and category_name.strip() and not category_name.startswith('SCALP VEIN SETS'):
            test_product = product
            break
    
    if not test_product:
        print("❌ No suitable test product found")
        return
    
    product_name = test_product['data']['name']
    category_name = test_product['data']['categoryName']
    divisions = test_product['data'].get('divisions', [])
    
    print(f"🎯 Selected test product: {product_name}")
    print(f"   Category: {category_name}")
    print(f"   Divisions: {divisions}")
    print(f"   Slug: {test_product['data'].get('slug', 'N/A')}")
    
    # Upload the product
    success = upload_product_to_production(test_product)
    
    if success:
        print("\n🎉 Production upload test successful!")
        print("📝 Next steps:")
        print("   1. Check the admin panel to verify the product")
        print("   2. Test the frontend URL if available")
        print("   3. Proceed with bulk upload if everything looks good")
    else:
        print("\n❌ Production upload test failed")
        print("📝 Check the error message above and verify:")
        print("   1. API token has write permissions")
        print("   2. Network connectivity to production")
        print("   3. Product data format is correct")

if __name__ == "__main__":
    main() 