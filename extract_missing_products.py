#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, json, re
from typing import Any, Dict, List, Optional
import pandas as pd

ALIASES = {
    "reference": [r"^id\.1$", r"^id$", r"^ref(erence)?(\s*string)?$", r"^product\s*id$"],
    "category_name": [r"^products?'?\s*category$", r"^category(\s*name)?$"],
    "product_name": [r"^products?$", r"^product\s*name$", r"^item$"],
    "size": [r"^sizes?$", r"^variant$", r"^model$"],
    "picture": [r"^picture$", r"^image$", r"^photo$"],
    "ce": [r"^ce$"],
    "ce_mdr": [r"^ce[_\s-]*mdr$"],
    "fda": [r"^fda$"],
    "iso": [r"^iso\s*st\s*/\s*ard$", r"^iso", r"^standard(s)?$"],
    "pcs_inner": [r"^pcs/?\s*inner\s*pack(aging)?$", r"^inner\s*(pcs|qty)$"],
    "pcs_outer": [r"^pcs/?\s*outer\s*pack(aging)?$", r"^outer\s*(pcs|qty)$", r"^carton\s*qty$"],
    "loading_20gp": [r"^loading\s*capacity$", r"20\s*gp", r"^20gp$"],
    "loading_40hc": [r"^unnamed:\s*16$", r"40\s*hc", r"^40hc$"],
    "carton_size": [r"^carton\s*size$", r"^ctn\s*size$", r"^box\s*size$"],
}

DEFAULT_PARENT = {
    "category": None,
    "divisions": [],
    "divisionNames": [],
    "standard": "",
    "description": "",
    "tableInMd": "",
    "images": [],
    "PackagingInformation": {
        "packing_per_inner_box": 0,
        "inner_boxes_per_carton": 0,
        "loading_capacity_20GP": 0,
        "loading_capacity_40HC": 0,
        "additional_notes": "Not specified",
    },
}

def normalize_header(h: str) -> str:
    return re.sub(r"\s+", " ", str(h or "")).strip().lower()

def match_header(name: str) -> Optional[str]:
    norm = normalize_header(name)
    for canon, pats in ALIASES.items():
        for p in pats:
            if re.search(p, norm, flags=re.IGNORECASE):
                return canon
    return None

def yesno_to_bool(x: Any) -> bool:
    if pd.isna(x): return False
    s = str(x).strip().lower()
    if s in {"yes","y","true","1"}: return True
    if s in {"n/a","na","no","false","0","-",""}: return False
    return False

DIGITS = re.compile(r"[0-9]+")
def parse_int(x: Any) -> Optional[int]:
    if pd.isna(x): return None
    s = str(x).strip().lower()
    if s in {"","n/a","na","-"}: return None
    s = s.replace("'","").replace(",","").replace(" ","")
    try:
        return int(float(s))
    except Exception:
        digits = "".join(DIGITS.findall(s))
        return int(digits) if digits else None

def parse_iso_list(x: Any) -> List[str]:
    if pd.isna(x): return []
    s = str(x).strip()
    if not s or s.lower() in {"n/a","na","-"}: return []
    parts = re.split(r"[\/,;]", s)
    return [p.strip() for p in parts if p.strip()]

def build_variation(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "size": str(r.get("size") or "").strip(),
        "picture": yesno_to_bool(r.get("picture")),
        "ce": yesno_to_bool(r.get("ce")),
        "ce_mdr": yesno_to_bool(r.get("ce_mdr")),
        "fda": yesno_to_bool(r.get("fda")),
        "iso": parse_iso_list(r.get("iso")),
        "pcs_inner": parse_int(r.get("pcs_inner")),
        "pcs_outer": parse_int(r.get("pcs_outer")),
        "loading_capacity": {
            "20GP": parse_int(r.get("loading_20gp")),
            "40HC": parse_int(r.get("loading_40hc")),
        },
        "carton_size": str(r.get("carton_size") or "").strip(),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True, help="Path to Excel file")
    ap.add_argument("--enriched", required=True, help="Path to products_enriched.json file")
    ap.add_argument("--output", required=True, help="Output path for missing products")
    ap.add_argument("--sheet", default="Sheet1", help="Excel sheet name")
    args = ap.parse_args()

    # Read existing enriched products to get reference strings
    print(f"Reading existing products from: {args.enriched}")
    with open(args.enriched, 'r', encoding='utf-8') as f:
        existing_products = json.load(f)
    
    existing_refs = set(p['data']['referenceString'] for p in existing_products)
    print(f"Found {len(existing_products)} existing products")

    # Read Excel file
    print(f"Reading Excel file: {args.excel}")
    df = pd.read_excel(args.excel, sheet_name=args.sheet)

    # Map headers to canonical names
    rename = {}
    for c in df.columns:
        canon = match_header(c)
        if canon: 
            # If we already have a mapping for this canonical name, prefer the more specific one
            if canon in rename.values():
                # Check if current column is more specific (e.g., "ID.1" vs "ID")
                existing_col = [k for k, v in rename.items() if v == canon][0]
                if len(c) > len(existing_col) or c == "ID.1":
                    # Remove the old mapping and add the new one
                    rename = {k: v for k, v in rename.items() if v != canon}
                    rename[c] = canon
            else:
                rename[c] = canon
    print(f"DEBUG: Column mapping: {rename}")
    df = df.rename(columns=rename)

    # Forward-fill merged cells
    for col in ["reference","product_name","category_name"]:
        if col in df.columns:
            df[col] = df[col].ffill()

    # Get all unique reference IDs from Excel
    excel_refs = set(df['reference'].dropna().unique())
    
    # Find missing products (in Excel but not in enriched)
    missing_refs = excel_refs - existing_refs
    print(f"Found {len(missing_refs)} missing products: {sorted(missing_refs)}")

    # Build missing products
    missing_products = []
    
    for ref in sorted(missing_refs):
        # Get all rows for this reference
        ref_rows = df[df['reference'] == ref]
        
        if len(ref_rows) == 0:
            continue
            
        # Get the first row for basic product info
        first_row = ref_rows.iloc[0]
        
        # Build product structure
        product = {
            "data": {
                "name": str(first_row.get("product_name") or "").strip(),
                "referenceString": str(ref),
                "category": DEFAULT_PARENT["category"],
                "categoryName": str(first_row.get("category_name") or "").strip(),
                "divisions": list(DEFAULT_PARENT["divisions"]),
                "divisionNames": list(DEFAULT_PARENT["divisionNames"]),
                "standard": DEFAULT_PARENT["standard"],
                "description": DEFAULT_PARENT["description"],
                "tableInMd": DEFAULT_PARENT["tableInMd"],
                "images": list(DEFAULT_PARENT["images"]),
                "PackagingInformation": dict(DEFAULT_PARENT["PackagingInformation"]),
                "variations": [],
            }
        }
        
        print(f"DEBUG: Building missing product for referenceString={ref}, name='{product['data']['name']}', categoryName='{product['data']['categoryName']}'")
        
        # Add variations
        for _, row in ref_rows.iterrows():
            variation = build_variation(row.to_dict())
            product["data"]["variations"].append(variation)
        
        missing_products.append(product)
        print(f"DEBUG: Added {len(product['data']['variations'])} variations to product {ref}")

    # Write missing products
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(missing_products, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(missing_products)} missing products to {args.output}")

if __name__ == "__main__":
    main()

