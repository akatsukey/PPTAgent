# 🗂️ LetsMed Scripts Directory

This directory contains all automation, data processing, and CLI tools for managing the LetsMed product pipeline, organized for clarity and maintainability.

---

## 📁 **Directory Structure**

```
scripts/
├── README.md                    # Main documentation
├── requirements.txt             # Dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
├── products.json               # Main products database
├── products_enriched.json      # Enriched products with slide data
├── categories_map.json         # Strapi category mappings
├── divisions_map.json          # Strapi division mappings
│
├── core/                       # 🎯 MAIN EXECUTION SCRIPTS
│   ├── cli_slide_driver.py    # Interactive CLI (main entry point)
│   ├── excel_to_json.py       # Standard Excel converter
│   ├── excel_to_json_custom.py # Custom Excel converter
│   ├── fetch_mappings.py      # Strapi mappings fetcher
│   └── slides_to_json_merger.py # Merge PowerPoint slides with Excel JSON
│
├── extractors/                 # 📊 DATA EXTRACTION TOOLS
│   ├── extract_product_from_pptx.py    # Extract product data from PowerPoint
│   ├── extract_slide_content.py        # Extract all text content from slides
│   ├── extract_tables_to_markdown.py   # Convert slide tables to markdown
│   ├── img_cli.py                     # CLI for managing product images
│   ├── update_missing_slides.py       # Update missing slides in products.json
│   ├── test_manual_update.py          # Test manual update functionality
│   ├── test_update.py                 # Test update logic
│   ├── products/                      # Individual product JSON files
│   └── slide_content/                 # Extracted slide content files
│
├── uploaders/                  # ⬆️ UPLOAD TOOLS
│   ├── upload_product.py              # Interactive upload script
│   ├── upload_specific_products.py    # Direct upload of specific products
│   ├── upload_random_products.py      # Upload random products
│   ├── extract_specific_products.py   # Extract specific products from JSON
│   ├── extract_4_3_4_4_products.py   # Extract 4.3/4.4 products
│   ├── upload_single.sh               # Bash script for single upload
│   └── products/                      # Product files for upload
│
├── output/                     # 📤 GENERATED FILES
│   ├── products.json
│   ├── products_converted.json
│   ├── products_enriched.json
│   ├── categories_map.json
│   ├── divisions_map.json
│   ├── image_index.json
│   ├── progress.json
│   └── issues.json
│
├── docs/                       # 📚 DOCUMENTATION
│   └── strapi_id_reference.md
│
├── data/                       # 📥 INPUT FILES
├── utils/                      # 🔧 HELPER MODULES
├── products/                   # 📦 PRODUCT FILES
├── products_uploaded/          # 📋 UPLOAD LOGS
└── venv/                      # 🐍 VIRTUAL ENVIRONMENT
```

---

## 📋 **Quick Reference Table**

| Script/File                | Purpose / Usage                                                                 |
|---------------------------|-------------------------------------------------------------------------------|
| `core/fetch_mappings.py`       | Download Strapi categories/divisions as JSON mappings.                        |
| `core/excel_to_json.py`        | Convert standard Excel to Strapi JSON (uses mappings, with validation).        |
| `core/excel_to_json_custom.py` | Convert custom-format Excel to Strapi JSON (uses mappings, with validation).   |
| `core/slides_to_json_merger.py` | Merge PowerPoint slide data with Excel JSON to create enriched products.      |
| `core/cli_slide_driver.py`     | Interactive CLI for extracting/uploading products from PowerPoint slides.      |
| `extractors/extract_product_from_pptx.py` | Extract product data from PowerPoint (used by CLI).                    |
| `extractors/extract_slide_content.py` | Extract all text content from PowerPoint slides including tables.        |
| `extractors/extract_tables_to_markdown.py` | Convert slide tables to markdown files.                              |
| `extractors/img_cli.py`              | CLI for managing and indexing product images.                                  |
| `extractors/update_missing_slides.py` | Update missing slides in products.json.                                |
| `uploaders/upload_product.py`       | Interactive upload script for single products.                               |
| `uploaders/upload_specific_products.py` | Direct upload of specific products without user input.                |
| `uploaders/upload_random_products.py` | Upload random products from products.json.                            |
| `uploaders/upload_single.sh`        | Bash script for uploading a single product JSON.                              |
| `output/`                     | Generated files (products.json, mappings, etc.)                               |
| `docs/strapi_id_reference.md`  | Reference for Strapi category/division IDs.                                   |
| `products_uploaded/`      | Audit log of uploaded product JSONs.                                          |
| `products/`               | Raw/processed product data files.                                             |
| `data/`                   | Source files (e.g., products.xlsx, PowerPoints).                              |
| `utils/`                  | Helper modules for Strapi, Excel, and image processing.                       |

