#!/usr/bin/env python3
"""
Batch upload products to production Strapi with error tracking and progress monitoring
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

class BatchUploader:
    def __init__(self, batch_size=5):
        self.batch_size = batch_size
        self.uploaded_products = []
        self.failed_products = []
        self.session_start = datetime.now()
        
    def load_products(self):
        """Load all products from products.json"""
        try:
            with open('products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            print(f"✅ Loaded {len(products)} products from products.json")
            return products
        except Exception as e:
            print(f"❌ Error reading products.json: {e}")
            return []
    
    def upload_single_product(self, product, index):
        """Upload a single product and return result"""
        product_name = product.get('data', {}).get('name', 'Unknown')
        reference = product.get('data', {}).get('referenceString', 'No Reference')
        
        headers = {
            "Authorization": f"Bearer {STRAPI_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(PRODUCTION_URL, json=product, headers=headers)
            
            if response.status_code in (200, 201):
                result = response.json()
                product_id = result["data"]["id"]
                return {
                    'success': True,
                    'product_id': product_id,
                    'product_name': product_name,
                    'reference': reference,
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
    
    def upload_batch(self, products, start_index=0):
        """Upload a batch of products"""
        end_index = min(start_index + self.batch_size, len(products))
        batch_products = products[start_index:end_index]
        
        print(f"\n🚀 Uploading batch {start_index//self.batch_size + 1}")
        print(f"📦 Products {start_index + 1} to {end_index} of {len(products)}")
        print("=" * 60)
        
        batch_results = []
        
        for i, product in enumerate(batch_products):
            global_index = start_index + i
            print(f"\n📤 Uploading product {global_index + 1}/{len(products)}: {product.get('data', {}).get('name', 'Unknown')}")
            
            result = self.upload_single_product(product, global_index)
            
            if result['success']:
                print(f"✅ Success! ID: {result['product_id']}")
                self.uploaded_products.append({
                    'product_id': result['product_id'],
                    'product_name': result['product_name'],
                    'reference': result['reference'],
                    'upload_time': datetime.now().isoformat()
                })
            else:
                print(f"❌ Failed: {result['error']}")
                self.failed_products.append({
                    'product_name': result['product_name'],
                    'reference': result['reference'],
                    'error': result['error'],
                    'product_data': product,
                    'upload_time': datetime.now().isoformat()
                })
            
            batch_results.append(result)
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
        
        return batch_results
    
    def save_progress(self):
        """Save upload progress and failed products"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save uploaded products
        if self.uploaded_products:
            uploaded_file = f"uploaded_products_{timestamp}.json"
            with open(uploaded_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'uploaded_count': len(self.uploaded_products),
                    'uploaded_products': self.uploaded_products,
                    'session_start': self.session_start.isoformat(),
                    'session_end': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved uploaded products to: {uploaded_file}")
        
        # Save failed products
        if self.failed_products:
            failed_file = f"failed_products_{timestamp}.json"
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'failed_count': len(self.failed_products),
                    'failed_products': self.failed_products,
                    'session_start': self.session_start.isoformat(),
                    'session_end': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved failed products to: {failed_file}")
    
    def print_summary(self, total_products):
        """Print upload summary"""
        print("\n" + "=" * 60)
        print("📊 UPLOAD SUMMARY")
        print("=" * 60)
        print(f"📦 Total products: {total_products}")
        print(f"✅ Successfully uploaded: {len(self.uploaded_products)}")
        print(f"❌ Failed uploads: {len(self.failed_products)}")
        print(f"📈 Success rate: {(len(self.uploaded_products)/total_products)*100:.1f}%")
        
        if self.uploaded_products:
            print(f"\n✅ Successfully uploaded products:")
            for product in self.uploaded_products:
                print(f"   - {product['product_name']} (ID: {product['product_id']})")
        
        if self.failed_products:
            print(f"\n❌ Failed products:")
            for product in self.failed_products:
                print(f"   - {product['product_name']} ({product['reference']}): {product['error']}")
    
    def run_upload(self):
        """Main upload process"""
        print("🚀 Batch Product Upload to Production")
        print("=" * 60)
        
        if not STRAPI_TOKEN:
            print("❌ STRAPI_TOKEN environment variable not set")
            return False
        
        # Load products
        products = self.load_products()
        if not products:
            return False
        
        total_products = len(products)
        print(f"📋 Batch size: {self.batch_size}")
        print(f"📦 Total products to upload: {total_products}")
        print(f"🔄 Number of batches: {(total_products + self.batch_size - 1) // self.batch_size}")
        
        # Confirm before starting
        response = input(f"\n🤔 Proceed with uploading {total_products} products in batches of {self.batch_size}? (y/n): ")
        if response.lower() != 'y':
            print("❌ Upload cancelled")
            return False
        
        print(f"\n🚀 Starting upload at {datetime.now().strftime('%H:%M:%S')}")
        
        # Upload in batches
        for start_index in range(0, total_products, self.batch_size):
            self.upload_batch(products, start_index)
            
            # Ask if user wants to continue after each batch
            if start_index + self.batch_size < total_products:
                response = input(f"\n⏸️  Batch complete. Continue with next batch? (y/n): ")
                if response.lower() != 'y':
                    print("⏹️  Upload stopped by user")
                    break
        
        # Save progress and print summary
        self.save_progress()
        self.print_summary(total_products)
        
        return True

def main():
    # Configurable batch size
    batch_size = int(input("📦 Enter batch size (default 5): ") or "5")
    
    uploader = BatchUploader(batch_size)
    success = uploader.run_upload()
    
    if success:
        print("\n🎉 Batch upload process completed!")
    else:
        print("\n❌ Batch upload process failed!")

if __name__ == "__main__":
    main() 