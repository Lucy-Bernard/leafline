export interface ChatMessage {
  id: string;
  chat_id: string;
  role: "USER" | "AI";
  content: string;
  created_at: string;
}

export interface GeneralChat {
  id: string;
  plant_id: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface IChatAdapter {
  getChats(plantId: string): Promise<GeneralChat[]>;
  createChat(plantId: string, content: string): Promise<GeneralChat>;
  continueChat(chatId: string, content: string): Promise<GeneralChat>;
  getChat(chatId: string): Promise<GeneralChat>;
  deleteChat(chatId: string): Promise<void>;
}
