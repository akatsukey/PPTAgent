#!/usr/bin/env python3
"""
Re-upload failed products with fixes
"""
import json
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")
PRODUCTION_URL = "https://adminpanel.lets-med.com/api/medical-products"

def load_failed_products():
    """Load failed products from the latest failed_products file"""
    import glob
    failed_files = glob.glob("failed_products_*.json")
    if not failed_files:
        print("❌ No failed products file found")
        return []
    
    # Get the latest file
    latest_file = max(failed_files)
    print(f"📁 Loading failed products from: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['failed_products']
    except Exception as e:
        print(f"❌ Error reading failed products: {e}")
        return []

def fix_product_slugs(product_data):
    """Fix duplicate slugs by adding timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    old_slug = product_data['data']['slug']
    new_slug = f"{old_slug}-{timestamp}"
    product_data['data']['slug'] = new_slug
    return product_data

def upload_single_product(product_data, index):
    """Upload a single product and return result"""
    product_name = product_data['data']['name']
    reference = product_data['data']['referenceString']
    
    # Fix slug if it's a duplicate
    if product_name in ["INSULINE SYRINGES", "HYPODERMIC 2-PARTS SYRINGES", 
                       "LIGHT PROOF HYPODERMIC SYRINGES", "ORAL/FEEDING SYRINGES"]:
        product_data = fix_product_slugs(product_data)
    
    headers = {
        "Authorization": f"Bearer {STRAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(PRODUCTION_URL, json=product_data, headers=headers)
        
        if response.status_code in (200, 201):
            result = response.json()
            product_id = result["data"]["id"]
            return {
                'success': True,
                'product_id': product_id,
                'product_name': product_name,
                'reference': reference,
                'new_slug': product_data['data']['slug'],
                'response': result
            }
        else:
            return {
                'success': False,
                'product_name': product_name,
                'reference': reference,
                'error': f"HTTP {response.status_code}: {response.text}",
                'response': response.text
            }
            
    except Exception as e:
        return {
            'success': False,
            'product_name': product_name,
            'reference': reference,
            'error': f"Network error: {str(e)}",
            'response': None
        }

def main():
    print("🔄 Re-uploading Failed Products")
    print("=" * 50)
    
    if not STRAPI_TOKEN:
        print("❌ STRAPI_TOKEN environment variable not set")
        return False
    
    # Load failed products
    failed_products = load_failed_products()
    if not failed_products:
        print("❌ No failed products to re-upload")
        return False
    
    print(f"📦 Found {len(failed_products)} failed products to re-upload")
    
    # Confirm before starting
    response = input(f"\n🤔 Proceed with re-uploading {len(failed_products)} failed products? (y/n): ")
    if response.lower() != 'y':
        print("❌ Re-upload cancelled")
        return False
    
    print(f"\n🚀 Starting re-upload at {datetime.now().strftime('%H:%M:%S')}")
    
    successful_uploads = []
    failed_uploads = []
    
    for i, failed_product in enumerate(failed_products, 1):
        product_data = failed_product['product_data']
        print(f"\n📤 Re-uploading product {i}/{len(failed_products)}: {product_data['data']['name']}")
        print(f"   Reference: {product_data['data']['referenceString']}")
        print(f"   Category: {product_data['data']['categoryName']} (ID: {product_data['data']['category']})")
        print(f"   Divisions: {product_data['data'].get('divisionNames', [])} (IDs: {product_data['data']['divisions']})")
        
        result = upload_single_product(product_data, i)
        
        if result['success']:
            print(f"✅ Success! ID: {result['product_id']}")
            if 'new_slug' in result:
                print(f"   New slug: {result['new_slug']}")
            successful_uploads.append(result)
        else:
            print(f"❌ Failed: {result['error']}")
            failed_uploads.append(result)
        
        # Small delay
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 RE-UPLOAD SUMMARY")
    print("=" * 60)
    print(f"📦 Total failed products: {len(failed_products)}")
    print(f"✅ Successfully re-uploaded: {len(successful_uploads)}")
    print(f"❌ Still failed: {len(failed_uploads)}")
    
    if successful_uploads:
        print(f"\n✅ Successfully re-uploaded products:")
        for product in successful_uploads:
            print(f"   - {product['product_name']} (ID: {product['product_id']})")
    
    if failed_uploads:
        print(f"\n❌ Still failed products:")
        for product in failed_uploads:
            print(f"   - {product['product_name']} ({product['reference']}): {product['error']}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Re-upload process completed!")
    else:
        print("\n❌ Re-upload process failed!") 