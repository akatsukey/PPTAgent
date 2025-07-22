#!/usr/bin/env python3
"""
Slug Builder for Products

This script reads products.json and adds unique slugs to products.
Slugs are generated from product names and made URL-safe.
"""

import json
import re
import argparse
from typing import Dict, List, Set
import unicodedata


def slugify(text: str) -> str:
    """
    Convert text to a URL-safe slug.
    
    Args:
        text: The text to convert
        
    Returns:
        A URL-safe slug string
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFD', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text


def generate_unique_slug(name: str, existing_slugs: Set[str]) -> str:
    """
    Generate a unique slug from a product name.
    
    Args:
        name: Product name
        existing_slugs: Set of existing slugs to avoid conflicts
        
    Returns:
        A unique slug
    """
    base_slug = slugify(name)
    
    if not base_slug:
        base_slug = "product"
    
    slug = base_slug
    counter = 1
    
    while slug in existing_slugs:
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def add_slugs_to_products(products: List[Dict], limit: int | None = None) -> List[Dict]:
    """
    Add slugs to products.
    
    Args:
        products: List of product dictionaries
        limit: Optional limit on number of products to process
        
    Returns:
        Updated list of products with slugs
    """
    existing_slugs = set()
    updated_products = []
    
    # Process products up to limit
    products_to_process = products[:limit] if limit else products
    
    print(f"Processing {len(products_to_process)} products...")
    
    for i, product in enumerate(products_to_process):
        # Use name from product['data']['name']
        name = product.get('data', {}).get('name', '')
        
        if not name:
            print(f"Warning: Product {i+1} has no name, skipping")
            updated_products.append(product)
            continue
        
        # Generate unique slug
        slug = generate_unique_slug(name, existing_slugs)
        existing_slugs.add(slug)
        
        # Add slug to product['data']
        if 'data' not in product:
            product['data'] = {}
        product['data']['slug'] = slug
        
        print(f"Product {i+1}: '{name}' -> slug: '{slug}'")
        
        updated_products.append(product)
    
    # Add remaining products without processing
    if limit and len(products) > limit:
        updated_products.extend(products[limit:])
    
    return updated_products


def main():
    parser = argparse.ArgumentParser(description='Add slugs to products in products.json')
    parser.add_argument('--limit', type=int, help='Limit number of products to process')
    parser.add_argument('--output', default='products.json', help='Output file (default: products.json)')
    parser.add_argument('--input', default='products.json', help='Input file (default: products.json)')
    
    args = parser.parse_args()
    
    try:
        # Read products
        print(f"Reading products from {args.input}...")
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("Error: Expected products.json to contain a list of products")
            return
        
        print(f"Found {len(data)} products")
        
        # Add slugs
        updated_products = add_slugs_to_products(data, args.limit)
        
        # Write back to file
        print(f"Writing updated products to {args.output}...")
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(updated_products, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully added slugs to {len(updated_products)} products")
        
        # Show summary
        products_with_slugs = [p for p in updated_products if p.get('slug')]
        print(f"Products with slugs: {len(products_with_slugs)}")
        
    except FileNotFoundError:
        print(f"Error: File {args.input} not found")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {args.input}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 