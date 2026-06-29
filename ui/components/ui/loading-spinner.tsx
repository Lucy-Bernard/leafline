// Reusable centered loading spinner. Use wherever a page or section is waiting for data.
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  text?: string;
  className?: string;
}

export function LoadingSpinner({ text, className }: LoadingSpinnerProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground",
        className
      )}
    >
      <Loader2 className="h-8 w-8 animate-spin" />
      {text && <p className="text-sm">{text}</p>}
    </div>
  );
}
