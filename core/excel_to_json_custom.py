#!/usr/bin/env python3
"""
Custom Excel to JSON product extractor for the specific products.xlsx format.
Focuses on Category, Reference, Name, and 3 Division columns only.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import pandas as pd
except ImportError:
    print("❌ pandas is required but not installed.")
    print("💡 Install with: pip install pandas openpyxl")
    sys.exit(1)

def load_mappings() -> tuple[Dict[str, str], Dict[str, str]]:
    """Load category and division mappings from JSON files."""
    try:
        with open("categories_map.json", 'r', encoding='utf-8') as f:
            categories_map = json.load(f)
        with open("divisions_map.json", 'r', encoding='utf-8') as f:
            divisions_map = json.load(f)
        return categories_map, divisions_map
    except FileNotFoundError:
        print("⚠️  Warning: Mapping files not found. Using hardcoded mappings.")
        return {}, {}

def parse_divisions(division1: str, division2: str, division3: str, divisions_map: Dict[str, str]) -> tuple[List[int], List[int]]:
    """Parse division columns and return division IDs and missing IDs."""
    division_ids = []
    missing_ids = []
    
    # Process each division column
    for division in [division1, division2, division3]:
        if pd.notna(division) and division and str(division).strip():
            # Try to find division ID by name (case-insensitive)
            found = False
            for div_id, div_name in divisions_map.items():
                if div_name.upper() == str(division).upper():
                    division_ids.append(int(div_id))
                    found = True
                    break
            
            if not found:
                # Try hardcoded mapping for common divisions
                hardcoded_divisions = {
                    "INJECTION": 48,
                    "DIABETES CARE": 49,
                    "INFUSION": 47,
                    "DIAGNOSTIC": 50,
                    "PROTECTION": 56,
                    "WOUND MANAGEMENT": 54,
                    "UROLOGY": 53,
                    "ANESTHESIA / RESPIRATORY": 58,
                    "NUTRITION": 52,
                    "HEMODIALYSIS": 51,
                }
                
                div_id = hardcoded_divisions.get(str(division).upper())
                if div_id:
                    division_ids.append(div_id)
                else:
                    missing_ids.append(division)
    
    return division_ids, missing_ids

def map_category_to_id(category_name: str, categories_map: Dict[str, str]) -> tuple[int, bool]:
    """Map category name to Strapi category ID and return if found."""
    # Try to find category by name in the mapping (case-insensitive)
    for cat_id, cat_name in categories_map.items():
        if cat_name.upper() == category_name.upper():
            return int(cat_id), True
    
    # Fallback to hardcoded mapping for missing categories
    category_mapping = {
        "SYRINGES": 59,
        "NEEDLES": 60,
        "SCALP VEIN SETS": 61,
        "BLOOD LANCETS": 62,
        "INFUSION SETS": 63,
        "INFUSION ACCESORIES": 64,
        "TRANSFUSION SETS": 65,
        "EXTENSION TUBES": 66,
        "IV CANNULAS": 67,
        "GLOVES": 68,
        "CONDOMS": 69,
        "ADHESIVE TAPES & DRESSINGS": 70,
        "GAUZE": 71,
        "DISPOSABLE NON-WOVEN GOURMENTS": 72,
        "URINARY CATHETERS": 73,
        "HEMODIALYSIS CATHETERS": 74,
        "SUCTION CATHETER": 75,
        "ENTERAL FEEDING TUBES": 76,
        # Add more mappings for missing categories
        "BLOOD EXTRACTION": 77,
        "CENTRAL VENOUS CATHETERS (CVC)": 78,
        "ELECTRODES": 79,
        "ENDOBRONCHEAL TUBES": 80,
        "ENDOTRACHEAL TUBES": 81,
        "LARYNGEAL MASKS": 82,
        "NASA OXYGEN CANNULA": 83,
        "NASOPHARINGEAL AIRWAYS": 84,
        "PHARINGEAL AIRWAYS": 85,
        "PRESSURE TRANSDUCERS": 86,
        "RESPIRATORY CIRCUITS": 87,
        "RESPIRATORY MASKS": 88,
        "STOMACH TUBES": 89,
        "SUCTION TUBE + JANKAUER HANDLE": 90,
        "TRACHEOSTOMY": 91,
        "URINE BAGS": 92,
        "DISPOSABLE NON-WOVEN OPERATION ROOMS": 93,
    }
    
    category_id = category_mapping.get(category_name.upper(), 59)  # Default to SYRINGES
    return category_id, False

def convert_row_to_strapi_format(row: pd.Series, categories_map: Dict[str, str], 
                                divisions_map: Dict[str, str]) -> tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """Convert a single row to Strapi format and return validation info."""
    validation_info = {
        "has_category": False,
        "has_divisions": False,
        "missing_category_id": None,
        "missing_division_ids": [],
        "row_index": None
    }
    
    # Extract data from the 4 requested columns
    category_name = str(row["PRODUCTS' CATEGORY"]) if pd.notna(row["PRODUCTS' CATEGORY"]) else ""
    reference_string = str(row["Reference"]) if pd.notna(row["Reference"]) else ""
    product_name = str(row["PRODUCTS"]) if pd.notna(row["PRODUCTS"]) else ""
    division1 = str(row["Division"]) if pd.notna(row["Division"]) else ""
    division2 = str(row["Division.1"]) if pd.notna(row["Division.1"]) else ""
    division3 = str(row["Division.2"]) if pd.notna(row["Division.2"]) else ""
    
    # Skip rows without proper data (need both reference and name)
    if not reference_string or reference_string == "nan" or not product_name or product_name == "nan":
        return None, validation_info
    
    # Get category info
    category_id_int, category_found = map_category_to_id(category_name, categories_map)
    validation_info["has_category"] = category_found
    if not category_found:
        validation_info["missing_category_id"] = category_name
    
    # Get category name from mapping
    category_name_from_map = ""
    if category_found:
        category_name_from_map = categories_map.get(str(category_id_int), category_name)
    else:
        category_name_from_map = category_name
    
    # Get division info from the 3 division columns
    division_ids, missing_division_ids = parse_divisions(division1, division2, division3, divisions_map)
    validation_info["has_divisions"] = len(division_ids) > 0
    validation_info["missing_division_ids"] = missing_division_ids
    
    # Get division names from mapping
    division_names = []
    for div_id in division_ids:
        div_name = divisions_map.get(str(div_id), f"Division {div_id}")
        division_names.append(div_name)
    
    # Process all products, even with missing mappings (for debugging)
    # if not category_found or missing_division_ids:
    #     return None, validation_info
    
    product_data = {
        "name": product_name,
        "referenceString": reference_string,
        "category": category_id_int,
        "categoryName": category_name_from_map,
        "divisions": division_ids,
        "divisionNames": division_names,
        "standard": "???",
        "description": "",
        "tableInMd": "",
        "images": [],
        "PackagingInformation": {
            "packing_per_inner_box": 0,
            "inner_boxes_per_carton": 0,
            "loading_capacity_20GP": 0,
            "loading_capacity_40HC": 0,
            "additional_notes": "Not specified"
        }
    }
    
    return {"data": product_data}, validation_info

def main():
    """Main function."""
    input_file = "data/products.xlsx"
    output_file = "products.json"
    
    # Check input file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)
    
    try:
        # Load mappings
        print("📋 Loading mappings...")
        categories_map, divisions_map = load_mappings()
        
        # Load Excel file with proper header
        print(f"📖 Loading {input_path}...")
        df = pd.read_excel(input_path, header=1)  # Use row 1 as header
        
        # Forward-fill category and divisions so blanks inherit the value above
        df[["PRODUCTS' CATEGORY", "Division", "Division.1", "Division.2"]] = (
            df[["PRODUCTS' CATEGORY", "Division", "Division.1", "Division.2"]].fillna(method='ffill')
        )
        
        print(f"📋 Found {len(df)} total rows")
        
        # Convert rows to Strapi format
        print(f"\n🔄 Converting products...")
        products = []
        skipped = 0
        validation_results = []
        
        for index, row in df.iterrows():
            try:
                product, validation_info = convert_row_to_strapi_format(row, categories_map, divisions_map)
                validation_info["row_index"] = index + 1  # 1-based row number
                
                if product:
                    products.append(product)
                    print(f"✅ {product['data']['name']} ({product['data']['referenceString']})")
                else:
                    skipped += 1
                    validation_results.append(validation_info)
            except Exception as e:
                print(f"⚠️  Warning: Error processing row {index + 1}: {e}")
                continue
        
        # Write JSON output
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Converted {len(products)} products ({skipped} skipped) to JSON -> {output_path}")
        
        # Print validation summary
        if validation_results:
            print("\n" + "="*60)
            print("🔍 VALIDATION SUMMARY - Products with Missing Mappings")
            print("="*60)
            
            missing_categories = []
            missing_divisions = []
            
            for result in validation_results:
                row_num = result["row_index"]
                product_name = df.iloc[row_num - 1].get("PRODUCTS", 'Unknown')
                ref_string = df.iloc[row_num - 1].get("Reference", 'Unknown')
                
                if result["missing_category_id"]:
                    missing_categories.append({
                        "row": row_num,
                        "name": product_name,
                        "reference": ref_string,
                        "category_id": result["missing_category_id"]
                    })
                
                if result["missing_division_ids"]:
                    missing_divisions.append({
                        "row": row_num,
                        "name": product_name,
                        "reference": ref_string,
                        "division_ids": result["missing_division_ids"]
                    })
            
            # Print missing categories
            if missing_categories:
                print(f"\n❌ Missing Categories ({len(missing_categories)} products):")
                for item in missing_categories:
                    print(f"  Row {item['row']}: '{item['name']}' (Ref: {item['reference']}) - Category: {item['category_id']}")
            
            # Print missing divisions
            if missing_divisions:
                print(f"\n❌ Missing Divisions ({len(missing_divisions)} products):")
                for item in missing_divisions:
                    print(f"  Row {item['row']}: '{item['name']}' (Ref: {item['reference']}) - Division IDs: {item['division_ids']}")
            
            print(f"\n💡 Tip: Update your Excel file with correct IDs or add missing categories/divisions to Strapi")
            print("="*60)
        
    except Exception as e:
        print(f"❌ Error processing Excel file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 