#!/usr/bin/env python3
"""
Upload JSON products to Strapi API
"""
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")
STRAPI_URL = "http://localhost:1337/api/medical-products"

def upload_product(json_file_path):
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

def list_available_files():
    """List all available JSON files"""
    products_dir = "products"
    if not os.path.exists(products_dir):
        print("❌ Products directory not found")
        return []
    
    json_files = [f for f in os.listdir(products_dir) if f.endswith('.json')]
    return json_files

def main():
    print("🚀 Strapi Product Uploader")
    print("=" * 40)
    
    # Check if token is available
    if not STRAPI_TOKEN:
        print("❌ STRAPI_TOKEN not found in .env file")
        print("Please make sure you have a valid API token with write permissions")
        return
    
    # List available files
    json_files = list_available_files()
    if not json_files:
        print("❌ No JSON files found in products/ directory")
        return
    
    print(f"📁 Found {len(json_files)} JSON files:")
    for i, filename in enumerate(json_files, 1):
        print(f"  {i}. {filename}")
    
    # Ask user which file to upload
    while True:
        try:
            choice = input(f"\n📌 Enter file number (1-{len(json_files)}) or 'q' to quit: ")
            
            if choice.lower() == 'q':
                print("👋 Exiting.")
                break
            
            file_index = int(choice) - 1
            if 0 <= file_index < len(json_files):
                selected_file = json_files[file_index]
                file_path = os.path.join("products", selected_file)
                
                # Upload the product
                success = upload_product(file_path)
                
                if success:
                    # Ask if user wants to upload another
                    continue_choice = input(f"\n🔄 Upload another file? (y/n): ")
                    if continue_choice.lower() != 'y':
                        print("👋 Exiting.")
                        break
                else:
                    print("⚠️ Upload failed. Please check your API token permissions.")
                    break
            else:
                print("❌ Invalid file number. Please try again.")
                
        except ValueError:
            print("❌ Please enter a valid number or 'q'.")
        except KeyboardInterrupt:
            print("\n👋 Exiting.")
            break

if __name__ == "__main__":
    main() 