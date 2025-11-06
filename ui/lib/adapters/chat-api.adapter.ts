import { IChatAdapter, GeneralChat } from "@/lib/types/chat.types";
import { ChatArraySchema, GeneralChatSchema } from "@/lib/schemas/chat.schema";
import { API_ENDPOINTS, getAuthHeaders } from "@/lib/config/api.config";

export class ChatApiAdapter implements IChatAdapter {
  async getChats(plantId: string): Promise<GeneralChat[]> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.PLANT_CHATS(plantId), {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch chats: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = ChatArraySchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to fetch chats");
    }
  }

  async createChat(plantId: string, content: string): Promise<GeneralChat> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.CHAT_CREATE(plantId), {
        method: "POST",
        headers,
        body: JSON.stringify({ content }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create chat: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = GeneralChatSchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to create chat");
    }
  }

  async continueChat(chatId: string, content: string): Promise<GeneralChat> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.CHAT(chatId), {
        method: "PUT",
        headers,
        body: JSON.stringify({ content }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Chat with ID ${chatId} not found`);
        }
        throw new Error(`Failed to continue chat: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = GeneralChatSchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to continue chat");
    }
  }

  async getChat(chatId: string): Promise<GeneralChat> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.CHAT(chatId), {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Chat with ID ${chatId} not found`);
        }
        throw new Error(`Failed to fetch chat: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = GeneralChatSchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to fetch chat");
    }
  }

  async deleteChat(chatId: string): Promise<void> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.CHAT(chatId), {
        method: "DELETE",
        headers,
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Chat with ID ${chatId} not found`);
        }
        throw new Error(`Failed to delete chat: ${response.statusText}`);
      }
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to delete chat");
    }
  }
}
