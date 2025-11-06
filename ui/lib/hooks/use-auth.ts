import { useState } from "react";
import { IAuthAdapter } from "@/lib/types/auth.types";
import { EmailSchema } from "@/lib/schemas/auth.schema";

interface UseAuthState {
  isLoading: boolean;
  error: string | null;
  isSuccess: boolean;
}

interface UseAuthReturn extends UseAuthState {
  sendMagicLink: (email: string) => Promise<void>;
  signOut: () => Promise<void>;
}

export function useAuth(adapter: IAuthAdapter): UseAuthReturn {
  const [state, setState] = useState<UseAuthState>({
    isLoading: false,
    error: null,
    isSuccess: false,
  });

  const sendMagicLink = async (email: string) => {
    setState({ isLoading: true, error: null, isSuccess: false });

    try {
      const validation = EmailSchema.safeParse({ email });

      if (!validation.success) {
        setState({
          isLoading: false,
          error: validation.error.issues[0]?.message || "Invalid email",
          isSuccess: false,
        });
        return;
      }

      const response = await adapter.sendMagicLink(email);

      if (response.success) {
        setState({ isLoading: false, error: null, isSuccess: true });
      } else {
        setState({
          isLoading: false,
          error: response.error || "Failed to send magic link",
          isSuccess: false,
        });
      }
    } catch (error) {
      setState({
        isLoading: false,
        error: error instanceof Error ? error.message : "An error occurred",
        isSuccess: false,
      });
    }
  };

  const signOut = async () => {
    setState({ isLoading: true, error: null, isSuccess: false });
    try {
      await adapter.signOut();
      setState({ isLoading: false, error: null, isSuccess: false });
    } catch (error) {
      setState({
        isLoading: false,
        error: error instanceof Error ? error.message : "Failed to sign out",
        isSuccess: false,
      });
    }
  };

  return {
    ...state,
    sendMagicLink,
    signOut,
  };
}
