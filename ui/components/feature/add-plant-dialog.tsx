"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, X } from "lucide-react";
import Image from "next/image";
import { fileToBase64 } from "@/lib/utils";

interface AddPlantDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (image: string) => Promise<void>;
  isLoading?: boolean;
}

export function AddPlantDialog({
  open,
  onOpenChange,
  onSubmit,
  isLoading = false,
}: AddPlantDialogProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError("Please select an image file");
      return;
    }

    setError(null);
    setSelectedFile(file);

    const previewUrl = URL.createObjectURL(file);
    setPreview(previewUrl);
  };

  const removeFile = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    
    setSelectedFile(null);
    setPreview(null);
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select an image");
      return;
    }

    try {
      setError(null);
      const base64Image = await fileToBase64(selectedFile);
      
      await onSubmit(base64Image);
      
      if (preview) {
        URL.revokeObjectURL(preview);
      }
      setSelectedFile(null);
      setPreview(null);
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add plant");
    }
  };

  const handleClose = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setSelectedFile(null);
    setPreview(null);
    setError(null);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add New Plant</DialogTitle>
          <DialogDescription>
            Upload a photo of your plant to identify it and start tracking its care.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="plant-image">Plant Image</Label>
            <div className="flex items-center gap-2">
              <Input
                id="plant-image"
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                disabled={isLoading}
                className="cursor-pointer"
              />
              <Upload className="h-4 w-4 text-muted-foreground" />
            </div>
          </div>

          {preview && (
            <div className="relative group">
              <Image
                src={preview}
                alt="Plant preview"
                width={400}
                height={256}
                className="w-full h-64 object-cover rounded-md border"
              />
              <Button
                type="button"
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2 h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={removeFile}
                disabled={isLoading}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleSubmit}
            disabled={isLoading || !selectedFile}
          >
            {isLoading ? "Identifying..." : "Add Plant"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
