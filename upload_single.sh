#!/bin/bash

# Upload a single JSON product to Strapi
# Usage: ./upload_single.sh products/slide_15_strapi_format.json

if [ $# -eq 0 ]; then
    echo "Usage: $0 <json_file_path>"
    echo "Example: $0 products/slide_15_strapi_format.json"
    exit 1
fi

JSON_FILE="$1"

if [ ! -f "$JSON_FILE" ]; then
    echo "❌ File not found: $JSON_FILE"
    exit 1
fi

echo "📤 Uploading $JSON_FILE to Strapi..."

# Load environment variables
source .env

# Upload using curl
curl -X POST \
  -H "Authorization: Bearer $STRAPI_TOKEN" \
  -H "Content-Type: application/json" \
  -d @"$JSON_FILE" \
  http://localhost:1337/api/medical-products

echo ""
echo "✅ Upload completed!" 