#!/usr/bin/env python3
"""
Fetch Categories and Divisions from Strapi CMS and save as mapping files.

Usage:
    python fetch_mappings.py --base-url https://cms.example.com
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Dict, Any


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import requests
    except ImportError:
        print("Error: requests package not found.")
        print("Install with: pip install requests")
        sys.exit(1)


def fetch_data(base_url: str, token: str, endpoint: str) -> Dict[str, Any]:
    """Fetch data from Strapi API endpoint."""
    url = f"{base_url}/api/{endpoint}?pagination[pageSize]=1000"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        sys.exit(1)


def create_mapping(data: Dict[str, Any], id_field: str = "id", name_field: str = "name") -> Dict[str, str]:
    """Create ID to name mapping from API response."""
    mapping = {}
    if "data" in data:
        for item in data["data"]:
            if "attributes" in item:
                item_id = str(item["id"])
                item_name = item["attributes"].get(name_field, "")
                mapping[item_id] = item_name
    return mapping


def save_mapping(mapping: Dict[str, str], filename: str):
    """Save mapping to JSON file."""
    script_dir = Path(__file__).parent
    filepath = script_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(mapping)} items to {filepath}")


def main():
    """Main function."""
    check_dependencies()
    
    parser = argparse.ArgumentParser(description="Fetch Strapi categories and divisions mappings")
    parser.add_argument("--base-url", required=True, help="Strapi base URL (e.g., https://cms.example.com)")
    args = parser.parse_args()
    
    # Check for required environment variable
    token = os.getenv("CMS_TOKEN")
    if not token:
        print("Error: CMS_TOKEN environment variable not set.")
        print("Set it with: export CMS_TOKEN=your_token_here")
        sys.exit(1)
    
    print(f"Fetching data from {args.base_url}...")
    
    # Fetch categories
    print("Fetching categories...")
    categories_data = fetch_data(args.base_url, token, "categories")
    categories_map = create_mapping(categories_data)
    save_mapping(categories_map, "categories_map.json")
    
    # Fetch divisions
    print("Fetching divisions...")
    divisions_data = fetch_data(args.base_url, token, "divisions")
    divisions_map = create_mapping(divisions_data)
    save_mapping(divisions_map, "divisions_map.json")
    
    print(f"\n✅ Fetched {len(categories_map)} categories, {len(divisions_map)} divisions")


if __name__ == "__main__":
    main() 