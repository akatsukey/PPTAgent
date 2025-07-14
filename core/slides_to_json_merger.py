#!/usr/bin/env python3
"""
Merge PowerPoint slide data with Excel JSON data to create enriched products.

Usage:
    python slides_to_json_merger.py --pptx "data/WEB MASTER Ver 9.pptx" \
           --input products.json --output products_enriched.json --issues issues.json \
           --start 5 --end 18
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from pptx import Presentation
    from extractors.extract_product_from_pptx import process_slide_two_steps
except ImportError:
    print("Error: python-pptx and extract_product_from_pptx required.")
    print("Install with: pip install python-pptx")
    sys.exit(1)


def load_products(input_file: Path) -> Dict[str, Dict[str, Any]]:
    """Load products from JSON file, keyed by referenceString."""
    with open(input_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # Create dict keyed by referenceString
    products_dict = {}
    for product in products:
        ref = product["data"]["referenceString"]
        products_dict[ref] = product["data"]
    
    return products_dict


def merge_slide_data(slide_payload: Dict[str, Any], 
                    excel_product: Dict[str, Any]) -> Dict[str, Any]:
    """Merge slide data into Excel product, only if Excel field is empty."""
    fields_to_merge = ["standard", "description", "tableInMd", 
                       "PackagingInformation", "images"]
    
    merged_product = excel_product.copy()
    slide_data = slide_payload["data"]
    
    for field in fields_to_merge:
        excel_value = excel_product.get(field)
        slide_value = slide_data.get(field)
        
        # Only copy slide value if Excel value is empty/falsey
        if not excel_value and slide_value:
            merged_product[field] = slide_value
    
    return merged_product


def check_completeness(product: Dict[str, Any]) -> List[str]:
    """Check which required fields are missing from a product."""
    required_fields = ["standard", "description", "tableInMd", 
                      "PackagingInformation", "images"]
    missing = []
    
    for field in required_fields:
        value = product.get(field)
        if not value:
            missing.append(field)
        elif field == "PackagingInformation" and isinstance(value, dict):
            # Check if PackagingInformation has meaningful data
            if not any(v for v in value.values() if v and v != "Not specified"):
                missing.append(field)
    
    return missing


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Merge PowerPoint slide data with Excel JSON")
    parser.add_argument("--pptx", required=True, help="PowerPoint file path")
    parser.add_argument("--input", required=True, help="Input JSON file path")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--issues", required=True, help="Issues JSON file path")
    parser.add_argument("--start", type=int, default=1, help="Start slide number (1-based)")
    parser.add_argument("--end", type=int, help="End slide number (1-based)")
    
    args = parser.parse_args()
    
    # Validate input files
    pptx_path = Path(args.pptx)
    input_path = Path(args.input)
    
    if not pptx_path.exists():
        print(f"Error: PowerPoint file not found: {pptx_path}")
        sys.exit(1)
    
    if not input_path.exists():
        print(f"Error: Input JSON file not found: {input_path}")
        sys.exit(1)
    
    # Load PowerPoint and products
    print(f"📖 Loading PowerPoint: {pptx_path}")
    prs = Presentation(pptx_path)
    
    print(f"📖 Loading products: {input_path}")
    products_dict = load_products(input_path)
    
    # Set end slide if not specified
    if args.end is None:
        args.end = len(prs.slides)
    
    # Process slides
    print(f"🔄 Processing slides {args.start}-{args.end}...")
    
    unmatched_slides = []
    updated_count = 0
    
    for slide_idx in range(args.start - 1, args.end):  # Convert to 0-based
        try:
            payload = process_slide_two_steps(prs, slide_idx)
            ref = payload["data"]["referenceString"]
            
            if not ref:
                unmatched_slides.append(f"slide_{slide_idx + 1}")
                continue
            
            # Find matching product
            if ref in products_dict:
                # Merge slide data into Excel product
                products_dict[ref] = merge_slide_data(payload, products_dict[ref])
                updated_count += 1
            else:
                unmatched_slides.append(ref)
                
        except Exception as e:
            print(f"⚠️  Warning: Error processing slide {slide_idx + 1}: {e}")
            unmatched_slides.append(f"slide_{slide_idx + 1}")
    
    # Check completeness and prepare output
    incomplete_products = []
    enriched_products = []
    
    for ref, product in products_dict.items():
        missing_fields = check_completeness(product)
        if missing_fields:
            incomplete_products.append({
                "referenceString": ref,
                "missing": missing_fields
            })
        
        enriched_products.append({"data": product})
    
    # Write output files
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_products, f, indent=2, ensure_ascii=False)
    
    issues_path = Path(args.issues)
    issues_data = {
        "unmatched_slides": unmatched_slides,
        "incomplete_products": incomplete_products
    }
    with open(issues_path, 'w', encoding='utf-8') as f:
        json.dump(issues_data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\nSlides {args.start}-{args.end} processed")
    print(f"✔  {updated_count} products updated")
    print(f"❓  {len(unmatched_slides)} slides unmatched      (see {args.issues})")
    print(f"⚠️   {len(incomplete_products)} product(s) incomplete   (see {args.issues})")


if __name__ == "__main__":
    main() 