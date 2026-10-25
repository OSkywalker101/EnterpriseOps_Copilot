const { createClient } = require("@supabase/supabase-js");

// Replace with your actual service role key
const SUPABASE_URL = "https://wwmxyfforktccebowpib.supabase.co";
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || "<your-service-role-key>";

const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

async function createUser() {
  const { data, error } = await supabase.auth.admin.createUser({
    email: "oskywalker@gmail.com",
    password: "OS10",
    email_confirm: true,
    user_metadata: { full_name: "Obiwan Skywalker", role: "Administrator" }
  });
  if (error) console.error("Error:", error.message);
  else console.log("User created:", data.user.id);
}
createUser();