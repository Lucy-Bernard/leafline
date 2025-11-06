import { useCallback, useEffect, useState } from "react";
import { IChatAdapter, GeneralChat } from "@/lib/types/chat.types";

export function useChats(adapter: IChatAdapter, plantId: string) {
  const [chats, setChats] = useState<GeneralChat[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchChats = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const fetchedChats = await adapter.getChats(plantId);
      const sortedChats = [...fetchedChats].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setChats(sortedChats);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to fetch chats");
    } finally {
      setIsLoading(false);
    }
  }, [adapter, plantId]);

  const deleteChat = useCallback(
    async (chatId: string) => {
      const previousChats = chats;
      setChats((prev) => prev.filter((chat) => chat.id !== chatId));

      try {
        await adapter.deleteChat(chatId);
      } catch (error) {
        setChats(previousChats);
        setError(
          error instanceof Error ? error.message : "Failed to delete chat"
        );
        throw error;
      }
    },
    [adapter, chats]
  );

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  return {
    chats,
    isLoading,
    error,
    refetch: fetchChats,
    deleteChat,
  };
}
