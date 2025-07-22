#!/usr/bin/env python3
"""
Test production Strapi connection and fetch current mappings
"""
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")
PRODUCTION_URL = "https://adminpanel.lets-med.com/api"

def test_connection():
    """Test connection to production Strapi"""
    print("🔗 Testing connection to production Strapi...")
    print(f"URL: {PRODUCTION_URL}")
    print(f"Token available: {'✅' if STRAPI_TOKEN else '❌'}")
    
    if not STRAPI_TOKEN:
        print("❌ STRAPI_TOKEN not found in .env file")
        return False
    
    headers = {
        "Authorization": f"Bearer {STRAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test basic connection
        response = requests.get(f"{PRODUCTION_URL}/categories", headers=headers)
        print(f"Categories endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def fetch_production_mappings():
    """Fetch current category and division mappings from production"""
    print("\n📊 Fetching production mappings...")
    
    headers = {
        "Authorization": f"Bearer {STRAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Fetch categories
    print("📋 Fetching categories...")
    categories_response = requests.get(f"{PRODUCTION_URL}/categories?pagination[limit]=100", headers=headers)
    
    if categories_response.status_code != 200:
        print(f"❌ Failed to fetch categories: {categories_response.status_code}")
        return None, None
    
    # Fetch divisions
    print("🏢 Fetching divisions...")
    divisions_response = requests.get(f"{PRODUCTION_URL}/divisions?pagination[limit]=100", headers=headers)
    
    if divisions_response.status_code != 200:
        print(f"❌ Failed to fetch divisions: {divisions_response.status_code}")
        return None, None
    
    # Parse categories
    categories_data = categories_response.json()
    production_categories = {}
    for category in categories_data.get("data", []):
        category_id = category["id"]
        category_name = category["attributes"]["name"]
        production_categories[category_name] = category_id
        print(f"  Category: {category_name} (ID: {category_id})")
    
    # Parse divisions
    divisions_data = divisions_response.json()
    production_divisions = {}
    for division in divisions_data.get("data", []):
        division_id = division["id"]
        division_name = division["attributes"]["name"]
        production_divisions[division_name] = division_id
        print(f"  Division: {division_name} (ID: {division_id})")
    
    print(f"\n✅ Fetched {len(production_categories)} categories and {len(production_divisions)} divisions from production")
    
    return production_categories, production_divisions

def compare_mappings(production_categories, production_divisions):
    """Compare production mappings with local mappings"""
    print("\n🔍 Comparing mappings...")
    
    # Load local mappings
    try:
        with open('categories_map.json', 'r') as f:
            local_categories = json.load(f)
        with open('divisions_map.json', 'r') as f:
            local_divisions = json.load(f)
    except Exception as e:
        print(f"❌ Error loading local mappings: {e}")
        return
    
    print("\n📊 CATEGORIES COMPARISON:")
    print("=" * 50)
    
    # Compare categories
    for name, local_id in local_categories.items():
        production_id = production_categories.get(name)
        if production_id:
            if str(local_id) == str(production_id):
                print(f"✅ {name}: {local_id} (matches)")
            else:
                print(f"⚠️  {name}: Local={local_id}, Production={production_id} (DIFFERENT)")
        else:
            print(f"❌ {name}: {local_id} (missing in production)")
    
    # Check for new categories in production
    for name, production_id in production_categories.items():
        if name not in local_categories:
            print(f"🆕 {name}: {production_id} (new in production)")
    
    print("\n🏢 DIVISIONS COMPARISON:")
    print("=" * 50)
    
    # Compare divisions
    for name, local_id in local_divisions.items():
        production_id = production_divisions.get(name)
        if production_id:
            if str(local_id) == str(production_id):
                print(f"✅ {name}: {local_id} (matches)")
            else:
                print(f"⚠️  {name}: Local={local_id}, Production={production_id} (DIFFERENT)")
        else:
            print(f"❌ {name}: {local_id} (missing in production)")
    
    # Check for new divisions in production
    for name, production_id in production_divisions.items():
        if name not in local_divisions:
            print(f"🆕 {name}: {production_id} (new in production)")

def main():
    print("🚀 Production Connection Test")
    print("=" * 50)
    
    # Test connection
    if not test_connection():
        print("❌ Cannot proceed without connection")
        return
    
    # Fetch production mappings
    production_categories, production_divisions = fetch_production_mappings()
    
    if not production_categories or not production_divisions:
        print("❌ Cannot proceed without mappings")
        return
    
    # Compare mappings
    compare_mappings(production_categories, production_divisions)
    
    print("\n✅ Test completed!")
    print("📝 Next steps:")
    print("  1. Review the mapping differences above")
    print("  2. Update local mappings if needed")
    print("  3. Proceed with product upload test")

if __name__ == "__main__":
    main() 