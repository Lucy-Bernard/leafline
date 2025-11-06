"use client";

import { cn } from "@/lib/utils";
import { memo } from "react";
import { Streamdown } from "streamdown";

interface MarkdownMessageProps {
  content: string;
  className?: string;
}

export const MarkdownMessage = memo(
  ({ content, className }: MarkdownMessageProps) => (
    <Streamdown
      className={cn(
        "text-sm prose prose-sm dark:prose-invert max-w-none",
        "prose-headings:font-semibold prose-headings:mt-3 prose-headings:mb-2",
        "prose-p:my-2 prose-p:leading-relaxed",
        "prose-ul:my-2 prose-ol:my-2 prose-li:my-1",
        "prose-code:text-xs prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:rounded",
        "prose-pre:my-2 prose-pre:bg-muted prose-pre:border prose-pre:border-border",
        "prose-a:text-primary prose-a:no-underline hover:prose-a:underline",
        "prose-strong:font-semibold prose-em:italic",
        "prose-table:text-sm prose-table:my-2",
        "prose-th:border prose-th:border-border prose-th:bg-muted prose-th:px-2 prose-th:py-1",
        "prose-td:border prose-td:border-border prose-td:px-2 prose-td:py-1",
        "[&>*:first-child]:mt-0 [&>*:last-child]:mb-0",
        className
      )}
    >
      {content}
    </Streamdown>
  ),
  (prevProps, nextProps) => prevProps.content === nextProps.content
);

MarkdownMessage.displayName = "MarkdownMessage";
