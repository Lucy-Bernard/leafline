import { createBrowserClient } from "@supabase/ssr";

// Creates a Supabase client for use in the browser (client components).
// Uses the public anon key — safe to expose on the frontend.
// This client reads/writes the session from cookies automatically.
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_OR_ANON_KEY!,
  );
}
