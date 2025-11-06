"use client";

import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function ConfirmPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const supabase = createClient();
        
        const hashParams = new URLSearchParams(
          window.location.hash.substring(1)
        );
        const access_token = hashParams.get("access_token");
        const refresh_token = hashParams.get("refresh_token");

        if (access_token && refresh_token) {
          const { error } = await supabase.auth.setSession({
            access_token,
            refresh_token,
          });

          if (error) {
            setError(error.message);
            return;
          }

          router.push("/dashboard");
        } else {
          const { data, error } = await supabase.auth.getSession();
          
          if (error) {
            setError(error.message);
            return;
          }

          if (data.session) {
            router.push("/dashboard");
          } else {
            setError("No session found. Please try logging in again.");
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      }
    };

    handleAuthCallback();
  }, [router]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Authentication Error</h1>
          <p className="text-red-500 mb-4">{error}</p>
          <a
            href="/auth/login"
            className="text-blue-500 hover:underline"
          >
            Return to login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Confirming authentication...</h1>
        <p className="text-muted-foreground">Please wait while we log you in.</p>
      </div>
    </div>
  );
}
