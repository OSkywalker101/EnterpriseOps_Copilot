const fs = require('fs');
const sql = fs.readFileSync('supabase/migrations/20251025_000001_init.sql', 'utf8');
const lines = sql.split('\n');
for(let i=0; i<lines.length; i++) {
  if(lines[i].includes('\\') || lines[i].includes('$$')) {
    console.log('Line ' + (i+1) + ':', lines[i].substring(0, 100));
  }
}