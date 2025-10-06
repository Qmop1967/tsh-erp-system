#!/usr/bin/env node

const http = require('http');

console.log('🔍 Testing /items API Endpoint Directly\n');

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/items?limit=5',
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

      console.log('📊 API Response:');
      console.log('='.repeat(70));
      console.log(`Total items returned: ${items.length}\n`);

      items.forEach((item, idx) => {
        console.log(`${idx + 1}. Product ID: ${item.product_id}`);
        console.log(`   Product: ${JSON.stringify(item.product, null, 2)}`);
        console.log('');
      });

      console.log('='.repeat(70));

    } catch (error) {
      console.error('❌ Error:', error.message);
      console.log('Raw response:', data.substring(0, 500));
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Request failed:', error.message);
});

req.end();
