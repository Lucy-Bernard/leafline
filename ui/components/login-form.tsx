"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useAuth } from "@/lib/hooks/use-auth";
import { SupabaseAuthAdapter } from "@/lib/adapters/supabase-auth.adapter";

const authAdapter = new SupabaseAuthAdapter();

export function LoginForm({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  const [email, setEmail] = useState("");
  const { isLoading, error, isSuccess, sendMagicLink } = useAuth(authAdapter);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendMagicLink(email);
  };

  if (isSuccess) {
    return (
      <div className={cn("flex flex-col gap-6", className)} {...props}>
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Check your email</CardTitle>
            <CardDescription>
              We sent you a magic link to {email}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Click the link in the email to log in to your account.
            </p>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => window.location.reload()}
            >
              Send another link
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Login</CardTitle>
          <CardDescription>
            Enter your email to receive a magic link
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin}>
            <div className="flex flex-col gap-6">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  data-testid="email-input"
                />
              </div>
              {error && (
                <p className="text-sm text-red-500" data-testid="error-message">
                  {error}
                </p>
              )}
              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
                data-testid="submit-button"
              >
                {isLoading ? "Sending..." : "Send Magic Link"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
