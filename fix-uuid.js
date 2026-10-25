const fs = require('fs');
const sql = fs.readFileSync('supabase/migrations/20251025_000001_init.sql', 'utf8');
const fixed = sql
  .replace(/UUID\s+ON DELETE CASCADE/g, 'UUID')
  .replace(/UUID\s+REFERENCES auth\.users\(id\)/g, 'UUID');
fs.writeFileSync('supabase/migrations/20251025_000001_init.sql', fixed);
console.log('Fixed all UUID refs');