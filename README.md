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
│
├── core/                       # 🎯 MAIN EXECUTION SCRIPTS
│   ├── cli_slide_driver.py    # Interactive CLI (main entry point)
│   ├── excel_to_json.py       # Standard Excel converter
│   ├── excel_to_json_custom.py # Custom Excel converter
│   ├── fetch_mappings.py      # Strapi mappings fetcher
│   └── slides_to_json_merger.py # Merge PowerPoint slides with Excel JSON
│
├── extractors/                 # 📊 DATA EXTRACTION TOOLS
│   ├── extract_product_from_pptx.py
│   └── img_cli.py
│
├── uploaders/                  # ⬆️ UPLOAD TOOLS
│   ├── upload_product.py
│   └── upload_single.sh
│
├── output/                     # 📤 GENERATED FILES
│   ├── products.json
│   ├── products_converted.json
│   ├── categories_map.json
│   ├── divisions_map.json
│   ├── image_index.json
│   └── progress.json
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
| `extractors/img_cli.py`              | CLI for managing and indexing product images.                                  |
| `uploaders/upload_product.py`       | Upload a single product JSON to Strapi via API.                               |
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
- **Purpose:** Extract product data from PowerPoint slides (used by CLI or standalone).
- **Usage:**
  ```bash
  python extractors/extract_product_from_pptx.py path/to/file.pptx
  ```

### 7. `img_cli.py`
- **Purpose:** CLI tool for managing and indexing product images.
- **Usage:**
  ```bash
  python img_cli.py
  ```
- **Notes:**
  - Used for associating images with products and building image indices.

### 8. `upload_product.py`
- **Purpose:** Upload a single product JSON to Strapi via API.
- **Usage:**
  ```bash
  python uploaders/upload_product.py path/to/product.json
  ```

### 9. `upload_single.sh`
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

---

## 🚀 Typical Workflow

1. **Fetch Strapi mappings:**
   ```bash
   python core/fetch_mappings.py --base-url https://cms.example.com
   ```
2. **Convert Excel to JSON:**
   - For standard format: `python core/excel_to_json.py products.xlsx products.json`
   - For custom format: `python core/excel_to_json_custom.py`
3. **Review validation summary and fix any missing mappings.**
4. **Upload products:**
   - Use `uploaders/upload_product.py` or `core/cli_slide_driver.py` for interactive/automated upload.
5. **Manage images:**
   - Use `extractors/img_cli.py` for image association and indexing.

---

## 📝 Usage Examples

- **Extract and Upload Products from Slides:**
  ```bash
  python core/cli_slide_driver.py
  ```
- **Convert Excel to JSON:**
  ```bash
  python core/excel_to_json.py products.xlsx products.json
  python core/excel_to_json_custom.py
  ```
- **Merge PowerPoint with Excel JSON:**
  ```bash
  python core/slides_to_json_merger.py \
         --pptx "data/WEB MASTER Ver 9.pptx" \
         --input products.json \
         --output products_enriched.json \
         --issues issues.json
  ```
- **Upload Single Product:**
  ```bash
  python uploaders/upload_product.py products/slide_5_strapi_format.json
  ```
- **Manage Images:**
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

---

## 🎯 Best Practices

- Always backup before bulk operations.
- Test with single products first.
- Use the CLI for interactive control.
- Check logs in `products_uploaded/` for audit trail.
- Keep `image_index.json` updated for image management.
- Keep mapping files (`categories_map.json`, `divisions_map.json`) up to date with Strapi.

---
