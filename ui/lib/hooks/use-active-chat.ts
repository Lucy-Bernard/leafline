import { useCallback, useState } from "react";
import { IChatAdapter, ChatMessage } from "@/lib/types/chat.types";

type ChatStatus = "idle" | "loading" | "active" | "error";

export function useActiveChat(adapter: IChatAdapter, plantId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState<ChatStatus>("idle");
  const [chatId, setChatId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startChat = useCallback(
    async (content: string) => {
      setStatus("loading");
      setError(null);
      setMessages([]);

      try {
        const chat = await adapter.createChat(plantId, content);
        setChatId(chat.id);
        setMessages(chat.messages);
        setStatus("active");
      } catch (error) {
        setError(
          error instanceof Error ? error.message : "Failed to start chat"
        );
        setStatus("error");
      }
    },
    [adapter, plantId]
  );

  const sendMessage = useCallback(
    async (content: string) => {
      if (!chatId) {
        setError("No active chat session");
        setStatus("error");
        return;
      }

      setStatus("loading");
      setError(null);

      try {
        const chat = await adapter.continueChat(chatId, content);
        setMessages(chat.messages);
        setStatus("active");
      } catch (error) {
        setError(
          error instanceof Error ? error.message : "Failed to send message"
        );
        setStatus("error");
      }
    },
    [adapter, chatId]
  );

  const reset = useCallback(() => {
    setMessages([]);
    setStatus("idle");
    setChatId(null);
    setError(null);
  }, []);

  return {
    messages,
    status,
    chatId,
    error,
    startChat,
    sendMessage,
    reset,
  };
}
