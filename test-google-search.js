#!/usr/bin/env node

const https = require('https');

const API_KEY = process.env.GOOGLE_SEARCH_API_KEY;
const ENGINE_ID = process.env.GOOGLE_SEARCH_ENGINE_ID;

if (!API_KEY || !ENGINE_ID) {
  console.error('❌ Missing environment variables');
  console.log('GOOGLE_SEARCH_API_KEY:', API_KEY ? '✓' : '✗');
  console.log('GOOGLE_SEARCH_ENGINE_ID:', ENGINE_ID ? '✓' : '✗');
  process.exit(1);
}

const query = 'OpenClaw AI assistant';
const url = `https://www.googleapis.com/customsearch/v1?key=${API_KEY}&cx=${ENGINE_ID}&q=${encodeURIComponent(query)}`;

console.log('🔍 Testing Google Custom Search API...');
console.log('Query:', query);
console.log('');

https.get(url, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    try {
      const result = JSON.parse(data);
      
      if (result.error) {
        console.error('❌ API Error:', result.error.message);
        console.error('Details:', result.error);
        process.exit(1);
      }
      
      console.log('✅ API Working!');
      console.log('Total results:', result.searchInformation?.totalResults || 0);
      console.log('');
      
      if (result.items && result.items.length > 0) {
        console.log('Top 3 Results:');
        result.items.slice(0, 3).forEach((item, i) => {
          console.log(`\n${i + 1}. ${item.title}`);
          console.log(`   ${item.link}`);
          console.log(`   ${item.snippet}`);
        });
      }
      
    } catch (err) {
      console.error('❌ Parse Error:', err.message);
      console.log('Raw response:', data);
      process.exit(1);
    }
  });
}).on('error', (err) => {
  console.error('❌ Request Error:', err.message);
  process.exit(1);
});
