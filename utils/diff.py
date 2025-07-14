"""
Diff utility module for comparing JSON data.

This module provides functions for comparing and displaying differences
between JSON objects using the rich library for colored output.
"""

from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.text import Text

# Initialize console for output
console = Console()

def print_diff(remote: Dict[str, Any], local: Dict[str, Any]) -> None:
    """
    Print a side-by-side diff of two JSON dictionaries.
    
    This function compares the remote and local dictionaries and displays
    differences in a formatted table. Unchanged keys are hidden, and
    additions/deletions are color-coded.
    
    Args:
        remote: Remote/existing JSON data
        local: Local/new JSON data
    """
    # Create table for comparison
    table = Table(title="JSON Diff")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Remote", style="red")
    table.add_column("Local", style="green")
    
    # Get all unique keys
    all_keys = set(remote.keys()) | set(local.keys())
    
    # Track if we have any differences
    has_differences = False
    
    for key in sorted(all_keys):
        remote_val = remote.get(key)
        local_val = local.get(key)
        
        # Only show rows where values differ
        if remote_val != local_val:
            has_differences = True
            
            # Format values for display
            remote_str = _format_value(remote_val)
            local_str = _format_value(local_val)
            
            # Add row to table
            table.add_row(key, remote_str, local_str)
    
    if has_differences:
        console.print(table)
    else:
        console.print("[green]No differences found[/green]")

def _format_value(value: Any) -> str:
    """
    Format a value for display in the diff table.
    
    Args:
        value: Value to format
        
    Returns:
        Formatted string representation
    """
    if value is None:
        return "[dim]None[/dim]"
    elif isinstance(value, (dict, list)):
        # For complex types, show a summary
        if isinstance(value, dict):
            return f"{{...}} ({len(value)} keys)"
        else:
            return f"[...] ({len(value)} items)"
    else:
        # For simple types, convert to string and truncate if needed
        str_val = str(value)
        if len(str_val) > 50:
            return str_val[:47] + "..."
        return str_val 