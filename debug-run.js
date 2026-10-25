const { Client } = require('pg');
const fs = require('fs');
const url = "postgresql://neondb_owner:npg_zNCJum0wyj3S@ep-late-frog-a1dvkthw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require";
const client = new Client({ connectionString: url });
const sql = fs.readFileSync("supabase/migrations/20251025_000001_init.sql", "utf8");

async function run() {
  await client.connect();
  // Split by semicolon but keep function body together
  const parts = sql.split(/;\s*$/m);
  for (let i = 0; i < parts.length; i++) {
    const stmt = parts[i].trim() + ";";
    if (!stmt || stmt === ";") continue;
    try {
      await client.query(stmt);
      console.log("OK:", i+1);
    } catch (e) {
      console.error("FAIL", i+1, ":", e.message);
      console.error(stmt.substring(0, 300));
      break;
    }
  }
  await client.end();
}
run();