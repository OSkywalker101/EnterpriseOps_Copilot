const fs = require('fs');
const sql = fs.readFileSync('supabase/migrations/20251025_000001_init.sql', 'utf8');
const fixed = sql
  .replace(/REFERENCES auth\.users\(id\) ON DELETE CASCADE/g, '')
  .replace(/REFERENCES auth\.users\(id\)/g, '');
fs.writeFileSync('supabase/migrations/20251025_000001_init.sql', fixed);
console.log('Fixed');