#!/usr/bin/env python3
"""
Convert Excel products to JSON format for Strapi import.

Usage:
    python excel_to_json.py products.xlsx products.json
    python excel_to_json.py products.xlsx products.json --mappings /path/to/mappings
"""

import os
import sys
import json
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional


def check_dependencies():
    """Check if required packages are installed."""
    missing_packages = []
    
    try:
        import pandas
    except ImportError:
        missing_packages.append("pandas")
    
    if missing_packages:
        print(f"Error: Missing packages: {', '.join(missing_packages)}")
        print(f"Install with: pip install {' '.join(missing_packages)}")
        sys.exit(1)


def load_mappings(mappings_dir: Path) -> tuple[Dict[str, str], Dict[str, str]]:
    """Load category and division mappings from JSON files."""
    categories_file = mappings_dir / "categories_map.json"
    divisions_file = mappings_dir / "divisions_map.json"
    
    if not categories_file.exists():
        print(f"Error: {categories_file} not found")
        sys.exit(1)
    
    if not divisions_file.exists():
        print(f"Error: {divisions_file} not found")
        sys.exit(1)
    
    with open(categories_file, 'r', encoding='utf-8') as f:
        categories_map = json.load(f)
    
    with open(divisions_file, 'r', encoding='utf-8') as f:
        divisions_map = json.load(f)
    
    return categories_map, divisions_map


def parse_divisions(divisions_str: str) -> List[int]:
    """Parse divisions string into list of integers."""
    if pd.isna(divisions_str) or not divisions_str:
        return []
    
    try:
        # Split by comma and convert to integers
        return [int(x.strip()) for x in str(divisions_str).split(',') if x.strip()]
    except ValueError:
        return []


def get_division_names(division_ids: List[int], divisions_map: Dict[str, str]) -> tuple[List[str], List[int]]:
    """Get division names from IDs and return missing IDs."""
    names = []
    missing_ids = []
    for div_id in division_ids:
        div_id_str = str(div_id)
        if div_id_str in divisions_map:
            names.append(divisions_map[div_id_str])
        else:
            missing_ids.append(div_id)
    return names, missing_ids


def process_row(row: pd.Series, categories_map: Dict[str, str], 
                divisions_map: Dict[str, str]) -> tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """Process a single Excel row into Strapi format and return validation info."""
    validation_info = {
        "has_category": False,
        "has_divisions": False,
        "missing_category_id": None,
        "missing_division_ids": [],
        "row_index": None
    }
    
    try:
        # Parse divisions
        division_ids = parse_divisions(row.get('divisions', ''))
        division_names, missing_division_ids = get_division_names(division_ids, divisions_map)
        
        # Track division validation
        validation_info["has_divisions"] = len(division_ids) > 0
        validation_info["missing_division_ids"] = missing_division_ids
        
        # Get category info
        category_id = row.get('category', '')
        category_name = ""
        category_found = False
        
        if category_id:
            if str(category_id) in categories_map:
                category_name = categories_map[str(category_id)]
                category_found = True
                validation_info["has_category"] = True
            else:
                validation_info["missing_category_id"] = category_id
        
        # Second layer of security: Skip products with missing mappings
        if not category_found or missing_division_ids:
            return None, validation_info
        
        # Build product object
        product = {
            "data": {
                "name": str(row.get('name', '')),
                "referenceString": str(row.get('referenceString', '')),
                "standard": str(row.get('standard', '')),
                "description": str(row.get('description', '')),
                "tableInMd": str(row.get('tableInMd', '')),
                "category": int(category_id) if category_id else None,
                "categoryName": category_name,
                "divisions": division_ids,
                "divisionNames": division_names,
                "images": [],
                "PackagingInformation": {
                    "packing_per_inner_box": 0,
                    "inner_boxes_per_carton": 0,
                    "loading_capacity_20GP": 0,
                    "loading_capacity_40HC": 0,
                    "additional_notes": "Not specified"
                }
            }
        }
        
        return product, validation_info
        
    except Exception as e:
        print(f"Error processing row: {e}")
        return None, validation_info


def main():
    """Main function."""
    check_dependencies()
    
    parser = argparse.ArgumentParser(description="Convert Excel products to JSON for Strapi import")
    parser.add_argument("input_file", help="Input Excel file path")
    parser.add_argument("output_file", help="Output JSON file path")
    parser.add_argument("--mappings", default=".", help="Directory containing mapping files (default: current)")
    args = parser.parse_args()
    
    # Check input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_path} not found")
        sys.exit(1)
    
    # Load mappings
    mappings_dir = Path(args.mappings)
    categories_map, divisions_map = load_mappings(mappings_dir)
    
    # Read Excel file
    try:
        df = pd.read_excel(input_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)
    
    # Forward-fill category and divisions so blanks inherit the value above
    df[['category', 'divisions']] = (
        df[['category', 'divisions']].fillna(method='ffill')
    )
    
    # Print detected columns
    print(f"Detected columns: {list(df.columns)}")
    print(f"Processing {len(df)} rows...")
    
    # Process rows
    products = []
    skipped = 0
    validation_results = []
    
    for index, row in df.iterrows():
        product, validation_info = process_row(row, categories_map, divisions_map)
        validation_info["row_index"] = index + 1  # 1-based row number
        
        if product:
            products.append(product)
        else:
            skipped += 1
            validation_results.append(validation_info)
    
    # Write output
    output_path = Path(args.output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"Converted {len(products)} rows ({skipped} skipped) ➜ {output_path}")
    
    # Print validation summary
    if validation_results:
        print("\n" + "="*60)
        print("🔍 VALIDATION SUMMARY - Products with Missing Mappings")
        print("="*60)
        
        missing_categories = []
        missing_divisions = []
        
        for result in validation_results:
            row_num = result["row_index"]
            product_name = df.iloc[row_num - 1].get('name', 'Unknown')
            ref_string = df.iloc[row_num - 1].get('referenceString', 'Unknown')
            
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
                print(f"  Row {item['row']}: '{item['name']}' (Ref: {item['reference']}) - Category ID: {item['category_id']}")
        
        # Print missing divisions
        if missing_divisions:
            print(f"\n❌ Missing Divisions ({len(missing_divisions)} products):")
            for item in missing_divisions:
                print(f"  Row {item['row']}: '{item['name']}' (Ref: {item['reference']}) - Division IDs: {item['division_ids']}")
        
        print(f"\n💡 Tip: Update your Excel file with correct IDs or add missing categories/divisions to Strapi")
        print("="*60)


if __name__ == "__main__":
    main() 