"use client";

// Browser-side Supabase client for client components
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

export function LogoutButton() {
  const router = useRouter();

  const logout = async () => {
    const supabase = createClient();

    // signOut() clears the session cookie — the user is fully logged out
    // on both the client and server after this
    await supabase.auth.signOut();

    // Redirect to login page after sign out
    router.push("/auth/login");
  };

  return <Button onClick={logout}>Logout</Button>;
}
