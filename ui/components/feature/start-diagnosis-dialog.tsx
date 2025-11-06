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
import { Stethoscope } from "lucide-react";

interface StartDiagnosisDialogProps {
  onStart: (prompt: string) => Promise<void>;
  disabled?: boolean;
}

export function StartDiagnosisDialog({
  onStart,
  disabled,
}: StartDiagnosisDialogProps) {
  const [open, setOpen] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!prompt.trim()) {
      setError("Please describe the issue with your plant");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onStart(prompt.trim());
      setPrompt("");
      setOpen(false);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to start diagnosis"
      );
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
          data-testid="start-diagnosis-button"
        >
          <Stethoscope className="h-4 w-4 mr-2" />
          Start Diagnosis
        </Button>
      </DialogTrigger>
      <DialogContent data-testid="start-diagnosis-dialog">
        <DialogHeader>
          <DialogTitle>Start Plant Diagnosis</DialogTitle>
          <DialogDescription>
            Describe the issue you&apos;re experiencing with your plant. Our AI
            will ask follow-up questions to provide an accurate diagnosis.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="prompt">What&apos;s wrong with your plant?</Label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., The leaves are turning yellow and drooping..."
              className="w-full min-h-[100px] p-3 rounded-md border border-input bg-background text-sm"
              disabled={isSubmitting}
              data-testid="diagnosis-prompt-input"
            />
          </div>
          {error && (
            <div
              className="text-sm text-destructive"
              data-testid="diagnosis-error"
            >
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
              {isSubmitting ? "Starting..." : "Start Diagnosis"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
