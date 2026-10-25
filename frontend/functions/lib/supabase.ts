import { createClient } from '@supabase/supabase-js';

export function getSupabaseServiceClient() {
  const url = process.env.SUPABASE_URL || '';
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
  return createClient(url, key);
}

export function getSupabaseUserClient(authHeader: string | undefined) {
  const url = process.env.SUPABASE_URL || '';
  const anonKey = process.env.SUPABASE_ANON_KEY || '';
  const client = createClient(url, anonKey);
  if (authHeader?.startsWith('Bearer ')) {
    client.auth.setSession({
      access_token: authHeader.replace('Bearer ', ''),
      refresh_token: '',
    } as any);
  }
  return client;
}

