#!/bin/bash

# Script to reorganize the scripts folder
echo "🗂️  Reorganizing scripts folder..."

# Create new directories
mkdir -p core extractors uploaders output docs

# Move core scripts
echo "📁 Moving core scripts..."
mv cli_slide_driver.py core/
mv excel_to_json.py core/
mv excel_to_json_custom.py core/
mv fetch_mappings.py core/

# Move extractors
echo "📁 Moving extractors..."
mv extract_product_from_pptx.py extractors/
mv img_cli.py extractors/

# Move uploaders
echo "📁 Moving uploaders..."
mv upload_product.py uploaders/
mv upload_single.sh uploaders/

# Move output files
echo "📁 Moving output files..."
mv products.json output/
mv products_converted.json output/
mv categories_map.json output/
mv divisions_map.json output/
mv image_index.json output/
mv progress.json output/

# Move documentation
echo "📁 Moving documentation..."
mv strapi_id_reference.md docs/

# Create symlinks for main scripts (optional)
echo "🔗 Creating symlinks for main scripts..."
ln -sf core/cli_slide_driver.py cli_slide_driver.py
ln -sf core/excel_to_json.py excel_to_json.py
ln -sf core/excel_to_json_custom.py excel_to_json_custom.py
ln -sf core/fetch_mappings.py fetch_mappings.py

echo "✅ Reorganization complete!"
echo ""
echo "📋 New structure:"
echo "├── core/           # Main execution scripts"
echo "├── extractors/     # Data extraction tools"
echo "├── uploaders/      # Upload tools"
echo "├── output/         # Generated files"
echo "├── docs/           # Documentation"
echo "├── data/           # Input files"
echo "├── utils/          # Helper modules"
echo "├── products/       # Product files"
echo "└── products_uploaded/ # Upload logs"
echo ""
echo "💡 Main scripts are now in core/ but accessible from root via symlinks" 