"use client";

import { DiagnosisMessage } from "@/lib/types/diagnosis.types";
import { Badge } from "@/components/ui/badge";
import { MarkdownMessage } from "@/components/ui/markdown-message";

interface DiagnosisMessageBubbleProps {
  message: DiagnosisMessage;
}

export function DiagnosisMessageBubble({
  message,
}: DiagnosisMessageBubbleProps) {
  return (
    <div
      className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in-50 slide-in-from-bottom-5`}
      data-testid={`message-${message.role}`}
    >
      <div
        className={`max-w-[80%] rounded-lg p-3 ${
          message.role === "user"
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        }`}
      >
        <div className="flex items-center gap-2 mb-1">
          <Badge
            variant={message.role === "user" ? "secondary" : "outline"}
            className="text-xs"
          >
            {message.role === "user" ? "You" : "AI"}
          </Badge>
        </div>
        {message.role === "assistant" ? (
          <MarkdownMessage content={message.message} />
        ) : (
          <p className="text-sm whitespace-pre-wrap">{message.message}</p>
        )}
      </div>
    </div>
  );
}
