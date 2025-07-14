"""
Utils package for medical product processing.

This package contains utility modules for Strapi API operations
and JSON diff functionality.
"""

from .strapi import find_by_name, find_by_reference, upsert_product, delete_product
from .diff import print_diff

__all__ = [
    "find_by_name",
    "find_by_reference",
    "upsert_product", 
    "delete_product",
    "print_diff"
] 