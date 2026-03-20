import Link from "next/link";
import { Button } from "./ui/button";

// Server-side Supabase client — reads cookies to check session on the server
import { createClient } from "@/lib/supabase/server";
import { LogoutButton } from "./logout-button";

// This is a server component — it runs on the server and checks auth state
// before rendering, so there's no flash of unauthenticated UI
export async function AuthButton() {
  const supabase = await createClient();

  // getClaims() reads the session from the cookie without making a network
  // request to Supabase — faster than getUser() which hits the auth server
  const { data } = await supabase.auth.getClaims();
  const user = data?.claims;

  return user ? (
    // If logged in, show dashboard link and logout button
    <div className="flex items-center gap-4">
      <Button asChild variant={"default"}>
        <Link href="/dashboard">Dashboard</Link>
      </Button>
      <LogoutButton />
    </div>
  ) : (
    // If not logged in, show sign in link
    <Button asChild size="sm" variant={"default"}>
      <Link href="/auth/login">Sign in</Link>
    </Button>
  );
}
