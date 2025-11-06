"use client";

import { useEffect, useRef, useState } from "react";
import { DiagnosisMessage, DiagnosisResult } from "@/lib/types/diagnosis.types";
import { DiagnosisMessageBubble } from "./diagnosis-message-bubble";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Loader2, X } from "lucide-react";

interface ActiveDiagnosisPanelProps {
  messages: DiagnosisMessage[];
  status: "idle" | "loading" | "pending_input" | "completed" | "error";
  error: string | null;
  result: DiagnosisResult | null;
  onSendMessage: (message: string) => Promise<void>;
  onCancel: () => void;
  onComplete: () => void;
}

export function ActiveDiagnosisPanel({
  messages,
  status,
  error,
  result,
  onSendMessage,
  onCancel,
  onComplete,
}: ActiveDiagnosisPanelProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (status === "completed" && result) {
      onComplete();
    }
  }, [status, result, onComplete]);

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
            Analyzing...
          </Badge>
        );
      case "pending_input":
        return <Badge variant="default">Awaiting Response</Badge>;
      case "completed":
        return <Badge variant="outline">Completed</Badge>;
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
    <Card className="w-full" data-testid="active-diagnosis-panel">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle>Diagnosis In Progress</CardTitle>
            {getStatusBadge()}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onCancel}
            data-testid="cancel-diagnosis-button"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          className="space-y-3 max-h-[400px] overflow-y-auto scroll-smooth pr-4"
          data-testid="diagnosis-messages"
        >
          {messages.map((message, index) => (
            <DiagnosisMessageBubble key={index} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div
            className="bg-destructive/10 text-destructive px-4 py-3 rounded text-sm"
            data-testid="diagnosis-panel-error"
          >
            {error}
          </div>
        )}

        {status === "pending_input" && (
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your answer..."
              data-testid="diagnosis-input"
            />
            <Button
              type="submit"
              disabled={!input.trim()}
              data-testid="send-diagnosis-message"
            >
              Send
            </Button>
          </form>
        )}

        {status === "loading" && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