---

## 🛠️ Script Details

### 1. `fetch_mappings.py`
- **Purpose:** Download all Strapi categories and divisions, saving as `categories_map.json` and `divisions_map.json`.
- **Usage:**
  ```bash
  export CMS_TOKEN=your_strapi_token
  python fetch_mappings.py --base-url https://cms.example.com
  ```
- **Notes:** Required for Excel-to-JSON conversion scripts.

### 2. `excel_to_json.py`
- **Purpose:** Convert a standard-format Excel file to Strapi-ready JSON, using mapping files for validation and enrichment.
- **Usage:**
  ```bash
  python excel_to_json.py products.xlsx products.json
  # Optionally specify mappings directory:
  python excel_to_json.py products.xlsx products.json --mappings /path/to/mappings
  ```
- **Notes:**
  - Prints a validation summary of skipped products with missing mappings.
  - Expects columns: `referenceString`, `name`, `category`, `divisions`, etc.

### 3. `excel_to_json_custom.py`
- **Purpose:** Convert a custom-format Excel file (as in `data/products.xlsx`) to Strapi JSON, using mapping files if present.
- **Usage:**
  ```bash
  python excel_to_json_custom.py
  ```
- **Notes:**
  - Looks for `data/products.xlsx` and outputs `products.json`.
  - Prints a validation summary for missing categories/divisions.

### 4. `slides_to_json_merger.py`
- **Purpose:** Merge PowerPoint slide data with Excel JSON to create enriched products.
- **Usage:**
  ```bash
  python core/slides_to_json_merger.py \
         --pptx "data/WEB MASTER Ver 9.pptx" \
         --input products.json \
         --output products_enriched.json \
         --issues issues.json \
         --start 5 --end 18
  ```
- **Notes:**
  - Enriches Excel products with slide data (standard, description, tableInMd, etc.)
  - Only copies slide data if Excel field is empty
  - Generates issues report for unmatched slides and incomplete products
  - Supports slide range specification (--start, --end)

### 5. `cli_slide_driver.py`
- **Purpose:** Interactive CLI for extracting product data from PowerPoint slides, processing, and uploading to Strapi.
- **Usage:**
  ```bash
  python cli_slide_driver.py
  ```
- **Notes:**
  - Guides you through slide selection, extraction, and upload.
  - Supports audit logging and progress tracking.

### 6. `extract_product_from_pptx.py`
- **Purpose:** Extract product data from PowerPoint slides with GPT-4 AI processing.
- **Usage:**
  ```bash
  # Extract specific slide range
  python extractors/extract_product_from_pptx.py --start 11 --finish 15
  
  # Extract single slide
  python extractors/extract_product_from_pptx.py --start 5 --finish 5
  ```
- **Features:**
  - Uses GPT-4 for intelligent data extraction
  - Extracts tables and converts to Markdown format
  - Two-step processing: general info + packaging details
  - Updates products.json automatically
  - Saves individual JSON files for audit

