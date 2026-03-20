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
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";

type Mode = "login" | "signup";

export function LoginForm({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const supabase = createClient();

    if (mode === "signup") {
      if (password !== confirmPassword) {
        setError("Passwords do not match");
        setIsLoading(false);
        return;
      }

      const { error: signUpError, data: signUpData } =
        await supabase.auth.signUp({ email, password });
      console.log("signup result:", { signUpError, signUpData });

      if (signUpError) {
        setError(signUpError.message);
        setIsLoading(false);
      } else {
        const { error: signInError, data: signInData } =
          await supabase.auth.signInWithPassword({
            email,
            password,
          });
        console.log("signup then signin result:", { signInError, signInData });

        if (signInError) {
          setError(
            "Account created! Please check your email to confirm before signing in.",
          );
          setIsLoading(false);
        } else {
          router.push("/dashboard");
        }
      }
    } else {
      const { error: loginError, data: loginData } =
        await supabase.auth.signInWithPassword({
          email,
          password,
        });
      console.log("login result:", { loginError, loginData });

      if (loginError) {
        setError(loginError.message);
        setIsLoading(false);
      } else {
        router.push("/dashboard");
      }
    }
  };

  const toggleMode = () => {
    setMode(mode === "login" ? "signup" : "login");
    setError(null);
    setPassword("");
    setConfirmPassword("");
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">
            {mode === "login" ? "Login" : "Create an account"}
          </CardTitle>
          <CardDescription>
            {mode === "login"
              ? "Enter your email and password to sign in"
              : "Enter your details to create an account"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
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
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              {mode === "signup" && (
                <div className="grid gap-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </div>
              )}

              {error && <p className="text-sm text-red-500">{error}</p>}

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading
                  ? mode === "login"
                    ? "Signing in..."
                    : "Creating account..."
                  : mode === "login"
                    ? "Sign in"
                    : "Create account"}
              </Button>

              <p className="text-sm text-center text-muted-foreground">
                {mode === "login"
                  ? "Don't have an account?"
                  : "Already have an account?"}{" "}
                <button
                  type="button"
                  onClick={toggleMode}
                  className="underline underline-offset-4 hover:text-primary"
                >
                  {mode === "login" ? "Sign up" : "Sign in"}
                </button>
              </p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
