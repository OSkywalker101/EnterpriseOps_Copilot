# Netlify Deployment Guide

## Prerequisites
1. [Netlify Account](https://netlify.com)
2. [Supabase Account](https://supabase.com)
3. [Groq Account](https://console.groq.com) (for AI features)

## Step 1: Set up Supabase

1. Create a new Supabase project
2. Go to Settings > API - copy URL and keys
3. Go to SQL Editor and run migrations:
   - supabase/migrations/20251025_000001_init.sql
   - supabase/migrations/20251025_000002_rls.sql
4. Run seed data: supabase/seed.sql
5. Enable Auth (Email/Password)

## Step 2: Configure Netlify

1. Connect your Git repository to Netlify
2. Build settings (auto-detected from netlify.toml):
   - Base directory: rontend
   - Build command: 
pm run build
   - Publish directory: dist
   - Functions directory: 
etlify/functions

## Step 3: Environment Variables

Add these in Netlify Site Settings > Environment variables:

### Frontend (Build-time)
- VITE_SUPABASE_URL - Your Supabase project URL
- VITE_SUPABASE_ANON_KEY - Supabase anon/public key
- VITE_API_URL - /api/v1 or your functions URL

### Backend/Functions (Server-side)
- SUPABASE_URL - Same as above
- SUPABASE_SERVICE_ROLE_KEY - Supabase service role key (keep secret!)
- SUPABASE_ANON_KEY - Supabase anon key
- GROQ_API_KEY - Groq API key
- AI_MODEL - llama-3.1-8b-instant (default)
- APP_ENV - production
- DEMO_MODE - alse for full AI, 	rue for deterministic fallback

## Step 4: Deploy

`ash
# Using Netlify CLI
netlify login
netlify init
netlify deploy --prod
`

Or just push to Git - Netlify will auto-deploy.

## Testing

After deployment:
1. Visit your Netlify URL
2. Sign up with a new account
3. Check that demo data appears
4. Try AI chat queries

## Security Notes
- Never commit service role keys
- RLS policies protect all data
- Groq API key only in Netlify Functions (server-side)
- All AI calls go through validated tools
- Citations link to real database records