### 7. `extract_slide_content.py`
- **Purpose:** Extract all text content from PowerPoint slides in original format.
- **Usage:**
  ```bash
  python extractors/extract_slide_content.py --start 29 --finish 32
  python extractors/extract_slide_content.py -s 6 -f 6
  ```
- **Features:**
  - Extracts text, tables, images, and shapes
  - Preserves original formatting and structure
  - Saves detailed JSON files for each slide
  - Supports slide range specification

### 8. `extract_tables_to_markdown.py`
- **Purpose:** Convert slide tables to markdown files for easy reading.
- **Usage:**
  ```bash
  python extractors/extract_tables_to_markdown.py
  ```
- **Features:**
  - Processes slide content JSON files
  - Converts tables to clean markdown format
  - Creates individual .md files for each table
  - Generates summary file with all tables

### 9. `img_cli.py`
- **Purpose:** CLI tool for managing and indexing product images.
- **Usage:**
  ```bash
  python extractors/img_cli.py
  ```
- **Notes:**
  - Used for associating images with products and building image indices.

### 10. `upload_product.py`
- **Purpose:** Interactive upload script for single products.
- **Usage:**
  ```bash
  python uploaders/upload_product.py
  ```
- **Features:**
  - Lists available JSON files
  - Interactive selection menu
  - Upload confirmation and status reporting

### 11. `upload_specific_products.py`
- **Purpose:** Direct upload of specific products without user input.
- **Usage:**
  ```bash
  python uploaders/upload_specific_products.py
  ```
- **Features:**
  - Uploads predefined list of products
  - No user interaction required
  - Batch processing capability

### 12. `upload_random_products.py`
- **Purpose:** Upload random products from products.json.
- **Usage:**
  ```bash
  python uploaders/upload_random_products.py
  ```
- **Features:**
  - Randomly selects products from products.json
  - Direct upload to Strapi
  - Progress reporting and error handling

### 13. `update_missing_slides.py`
- **Purpose:** Update missing slides in products.json.
- **Usage:**
  ```bash
  python extractors/update_missing_slides.py
  ```
- **Features:**
  - Checks which slides are missing from products.json
  - Updates products with extracted data
  - Validation and reporting

### 14. `upload_single.sh`
- **Purpose:** Bash script for uploading a single product JSON file to Strapi.
- **Usage:**
  ```bash
  ./uploaders/upload_single.sh path/to/product.json
  ```

---

## 🧩 Supporting Files & Folders

- **`requirements.txt`** — Python dependencies (install with `pip install -r requirements.txt`).
- **`strapi_id_reference.md`** — Strapi category/division ID reference.
- **`products_uploaded/`** — Audit log of uploaded product JSONs.
- **`products/`** — Raw/processed product data files.
- **`data/`** — Source files like `products.xlsx` and PowerPoints.
- **`utils/`** — Helper modules for Strapi, Excel, and image processing.
- **`progress.json`, `image_index.json`** — Track progress and image associations for CLI tools.
- **`products.json`** — Main products database with all extracted data.
- **`products_enriched.json`** — Enriched products with slide data merged.

---

## 🚀 Typical Workflow

### **Option 1: Excel to JSON Pipeline**
1. **Fetch Strapi mappings:**
   ```bash
   python core/fetch_mappings.py --base-url https://cms.example.com
   ```
2. **Convert Excel to JSON:**
   - For standard format: `python core/excel_to_json.py products.xlsx products.json`
   - For custom format: `python core/excel_to_json_custom.py`
3. **Review validation summary and fix any missing mappings.**
4. **Upload products:**
   - Use `uploaders/upload_product.py` for interactive upload
   - Use `uploaders/upload_specific_products.py` for batch upload
   - Use `uploaders/upload_random_products.py` for random upload

### **Option 2: PowerPoint Extraction Pipeline**
1. **Extract product data from slides:**
   ```bash
   python extractors/extract_product_from_pptx.py --start 11 --finish 15
   ```
