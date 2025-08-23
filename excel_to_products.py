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
        "size": (r.get("size") or "").strip(),
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
        "carton_size": (r.get("carton_size") or "").strip(),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    ap.add_argument("--sheet", default=0)
    ap.add_argument("--only-ref", default=None, help="Process only this reference id (e.g., 1.1)")
    ap.add_argument("--limit-variations", type=int, default=None, help="Keep only first N variations (test)")
    args = ap.parse_args()

    df = pd.read_excel(args.inp, sheet_name=args.sheet)

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

    # Keep rows that actually represent variations (must have a size)
    if "size" in df.columns:
        df = df[df["size"].astype(str).str.strip().ne("")]

    # If only-ref is set, filter to that reference
    if args.only_ref and "reference" in df.columns:
        # be tolerant: "1.1", " 1.1 ", etc.
        df = df[df["reference"].astype(str).str.strip().str.match(rf"^{re.escape(args.only_ref)}(\b|$)")]

    df = df.reset_index(drop=True)

    if args.only_ref:
        print(f"DEBUG: total rows for reference {args.only_ref}: {len(df)}")

    # Build products grouped by reference
    products = {}
    for _, r in df.iterrows():
        ref = str(r.get("reference") or "").strip()
        if not ref: continue

        if args.only_ref and ref != args.only_ref:
            continue

        cat_name = str(r.get("category_name") or "").strip()
        prod_name = str(r.get("product_name") or "").strip()

        if ref not in products:
            print(f"DEBUG: building product for referenceString={ref}, name='{prod_name}', categoryName='{cat_name}'")
            parent = {
                "name": prod_name,
                "referenceString": ref,
                "category": DEFAULT_PARENT["category"],
                "categoryName": cat_name,
                "divisions": list(DEFAULT_PARENT["divisions"]),
                "divisionNames": list(DEFAULT_PARENT["divisionNames"]),
                "standard": DEFAULT_PARENT["standard"],
                "description": DEFAULT_PARENT["description"],
                "tableInMd": DEFAULT_PARENT["tableInMd"],
                "images": list(DEFAULT_PARENT["images"]),
                "PackagingInformation": dict(DEFAULT_PARENT["PackagingInformation"]),
                "variations": [],
            }
            products[ref] = {"data": parent}

        products[ref]["data"]["variations"].append(build_variation(r.to_dict()))

    # Optional: limit number of variations for quick smoke test
    if args.limit_variations is not None:
        for ref, obj in products.items():
            obj["data"]["variations"] = obj["data"]["variations"][:args.limit_variations]
            if obj["data"]["variations"]:
                v0 = obj["data"]["variations"][0]
                print(f"DEBUG: first variation for {ref}: size='{v0.get('size','')}'")

    # Serialize as array
    result = [products[k] for k in sorted(products.keys(), key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", x)])]

    # If only-ref, keep just that product in output to simplify testing
    if args.only_ref:
        result = [products[args.only_ref]] if args.only_ref in products else []

    with open(args.outp, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(result)} product(s) to {args.outp}")

if __name__ == "__main__":
    main()
