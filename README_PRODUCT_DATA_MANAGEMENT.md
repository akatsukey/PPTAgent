# Product Data Management System

## Overview
This system manages product data from Excel catalogs and maintains two separate JSON files for complete and incomplete products.

## File Structure

### 📁 Data Sources
- **Excel Catalog**: `./data/Index VER 8.xlsx` (Sheet1)
- **Complete Products**: `./output/products_enriched.json` (141 products)
- **Incomplete Products**: `./output/products_missing_in_the_enriched.json` (27 products)

### 📊 Data Status

#### ✅ Complete Products (`products_enriched.json`)
- **141 products** with full data
- Includes: name, category, divisions, descriptions, images, variations
- **Ready for website publication**
- All variations extracted from Excel with proper data conversion

#### ⚠️ Incomplete Products (`products_missing_in_the_enriched.json`)
- **27 products** with basic structure only
- **Missing**: divisions, descriptions, images, detailed metadata
- **Needs manual completion** before website publication
- Contains all available Excel data (variations, certifications, packaging)

## Data Processing Scripts

### 🔄 Update Existing Products
```bash
python3 excel_to_products_enriched.py \
  --excel "./data/Index VER 8.xlsx" \
  --enriched "./output/products_enriched.json" \
  --output "./output/products_enriched_updated.json" \
  --sheet "Sheet1"
```

### 📤 Extract Missing Products
```bash
python3 extract_missing_products.py \
  --excel "./data/Index VER 8.xlsx" \
  --enriched "./output/products_enriched.json" \
  --output "./output/products_missing_in_the_enriched.json" \
  --sheet "Sheet1"
```

### 🔍 Analyze Data Status
```bash
python3 analyze_missing_products.py
```

## Data Conversion Rules

### ✅ Automatic Conversions
- **Booleans**: YES/n/a → true/false
- **Numbers**: 3'200, 3,200 → 3200
- **ISO Standards**: "ISO 7886-1 / ISO 80369-7" → ["ISO 7886-1", "ISO 80369-7"]
- **Merged Cells**: Forward-fill for ID, category, product name

### 📋 Product Structure
```json
{
  "data": {
    "name": "Product Name",
    "referenceString": "4.1.1",
    "category": null,
    "categoryName": "Category Name",
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
      "additional_notes": "Not specified"
    },
    "variations": [
      {
        "size": "Size description",
        "picture": true,
        "ce": true,
        "ce_mdr": true,
        "fda": true,
        "iso": ["ISO 7886-1"],
        "pcs_inner": 100,
        "pcs_outer": 3200,
        "loading_capacity": {"20GP": 800000, "40HC": 1984000},
        "carton_size": "63x44x40"
      }
    ]
  }
}
```

## Workflow for New Products

### 1. Add to Excel
- Add new products to `./data/Index VER 8.xlsx`
- Include: ID.1, PRODUCTS, PRODUCTS' CATEGORY, SIZES, certifications, packaging info

### 2. Extract Missing Products
```bash
python3 extract_missing_products.py
```

### 3. Complete Product Data
- Open `products_missing_in_the_enriched.json`
- Add: divisions, descriptions, images, detailed metadata
- Save as `products_enriched.json`

### 4. Update Existing Products
```bash
python3 excel_to_products_enriched.py
```

## File Naming Convention

### 📝 Required Fields for Website Publication
- **name**: Product name
- **referenceString**: Unique product ID
- **categoryName**: Product category
- **divisions**: Product divisions (manual)
- **description**: Product description (manual)
- **images**: Product images (manual)
- **variations**: Size variations with all data

### 🚫 Products Not Ready for Publication
- Missing divisions
- Missing descriptions
- Missing images
- Incomplete metadata

## Troubleshooting

### Common Issues
1. **Missing products**: Check Excel file for new additions
2. **Empty variations**: Products without size data are still processed
3. **Data conversion errors**: Check Excel format and column names

### Validation Commands
```bash
# Check product counts
python3 -c "import json; data=json.load(open('./output/products_enriched.json')); print(f'Complete: {len(data)}')"
python3 -c "import json; data=json.load(open('./output/products_missing_in_the_enriched.json')); print(f'Incomplete: {len(data)}')"

# Check variations
python3 -c "import json; data=json.load(open('./output/products_enriched.json')); products_with_variations = [p for p in data if p['data'].get('variations')]; print(f'Products with variations: {len(products_with_variations)}')"
```

## Notes
- **Total Excel products**: 167
- **Complete products**: 141
- **Incomplete products**: 27
- **Products not in Excel**: 1 (4.10.8)
- **Last updated**: August 23, 2024

