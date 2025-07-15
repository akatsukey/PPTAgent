#!/usr/bin/env python3
"""
Table Extractor - Finds tables in slide content and saves them as markdown files
"""

import json
import os
import glob
from pathlib import Path

# === CONFIGURATION ===
SLIDE_CONTENT_DIR = "slide_content"
OUTPUT_DIR = "slide_content/tables"

def find_slide_content_files():
    """Find all slide content JSON files"""
    pattern = os.path.join(SLIDE_CONTENT_DIR, "slide_*_content.json")
    return glob.glob(pattern)

def extract_tables_from_slide_content(file_path):
    """Extract tables from a slide content JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        slide_content = json.load(f)
    
    slide_number = slide_content.get('slide_number', 'unknown')
    tables = slide_content.get('tables', [])
    
    results = []
    for i, table in enumerate(tables):
        if 'text' in table and 'markdown' in table['text']:
            table_markdown = table['text']['markdown']
            if table_markdown.strip():
                results.append({
                    'slide_number': slide_number,
                    'table_index': i + 1,
                    'markdown': table_markdown,
                    'headers': table['text'].get('headers', []),
                    'rows': table['text'].get('rows', [])
                })
    
    return results

def save_table_as_markdown(table_data, output_dir):
    """Save a table as a markdown file"""
    os.makedirs(output_dir, exist_ok=True)
    
    slide_num = table_data['slide_number']
    table_index = table_data['table_index']
    
    # Create filename
    filename = f"slide_{slide_num}_table_{table_index}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Create markdown content
    markdown_content = f"""# Slide {slide_num} - Table {table_index}

{table_data['markdown']}

## Table Information
- **Slide Number**: {slide_num}
- **Table Index**: {table_index}
- **Headers**: {', '.join(table_data['headers'])}
- **Rows**: {len(table_data['rows'])} data rows
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filepath

def main():
    """Main function to extract tables and save as markdown"""
    print("🔍 Starting table extraction from slide content...")
    
    # Find all slide content files
    slide_files = find_slide_content_files()
    print(f"📄 Found {len(slide_files)} slide content files")
    
    if not slide_files:
        print("❌ No slide content files found!")
        return
    
    all_tables = []
    
    # Process each slide file
    for file_path in slide_files:
        print(f"\n📄 Processing {os.path.basename(file_path)}...")
        
        try:
            tables = extract_tables_from_slide_content(file_path)
            all_tables.extend(tables)
            
            if tables:
                print(f"   ✅ Found {len(tables)} table(s)")
                for table in tables:
                    print(f"      - Slide {table['slide_number']}, Table {table['table_index']}")
            else:
                print("   ⚠️  No tables found")
                
        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")
    
    # Save tables as markdown files
    if all_tables:
        print(f"\n💾 Saving {len(all_tables)} tables as markdown files...")
        
        for table_data in all_tables:
            try:
                filepath = save_table_as_markdown(table_data, OUTPUT_DIR)
                print(f"   ✅ Saved: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"   ❌ Error saving table: {e}")
        
        # Create summary file
        summary_file = os.path.join(OUTPUT_DIR, "tables_summary.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Tables Summary\n\n")
            f.write(f"Total tables found: {len(all_tables)}\n\n")
            
            for table in all_tables:
                f.write(f"## Slide {table['slide_number']} - Table {table['table_index']}\n")
                f.write(f"- Headers: {', '.join(table['headers'])}\n")
                f.write(f"- Rows: {len(table['rows'])}\n\n")
                f.write(f"{table['markdown']}\n\n")
                f.write("---\n\n")
        
        print(f"   ✅ Created summary: tables_summary.md")
        print(f"\n🎉 Successfully extracted {len(all_tables)} tables!")
        print(f"📁 Files saved in: {OUTPUT_DIR}/")
        
    else:
        print("\n❌ No tables found in any slides!")

if __name__ == "__main__":
    main() 