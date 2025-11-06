"use client";

import { ChatMessage } from "@/lib/types/chat.types";
import { Badge } from "@/components/ui/badge";
import { MarkdownMessage } from "@/components/ui/markdown-message";

interface ChatConversationProps {
  messages: ChatMessage[];
}

export function ChatConversation({ messages }: ChatConversationProps) {
  return (
    <div className="space-y-3" data-testid="chat-conversation">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === "USER" ? "justify-end" : "justify-start"}`}
          data-testid={`message-${message.role}`}
        >
          <div
            className={`max-w-[80%] rounded-lg p-3 ${
              message.role === "USER"
                ? "bg-primary text-primary-foreground"
                : "bg-muted"
            }`}
          >
            <div className="flex items-center gap-2 mb-1">
              <Badge
                variant={message.role === "USER" ? "secondary" : "outline"}
                className="text-xs"
              >
                {message.role === "USER" ? "You" : "AI"}
              </Badge>
              <span className="text-xs opacity-70">
                {new Date(message.created_at).toLocaleTimeString()}
              </span>
            </div>
            {message.role === "AI" ? (
              <MarkdownMessage content={message.content} />
            ) : (
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
