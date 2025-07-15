import json

# Load products.json
with open('../products.json', 'r') as f:
    products = json.load(f)

# Load extracted data
with open('products/slide_101_strapi_format.json', 'r') as f:
    extracted = json.load(f)

ref = '4.14.2'

# Find the product in products.json
prod_name = None
for p in products:
    if p['data']['referenceString'] == ref:
        prod_name = p['data']['name']
        break

extracted_name = extracted['data']['name']

print(f'Reference: {ref}')
print(f'Products.json name: {prod_name}')
print(f'Extracted name: {extracted_name}')
print(f'Names match: {prod_name == extracted_name}')

# Check if the update logic would work
ref_to_product = {p['data']['referenceString']: p for p in products}
if ref in ref_to_product:
    prod = ref_to_product[ref]['data']
    print(f'\nCurrent product data:')
    print(f'  Name: {prod["name"]}')
    print(f'  Description length: {len(prod.get("description", ""))}')
    print(f'  Table length: {len(prod.get("tableInMd", ""))}')
    
    # Simulate update
    new_desc = extracted['data']['description']
    new_table = extracted['data']['tableInMd']
    
    if new_desc and new_desc != "???" and new_desc != "??????????":
        prod['description'] = new_desc
        print(f'  Would update description to length: {len(new_desc)}')
    
    if new_table and new_table != "???" and new_table != "??????????":
        prod['tableInMd'] = new_table
        print(f'  Would update table to length: {len(new_table)}')
else:
    print(f'Reference {ref} not found in products.json') 