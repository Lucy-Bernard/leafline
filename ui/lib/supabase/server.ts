import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

// Creates a Supabase client for use on the server (server components, route handlers).
// Reads and writes session cookies directly from the Next.js cookie store.
// Important: always create a new instance per request — never store in a global variable.
export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_OR_ANON_KEY!,
    {
      cookies: {
        // Read all cookies from the incoming request
        getAll() {
          return cookieStore.getAll();
        },
        // Write cookies back to the response (e.g. to refresh the session token)
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            );
          } catch {
            // setAll can be called from a Server Component where cookies are read-only.
            // This is safe to ignore — the middleware handles session refreshing instead.
          }
        },
      },
    },
  );
}
