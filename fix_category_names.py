#!/usr/bin/env python3
"""
Fix category names for problematic products by extracting from Excel
"""
import json
import pandas as pd
from pathlib import Path

def load_problematic_products():
    """Load the list of problematic products"""
    try:
        with open('problematic_references.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['problematic_products'], data['reference_list']
    except Exception as e:
        print(f"❌ Error loading problematic products: {e}")
        return [], []

def load_excel_data():
    """Load the Excel file and extract category information"""
    excel_path = Path("data/products.xlsx")
    
    if not excel_path.exists():
        print(f"❌ Excel file not found: {excel_path}")
        return None
    
    try:
        # Load Excel with same logic as excel_to_json_custom.py
        df = pd.read_excel(excel_path, header=1)  # Use row 1 as header
        
        # Forward-fill category and divisions
        df[["PRODUCTS' CATEGORY", "Division", "Division.1", "Division.2"]] = (
            df[["PRODUCTS' CATEGORY", "Division", "Division.1", "Division.2"]].fillna(method='ffill')
        )
        
        print(f"✅ Loaded Excel with {len(df)} rows")
        return df
        
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        return None

def find_correct_categories(df, problematic_products):
    """Find correct category names from Excel for problematic products"""
    print("\n🔍 Searching for correct category names in Excel...")
    
    corrections = []
    
    for product in problematic_products:
        reference = product['reference']
        current_category = product['category_name']
        product_name = product['name']
        
        # Search in Excel by reference
        excel_row = df[df['Reference'] == reference]
        
        if not excel_row.empty:
            excel_category = excel_row.iloc[0]["PRODUCTS' CATEGORY"]
            excel_category = str(excel_category).strip() if pd.notna(excel_category) else ""
            
            corrections.append({
                'reference': reference,
                'product_name': product_name,
                'old_category': current_category,
                'new_category': excel_category,
                'found_in_excel': True
            })
            
            print(f"✅ {reference}: '{current_category}' → '{excel_category}'")
        else:
            corrections.append({
                'reference': reference,
                'product_name': product_name,
                'old_category': current_category,
                'new_category': "",
                'found_in_excel': False
            })
            
            print(f"❌ {reference}: Not found in Excel")
    
    return corrections

def update_products_json(corrections):
    """Update products.json with corrected category names"""
    print("\n🔄 Updating products.json with corrected category names...")
    
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Error reading products.json: {e}")
        return False
    
    updated_count = 0
    
    for correction in corrections:
        if not correction['found_in_excel']:
            continue
            
        # Find product by reference
        for product in products:
            product_data = product.get('data', {})
            if product_data.get('referenceString') == correction['reference']:
                # Update category name
                product_data['categoryName'] = correction['new_category']
                updated_count += 1
                print(f"✅ Updated {correction['product_name']}: '{correction['old_category']}' → '{correction['new_category']}'")
                break
    
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
    print("🔧 Category Name Fix Script")
    print("=" * 50)
    
    # Load problematic products
    problematic_products, reference_list = load_problematic_products()
    if not problematic_products:
        print("❌ No problematic products found")
        return
    
    print(f"📋 Found {len(problematic_products)} problematic products")
    
    # Load Excel data
    df = load_excel_data()
    if df is None:
        return
    
    # Find correct categories
    corrections = find_correct_categories(df, problematic_products)
    
    # Summary
    found_in_excel = [c for c in corrections if c['found_in_excel']]
    not_found = [c for c in corrections if not c['found_in_excel']]
    
    print(f"\n📊 Summary:")
    print(f"   Found in Excel: {len(found_in_excel)}")
    print(f"   Not found in Excel: {len(not_found)}")
    
    if not_found:
        print(f"\n❌ Products not found in Excel:")
        for correction in not_found:
            print(f"   - {correction['reference']}: {correction['product_name']}")
    
    # Update products.json
    if found_in_excel:
        success = update_products_json(corrections)
        if success:
            print(f"\n🎉 Successfully updated {len(found_in_excel)} products!")
            print("📝 Next step: Re-run the ID update script to get correct production IDs")
        else:
            print("❌ Failed to update products.json")
    else:
        print("❌ No corrections found in Excel")

if __name__ == "__main__":
    main() 