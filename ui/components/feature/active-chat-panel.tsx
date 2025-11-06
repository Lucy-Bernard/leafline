"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMessage } from "@/lib/types/chat.types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Loader2, X, Send } from "lucide-react";
import { cn } from "@/lib/utils";
import { MarkdownMessage } from "@/components/ui/markdown-message";

interface ActiveChatPanelProps {
  messages: ChatMessage[];
  status: "idle" | "loading" | "active" | "error";
  error: string | null;
  onSendMessage: (message: string) => Promise<void>;
  onCancel: () => void;
}

export function ActiveChatPanel({
  messages,
  status,
  error,
  onSendMessage,
  onCancel,
}: ActiveChatPanelProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || status === "loading") {
      return;
    }

    const message = input.trim();
    setInput("");

    await onSendMessage(message);
  };

  const getStatusBadge = () => {
    switch (status) {
      case "loading":
        return (
          <Badge variant="secondary">
            <Loader2 className="h-3 w-3 mr-1 animate-spin" />
            AI is typing...
          </Badge>
        );
      case "active":
        return <Badge variant="default">Active</Badge>;
      case "error":
        return <Badge variant="destructive">Error</Badge>;
      default:
        return null;
    }
  };

  if (status === "idle") {
    return null;
  }

  return (
    <Card className="w-full" data-testid="active-chat-panel">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle>General Chat</CardTitle>
            {getStatusBadge()}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onCancel}
            data-testid="cancel-chat-button"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          className="space-y-3 max-h-[500px] overflow-y-auto scroll-smooth pr-4"
          data-testid="chat-messages"
        >
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex",
                message.role === "USER" ? "justify-end" : "justify-start"
              )}
              data-testid={`chat-message-${message.role}`}
            >
              <div
                className={cn(
                  "max-w-[80%] rounded-lg p-3",
                  message.role === "USER"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
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
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div
            className="bg-destructive/10 text-destructive px-4 py-3 rounded text-sm"
            data-testid="chat-panel-error"
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={status === "loading"}
            data-testid="chat-input"
          />
          <Button
            type="submit"
            disabled={!input.trim() || status === "loading"}
            data-testid="send-chat-message"
          >
            {status === "loading" ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
