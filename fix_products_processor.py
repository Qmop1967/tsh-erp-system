#!/usr/bin/env python3
"""
Fix product processor to handle invalid decimal values
"""

import re

# Read the file
with open('/root/TSH_ERP_Ecosystem/app/tds/integrations/zoho/processors/products.py', 'r') as f:
    content = f.read()

# Add safe_decimal helper function after the class definition
helper_function = '''
    @staticmethod
    def safe_decimal(value, default=0):
        """
        Safely convert a value to Decimal, handling invalid inputs

        Args:
            value: Value to convert
            default: Default value if conversion fails

        Returns:
            Decimal: Converted value or default
        """
        if value is None or value == '':
            return Decimal(str(default))

        try:
            # Handle string values
            if isinstance(value, str):
                value = value.strip()
                if not value or value.lower() in ('n/a', 'none', 'null'):
                    return Decimal(str(default))

            return Decimal(str(value))
        except (ValueError, TypeError, ArithmeticError):
            logger.warning(f"Invalid decimal value: {value}, using default: {default}")
            return Decimal(str(default))

'''

# Find the position to insert (after class definition, before first @staticmethod)
class_pos = content.find('class ProductProcessor:')
docstring_end = content.find('"""', class_pos + 50)
next_method = content.find('    @staticmethod', docstring_end)

# Insert the helper function
content = content[:next_method] + helper_function + content[next_method:]

# Replace Decimal(str(product_data.get(...))) with ProductProcessor.safe_decimal(product_data.get(...))
patterns = [
    (r"Decimal\(str\(product_data\.get\('rate', 0\)\)\)", "ProductProcessor.safe_decimal(product_data.get('rate', 0))"),
    (r"Decimal\(str\(product_data\.get\('purchase_rate', 0\)\)\)", "ProductProcessor.safe_decimal(product_data.get('purchase_rate', 0))"),
    (r"Decimal\(str\(product_data\.get\('actual_available_stock', 0\)\)\)", "ProductProcessor.safe_decimal(product_data.get('actual_available_stock', 0))"),
    (r"Decimal\(str\(product_data\.get\('available_stock', 0\)\)\)", "ProductProcessor.safe_decimal(product_data.get('available_stock', 0))"),
    (r"Decimal\(str\(product_data\.get\('reorder_level', 0\)\)\)", "ProductProcessor.safe_decimal(product_data.get('reorder_level', 0))"),
    (r"Decimal\(str\(product_data\.get\('tax_percentage', 0\)\)\)", "ProductProcessor.safe_decimal(product_data.get('tax_percentage', 0))"),
    (r"Decimal\(str\(variant\.get\('rate', 0\)\)\)", "ProductProcessor.safe_decimal(variant.get('rate', 0))"),
    (r"Decimal\(str\(variant\.get\('stock', 0\)\)\)", "ProductProcessor.safe_decimal(variant.get('stock', 0))"),
]

for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

# Write back
with open('/root/TSH_ERP_Ecosystem/app/tds/integrations/zoho/processors/products.py', 'w') as f:
    f.write(content)

print('✅ Fixed product processor to handle invalid decimal values')
