#!/usr/bin/env node

const http = require('http');

console.log('🔍 Testing API Response for Product Images\n');

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/items?limit=10',
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
};

const req = http.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    try {
      const items = JSON.parse(data);

      console.log('📊 API Response Analysis:');
      console.log('='.repeat(60));
      console.log(`Total items returned: ${items.length}\n`);

      let imagesFound = 0;
      let noImages = 0;

      console.log('First 10 products:\n');
      items.slice(0, 10).forEach((item, idx) => {
        const product = item.product;
        const hasImage = product.image_url ? '✅ HAS IMAGE' : '❌ NO IMAGE';

        if (product.image_url) {
          imagesFound++;
          console.log(`${idx + 1}. ${product.sku}`);
          console.log(`   Name: ${product.name}`);
          console.log(`   Image URL: ${product.image_url}`);
          console.log(`   ${hasImage}\n`);
        } else {
          noImages++;
        }
      });

      console.log('='.repeat(60));
      console.log(`✅ Products with images: ${imagesFound}`);
      console.log(`❌ Products without images: ${noImages}`);
      console.log('='.repeat(60));

    } catch (error) {
      console.error('❌ Error parsing response:', error.message);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Request failed:', error.message);
});

req.end();
