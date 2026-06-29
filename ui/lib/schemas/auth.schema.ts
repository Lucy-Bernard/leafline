// Zod schema for validating the email field on the login form before sending it to Supabase.
import { z } from "zod";

export const EmailSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address" }),
});

export type EmailInput = z.infer<typeof EmailSchema>;
