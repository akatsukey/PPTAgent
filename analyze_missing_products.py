#!/usr/bin/env python3
import pandas as pd
import json

def analyze_data():
    # Read Excel data
    df = pd.read_excel('./data/Index VER 8.xlsx', sheet_name='Sheet1')
    
    # Read enriched data
    with open('./output/products_enriched.json', 'r') as f:
        enriched_data = json.load(f)
    
    print("=== DATA ANALYSIS ===")
    print(f"Total rows in Excel: {len(df)}")
    print(f"Unique reference IDs in Excel: {len(df['ID.1'].dropna().unique())}")
    print(f"Products in enriched data: {len(enriched_data)}")
    
    # Get all reference IDs from Excel
    excel_refs = set(df['ID.1'].dropna().unique())
    enriched_refs = set(p['data']['referenceString'] for p in enriched_data)
    
    print(f"\n=== MISSING PRODUCTS ===")
    print("Products in Excel but not in enriched data:")
    missing_in_enriched = excel_refs - enriched_refs
    print(f"Count: {len(missing_in_enriched)}")
    print("References:", sorted(missing_in_enriched))
    
    print(f"\n=== PRODUCTS NOT IN EXCEL ===")
    print("Products in enriched data but not in Excel:")
    missing_in_excel = enriched_refs - excel_refs
    print(f"Count: {len(missing_in_excel)}")
    print("References:", sorted(missing_in_excel))
    
    print(f"\n=== EMPTY VARIATIONS ===")
    # Find rows with empty sizes
    empty_sizes = df[df['SIZES'].isna() | (df['SIZES'].astype(str).str.strip() == '')]
    print(f"Rows with empty sizes: {len(empty_sizes)}")
    
    # Check which products have no size variations
    products_without_sizes = empty_sizes['ID.1'].dropna().unique()
    print(f"Products with no size variations: {len(products_without_sizes)}")
    print("References:", sorted(products_without_sizes))
    
    print(f"\n=== PRODUCTS WITH NO VARIATIONS IN ENRICHED ===")
    products_without_variations = [p for p in enriched_data if 'variations' not in p['data'] or not p['data']['variations']]
    print(f"Count: {len(products_without_variations)}")
    for p in products_without_variations:
        print(f"- {p['data']['referenceString']}: {p['data']['name']}")

if __name__ == "__main__":
    analyze_data()