2. **Extract slide content (optional):**
   ```bash
   python extractors/extract_slide_content.py --start 29 --finish 32
   ```
3. **Convert tables to markdown (optional):**
   ```bash
   python extractors/extract_tables_to_markdown.py
   ```
4. **Upload extracted products:**
   ```bash
   python uploaders/upload_specific_products.py
   ```

### **Option 3: Interactive CLI**
1. **Run the interactive CLI:**
   ```bash
   python core/cli_slide_driver.py
   ```
2. **Follow the guided process for slide selection and upload.**

---

## 📝 Usage Examples

### **Extract and Upload Products from Slides:**
```bash
# Extract slides 11-15
python extractors/extract_product_from_pptx.py --start 11 --finish 15

# Upload specific products
python uploaders/upload_specific_products.py

# Upload random products
python uploaders/upload_random_products.py
```

### **Convert Excel to JSON:**
```bash
python core/excel_to_json.py products.xlsx products.json
python core/excel_to_json_custom.py
```

### **Merge PowerPoint with Excel JSON:**
```bash
python core/slides_to_json_merger.py \
       --pptx "data/WEB MASTER Ver 9.pptx" \
       --input products.json \
       --output products_enriched.json \
       --issues issues.json
```

### **Extract Slide Content:**
```bash
# Extract specific slides
python extractors/extract_slide_content.py --start 29 --finish 32

# Convert tables to markdown
python extractors/extract_tables_to_markdown.py
```

### **Upload Products:**
```bash
# Interactive upload
python uploaders/upload_product.py

# Direct upload of specific products
python uploaders/upload_specific_products.py

# Upload random products
python uploaders/upload_random_products.py
```

### **Manage Images:**
```bash
python extractors/img_cli.py
# Commands: list, find <ref>, stats, exit
```

---

## 🔍 Troubleshooting

- **API Errors:** Check `.env` configuration and Strapi token.
- **Missing Dependencies:** Run `pip install -r requirements.txt`.
- **Permission Errors:** Ensure write access to directories.
- **Strapi Connection:** Verify Strapi is running and accessible.
- **Category/Division Errors:** Update mapping files with `fetch_mappings.py`.
- **Table Extraction Issues:** Check slide content format and table structure.

---

## 🎯 Best Practices

- Always backup before bulk operations.
- Test with single products first.
- Use the CLI for interactive control.
- Check logs in `products_uploaded/` for audit trail.
- Keep `image_index.json` updated for image management.
- Keep mapping files (`categories_map.json`, `divisions_map.json`) up to date with Strapi.
- Use slide ranges for large PowerPoint files to avoid timeouts.
- Validate extracted data before uploading to Strapi.
- Monitor upload success rates and handle errors appropriately.

---

## 📊 Recent Updates

### **New Features Added:**
- **Table Extraction**: Automatic extraction of tables from PowerPoint slides with Markdown conversion
- **Slide Content Extraction**: Complete text extraction from slides with structured output
- **Direct Upload Scripts**: Non-interactive upload options for batch processing
- **Random Upload**: Upload random products from the database
- **Missing Slide Updates**: Tools to update products.json with missing slide data
- **Enhanced Error Handling**: Better error reporting and validation

### **Improved Workflows:**
- **Two-step Extraction**: GPT-4 powered extraction with general info + packaging details
- **Batch Processing**: Support for processing multiple slides at once
- **Audit Logging**: Comprehensive logging of all uploads and extractions
- **Progress Tracking**: Real-time progress reporting for long operations

---

## 🔗 Related Documentation

- **Frontend Setup**: See `letsmed-frontend/frontend/README.md`
- **Backend Setup**: See `letsmed-backend/README.md`
- **API Reference**: See `docs/strapi_id_reference.md`
- **Product Schema**: See Strapi admin panel for field definitions

---
