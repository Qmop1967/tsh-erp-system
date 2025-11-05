// Mock TDS Core API Server for Testing Dashboard
// Run with: node mock-api-server.js

const http = require('http');
const url = require('url');

const PORT = 8001;

// Mock data
const mockHealth = {
  status: 'healthy',
  timestamp: new Date().toISOString(),
  uptime_seconds: 345678,
  database: {
    status: 'connected',
    response_time_ms: 15
  },
  queue: {
    pending: 42,
    processing: 5,
    failed: 3,
    completed_last_hour: 1234
  },
  version: '1.0.0'
};

const mockQueueStats = {
  timestamp: new Date().toISOString(),
  stats: {
    total: 5432,
    by_status: {
      pending: 42,
      processing: 5,
      completed: 5280,
      failed: 3,
      retry: 2,
      dead_letter: 0
    },
    by_entity: {
      product: 2100,
      customer: 850,
      invoice: 1200,
      bill: 450,
      credit_note: 320,
      stock_adjustment: 180,
      price_list: 232,
      branch: 50,
      user: 30,
      order: 20
    },
    by_source: {
      zoho: 5100,
      manual: 200,
      scheduled: 100,
      reconciliation: 32
    },
    oldest_pending: {
      id: 'evt_12345',
      created_at: new Date(Date.now() - 3600000).toISOString(),
      entity_type: 'product',
      age_minutes: 60
    },
    processing_rate: {
      last_minute: Math.floor(Math.random() * 20) + 10,
      last_hour: 1234,
      last_24_hours: 28500
    }
  }
};

const mockWebhookHealth = {
  status: 'healthy',
  timestamp: new Date().toISOString(),
  checks: {
    database: true,
    queue_processing: true,
    recent_failures: false
  },
  metrics: {
    total_webhooks_received: 5432,
    successful_last_hour: 1231,
    failed_last_hour: 3,
    average_processing_time_ms: 145,
    queue_backlog: 42
  }
};

const mockPing = {
  status: 'ok',
  timestamp: Date.now() / 1000
};

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json'
};

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(200, corsHeaders);
    res.end();
    return;
  }

  // Handle routes
  if (pathname === '/health') {
    // Randomly update queue stats to simulate real-time
    mockHealth.queue.processing = Math.floor(Math.random() * 10) + 1;
    mockHealth.queue.pending = Math.floor(Math.random() * 100) + 20;
    mockHealth.timestamp = new Date().toISOString();
    mockHealth.uptime_seconds += 5;

    res.writeHead(200, corsHeaders);
    res.end(JSON.stringify(mockHealth));
  }
  else if (pathname === '/queue/stats') {
    // Update processing rate to simulate activity
    mockQueueStats.stats.processing_rate.last_minute = Math.floor(Math.random() * 30) + 10;
    mockQueueStats.stats.by_status.processing = Math.floor(Math.random() * 10) + 1;
    mockQueueStats.stats.by_status.pending = Math.floor(Math.random() * 100) + 20;
    mockQueueStats.timestamp = new Date().toISOString();

    res.writeHead(200, corsHeaders);
    res.end(JSON.stringify(mockQueueStats));
  }
  else if (pathname === '/webhooks/health') {
    mockWebhookHealth.timestamp = new Date().toISOString();
    res.writeHead(200, corsHeaders);
    res.end(JSON.stringify(mockWebhookHealth));
  }
  else if (pathname === '/ping') {
    mockPing.timestamp = Date.now() / 1000;
    res.writeHead(200, corsHeaders);
    res.end(JSON.stringify(mockPing));
  }
  else if (pathname === '/') {
    res.writeHead(200, corsHeaders);
    res.end(JSON.stringify({
      service: 'TDS Core API (Mock)',
      version: '1.0.0',
      status: 'running'
    }));
  }
  else {
    res.writeHead(404, corsHeaders);
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

server.listen(PORT, () => {
  console.log(`\n🚀 Mock TDS Core API Server running on http://localhost:${PORT}`);
  console.log(`\n📊 Available endpoints:`);
  console.log(`   - GET /health`);
  console.log(`   - GET /queue/stats`);
  console.log(`   - GET /webhooks/health`);
  console.log(`   - GET /ping`);
  console.log(`\n✨ Dashboard should now work at http://localhost:5173\n`);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`\n❌ Port ${PORT} is already in use!`);
    console.error(`   Try: lsof -ti:${PORT} | xargs kill -9\n`);
  } else {
    console.error('Server error:', err);
  }
  process.exit(1);
});
