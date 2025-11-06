"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { MessageSquarePlus } from "lucide-react";

interface StartChatDialogProps {
  onStart: (content: string) => Promise<void>;
  disabled?: boolean;
}

export function StartChatDialog({ onStart, disabled }: StartChatDialogProps) {
  const [open, setOpen] = useState(false);
  const [content, setContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim()) {
      setError("Please enter a message");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onStart(content.trim());
      setContent("");
      setOpen(false);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to start chat");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="default"
          disabled={disabled}
          data-testid="start-chat-button"
        >
          <MessageSquarePlus className="h-4 w-4 mr-2" />
          Start Chat
        </Button>
      </DialogTrigger>
      <DialogContent data-testid="start-chat-dialog">
        <DialogHeader>
          <DialogTitle>Start General Chat</DialogTitle>
          <DialogDescription>
            Ask anything about your plant - care tips, propagation, ideal
            growing conditions, and more. Our AI is here to help!
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="content">Your Question</Label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="e.g., How often should I water my plant in winter?"
              className="w-full min-h-[100px] p-3 rounded-md border border-input bg-background text-sm"
              disabled={isSubmitting}
              data-testid="chat-content-input"
            />
          </div>
          {error && (
            <div className="text-sm text-destructive" data-testid="chat-error">
              {error}
            </div>
          )}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Starting..." : "Start Chat"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
