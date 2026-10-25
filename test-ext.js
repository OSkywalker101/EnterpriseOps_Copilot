const { Client } = require('pg');
const url = 'postgresql://neondb_owner:npg_zNCJum0wyj3S@ep-late-frog-a1dvkthw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require';
const client = new Client({ connectionString: url });
client.connect()
  .then(() => client.query("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
  .then(() => console.log('Extension OK'))
  .catch(e => console.error('Ext:', e.message))
  .finally(() => client.end());