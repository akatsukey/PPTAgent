# 🗂️ LetsMed Scripts Directory (Reorganized)

This directory contains all automation, data processing, and CLI tools for managing the LetsMed product pipeline, organized for clarity and maintainability.

---

## 📁 **New Directory Structure**

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
│   └── fetch_mappings.py      # Strapi mappings fetcher
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
│   ├── products.xlsx
│   ├── WEB MASTER Ver 9.pptx
│   └── IMAGES/
│
├── utils/                      # 🔧 HELPER MODULES
│   ├── __init__.py
│   ├── strapi.py
│   └── diff.py
│
├── products/                   # 📦 PRODUCT FILES
├── products_uploaded/          # 📋 UPLOAD LOGS
└── venv/                      # 🐍 VIRTUAL ENVIRONMENT
```

---

## 🎯 **Core Scripts** (`core/`)

These are your main execution scripts - the ones you'll use most often:

### **`cli_slide_driver.py`** ⭐ **MAIN ENTRY POINT**
- **Purpose:** Interactive CLI for extracting/uploading products from PowerPoint slides
- **Usage:** `python core/cli_slide_driver.py`
- **Notes:** Your primary tool for processing slides

### **`excel_to_json.py`**
- **Purpose:** Convert standard-format Excel to Strapi JSON with validation
- **Usage:** `python core/excel_to_json.py products.xlsx products.json`

### **`excel_to_json_custom.py`**
- **Purpose:** Convert custom-format Excel to Strapi JSON with validation
- **Usage:** `python core/excel_to_json_custom.py`

### **`fetch_mappings.py`**
- **Purpose:** Download Strapi categories/divisions as JSON mappings
- **Usage:** `python core/fetch_mappings.py --base-url https://cms.example.com`

---

## 📊 **Extractors** (`extractors/`)

Specialized tools for data extraction:

### **`extract_product_from_pptx.py`**
- **Purpose:** Extract product data from PowerPoint slides
- **Usage:** `python extractors/extract_product_from_pptx.py path/to/file.pptx`

### **`img_cli.py`**
- **Purpose:** CLI for managing and indexing product images
- **Usage:** `python extractors/img_cli.py`

---

## ⬆️ **Uploaders** (`uploaders/`)

Tools for uploading data to Strapi:

### **`upload_product.py`**
- **Purpose:** Upload a single product JSON to Strapi
- **Usage:** `python uploaders/upload_product.py path/to/product.json`

### **`upload_single.sh`**
- **Purpose:** Bash script for uploading a single product JSON
- **Usage:** `./uploaders/upload_single.sh path/to/product.json`

---

## 📤 **Output** (`output/`)

Generated files from your scripts:

- **`products.json`** - Current product data with category/division names
- **`products_converted.json`** - Previous conversion results
- **`categories_map.json`** - Strapi category mappings
- **`divisions_map.json`** - Strapi division mappings
- **`image_index.json`** - Product image associations
- **`progress.json`** - CLI progress tracking

---

## 📚 **Documentation** (`docs/`)

- **`strapi_id_reference.md`** - Complete reference for Strapi IDs

---

## 🚀 **Quick Start (After Reorganization)**

1. **Fetch Strapi mappings:**
   ```bash
   python core/fetch_mappings.py --base-url https://cms.example.com
   ```

2. **Convert Excel to JSON:**
   ```bash
   python core/excel_to_json_custom.py
   ```

3. **Process PowerPoint slides:**
   ```bash
   python core/cli_slide_driver.py
   ```

4. **Upload products:**
   ```bash
   python uploaders/upload_product.py output/products.json
   ```

---

## 💡 **Benefits of This Organization**

✅ **Clear separation** of concerns (core, extractors, uploaders)  
✅ **Easy to find** the right tool for the job  
✅ **Clean main directory** with only essential files  
✅ **Logical grouping** of related functionality  
✅ **Scalable structure** for future additions  

---

## 🔧 **Maintenance**

- **Core scripts** are your primary tools
- **Extractors** handle data extraction from various sources
- **Uploaders** handle data upload to Strapi
- **Output** contains all generated files
- **Docs** contains all documentation

This organization makes it much easier to understand what each script does and where to find it! 🎯 