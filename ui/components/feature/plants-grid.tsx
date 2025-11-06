"use client";

import { Plant } from "@/lib/types/plant.types";
import { PlantCard } from "./plant-card";

interface PlantsGridProps {
  plants: Plant[];
  onDelete: (id: string) => Promise<void>;
}

export function PlantsGrid({ plants, onDelete }: PlantsGridProps) {
  if (plants.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center py-12 text-center"
        data-testid="empty-state"
      >
        <span className="text-6xl mb-4">🌱</span>
        <h3 className="text-xl font-semibold mb-2">No plants yet</h3>
        <p className="text-muted-foreground">
          Add your first plant to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1  gap-6" data-testid="plants-grid">
      {plants.map((plant) => (
        <PlantCard key={plant.id} plant={plant} onDelete={onDelete} />
      ))}
    </div>
  );
}
