#!/usr/bin/env node

const https = require('https');

const API_KEY = process.env.BRAVE_API_KEY || process.env.BRAVE_SEARCH_API_KEY;

if (!API_KEY) {
  console.error('❌ Missing BRAVE_API_KEY or BRAVE_SEARCH_API_KEY');
  process.exit(1);
}

const query = 'OpenClaw AI assistant';
const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=5`;

console.log('🔍 Testing Brave Search API...');
console.log('Query:', query);
console.log('');

const options = {
  headers: {
    'Accept': 'application/json',
    'X-Subscription-Token': API_KEY
  }
};

https.get(url, options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    try {
      const result = JSON.parse(data);
      
      if (result.message) {
        console.error('❌ API Error:', result.message);
        process.exit(1);
      }
      
      console.log('✅ API Working!');
      console.log('Query time:', result.query?.posted_at || 'N/A');
      console.log('');
      
      if (result.web && result.web.results && result.web.results.length > 0) {
        console.log('Top Results:');
        result.web.results.forEach((item, i) => {
          console.log(`\n${i + 1}. ${item.title}`);
          console.log(`   ${item.url}`);
          console.log(`   ${item.description}`);
        });
      } else {
        console.log('No results found.');
      }
      
    } catch (err) {
      console.error('❌ Parse Error:', err.message);
      console.log('Raw response:', data.substring(0, 500));
      process.exit(1);
    }
  });
}).on('error', (err) => {
  console.error('❌ Request Error:', err.message);
  process.exit(1);
});
