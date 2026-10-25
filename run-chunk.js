const { Client } = require('pg');
const fs = require('fs');
const url = 'postgresql://neondb_owner:npg_zNCJum0wyj3S@ep-late-frog-a1dvkthw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require';
const client = new Client({ connectionString: url });
const sql = fs.readFileSync('supabase/migrations/20251025_000001_init.sql', 'utf8');

// Split by semicolon and run each statement
const statements = sql.split(';').map(s => s.trim()).filter(s => s.length > 0);

async function run() {
  await client.connect();
  for (let i = 0; i < statements.length; i++) {
    const stmt = statements[i] + ';';
    try {
      await client.query(stmt);
      console.log('OK statement', i+1);
    } catch (e) {
      console.error('Error at', i+1, ':', e.message);
      console.error('Statement:', stmt.substring(0, 200));
    }
  }
  await client.end();
}
run();