import { createClient } from "@/lib/supabase/client";
import { IAuthAdapter, AuthResponse, User } from "@/lib/types/auth.types";

export class SupabaseAuthAdapter implements IAuthAdapter {
  async sendMagicLink(email: string): Promise<AuthResponse> {
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/confirm`,
        },
      });

      if (error) {
        return {
          success: false,
          error: error.message,
        };
      }

      return {
        success: true,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "An error occurred",
      };
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const supabase = createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();
      return user;
    } catch {
      return null;
    }
  }

  async signOut(): Promise<void> {
    const supabase = createClient();
    await supabase.auth.signOut();
  }
}
