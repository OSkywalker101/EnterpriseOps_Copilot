const fs = require('fs');
const sql = fs.readFileSync('supabase/migrations/20251025_000002_rls.sql', 'utf8');
const fixed = sql
  .replace(/auth\.uid\(\)/g, "current_user")
  .replace(/auth\.users/g, "profiles")
  .replace(/CREATE TRIGGER on_auth_user_created[\s\S]*?;/g, '')
  .replace(/CREATE OR REPLACE FUNCTION public\.handle_new_user\(\)[\s\S]*?LANGUAGE plpgsql SECURITY DEFINER;/g, '');
fs.writeFileSync('supabase/migrations/20251025_000002_rls.sql', fixed);
console.log('Fixed RLS');