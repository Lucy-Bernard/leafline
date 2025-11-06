"use client";

import { DiagnosisSession } from "@/lib/types/diagnosis.types";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trash2 } from "lucide-react";
import { useState } from "react";
import { DiagnosisConversation } from "./diagnosis-conversation";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface DiagnosisHistoryProps {
  diagnoses: DiagnosisSession[];
  isLoading: boolean;
  onDelete: (id: string) => Promise<void>;
}

export function DiagnosisHistory({
  diagnoses,
  isLoading,
  onDelete,
}: DiagnosisHistoryProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const handleDelete = async (id: string) => {
    if (confirmDeleteId !== id) {
      setConfirmDeleteId(id);
      return;
    }

    setDeletingId(id);
    try {
      await onDelete(id);
      setConfirmDeleteId(null);
    } catch {
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4" data-testid="diagnosis-loading">
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  if (diagnoses.length === 0) {
    return (
      <Card data-testid="diagnosis-empty-state">
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              No diagnosis history yet. Start a diagnosis to get AI-powered help
              with plant issues.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getStatusVariant = (
    status: DiagnosisSession["status"]
  ): "default" | "secondary" | "outline" => {
    switch (status) {
      case "COMPLETED":
        return "default";
      case "PENDING_USER_INPUT":
        return "secondary";
      case "CANCELLED":
        return "outline";
    }
  };

  return (
    <div data-testid="diagnosis-history">
      <Accordion type="single" collapsible className="space-y-4">
        {diagnoses.map((diagnosis) => (
          <AccordionItem
            key={diagnosis.id}
            value={diagnosis.id}
            className="!border rounded-lg px-4"
            data-testid="diagnosis-item"
          >
            <AccordionTrigger className="hover:no-underline">
              <div className="flex items-start justify-between w-full pr-4">
                <div className="flex-1 text-left">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={getStatusVariant(diagnosis.status)}>
                      {diagnosis.status.replace("_", " ")}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(diagnosis.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-sm font-normal line-clamp-2">
                    {diagnosis.diagnosis_context.initial_prompt}
                  </p>
                </div>
                <div
                  role="button"
                  tabIndex={0}
                  className={cn(
                    "inline-flex items-center justify-center rounded-md size-9 transition-all hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-50",
                    confirmDeleteId === diagnosis.id &&
                      "bg-destructive text-white hover:bg-destructive/90",
                    deletingId === diagnosis.id && "pointer-events-none opacity-50"
                  )}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(diagnosis.id);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      e.stopPropagation();
                      handleDelete(diagnosis.id);
                    }
                  }}
                  data-testid="delete-diagnosis-button"
                >
                  {deletingId === diagnosis.id ? (
                    <span className="animate-spin">⏳</span>
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                </div>
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <div className="pt-4">
                <DiagnosisConversation
                  conversation={diagnosis.diagnosis_context.conversation_history}
                  result={diagnosis.diagnosis_context.result}
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}
