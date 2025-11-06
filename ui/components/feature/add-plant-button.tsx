"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Plus } from "lucide-react";
import { AddPlantDialog } from "./add-plant-dialog";

interface AddPlantButtonProps {
  onAddPlant: (image: string) => Promise<void>;
  isLoading?: boolean;
}

export function AddPlantButton({ onAddPlant, isLoading = false }: AddPlantButtonProps) {
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <>
      <Card
        className="overflow-hidden hover:shadow-lg transition-shadow border-dashed cursor-pointer"
        data-testid="add-plant-button"
        onClick={() => setDialogOpen(true)}
      >
        <CardContent className="flex flex-col items-center justify-center py-12 px-6">
          <div className="rounded-full bg-primary/10 p-6 mb-4">
            <Plus className="h-12 w-12 text-primary" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Add New Plant</h3>
          <p className="text-muted-foreground text-center mb-4">
            Identify your plant and start tracking its care
          </p>
          <Button size="lg">Add Plant</Button>
        </CardContent>
      </Card>

      <AddPlantDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onSubmit={onAddPlant}
        isLoading={isLoading}
      />
    </>
  );
}
