import { z } from "zod";

export const EmailSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address" }),
});

export type EmailInput = z.infer<typeof EmailSchema>;
