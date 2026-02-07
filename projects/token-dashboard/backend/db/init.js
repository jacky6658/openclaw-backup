// Database initialization
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, 'openclaw-tokens.db');
const SCHEMA_PATH = path.join(__dirname, 'schema.sql');

function initDatabase() {
  console.log('📦 Initializing database...');
  
  const db = new sqlite3.Database(DB_PATH);
  
  // Read schema
  const schema = fs.readFileSync(SCHEMA_PATH, 'utf8');
  
  // Execute schema
  db.exec(schema, (err) => {
    if (err) {
      console.error('❌ Database initialization failed:', err);
      process.exit(1);
    }
    
    console.log('✅ Database initialized successfully');
    console.log(`📍 Location: ${DB_PATH}`);
    
    db.close();
  });
}

// Run if executed directly
if (require.main === module) {
  initDatabase();
}

module.exports = { initDatabase, DB_PATH };
