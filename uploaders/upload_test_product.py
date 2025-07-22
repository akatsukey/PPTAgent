#!/usr/bin/env python3
"""
Upload test product to production Strapi
"""
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")
PRODUCTION_URL = "https://adminpanel.lets-med.com/api/medical-products"

def upload_test_product():
    """Upload the BLOOD EXTRACTION TUBES' HOLDERS product to production"""
    
    print("🚀 Test Product Upload to Production")
    print("=" * 50)
    
    if not STRAPI_TOKEN:
        print("❌ STRAPI_TOKEN environment variable not set")
        return False
    
    # Load the specific product from products.json
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Error reading products.json: {e}")
        return False
    
    # Find the BLOOD EXTRACTION TUBES' HOLDERS product
    test_product = None
    for product in products:
        product_name = product.get('data', {}).get('name', '')
        if "BLOOD EXTRACTION TUBES" in product_name and "HOLDERS" in product_name:
            test_product = product
            break
    
    if not test_product:
        print("❌ Test product not found in products.json")
        return False
    
    print(f"📦 Found test product: {test_product['data']['name']}")
    print(f"📋 Reference: {test_product['data']['referenceString']}")
    print(f"📂 Category: {test_product['data']['categoryName']} (ID: {test_product['data']['category']})")
    print(f"🏷️  Divisions: {test_product['data']['divisionNames']} (IDs: {test_product['data']['divisions']})")
    print(f"🔗 Slug: {test_product['data']['slug']}")
    print(f"📝 Description: {test_product['data']['description'][:100]}...")
    print()
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {STRAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("📤 Uploading to production Strapi...")
    print(f"🌐 URL: {PRODUCTION_URL}")
    
    try:
        response = requests.post(PRODUCTION_URL, json=test_product, headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code in (200, 201):
            result = response.json()
            product_id = result["data"]["id"]
            product_name = result["data"]["attributes"]["name"]
            print(f"✅ Successfully uploaded product!")
            print(f"   Product ID: {product_id}")
            print(f"   Product Name: {product_name}")
            print(f"   View in admin: https://adminpanel.lets-med.com/admin/content-manager/collectionType/api::medical-product.medical-product/{product_id}")
            return True
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def main():
    success = upload_test_product()
    if success:
        print("\n🎉 Test upload successful!")
        print("📝 You can now proceed with uploading all products")
    else:
        print("\n❌ Test upload failed!")
        print("📝 Please check the error and fix before proceeding")

if __name__ == "__main__":
    main() 