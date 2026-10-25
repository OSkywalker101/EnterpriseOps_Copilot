const fs = require('fs');
const sql = fs.readFileSync('supabase/migrations/20251025_000001_init.sql', 'utf8');
const fixed = sql.replace(/PRIMARY KEY\s+ON DELETE CASCADE/g, 'PRIMARY KEY');
fs.writeFileSync('supabase/migrations/20251025_000001_init.sql', fixed);
console.log('Fixed PK');