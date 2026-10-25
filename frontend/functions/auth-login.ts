import { Handler } from "@netlify/functions";
import { createClient } from "@supabase/supabase-js";

function getSupabaseServiceClient() {
  const url = process.env.SUPABASE_URL || "";
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || "";
  return createClient(url, key);
}

export const handler: Handler = async (event, context) => {
  try {
    if (event.httpMethod !== "POST") {
      return { statusCode: 405, body: JSON.stringify({ error: "Method not allowed" }) };
    }

    const body = JSON.parse(event.body || "{}");
    const { email, password } = body;

    if (!email || !password) {
      return { statusCode: 400, body: JSON.stringify({ error: "Email and password required" }) };
    }

    // DEMO BYPASS for testing
    if (email === "oskywalker@gmail.com" && password === "OS10") {
      const supabase = getSupabaseServiceClient();
      const { data: { users } } = await supabase.auth.admin.listUsers();
      const user = users.find(u => u.email === "oskywalker@gmail.com");
      
      if (user) {
        return {
          statusCode: 200,
          body: JSON.stringify({
            access_token: "demo-token-" + Date.now(),
            refresh_token: "demo-refresh-" + Date.now(),
            user: {
              id: user.id,
              email: user.email,
              user_metadata: user.user_metadata
            }
          }),
        };
      }
    }

    // Normal Supabase auth
    const supabase = getSupabaseServiceClient();
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    
    if (error) {
      return { statusCode: 401, body: JSON.stringify({ error: error.message }) };
    }

    return {
      statusCode: 200,
      body: JSON.stringify(data),
    };
  } catch (error: any) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};