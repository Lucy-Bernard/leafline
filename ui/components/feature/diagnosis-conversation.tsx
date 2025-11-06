"use client";

import {
  DiagnosisMessage,
  DiagnosisResult,
} from "@/lib/types/diagnosis.types";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { MarkdownMessage } from "@/components/ui/markdown-message";

interface DiagnosisConversationProps {
  conversation: DiagnosisMessage[];
  result?: DiagnosisResult;
}

export function DiagnosisConversation({
  conversation,
  result,
}: DiagnosisConversationProps) {
  return (
    <div className="space-y-4" data-testid="diagnosis-conversation">
      <div className="space-y-3">
        {conversation.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
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
        ))}
      </div>

      {result && (
        <>
          <Separator />
          <Card data-testid="diagnosis-result">
            <CardContent className="pt-6">
              <div className="space-y-3">
                <div>
                  <h4 className="font-semibold text-sm text-muted-foreground mb-1">
                    DIAGNOSIS
                  </h4>
                  <MarkdownMessage content={result.finding} className="font-semibold" />
                </div>
                <Separator />
                <div>
                  <h4 className="font-semibold text-sm text-muted-foreground mb-1">
                    RECOMMENDATION
                  </h4>
                  <MarkdownMessage content={result.recommendation} />
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
