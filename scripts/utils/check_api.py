import requests
import json

response = requests.get('http://localhost:8000/items?limit=5')
items = response.json()

print("API Response - First 5 products:")
count = 0
for item in items:
    if count >= 5:
        break
    product = item['product']
    print(f"{product['sku']}: image_url = {product.get('image_url', 'NO IMAGE')}")
    count += 1
