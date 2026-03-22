"use client";

import { PlantsGrid } from "@/components/feature/plants-grid";
import { PlantsLoading } from "@/components/feature/plants-loading";
import { AddPlantButton } from "@/components/feature/add-plant-button";
import { usePlants } from "@/lib/hooks/use-plants";
import { PlantApiAdapter } from "@/lib/adapters/plant-api.adapter";

const plantAdapter = new PlantApiAdapter();

export default function DashboardPage() {
  const { plants, isLoading, isCreating, error, createPlant, deletePlant } =
    usePlants(plantAdapter);

  const handleAddPlant = async (image: string) => {
    await createPlant({ image });
  };

  return (
    <div className="flex-1 w-full flex flex-col gap-12">
      <div className="flex flex-col gap-2 items-start">
        <h1 className="font-bold text-4xl mb-4">My Plants</h1>
        <p className="text-lg text-muted-foreground">
          View and manage all your plants.
        </p>
      </div>

      {error &&
        (() => {
          console.log("Plant loading error:", error);
          return (
            <div
              className="bg-destructive/10 text-destructive px-4 py-3 rounded"
              data-testid="error-message"
            >
              <p className="font-semibold">Error loading plants</p>
              <p className="text-sm">Try uploading a clearer image.</p>
            </div>
          );
        })()}

      {isLoading && <PlantsLoading />}

      {!isLoading && !error && plants.length === 0 && (
        <div className="grid grid-cols-1 gap-6">
          <AddPlantButton onAddPlant={handleAddPlant} isLoading={isCreating} />
        </div>
      )}

      {!isLoading && !error && plants.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AddPlantButton onAddPlant={handleAddPlant} isLoading={isCreating} />
          {plants.map((plant) => (
            <PlantsGrid
              key={plant.id}
              plants={[plant]}
              onDelete={deletePlant}
            />
          ))}
        </div>
      )}
    </div>
  );
}
