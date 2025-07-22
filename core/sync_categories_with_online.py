#!/usr/bin/env python3
"""
Sync Excel categories with online Strapi categories and identify missing ones
"""
import json
import pandas as pd
from pathlib import Path

def load_online_categories():
    """Load categories from online Strapi (from categories_map.json)"""
    try:
        with open('categories_map.json', 'r', encoding='utf-8') as f:
            categories_map = json.load(f)
        return categories_map
    except Exception as e:
        print(f"❌ Error loading online categories: {e}")
        return {}

def load_excel_categories():
    """Load unique categories from Excel file"""
    excel_path = Path("data/products.xlsx")
    
    if not excel_path.exists():
        print(f"❌ Excel file not found: {excel_path}")
        return {}
    
    try:
        # Load Excel with same logic as excel_to_json_custom.py
        df = pd.read_excel(excel_path, header=1)  # Use row 1 as header
        
        # Forward-fill category
        df[["PRODUCTS' CATEGORY"]] = df[["PRODUCTS' CATEGORY"]].fillna(method='ffill')
        
        # Get unique categories
        unique_categories = df["PRODUCTS' CATEGORY"].dropna().unique()
        excel_categories = {str(cat).strip(): True for cat in unique_categories if str(cat).strip()}
        
        print(f"✅ Loaded {len(excel_categories)} unique categories from Excel")
        return excel_categories
        
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        return {}

def find_closest_match(excel_category, online_categories):
    """Find the closest matching online category for an Excel category"""
    
    # Direct matches (case-insensitive)
    for online_cat in online_categories:
        if excel_category.upper() == online_cat.upper():
            return online_cat
    
    # Partial matches
    excel_lower = excel_category.lower()
    for online_cat in online_categories:
        online_lower = online_cat.lower()
        
        # Check if one contains the other
        if excel_lower in online_lower or online_lower in excel_lower:
            return online_cat
        
        # Check for key words
        excel_words = set(excel_lower.split())
        online_words = set(online_lower.split())
        if excel_words & online_words:  # intersection
            return online_cat
    
    # Manual mappings for specific cases
    manual_mappings = {
        "SCALP VEIN SETS": "Scalp vein sets",
        "INFUSION ACCESORIES": "Infusion Accessories", 
        "IV CANNULAS": "IV CANNULA",
        "ELECTRODES": "Electrodes",
        "URINARY CATHETERS": "Urinary Catheters",
        "URINE BAGS": "Urinary Catheters",  # Related to urinary system
        "ENDOTRACHEAL TUBES": "Suction Catheter",  # Respiratory/airway
        "ENDOBRONCHEAL TUBES": "Suction Catheter",  # Respiratory/airway
        "PHARINGEAL AIRWAYS": "Suction Catheter",  # Respiratory/airway
        "NASOPHARINGEAL AIRWAYS": "Suction Catheter",  # Respiratory/airway
        "LARYNGEAL MASKS": "Suction Catheter",  # Respiratory/airway
        "TRACHEOSTOMY": "Suction Catheter",  # Respiratory/airway
        "RESPIRATORY CIRCUITS": "Suction Catheter",  # Respiratory/airway
        "NASA OXYGEN CANNULA": "Suction Catheter",  # Respiratory/airway
        "RESPIRATORY MASKS": "Suction Catheter",  # Respiratory/airway
        "SUCTION TUBE + JANKAUER HANDLE": "Suction Catheter",  # Direct match
        "STOMACH TUBES": "Enteral Feeding Tubes",  # Feeding tubes
        "CENTRAL VENOUS CATHETERS (CVC)": "Hemodialysis Catheters",  # Vascular access
        "PRESSURE TRANSDUCERS": "Electrodes",  # Monitoring equipment
        "BLOOD EXTRACTION": "Blood lancets",  # Blood collection
        "DISPOSABLE NON-WOVEN OPERATION ROOMS": "Disposable Non-Woven Gourments",  # Surgical wear
    }
    
    return manual_mappings.get(excel_category, None)

def create_category_mapping(excel_categories, online_categories):
    """Create mapping from Excel categories to online categories"""
    
    mapping = {}
    unmapped = []
    
    print("\n🔍 Creating category mappings...")
    print("=" * 50)
    
    for excel_cat in excel_categories:
        closest_match = find_closest_match(excel_cat, online_categories)
        
        if closest_match:
            mapping[excel_cat] = closest_match
            print(f"✅ '{excel_cat}' → '{closest_match}'")
        else:
            unmapped.append(excel_cat)
            print(f"❌ '{excel_cat}' → No match found")
    
    return mapping, unmapped

def update_products_json(mapping):
    """Update products.json with online category names"""
    
    print("\n🔄 Updating products.json with online category names...")
    
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Error reading products.json: {e}")
        return False
    
    updated_count = 0
    
    for i, product in enumerate(products):
        product_data = product.get('data', {})
        current_category = product_data.get('categoryName', '')
        
        if current_category and current_category in mapping:
            new_category = mapping[current_category]
            product_data['categoryName'] = new_category
            updated_count += 1
            print(f"✅ Product {i+1}: '{current_category}' → '{new_category}'")
    
    # Save updated products
    try:
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Updated {updated_count} products in products.json")
        return True
        
    except Exception as e:
        print(f"❌ Error saving products.json: {e}")
        return False

def main():
    print("🔄 Category Sync with Online Strapi")
    print("=" * 50)
    
    # Load online categories
    online_categories = load_online_categories()
    if not online_categories:
        return
    
    print(f"📋 Online categories: {list(online_categories.keys())}")
    
    # Load Excel categories
    excel_categories = load_excel_categories()
    if not excel_categories:
        return
    
    print(f"📋 Excel categories: {list(excel_categories.keys())}")
    
    # Create mapping
    mapping, unmapped = create_category_mapping(excel_categories, online_categories)
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Excel categories: {len(excel_categories)}")
    print(f"   Online categories: {len(online_categories)}")
    print(f"   Mapped categories: {len(mapping)}")
    print(f"   Unmapped categories: {len(unmapped)}")
    
    # Update products.json
    if mapping:
        success = update_products_json(mapping)
        if success:
            print(f"\n🎉 Successfully mapped {len(mapping)} categories!")
        else:
            print("❌ Failed to update products.json")
    
    # Show unmapped categories that need to be created
    if unmapped:
        print(f"\n🚨 CATEGORIES TO CREATE IN ONLINE STRAPI:")
        print("=" * 50)
        for i, category in enumerate(unmapped, 1):
            print(f"{i:2d}. {category}")
        print(f"\n💡 Total: {len(unmapped)} categories need to be created in online Strapi")
        print("📝 After creating these categories, re-run this script to map them")
    else:
        print(f"\n✅ All categories are mapped! No new categories needed.")

if __name__ == "__main__":
    main() 