"""
Strapi API utility module for medical products.

This module provides functions for interacting with the Strapi API,
including finding, creating, updating, and deleting medical products.
All functions use environment-based configuration and include proper
error handling with timeouts and retries.
"""

import os
import requests
from typing import Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
STRAPI_URL = os.getenv("STRAPI_URL", "http://localhost:1337")
STRAPI_TOKEN = os.getenv("STRAPI_TOKEN")

# Request configuration
TIMEOUT = 5
MAX_RETRIES = 3

def _get_headers() -> Dict[str, str]:
    """Get headers for Strapi API requests."""
    headers = {"Content-Type": "application/json"}
    if STRAPI_TOKEN:
        headers["Authorization"] = f"Bearer {STRAPI_TOKEN}"
    return headers

def _make_request(method: str, url: str, **kwargs) -> Optional[requests.Response]:
    """
    Make a request to the Strapi API with retries and timeout.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: Full URL to request
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        Response object or None if all retries failed
    """
    kwargs.setdefault("timeout", TIMEOUT)
    kwargs.setdefault("headers", _get_headers())
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                print(f"Error making request to {url}: {e}")
                return None
            continue
    
    return None

def find_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Find a medical product by name in Strapi.
    
    Args:
        name: Product name to search for
        
    Returns:
        Product data dictionary if found, None otherwise
    """
    url = f"{STRAPI_URL}/api/medical-products"
    params = {"filters[name][$eq]": name}
    
    response = _make_request("GET", url, params=params)
    if not response or response.status_code != 200:
        return None
    
    data = response.json()
    if data.get("data") and len(data["data"]) > 0:
        return data["data"][0]
    
    return None

def find_by_reference(reference_string: str) -> Optional[Dict[str, Any]]:
    """
    Find a medical product by referenceString in Strapi.
    
    Args:
        reference_string: Product reference string to search for
        
    Returns:
        Product data dictionary if found, None otherwise
    """
    url = f"{STRAPI_URL}/api/medical-products"
    params = {"filters[referenceString][$eq]": reference_string}
    
    response = _make_request("GET", url, params=params)
    if not response or response.status_code != 200:
        return None
    
    data = response.json()
    if data.get("data") and len(data["data"]) > 0:
        return data["data"][0]
    
    return None

def upsert_product(payload: Dict[str, Any], existing: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Create or update a medical product in Strapi.
    
    If existing product is provided, it will be updated. Otherwise, a new product
    will be created. Success messages are printed for both operations.
    
    Args:
        payload: Product data to create/update
        existing: Existing product data (for updates)
        
    Returns:
        Updated product data if successful, None otherwise
    """
    if existing:
        # Update existing product
        product_id = existing["id"]
        url = f"{STRAPI_URL}/api/medical-products/{product_id}"
        
        response = _make_request("PUT", url, json=payload)
        if response and response.status_code in (200, 201):
            result = response.json()
            product_name = payload.get("data", {}).get("name", "Unknown")
            print(f"✅ updated {product_name} (ID: {product_id})")
            return result["data"]
        else:
            return None
    else:
        # Create new product
        url = f"{STRAPI_URL}/api/medical-products"
        
        response = _make_request("POST", url, json=payload)
        if response and response.status_code in (200, 201):
            result = response.json()
            product_name = payload.get("data", {}).get("name", "Unknown")
            product_id = result["data"]["id"]
            print(f"✅ created {product_name} (ID: {product_id})")
            return result["data"]
        else:
            return None

def delete_product(product_id: int) -> bool:
    """
    Delete a medical product from Strapi.
    
    Args:
        product_id: ID of the product to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    url = f"{STRAPI_URL}/api/medical-products/{product_id}"
    
    response = _make_request("DELETE", url)
    if response and response.status_code in (200, 204):
        return True
    else:
        return False 