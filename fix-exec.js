const fs = require('fs');
const sql = fs.readFileSync('supabase/migrations/20251025_000001_init.sql', 'utf8');
const fixed = sql.replace(/EXECUTE PROCEDURE/g, 'EXECUTE FUNCTION');
fs.writeFileSync('supabase/migrations/20251025_000001_init.sql', fixed);
console.log('Fixed EXECUTE');