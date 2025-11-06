"use client";

import { useState } from "react";
import { GeneralChat } from "@/lib/types/chat.types";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { ChatConversation } from "./chat-conversation";
import { Skeleton } from "@/components/ui/skeleton";
import { Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatHistoryProps {
  chats: GeneralChat[];
  isLoading: boolean;
  onDelete?: (chatId: string) => Promise<void>;
}

export function ChatHistory({ chats, isLoading, onDelete }: ChatHistoryProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [chatToDelete, setChatToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setChatToDelete(chatId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!chatToDelete || !onDelete) return;

    setIsDeleting(true);
    try {
      await onDelete(chatToDelete);
      setDeleteDialogOpen(false);
      setChatToDelete(null);
    } catch (error) {
      console.error("Failed to delete chat:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4" data-testid="chat-loading">
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  if (chats.length === 0) {
    return (
      <Card data-testid="chat-empty-state">
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              No chat history yet. Start a conversation to get general advice
              about your plant.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <div data-testid="chat-history">
        <Accordion type="single" collapsible className="space-y-4">
          {chats.map((chat) => (
            <AccordionItem
              key={chat.id}
              value={chat.id}
              className="!border rounded-lg px-4"
              data-testid="chat-item"
            >
              <AccordionTrigger className="hover:no-underline">
                <div className="flex items-start justify-between w-full pr-4">
                  <div className="flex-1 text-left">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline">
                        {chat.messages.length} messages
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(chat.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {chat.messages.length > 0 && (
                      <p className="text-sm font-normal line-clamp-2">
                        {chat.messages[0].content}
                      </p>
                    )}
                  </div>
                  {onDelete && (
                    <div
                      role="button"
                      tabIndex={0}
                      className={cn(
                        "inline-flex items-center justify-center rounded-md size-8 transition-all hover:bg-accent hover:text-accent-foreground shrink-0"
                      )}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteClick(chat.id, e);
                      }}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          e.stopPropagation();
                          handleDeleteClick(chat.id, e as unknown as React.MouseEvent);
                        }
                      }}
                      data-testid="delete-chat-button"
                    >
                      <Trash2 className="h-4 w-4" />
                    </div>
                  )}
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <div className="pt-4">
                  <ChatConversation messages={chat.messages} />
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent data-testid="delete-chat-dialog">
          <DialogHeader>
            <DialogTitle>Delete Chat</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this chat? This action cannot be
              undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={isDeleting}
              data-testid="confirm-delete-chat"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
