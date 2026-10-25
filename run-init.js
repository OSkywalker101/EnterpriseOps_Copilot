const { Client } = require('pg');
const fs = require('fs');
const url = 'postgresql://neondb_owner:npg_zNCJum0wyj3S@ep-late-frog-a1dvkthw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require';
const client = new Client({ connectionString: url });
const sql = fs.readFileSync('supabase/migrations/20251025_000001_init.sql', 'utf8');
client.connect().then(() => client.query(sql)).then(r => console.log('OK:', r.command)).catch(e => console.error(e.message)).finally(() => client.end());