#!/usr/bin/env python3
"""
Map Excel category names to production category names
"""
import json

def create_category_mapping():
    """Create a mapping from Excel category names to production category names"""
    
    # Production categories available
    production_categories = {
        "Condoms": 209,
        "Syringes": 210,
        "Needles": 211,
        "Scalp vein sets": 212,
        "Blood lancets": 213,
        "Infusion Sets": 214,
        "Infusion Accessories": 215,
        "Transfusion Sets": 216,
        "Extension Tubes": 217,
        "IV CANNULA": 218,
        "Electrodes": 219,
        "Gloves": 220,
        "Adhesive tapes & dressings": 221,
        "Gauze": 222,
        "Disposable Non-Woven Gourments": 223,
        "Suction Catheter": 224,
        "Urinary Catheters": 225,
        "Enteral Feeding Tubes": 226,
        "Hemodialysis Catheters": 227
    }
    
    # Mapping from Excel categories to production categories
    excel_to_production_mapping = {
        # Direct matches (case-insensitive)
        "URINARY CATHETERS": "Urinary Catheters",
        "SCALP VEIN SETS": "Scalp vein sets",
        "INFUSION ACCESORIES": "Infusion Accessories",
        "IV CANNULAS": "IV CANNULA",
        "ELECTRODES": "Electrodes",
        
        # Logical mappings
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
    
    return excel_to_production_mapping, production_categories

def update_products_with_mapping():
    """Update products.json with mapped category names"""
    
    excel_to_production_mapping, production_categories = create_category_mapping()
    
    print("🔧 Category Mapping Script")
    print("=" * 50)
    print(f"📋 Production categories: {list(production_categories.keys())}")
    print(f"📋 Excel to production mappings: {len(excel_to_production_mapping)}")
    print()
    
    # Load products
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"❌ Error reading products.json: {e}")
        return
    
    updated_count = 0
    unmapped_categories = set()
    
    for i, product in enumerate(products):
        product_data = product.get('data', {})
        current_category = product_data.get('categoryName', '')
        
        if current_category and current_category in excel_to_production_mapping:
            new_category = excel_to_production_mapping[current_category]
            product_data['categoryName'] = new_category
            updated_count += 1
            print(f"✅ Product {i+1}: '{current_category}' → '{new_category}'")
        elif current_category and current_category not in production_categories:
            unmapped_categories.add(current_category)
            print(f"⚠️  Product {i+1}: '{current_category}' - No mapping found")
    
    # Save updated products
    try:
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Updated {updated_count} products in products.json")
        
        if unmapped_categories:
            print(f"\n⚠️  Unmapped categories: {list(unmapped_categories)}")
            print("💡 These categories need to be added to production Strapi or mapped manually")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving products.json: {e}")
        return False

def main():
    success = update_products_with_mapping()
    if success:
        print("\n🎉 Category mapping completed!")
        print("📝 Next step: Re-run the ID update script to get correct production IDs")
    else:
        print("\n❌ Category mapping failed!")

if __name__ == "__main__":
    main() 