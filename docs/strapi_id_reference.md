# Strapi ID Reference Guide

## Categories (for `category` field)

| ID | Name |
|----|------|
| 69 | Gloves |
| 70 | Adhesive tapes & dressings |
| 71 | Gauze |
| 72 | Disposable Non-Woven Gourments |
| 73 | Suction Catheter |
| 74 | Urinary Catheters |
| 75 | Enteral Feeding Tubes |
| 76 | Hemodialysis Catheters |

## Divisions (for `divisions` field - comma-separated)

| ID | Name |
|----|------|
| 47 | Infusion |
| 48 | Injectables |
| 49 | Diabetis care |
| 50 | Diagnostic |
| 51 | Hemodialysis |
| 52 | Nutrition |
| 53 | Urology |
| 54 | Wound management |
| 55 | Ortopedic |
| 56 | Protection |
| 57 | Measurement devices |
| 58 | Anesthesia / Respiratory |
| 59 | Surgery |
| 60 | Safety devices |

## Example Excel Format

| referenceString | name | category | divisions | standard | description |
|----------------|------|----------|-----------|----------|-------------|
| 4.1.6 | Product Name | 69 | 56,58 | ISO Standard | Product description |

## Notes

- **category**: Use a single integer ID from the Categories table above
- **divisions**: Use comma-separated integer IDs from the Divisions table above (e.g., "56,58")
- **referenceString**: The product reference code (e.g., "4.1.6")
- **name**: The product name
- **standard**: Manufacturing standard (optional)
- **description**: Product description in markdown format (optional)
- **tableInMd**: Technical specifications table in markdown (optional)

## Usage with excel_to_json.py

```bash
python excel_to_json.py products.xlsx output.json
```

The script will convert your Excel file to the proper Strapi JSON format for import. 