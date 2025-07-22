#!/usr/bin/env python3
"""
List problematic products with their reference numbers and category names
"""
import json

def main():
    print("🚨 Problematic Products Analysis")
    print("=" * 60)
    
    # Load products.json
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Error reading products.json: {e}")
        return
    
    # Load production mappings
    try:
        with open('categories_map.json', 'r', encoding='utf-8') as f:
            categories_map = json.load(f)
    except Exception as e:
        print(f"❌ Error reading categories_map.json: {e}")
        return
    
    print(f"📊 Analyzing {len(products)} products...")
    print(f"📋 Production categories available: {list(categories_map.keys())}")
    print()
    
    problematic_products = []
    
    for i, product in enumerate(products):
        product_data = product.get('data', {})
        category_name = product_data.get('categoryName', '')
        reference = product_data.get('referenceString', '')
        name = product_data.get('name', '')
        
        # Check if category name is missing or not in production mapping
        if not category_name or category_name not in categories_map:
            problematic_products.append({
                'index': i + 1,
                'reference': reference,
                'name': name,
                'category_name': category_name,
                'issue': 'Missing category name' if not category_name else f'Category not in production: "{category_name}"'
            })
    
    print(f"🚨 Found {len(problematic_products)} problematic products:")
    print("=" * 60)
    
    for product in problematic_products:
        print(f"📦 Product {product['index']}: {product['name']}")
        print(f"   Reference: {product['reference']}")
        print(f"   Category: '{product['category_name']}'")
        print(f"   Issue: {product['issue']}")
        print()
    
    # Group by issue type
    missing_categories = [p for p in problematic_products if not p['category_name']]
    invalid_categories = [p for p in problematic_products if p['category_name'] and p['category_name'] not in categories_map]
    
    print("📊 Summary:")
    print(f"   Products with missing category names: {len(missing_categories)}")
    print(f"   Products with invalid category names: {len(invalid_categories)}")
    print(f"   Total problematic products: {len(problematic_products)}")
    
    # Save reference list for the fix script
    reference_list = [p['reference'] for p in problematic_products]
    
    with open('problematic_references.json', 'w', encoding='utf-8') as f:
        json.dump({
            'problematic_products': problematic_products,
            'reference_list': reference_list,
            'total_count': len(problematic_products)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved detailed list to: problematic_references.json")
    print("📝 Next step: Run fix script to extract correct category names from Excel")

if __name__ == "__main__":
    main() 