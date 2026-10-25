const { Client } = require('pg');
const fs = require('fs');
const url = "postgresql://neondb_owner:npg_zNCJum0wyj3S@ep-late-frog-a1dvkthw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require";
const client = new Client({ connectionString: url });
const sql = fs.readFileSync('run-all.sql', 'utf8');

client.connect()
  .then(() => client.query(sql))
  .then(r => {
    console.log('Migration result:', r.command, r.rowCount);
    return client.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name");
  })
  .then(r => {
    console.log('Tables:', r.rows.map(x => x.table_name).join(', '));
    client.end();
  })
  .catch(e => { console.error('Error:', e.message); client.end(); });