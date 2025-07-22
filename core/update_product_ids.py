#!/usr/bin/env python3
"""
Update category and division IDs in products.json to match production mappings
"""
import json
import os
from typing import Dict, List, Any

def load_mappings():
    """Load the updated category and division mappings"""
    print("📋 Loading updated mappings...")
    
    try:
        with open('categories_map.json', 'r', encoding='utf-8') as f:
            categories_map = json.load(f)
        
        with open('divisions_map.json', 'r', encoding='utf-8') as f:
            divisions_map = json.load(f)
        
        print(f"✅ Loaded {len(categories_map)} categories and {len(divisions_map)} divisions")
        return categories_map, divisions_map
        
    except Exception as e:
        print(f"❌ Error loading mappings: {e}")
        return None, None

def load_products():
    """Load the products.json file"""
    print("📦 Loading products.json...")
    
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"✅ Loaded {len(products)} products")
        return products
        
    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return None

def update_product_ids(products: List[Dict], categories_map: Dict, divisions_map: Dict):
    """Update category and division IDs in products"""
    print("\n🔄 Updating product IDs...")
    
    updated_count = 0
    errors = []
    
    for i, product in enumerate(products):
        product_data = product.get('data', {})
        
        # Get current values
        current_category_id = product_data.get('category')
        current_divisions = product_data.get('divisions', [])
        category_name = product_data.get('categoryName', '')
        division_names = product_data.get('divisionNames', [])
        
        print(f"\n📦 Product {i+1}: {product_data.get('name', 'Unknown')}")
        print(f"   Current category ID: {current_category_id}")
        print(f"   Current divisions: {current_divisions}")
        
        # Update category ID
        if category_name and category_name in categories_map:
            new_category_id = categories_map[category_name]
            if current_category_id != new_category_id:
                product_data['category'] = new_category_id
                print(f"   ✅ Updated category: {current_category_id} → {new_category_id}")
                updated_count += 1
            else:
                print(f"   ✅ Category already correct: {current_category_id}")
        else:
            print(f"   ⚠️  Category name not found in mapping: '{category_name}'")
            errors.append(f"Product {i+1}: Category '{category_name}' not found")
        
        # Update division IDs
        if division_names and isinstance(division_names, list):
            new_divisions = []
            for div_name in division_names:
                if div_name in divisions_map:
                    new_divisions.append(divisions_map[div_name])
                else:
                    print(f"   ⚠️  Division name not found: '{div_name}'")
                    errors.append(f"Product {i+1}: Division '{div_name}' not found")
            
            if new_divisions:
                product_data['divisions'] = new_divisions
                print(f"   ✅ Updated divisions: {current_divisions} → {new_divisions}")
                updated_count += 1
            else:
                print(f"   ⚠️  No valid divisions found")
        else:
            print(f"   ⚠️  No division names available")
    
    print(f"\n📊 Summary:")
    print(f"   Products processed: {len(products)}")
    print(f"   Updates made: {updated_count}")
    print(f"   Errors: {len(errors)}")
    
    if errors:
        print(f"\n❌ Errors found:")
        for error in errors:
            print(f"   - {error}")
    
    return products, updated_count, errors

def save_updated_products(products: List[Dict]):
    """Save the updated products back to products.json"""
    print("\n💾 Saving updated products...")
    
    try:
        # Create backup
        backup_filename = 'products_backup.json'
        with open('products.json', 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_filename, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print(f"✅ Created backup: {backup_filename}")
        
        # Save updated products
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print("✅ Updated products.json successfully")
        
    except Exception as e:
        print(f"❌ Error saving products: {e}")
        return False
    
    return True

def main():
    print("🚀 Product ID Update Script")
    print("=" * 50)
    
    # Load mappings
    categories_map, divisions_map = load_mappings()
    if not categories_map or not divisions_map:
        print("❌ Cannot proceed without mappings")
        return
    
    # Load products
    products = load_products()
    if not products:
        print("❌ Cannot proceed without products")
        return
    
    # Update product IDs
    updated_products, update_count, errors = update_product_ids(products, categories_map, divisions_map)
    
    # Save updated products
    if save_updated_products(updated_products):
        print(f"\n🎉 Successfully updated {update_count} products!")
        print("📝 Next steps:")
        print("   1. Review the backup file if needed")
        print("   2. Test uploading a product to production")
        print("   3. Verify the product appears correctly in Strapi admin")
    else:
        print("❌ Failed to save updated products")

if __name__ == "__main__":
    main() 