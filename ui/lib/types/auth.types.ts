// TypeScript interfaces for authentication — re-exports Supabase's User type so the
// rest of the app doesn't need to import from @supabase/supabase-js directly.
import { User as SupabaseUser } from "@supabase/supabase-js";

export interface AuthResponse {
  success: boolean;
  error?: string;
}

export type User = SupabaseUser;

export interface IAuthAdapter {
  sendMagicLink(email: string): Promise<AuthResponse>;
  getCurrentUser(): Promise<User | null>;
  signOut(): Promise<void>;
}
