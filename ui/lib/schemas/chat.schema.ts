import { z } from "zod";

export const ChatMessageSchema = z.object({
  id: z.string(),
  chat_id: z.string(),
  role: z.enum(["USER", "AI"]),
  content: z.string(),
  created_at: z.string(),
});

export const GeneralChatSchema = z.object({
  id: z.string(),
  plant_id: z.string(),
  messages: z.array(ChatMessageSchema),
  created_at: z.string(),
  updated_at: z.string(),
});

export const ChatArraySchema = z.array(GeneralChatSchema);

export const CreateChatRequestSchema = z.object({
  content: z.string().min(1, "Message cannot be empty"),
});

export const ContinueChatRequestSchema = z.object({
  content: z.string().min(1, "Message cannot be empty"),
});
